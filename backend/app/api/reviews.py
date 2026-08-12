from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.db.database import get_db
from app.models.review import Review
from app.models.product import Product
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewResponse
from app.core.security import get_current_user
import json

from app.core.summarization import generate_review_summary
from app.schemas.review import ReviewSummaryResponse

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.get("/product/{product_id}", response_model=list[ReviewResponse])
def get_product_reviews(product_id: int, db: Session = Depends(get_db)):
    return (
        db.query(Review)
        .options(joinedload(Review.user))
        .filter(Review.product_id == product_id)
        .order_by(Review.id.desc())
        .all()
    )


@router.post("/product/{product_id}", response_model=ReviewResponse)
def submit_review(
    product_id: int,
    review_in: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    existing = (
        db.query(Review)
        .filter(Review.user_id == current_user.id, Review.product_id == product_id)
        .first()
    )

    if existing:
        existing.rating = review_in.rating
        existing.comment = review_in.comment
        db.commit()
        db.refresh(existing)
        return existing

    new_review = Review(
        user_id=current_user.id,
        product_id=product_id,
        rating=review_in.rating,
        comment=review_in.comment,
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    if review.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own review")

    db.delete(review)
    db.commit()

MIN_REVIEWS_FOR_SUMMARY = 3


@router.get("/product/{product_id}/summary", response_model=ReviewSummaryResponse)
def get_review_summary(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    reviews = db.query(Review).filter(Review.product_id == product_id).all()
    if len(reviews) < MIN_REVIEWS_FOR_SUMMARY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Summary ke liye kam se kam {MIN_REVIEWS_FOR_SUMMARY} reviews chahiye.",
        )

    cached = None
    if product.review_summary:
        try:
            cached = json.loads(product.review_summary)
        except (TypeError, ValueError):
            cached = None

    if cached and cached.get("based_on") == len(reviews):
        return cached

    comments = [r.comment for r in reviews if r.comment]
    ratings = [r.rating for r in reviews]
    result = generate_review_summary(product.name, comments, ratings)
    result["based_on"] = len(reviews)

    product.review_summary = json.dumps(result)
    db.commit()

    return result