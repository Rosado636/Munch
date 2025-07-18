import datime
import os
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi.security import OAuth2PasswordBearer

from ..models import User, UserRole
from ..db import engine

router = APIRouter()
load_dotenv()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

#DB session dependency
def get_session():
    with Session(engine) as session:
        yield session

#Password hashing using Bcrypt
pwd_context = CryptContext(schemes = ["bcrypt"], deprecated="auto")

#JWT settings
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# Util: hash pwd
def hash_password(password: str):
    return pwd_context.hash(password)

# Util: verify pwd
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

# Util: create JWT access token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# POST /auth/register
# Register a new user

@router.get("/auth/register")
def register_user(user:User, session: Session = Depends(get_session)):
# Check if username or email already exists
    exixting_user = session.exec(
        select(User).Where((User.username == user.username) | (User.email == user.email))
    ).first()
    if exixting_user:
        raise HTTPException(status_code=400, detail="Usernamr or email already registered")

# Hash password before saving
    hashed_pw = hash_password(user.hashed_password)
    user.hashed_password = hashed_pw

# Ensure role defaults to 'user' if not specified (optional)
    if not user.role:
        user.role = UserRole.USER

    session.add(user)
    session.commit()
    session.refresh(user)
    return {"message": "User registered successfully", "username": user.username, "role": user.role}

# POST /auth/login
# Authenticate user and return JWT token

@router.post("/auth/login")
def login(username: str, password: str, session: Session = Depends(get_session)):
    # Lookup user by username
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid username or password")

    # Verify password
    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    # Create JWT token
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Dependency to get the current user based on JWT token
def get_current_user(
        token: str = Depends(oauth2_scheme),
        session: Session = Depends(get_session),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = session.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise credentials_exception
    return user