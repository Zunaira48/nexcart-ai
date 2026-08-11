"""
Purane DummyJSON products (seed_bulk.py se aaye) database se delete karta
hai, taake sirf Kaggle Flipkart dataset ke 19,920 products rahen.

Pehchan kaise: DummyJSON product ki slug hoti hai "<name>-<id>" jahan id
DummyJSON ka apna chhota number hai (1-3 digits, e.g. "red-lipstick-42").
Kaggle products ki slug lambi 8-character hex string se end hoti hai
(e.g. "..._-a1b2c3d4"), isliye ye pattern unhe kabhi touch nahi karega.

Safety: agar kisi DummyJSON product par order history hai (order_items
mein reference), us product ko SKIP kar diya jayega — order records
kabhi delete nahi karne chahiye. Cart/wishlist/review entries (jo sirf
test data hain) pehle clean kar di jaati hain taake foreign-key error
na aaye.

Run: backend/ folder se (venv active):
    python -m app.db.cleanup_dummyjson
"""

import re

from app.db.database import SessionLocal
from app.models import Product, Category, CartItem, WishlistItem, Review, OrderItem

DUMMYJSON_SLUG_PATTERN = re.compile(r"-\d{1,3}$")


def cleanup():
    db = SessionLocal()
    try:
        all_products = db.query(Product).all()
        candidates = [p for p in all_products if DUMMYJSON_SLUG_PATTERN.search(p.slug)]

        print(f"Total products in DB: {len(all_products)}")
        print(f"DummyJSON products matched: {len(candidates)}")

        if not candidates:
            print("Kuch delete karne layak nahi mila.")
            return

        # Jin products par order history hai unhe skip karo
        candidate_ids = [p.id for p in candidates]
        ordered_product_ids = {
            row.product_id
            for row in db.query(OrderItem.product_id)
            .filter(OrderItem.product_id.in_(candidate_ids))
            .all()
        }

        to_delete = [p for p in candidates if p.id not in ordered_product_ids]
        skipped = [p for p in candidates if p.id in ordered_product_ids]

        print(f"Deletable (no order history): {len(to_delete)}")
        if skipped:
            print(f"Skipped (has order history, kept safe): {len(skipped)}")
            for p in skipped:
                print(f"  - kept: {p.name} (id={p.id})")

        if not to_delete:
            print("Sab candidates par order history hai, kuch delete nahi hua.")
            return

        confirm = input(f"\n{len(to_delete)} products (+ unke cart/wishlist/review) delete karne hain? (yes/no): ")
        if confirm.strip().lower() != "yes":
            print("Cancelled.")
            return

        delete_ids = [p.id for p in to_delete]

        cart_deleted = db.query(CartItem).filter(CartItem.product_id.in_(delete_ids)).delete(synchronize_session=False)
        wishlist_deleted = db.query(WishlistItem).filter(WishlistItem.product_id.in_(delete_ids)).delete(synchronize_session=False)
        review_deleted = db.query(Review).filter(Review.product_id.in_(delete_ids)).delete(synchronize_session=False)

        for p in to_delete:
            db.delete(p)

        db.commit()
        print(f"\nCart items removed: {cart_deleted}")
        print(f"Wishlist items removed: {wishlist_deleted}")
        print(f"Reviews removed: {review_deleted}")
        print(f"Products deleted: {len(to_delete)}")

        # Ab empty categories clean karo (jinke koi products nahi bache)
        empty_categories = db.query(Category).filter(~Category.products.any()).all()
        for c in empty_categories:
            db.delete(c)
        db.commit()
        print(f"Empty categories removed: {len(empty_categories)}")
        print("\nCleanup complete.")
    finally:
        db.close()


if __name__ == "__main__":
    cleanup()
