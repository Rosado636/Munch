from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from ..models import Restaurant
from ..db import engine

router = APIRouter()

def get_session():
    with Session(engine) as session:
        yield session

@router.get("/restaurants")
def list_restaurants(session: Session = Depends(get_session)):
    return session.exec(select(Restaurant)).all()

@router.post("/restaurants")
def create_restaurant(restaurant: Restaurant, session: Session = Depends(get_session)):
    session.add(restaurant)
    session.commit()
    session.refresh(restaurant)
    return restaurant