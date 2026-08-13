"""
Dataset ko ~1000 products tak trim karta hai — Render ke free tier
(512 MB RAM) ke sath compatible rehne ke liye. Jin products pe reviews
hain unhe hamesha rakhta hai, baaki har category se proportionally
kuch products rakhta hai, baaki DELETE kar deta hai (unke cart/
wishlist/reviews bhi, taake koi orphan data na bache).

⚠️ DESTRUCTIVE hai — sirf us DB ke against chalao jise trim karna hai
(production ke liye DATABASE_URL Supabase ki taraf point karo).
Confirm maangta hai chalane se pehle.

Run: backend/ folder se:
    python -m app.db.trim_products
"""

from app.db.database import SessionLocal
from app.models.product import Product
from app.models.category import Category
from app.models.review import Review
from app.models.cart import CartItem
from app.models.wishlist import WishlistItem

TARGET_TOTAL = 1000
CHUNK = 500


def trim():
    db = SessionLocal()
    try:
        all_ids = [row[0] for row in db.query(Product.id).all()]
        total_before = len(all_ids)
        print(f"Total products abhi: {total_before}")

        reviewed_ids = {row[0] for row in db.query(Review.product_id).distinct().all()}
        print(f"Reviews wale products (hamesha rakhenge): {len(reviewed_ids)}")

        remaining_slots = max(TARGET_TOTAL - len(reviewed_ids), 0)
        categories = db.query(Category).all()
        per_category = max(1, remaining_slots // max(len(categories), 1))

        keep_ids = set(reviewed_ids)
        for category in categories:
            query = db.query(Product.id).filter(Product.category_id == category.id)
            if reviewed_ids:
                query = query.filter(~Product.id.in_(reviewed_ids))
            products = query.order_by(Product.id).limit(per_category).all()
            keep_ids.update(row[0] for row in products)

        delete_ids = [i for i in all_ids if i not in keep_ids]
        print(f"Rakhe jayenge: {len(keep_ids)}, delete honge: {len(delete_ids)}")

        confirm = input(f"\n{len(delete_ids)} products PERMANENTLY delete honge. Confirm? (yes/no): ")
        if confirm.strip().lower() != "yes":
            print("Cancelled.")
            return

        for i in range(0, len(delete_ids), CHUNK):
            chunk = delete_ids[i:i + CHUNK]
            db.query(Review).filter(Review.product_id.in_(chunk)).delete(synchronize_session=False)
            db.query(CartItem).filter(CartItem.product_id.in_(chunk)).delete(synchronize_session=False)
            db.query(WishlistItem).filter(WishlistItem.product_id.in_(chunk)).delete(synchronize_session=False)
            db.query(Product).filter(Product.id.in_(chunk)).delete(synchronize_session=False)
            db.commit()
            print(f"  {min(i + CHUNK, len(delete_ids))}/{len(delete_ids)} delete hue...")

        for category in db.query(Category).all():
            if db.query(Product).filter(Product.category_id == category.id).count() == 0:
                db.delete(category)
        db.commit()

        print(f"\nDone. Final product count: {db.query(Product).count()}")
    finally:
        db.close()


if __name__ == "__main__":
    trim()