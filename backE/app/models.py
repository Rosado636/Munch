from typing import Optional, List
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum

# Restaurant model

class Restaurant(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str
    location: str
    rating: Optional[float] = 0.0
    image: str
    category: str
    website: Optional[str] = None

    # Relationships (not required for basic functionality but useful)
    reviews: List["Review"] = Relationship(back_populates="restaurant")
    menu_items: List["Menu"] = Relationship(back_populates="restaurant")

# Review model

class Review(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    restaurant_id: int = Field(foreign_key="restaurant.id")
    reviewer: str
    rating: float
    comment: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    deleted: bool = Field(default=False)
    delete_reason: Optional[str] = Field(default=None)

    # Relationship back to Restaurant (optional)
    restaurant: Optional[Restaurant] = Relationship(back_populates="reviews")

# ReviewCreate schema
# Used for POST/PUT input

class ReviewCreate(SQLModel):
    reviewer: str
    rating: float
    comment: str

# Menu model
# Represents a menu item for a restaurant

class Menu(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    restaurant_id: int = Field(foreign_key="restaurant.id")  # Link menu item to restaurant
    name: str  # Menu item name
    description: Optional[str] = None  # Menu item description
    price: float  # Price of the item

    # Relationship back to Restaurant (optional)
    restaurant: Optional[Restaurant] = Relationship(back_populates="menu_items")

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    BLOGGER = "blogger"
    RESTAURANT_OWNER = "restaurant_owner"


    #User model
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    role: UserRole = Field(default=UserRole.USER)
