from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..models import Review, ReviewCreate, Restaurant, User
from routes.auth import get_current_user
from ..db import engine

router = APIRouter()

# Dependency to provide a database session
def get_session():
    with Session(engine) as session:
        yield session

# POST /restaurants/{restaurant_id}/reviews
# Add a new review for a restaurant
@router.post("/restaurants/{restaurant_id}/reviews")
def add_review(
        restaurant_id: int,
        review_data: ReviewCreate,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    # Check if the restaurant exists
    restaurant = session.get(Restaurant, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    # Create new review object
    review = Review(
        restaurant_id=restaurant_id,
        reviewer=review_data.reviewer,
        rating=review_data.rating,
        comment=review_data.comment
    )

    # Save to database
    session.add(review)
    session.commit()
    session.refresh(review)
    return review

# GET /restaurants/{restaurant_id}/reviews
# Get paginated list of reviews (excluding soft-deleted)
@router.get("/restaurants/{restaurant_id}/reviews")
def get_reviews(
        restaurant_id: int,
        session: Session = Depends(get_session),
        limit: int = 10,
        offset: int = 0
):
    # Check if the restaurant exists
    restaurant = session.get(Restaurant, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    # Query reviews, apply offset and limit, exclude deleted
    reviews = session.exec(
        select(Review)
        .where(
            (Review.restaurant_id == restaurant_id) & (Review.deleted == False)
        )
        .offset(offset)
        .limit(limit)
    ).all()

    return reviews

# PUT /reviews/{review_id}
# Update an existing review (only if not deleted)
@router.put("/reviews/{review_id}")
def update_review(
        review_id: int,
        updated_data: ReviewCreate,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    # Fetch review by ID
    review = session.get(Review, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    # Block updates if review is soft-deleted
    if review.deleted:
        raise HTTPException(status_code=400, detail="Cannot update a deleted review")

    # Update fields
    review.reviewer = updated_data.reviewer
    review.rating = updated_data.rating
    review.comment = updated_data.comment

    # Commit changes
    session.commit()
    session.refresh(review)
    return review

# DELETE /reviews/{review_id}
# Soft delete a review with a required reason
@router.delete("/reviews/{review_id}")
def delete_review(
        review_id: int,
        reason: str,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    # Fetch review by ID
    review = session.get(Review, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    # Validate allowed reasons
    valid_reasons = ["spam", "offensive", "admin_request", "other"]
    if reason.lower() not in valid_reasons:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid reason provided. Allowed values: {', '.join(valid_reasons)}"
        )

    # Apply soft delete and record reason
    review.deleted = True
    review.delete_reason = reason
    session.commit()

    return {"message": f"Review {review_id} marked as deleted for reason: {reason}"}

