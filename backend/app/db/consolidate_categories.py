"""
Chhoti categories (jaise sirf 1-2 products wali, messy Flipkart category
tree data ki wajah se) ko ek "Other" category mein merge karta hai,
taake category list saaf aur usable rahe.

Run: backend/ folder se (venv active):
    python -m app.db.consolidate_categories
"""

from app.db.database import SessionLocal
from app.models import Category, Product

MIN_PRODUCTS_PER_CATEGORY = 15  # is se kam wali categories "Other" mein chali jayengi


def consolidate():
    db = SessionLocal()
    try:
        categories = db.query(Category).all()
        print(f"Total categories before: {len(categories)}")

        small_categories = []
        for c in categories:
            count = db.query(Product).filter(Product.category_id == c.id).count()
            if count < MIN_PRODUCTS_PER_CATEGORY and c.slug != "other":
                small_categories.append(c)

        print(f"Small categories to merge into 'Other': {len(small_categories)}")

        if not small_categories:
            print("Kuch merge karne layak nahi mila.")
            return

        confirm = input(f"\n{len(small_categories)} categories ko 'Other' mein merge karein? (yes/no): ")
        if confirm.strip().lower() != "yes":
            print("Cancelled.")
            return

        other_category = db.query(Category).filter(Category.slug == "other").first()
        if not other_category:
            other_category = Category(name="Other", slug="other")
            db.add(other_category)
            db.flush()

        small_ids = [c.id for c in small_categories]

        # Step 1: PLAIN bulk SQL update (bypasses ORM relationship
        # machinery entirely, so nothing can null this out later).
        moved_products = (
            db.query(Product)
            .filter(Product.category_id.in_(small_ids))
            .update({Product.category_id: other_category.id}, synchronize_session=False)
        )
        db.commit()

        # Step 2: ab koi product in categories ko point nahi karta,
        # ab safely delete karo.
        db.query(Category).filter(Category.id.in_(small_ids)).delete(synchronize_session=False)
        db.commit()

        print(f"\nProducts moved to 'Other': {moved_products}")
        print(f"Empty categories deleted: {len(small_ids)}")
        print(f"Total categories after: {db.query(Category).count()}")
        print("\nConsolidation complete.")
    finally:
        db.close()


if __name__ == "__main__":
    consolidate()