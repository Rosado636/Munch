# app/models.py
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field
from typing import Optional

class Restaurant(SQLModel, table=True):
    # Primary key - auto-generated
    id: Optional[int] = Field(default=None, primary_key=True)

    # Restaurant name (required)
    name: str

    # Short description (required)
    description: str

    # Location, e.g. "Austin, TX" (required)
    location: str

    # Average rating, default is 0.0
    rating: Optional[float] = 0.0

    # Image URL to display the restaurant
    image: str

    # Food category, e.g. "Mexican", "Burgers"
    category: str

    # Website link (optional)
    website: Optional[str] = None

class Review(SQLModel, table=True):
    #Primary key
    id: Optional[int] = Field(default=None, primary_key=True)

    # Link this review to a specific restaurant
    restaurant_id: int = Field(foreign_key="restaurant.id")

    # Reviewer's name
    reviewer: str

    #Review rating
    rating: float

    #Comment
    comment: str

    # When it was created (auto-generated)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ReviewCreate(SQLModel):
    reviewer: str
    rating: float
    comment: str