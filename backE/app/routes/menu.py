from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..models import Menu, Restaurant
from ..db import engine

router = APIRouter()

# Dependency to provide a DB session
def get_session():
    with Session(engine) as session:
        yield session

# POST /restaurants/{restaurant_id}/menu
# Add a new menu item for a restaurant
@router.post("/restaurants/{restaurant_id}/menu")
def create_menu_item(
        restaurant_id: int,
        menu_item: Menu,
        session: Session = Depends(get_session)
):
    # Check if restaurant exists
    restaurant = session.get(Restaurant, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    # Link menu item to restaurant
    menu_item.restaurant_id = restaurant_id

    # Save to DB
    session.add(menu_item)
    session.commit()
    session.refresh(menu_item)
    return menu_item

# GET /restaurants/{restaurant_id}/menu
# Get paginated list of menu items for a restaurant
@router.get("/restaurants/{restaurant_id}/menu")
def list_menu_items(
        restaurant_id: int,
        session: Session = Depends(get_session),
        limit: int = 10,
        offset: int = 0
):
    # Ensure restaurant exists
    restaurant = session.get(Restaurant, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    # Query menu items with pagination
    menu_items = session.exec(
        select(Menu)
        .where(Menu.restaurant_id == restaurant_id)
        .offset(offset)
        .limit(limit)
    ).all()

    return menu_items

# GET /menu/{menu_id}
# Retrieve a single menu item by ID
@router.get("/menu/{menu_id}")
def get_menu_item(menu_id: int, session: Session = Depends(get_session)):
    menu_item = session.get(Menu, menu_id)
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return menu_item

# PUT /menu/{menu_id}
# Update an existing menu item
@router.put("/menu/{menu_id}")
def update_menu_item(
        menu_id: int,
        updated_item: Menu,
        session: Session = Depends(get_session)
):
    menu_item = session.get(Menu, menu_id)
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    # Update fields
    menu_item.name = updated_item.name
    menu_item.description = updated_item.description
    menu_item.price = updated_item.price

    session.commit()
    session.refresh(menu_item)
    return menu_item

# DELETE /menu/{menu_id}
# Delete a menu item
@router.delete("/menu/{menu_id}")
def delete_menu_item(menu_id: int, session: Session = Depends(get_session)):
    menu_item = session.get(Menu, menu_id)
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    session.delete(menu_item)
    session.commit()
    return {"message": f"Menu item {menu_id} deleted successfully"}
