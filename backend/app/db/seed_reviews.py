"""
Demo/testing ke liye realistic dummy reviews seed karta hai — kuch
fake "customer" users banata hai, aur chuninda products pe mixed
(positive/negative/neutral) reviews chhod deta hai.

Ye sirf demo purpose ke liye hai (asli users ke reviews nahi hain
abhi tak) — AI Review Summarization feature test karne ke liye
kuch real text chahiye tha.

Resumable hai: dobara chalane par pehle se maujood reviews (same
user+product) dobara nahi banega.

Run: backend/ folder se (venv active):
    python -m app.db.seed_reviews
"""

import random

from app.core.security import hash_password
from app.db.database import SessionLocal
from app.models.category import Category
from app.models.product import Product
from app.models.review import Review
from app.models.user import User

random.seed(42)  # taake har baar chalane pe same demo data bane

REVIEWER_NAMES = [
    "Ayesha K.", "Bilal Ahmed", "Sara Malik", "Usman Tariq",
    "Hina Raza", "Faisal Iqbal", "Mehak Noor", "Ali Hassan",
    "Sana Yousaf", "Kamran Sheikh",
]

COMMENTS_BY_RATING = {
    5: [
        "Excellent quality, exactly as described. Very happy with this purchase.",
        "Loved it! Fast delivery and the product feels premium.",
        "Best purchase I've made on this site so far, highly recommend.",
        "Perfect fit and great material. Will buy again.",
        "Exceeded my expectations, worth every rupee.",
    ],
    4: [
        "Good product overall, though packaging could be better.",
        "Quality is nice but delivery took a bit longer than expected.",
        "Pretty satisfied, minor color difference from the photo.",
        "Works well, comfortable, just wish it came in more sizes.",
        "Solid purchase, would recommend with small reservations.",
    ],
    3: [
        "It's okay, nothing special but does the job.",
        "Average quality for the price, expected slightly better.",
        "Decent but not as durable as I hoped.",
        "Mixed feelings — looks good but feels a bit cheaply made.",
    ],
    2: [
        "Quality was below expectations, started wearing out quickly.",
        "Delivery was delayed by almost a week, product is okay though.",
        "Not as comfortable as it looked in pictures.",
        "Sizing runs small, had to return for exchange.",
    ],
    1: [
        "Very disappointed, product arrived damaged.",
        "Poor quality material, would not recommend.",
        "Completely different from what was shown in photos.",
        "Waste of money, broke within a week of use.",
    ],
}

# E-commerce mein reviews aksar positive-skewed hoti hain — isliye
# weights aise rakhe hain (5-star sabse common, 1-star sabse rare)
RATING_WEIGHTS = {5: 40, 4: 30, 3: 15, 2: 10, 1: 5}

REVIEWS_PER_PRODUCT_RANGE = (4, 9)
PRODUCTS_TO_SEED = 30


def get_or_create_reviewers(db):
    reviewers = []
    for i, name in enumerate(REVIEWER_NAMES, start=1):
        email = f"demo.reviewer{i}@nexcart.local"
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                full_name=name,
                email=email,
                hashed_password=hash_password("DemoReviewer123!"),
                role="customer",
                is_active=True,
                is_verified=True,
            )
            db.add(user)
            db.flush()
        reviewers.append(user)
    return reviewers


def pick_products(db):
    categories = (
        db.query(Category)
        .filter(Category.slug != "other")
        .all()
    )
    chosen = []
    per_category = max(1, PRODUCTS_TO_SEED // max(len(categories), 1))
    for category in categories:
        products = (
            db.query(Product)
            .filter(Product.category_id == category.id)
            .order_by(Product.id)
            .limit(per_category)
            .all()
        )
        chosen.extend(products)

    random.shuffle(chosen)
    return chosen[:PRODUCTS_TO_SEED]


def weighted_rating():
    ratings = list(RATING_WEIGHTS.keys())
    weights = list(RATING_WEIGHTS.values())
    return random.choices(ratings, weights=weights, k=1)[0]


def seed():
    db = SessionLocal()
    try:
        reviewers = get_or_create_reviewers(db)
        db.commit()

        products = pick_products(db)
        print(f"{len(products)} products chuni gayi hain reviews ke liye.")

        total_created = 0
        for product in products:
            n_reviews = random.randint(*REVIEWS_PER_PRODUCT_RANGE)
            chosen_reviewers = random.sample(reviewers, min(n_reviews, len(reviewers)))

            for reviewer in chosen_reviewers:
                existing = (
                    db.query(Review)
                    .filter(Review.user_id == reviewer.id, Review.product_id == product.id)
                    .first()
                )
                if existing:
                    continue

                rating = weighted_rating()
                comment = random.choice(COMMENTS_BY_RATING[rating])

                review = Review(
                    user_id=reviewer.id,
                    product_id=product.id,
                    rating=rating,
                    comment=comment,
                )
                db.add(review)
                total_created += 1

            db.commit()

        print(f"\nDone. {total_created} naye reviews create hue, {len(products)} products pe.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()