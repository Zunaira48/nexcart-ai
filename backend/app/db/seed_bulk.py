"""
DummyJSON (https://dummyjson.com) se real product data fetch kar ke
database mein bulk seed karta hai — Load More pagination ki performance
test karne ke liye 100+ real products deta hai.

Idempotent hai (jaisa seed.py): slug se match karta hai, dobara chalane
par duplicate nahi banega, sirf update karega.

Run: backend/ folder se (venv active):
    python -m app.db.seed_bulk
"""

import json
import re
import urllib.request

from app.db.database import SessionLocal
from app.models.category import Category
from app.models.product import Product

DUMMYJSON_URL = "https://dummyjson.com/products?limit=150"


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def fetch_products():
    request = urllib.request.Request(
        DUMMYJSON_URL,
        headers={"User-Agent": "Mozilla/5.0 (NexCartAI Seed Script)"},
    )
    with urllib.request.urlopen(request) as response:
        data = json.loads(response.read())
    return data["products"]


def seed_bulk():
    db = SessionLocal()
    try:
        products_data = fetch_products()
        print(f"Fetched {len(products_data)} products from DummyJSON.\n")

        category_cache = {}
        created_categories = 0
        created_products = 0
        updated_products = 0

        for item in products_data:
            category_slug = item["category"]
            category_name = category_slug.replace("-", " ").title()

            if category_slug not in category_cache:
                category = db.query(Category).filter(Category.slug == category_slug).first()
                if not category:
                    category = Category(name=category_name, slug=category_slug)
                    db.add(category)
                    db.flush()
                    created_categories += 1
                category_cache[category_slug] = category

            category = category_cache[category_slug]

            # DummyJSON ki id bhi slug mein shamil kar rahe hain, taake
            # milte-julte naam wale products bhi guaranteed unique slug rakhein
            product_slug = f"{slugify(item['title'])}-{item['id']}"

            product = db.query(Product).filter(Product.slug == product_slug).first()
            if product:
                product.name = item["title"]
                product.description = item["description"]
                product.price = item["price"]
                product.stock_quantity = item["stock"]
                product.image_url = item["thumbnail"]
                product.category_id = category.id
                updated_products += 1
            else:
                new_product = Product(
                    name=item["title"],
                    slug=product_slug,
                    description=item["description"],
                    price=item["price"],
                    stock_quantity=item["stock"],
                    image_url=item["thumbnail"],
                    category_id=category.id,
                )
                db.add(new_product)
                created_products += 1

        db.commit()
        print(f"Categories created: {created_categories}")
        print(f"Products created: {created_products}")
        print(f"Products updated: {updated_products}")
        print("\nBulk seeding complete.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_bulk()