"""
Database seed script — categories aur products ko ek command se
create/update karta hai. Idempotent hai: dobara chalane par duplicate
nahi banega, sirf existing rows update ho jayengi (slug ke zariye match).

Run: backend/ folder se (venv active hone ke sath):
    python -m app.db.seed
"""

from app.db.database import SessionLocal
from app.models.category import Category
from app.models.product import Product

CATEGORIES = [
    {"name": "Laptops", "slug": "laptops"},
    {"name": "Headphones", "slug": "headphones"},
    {"name": "Smartphones", "slug": "smartphones"},
    {"name": "Accessories", "slug": "accessories"},
]

PRODUCTS = [
    {
        "slug": "test-gaming-laptop",
        "name": "Test Gaming Laptop",
        "description": "A great laptop for testing",
        "price": 899.99,
        "stock_quantity": 10,
        "image_url": "https://images.unsplash.com/photo-1656639969809-ebc544c96955?auto=format&fit=crop&w=800&q=80",
        "category_slug": "laptops",
    },
    {
        "slug": "ultrabook-pro-14",
        "name": "Ultrabook Pro 14",
        "description": "Thin and light laptop built for productivity",
        "price": 1299.00,
        "stock_quantity": 8,
        "image_url": "https://images.unsplash.com/photo-1656639969809-ebc544c96955?auto=format&fit=crop&w=800&q=80",
        "category_slug": "laptops",
    },
    {
        "slug": "wireless-noise-cancelling-headphones",
        "name": "Wireless Noise-Cancelling Headphones",
        "description": "Premium over-ear headphones with 30-hour battery life",
        "price": 249.99,
        "stock_quantity": 25,
        "image_url": "https://images.unsplash.com/photo-1567928513899-997d98489fbd?auto=format&fit=crop&w=800&q=80",
        "category_slug": "headphones",
    },
    {
        "slug": "budget-wired-earbuds",
        "name": "Budget Wired Earbuds",
        "description": "Reliable everyday earbuds with in-line mic",
        "price": 14.99,
        "stock_quantity": 100,
        "image_url": "https://picsum.photos/seed/earbuds-budget/800/600",
        "category_slug": "headphones",
    },
    {
        "slug": "flagship-smartphone-pro",
        "name": "Flagship Smartphone Pro",
        "description": "6.7-inch display, triple camera system, 5G",
        "price": 1099.00,
        "stock_quantity": 15,
        "image_url": "https://images.unsplash.com/photo-1541591708423-9001fe827349?auto=format&fit=crop&w=800&q=80",
        "category_slug": "smartphones",
    },
    {
        "slug": "budget-smartphone",
        "name": "Budget Smartphone",
        "description": "Solid daily driver with great battery life",
        "price": 199.99,
        "stock_quantity": 40,
        "image_url": "https://images.unsplash.com/photo-1541591708423-9001fe827349?auto=format&fit=crop&w=800&q=80",
        "category_slug": "smartphones",
    },
    {
        "slug": "mechanical-gaming-keyboard",
        "name": "Mechanical Gaming Keyboard",
        "description": "RGB backlit mechanical keyboard with tactile switches",
        "price": 79.99,
        "stock_quantity": 30,
        "image_url": "https://images.unsplash.com/photo-1520092352425-9699926a9b0b?auto=format&fit=crop&w=800&q=80",
        "category_slug": "accessories",
    },
    {
        "slug": "4k-ultrawide-monitor",
        "name": "4K Ultrawide Monitor",
        "description": "34-inch curved display for productivity and gaming",
        "price": 599.00,
        "stock_quantity": 12,
        "image_url": "https://picsum.photos/seed/ultrawide-monitor/800/600",
        "category_slug": "laptops",
    },
    {
        "slug": "wireless-gaming-mouse",
        "name": "Wireless Gaming Mouse",
        "description": "Lightweight mouse with adjustable DPI and RGB lighting",
        "price": 49.99,
        "stock_quantity": 45,
        "image_url": "https://images.unsplash.com/photo-1613141411244-0e4ac259d217?auto=format&fit=crop&w=800&q=80",
        "category_slug": "accessories",
    },
    {
        "slug": "portable-bluetooth-speaker",
        "name": "Portable Bluetooth Speaker",
        "description": "Waterproof speaker with 12-hour battery life",
        "price": 39.99,
        "stock_quantity": 60,
        "image_url": "https://picsum.photos/seed/bt-speaker/800/600",
        "category_slug": "headphones",
    },
    {
        "slug": "smartwatch-series-x",
        "name": "Smartwatch Series X",
        "description": "Fitness tracking, heart rate monitor, and notifications",
        "price": 179.99,
        "stock_quantity": 20,
        "image_url": "https://picsum.photos/seed/smartwatch/800/600",
        "category_slug": "smartphones",
    },
    {
        "slug": "fast-charging-power-bank",
        "name": "Fast Charging Power Bank",
        "description": "20000mAh capacity with USB-C fast charging",
        "price": 29.99,
        "stock_quantity": 80,
        "image_url": "https://picsum.photos/seed/power-bank/800/600",
        "category_slug": "accessories",
    },
]


def seed():
    db = SessionLocal()
    try:
        # ---- Categories: get-or-create by slug ----
        category_map = {}
        for cat_data in CATEGORIES:
            category = db.query(Category).filter(Category.slug == cat_data["slug"]).first()
            if not category:
                category = Category(**cat_data)
                db.add(category)
                db.flush()  # id turant milta hai bina full commit ke
                print(f"Created category: {category.name}")
            else:
                print(f"Category already exists: {category.name}")
            category_map[cat_data["slug"]] = category

        db.commit()

        # ---- Products: get-or-create/update by slug ----
        for prod_data in PRODUCTS:
            category_slug = prod_data.pop("category_slug")
            category = category_map[category_slug]

            product = db.query(Product).filter(Product.slug == prod_data["slug"]).first()
            if product:
                # Already exists — sirf image_url aur baaki fields update karo
                for key, value in prod_data.items():
                    setattr(product, key, value)
                product.category_id = category.id
                print(f"Updated product: {product.name}")
            else:
                new_product = Product(**prod_data, category_id=category.id)
                db.add(new_product)
                print(f"Created product: {prod_data['name']}")

        db.commit()
        print("\nSeeding complete.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()