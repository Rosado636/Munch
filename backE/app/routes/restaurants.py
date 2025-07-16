# app/routes/restaurants.py

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..models import Restaurant, Review
from ..db import engine

router = APIRouter()

# Dependency to get a DB session
def get_session():
    with Session(engine) as session:
        yield session

# GET /restaurants - list all restaurants
# Get a paginated list of restaurants
@router.get("/restaurants")
def list_restaurants(session: Session = Depends(get_session),
                     limit: int = 10,
                     offset: int = 0
):
    # Query restaurants with pagination
    restaurants = (session.exec(select(Restaurant)
                               .offset(offset)
                               .limit(limit))
                   .all())
    return restaurants

# GET /restaurants/{id} - get a single restaurant by ID
@router.get("/restaurants/{id}")
def get_restaurant(id: int, session: Session = Depends(get_session)
):
    restaurant = session.get(Restaurant, id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    return restaurant

# POST /restaurants - create a new restaurant
@router.post("/restaurants")
def create_restaurant(restaurant: Restaurant, session: Session = Depends(get_session)):
    session.add(restaurant)
    session.commit()
    session.refresh(restaurant)
    return restaurant

# PUT /restaurants/{id} - update an existing restaurant
@router.put("/restaurants/{id}")
def update_restaurant(id: int, updated_data: Restaurant, session: Session = Depends(get_session)):
    restaurant = session.get(Restaurant, id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    restaurant.name = updated_data.name
    restaurant.description = updated_data.description
    restaurant.location = updated_data.location
    restaurant.rating = updated_data.rating
    restaurant.image = updated_data.image
    restaurant.category = updated_data.category
    restaurant.website = updated_data.website

    session.commit()
    session.refresh(restaurant)
    return restaurant

# DELETE /restaurants/{id} - delete a restaurant
@router.delete("/restaurants/{id}")
def delete_restaurant(id: int, session: Session = Depends(get_session)):
    restaurant = session.get(Restaurant, id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    session.delete(restaurant)
    session.commit()
    return {"message": f"Restaurant {id} deleted successfully"}

# GET /restaurants/{id}/average-rating
# Returns the average rating and review count for a given restaurant.
@router.get("/restaurants/{id}/average-rating")
def get_average_rating(id: int, session: Session = Depends(get_session)
):
# Fetch the restaurant by ID to ensure it exists
    restaurant = session.get(Restaurant, id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

# Fetch all non-deleted reviews for this restaurant
    reviews = session.exec(
        select(Review)
        .where(
            (Review.restaurant_id) & (Review.deleted == False)  # Combine conditions with &
        )
    ).all()

# If there are no reviews, return None for average_rating
    if not reviews:
        return {
            "average_rating": None,
            "review_count": 0
        }

# Calculate average rating from review ratings
    average = sum([r.rating for r in reviews]) / len(reviews)

# Return rounded average and count
    return {
        "average_rating": round(average, 2),
        "review_count": len(reviews)
    }