# app/routes/restaurants.py

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..models import Restaurant
from ..db import engine

router = APIRouter()

# Dependency to get a DB session
def get_session():
    with Session(engine) as session:
        yield session

# GET /restaurants - list all restaurants
@router.get("/restaurants")
def list_restaurants(session: Session = Depends(get_session)):
    restaurants = session.exec(select(Restaurant)).all()
    return restaurants

# GET /restaurants/{id} - get a single restaurant by ID
@router.get("/restaurants/{id}")
def get_restaurant(id: int, session: Session = Depends(get_session)):
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
