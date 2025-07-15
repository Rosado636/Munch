from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..models import Review, ReviewCreate, Restaurant
from ..db import engine

router = APIRouter()

# Dependency to get a DB session
def get_session():
    with Session(engine) as session:
        yield session

# POST /restaurants/{id}/reviews - Add a review to a restaurant
@router.post("/restaurants/{restaurant_id}/reviews")
def add_review(restaurant_id: int, review_data: ReviewCreate, session: Session = Depends(get_session)):
    # Look up the restaurant
    restaurant = session.get(Restaurant, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    # Create review object and link to restaurant
    review = Review(
        restaurant_id=restaurant_id,
        reviewer=review_data.reviewer,
        rating=review_data.rating,
        comment=review_data.comment
    )

    session.add(review)
    session.commit()
    session.refresh(review)
    return review

# GET /restaurants/{id}/reviews - Get all reviews for a restaurant
@router.get("/restaurants/{restaurant_id}/reviews")
def get_reviews(restaurant_id: int, session: Session = Depends(get_session)):
    # Ensure the restaurant exists
    restaurant = session.get(Restaurant, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    # Fetch all reviews tied to this restaurant
    reviews = session.exec(
        select(Review)
        .where(
            Review.restaurant_id == restaurant_id,
            Review.deleted == False #Exclude soft deletes
        )
    ).all()
    return reviews

@router.delete("/reviews/{review_id}")
def delete_review(review_id: int, reason: str, session: Session = Depends(get_session)):
    review = session.get(Review, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    #Validate deletion reason
    valid_reasons = ["Spam", "Offensive", "Admin_request", "Other"]
    if reason.lower() not in valid_reasons:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid reason provided. Allowed values: {', '.join(valid_reasons)}"
        )
    #Soft delete the review and record reason
    review.deleted = True
    review.delete_reason = reason
    session.commit()

    return {"message": f"Review {review_id} marked as deleted for reason: {reason}"}

@router.put("/reviews/{review_id}")
def update_review(
        review_id: int,
        updated_data: ReviewCreate,
        session: Session = Depends(get_session)
):
    #Fetch the review
    review = session.get(Review, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    #Prevent editing if review have been soft delete
    if review.deleted:
        raise HTTPException(status_code=404, detail="Cannot update deleted review")

    #update fields
    review.reviewer = updated_data.reviewer
    review.rating = updated_data.rating
    review.comment = updated_data.comment

    #save changes
    session.commit()
    session.refresh(review)
    return review
