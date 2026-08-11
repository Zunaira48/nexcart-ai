"""
Kaggle 'Flipkart Products' dataset (PromptCloudHQ/flipkart-products) se
20,000 real products database mein seed karta hai — AI features
(semantic search, recommendations, review summarization) ke liye
zyada volume aur variety ke real-world text data ke liye.

CSV path: backend/data/flipkart_com-ecommerce_sample.csv
(agar tumhare paas alag naam/path hai to neeche CSV_PATH badal do)

Idempotent hai (jaisa seed.py/seed_bulk.py): slug se match karta hai,
dobara chalane par duplicate nahi banega, sirf update karega.

Run: backend/ folder se (venv active):
    python -m app.db.seed_kaggle
"""

import ast
import random
import re

import pandas as pd

from app.db.database import SessionLocal
from app.models.category import Category
from app.models.product import Product

CSV_PATH = "data/flipkart_com-ecommerce_sample.csv"
COMMIT_EVERY = 1000  # kitne rows ke baad progress commit + print karna hai


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def parse_top_category(raw_tree) -> str:
    """
    product_category_tree column ka format hota hai:
    '["Clothing >> Women's Clothing >> Lingerie"]'
    Hum sirf sabse pehla (top-level) hissa lete hain: "Clothing"
    """
    try:
        tree_list = ast.literal_eval(raw_tree)
        first_path = tree_list[0]
        top_level = first_path.split(">>")[0].strip()
        return top_level if top_level else "Uncategorized"
    except (ValueError, SyntaxError, IndexError, TypeError):
        return "Uncategorized"


def parse_first_image(raw_images) -> str | None:
    """
    image column ka format hota hai: '["http://...", "http://..."]'
    Hum sirf pehli image URL lete hain.
    """
    try:
        image_list = ast.literal_eval(raw_images)
        return image_list[0] if image_list else None
    except (ValueError, SyntaxError, IndexError, TypeError):
        return None


def seed_kaggle():
    db = SessionLocal()
    try:
        print(f"Reading CSV: {CSV_PATH} ...")
        df = pd.read_csv(CSV_PATH)
        print(f"Total rows in CSV: {len(df)}\n")

        category_cache = {}
        created_categories = 0
        created_products = 0
        updated_products = 0
        skipped_rows = 0

        for i, row in df.iterrows():
            # Zaroori fields missing hon to row skip karo
            if (
                pd.isna(row.get("product_name"))
                or pd.isna(row.get("description"))
                or pd.isna(row.get("retail_price"))
            ):
                skipped_rows += 1
                continue

            category_name = parse_top_category(row.get("product_category_tree"))
            category_slug = slugify(category_name)

            if category_slug not in category_cache:
                category = db.query(Category).filter(Category.slug == category_slug).first()
                if not category:
                    category = Category(name=category_name, slug=category_slug)
                    db.add(category)
                    db.flush()
                    created_categories += 1
                category_cache[category_slug] = category

            category = category_cache[category_slug]

            # uniq_id ko slug mein shamil kar rahe hain taake milte-julte
            # naam wale products bhi guaranteed unique slug rakhein
            product_slug = f"{slugify(str(row['product_name']))[:80]}-{row['uniq_id'][:8]}"

            image_url = parse_first_image(row.get("image"))
            stock_quantity = random.randint(5, 100)  # dataset mein stock nahi hai

            product = db.query(Product).filter(Product.slug == product_slug).first()
            if product:
                product.name = str(row["product_name"])[:200]
                product.description = str(row["description"])
                product.price = round(float(row["retail_price"]), 2)
                product.image_url = image_url
                product.category_id = category.id
                updated_products += 1
            else:
                new_product = Product(
                    name=str(row["product_name"])[:200],
                    slug=product_slug,
                    description=str(row["description"]),
                    price=round(float(row["retail_price"]), 2),
                    stock_quantity=stock_quantity,
                    image_url=image_url,
                    category_id=category.id,
                )
                db.add(new_product)
                created_products += 1

            if (i + 1) % COMMIT_EVERY == 0:
                db.commit()
                print(f"  Processed {i + 1}/{len(df)} rows...")

        db.commit()
        print("\n--- Done ---")
        print(f"Categories created: {created_categories}")
        print(f"Products created:   {created_products}")
        print(f"Products updated:   {updated_products}")
        print(f"Rows skipped (missing data): {skipped_rows}")
        print("\nKaggle seeding complete.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_kaggle()
