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
    {
        "slug": "business-laptop-15",
        "name": "15-inch Business Laptop",
        "description": "Reliable everyday laptop for work and study",
        "price": 649.00,
        "stock_quantity": 18,
        "image_url": "https://picsum.photos/seed/business-laptop-15/800/600",
        "category_slug": "laptops",
    },
    {
        "slug": "budget-chromebook",
        "name": "Budget Chromebook",
        "description": "Lightweight laptop for browsing and basic tasks",
        "price": 279.00,
        "stock_quantity": 25,
        "image_url": "https://picsum.photos/seed/budget-chromebook/800/600",
        "category_slug": "laptops",
    },
    {
        "slug": "gaming-laptop-17",
        "name": "Gaming Laptop 17-inch",
        "description": "High refresh-rate display with dedicated graphics",
        "price": 1599.00,
        "stock_quantity": 6,
        "image_url": "https://picsum.photos/seed/gaming-laptop-17/800/600",
        "category_slug": "laptops",
    },
    {
        "slug": "true-wireless-earbuds-pro",
        "name": "True Wireless Earbuds Pro",
        "description": "Compact earbuds with active noise cancellation",
        "price": 129.99,
        "stock_quantity": 35,
        "image_url": "https://picsum.photos/seed/true-wireless-earbuds-pro/800/600",
        "category_slug": "headphones",
    },
    {
        "slug": "on-ear-bluetooth-headphones",
        "name": "On-Ear Bluetooth Headphones",
        "description": "Foldable design with 20-hour battery life",
        "price": 59.99,
        "stock_quantity": 50,
        "image_url": "https://picsum.photos/seed/on-ear-bluetooth-headphones/800/600",
        "category_slug": "headphones",
    },
    {
        "slug": "studio-monitor-headphones",
        "name": "Studio Monitor Headphones",
        "description": "Flat frequency response for accurate audio mixing",
        "price": 149.00,
        "stock_quantity": 14,
        "image_url": "https://picsum.photos/seed/studio-monitor-headphones/800/600",
        "category_slug": "headphones",
    },
    {
        "slug": "mid-range-smartphone",
        "name": "Mid-Range Smartphone",
        "description": "Balanced performance and camera for everyday use",
        "price": 449.00,
        "stock_quantity": 28,
        "image_url": "https://picsum.photos/seed/mid-range-smartphone/800/600",
        "category_slug": "smartphones",
    },
    {
        "slug": "compact-smartphone-mini",
        "name": "Compact Smartphone Mini",
        "description": "Small form factor without compromising on power",
        "price": 599.00,
        "stock_quantity": 22,
        "image_url": "https://picsum.photos/seed/compact-smartphone-mini/800/600",
        "category_slug": "smartphones",
    },
    {
        "slug": "rugged-outdoor-smartphone",
        "name": "Rugged Outdoor Smartphone",
        "description": "Shockproof and waterproof build for tough conditions",
        "price": 379.00,
        "stock_quantity": 16,
        "image_url": "https://picsum.photos/seed/rugged-outdoor-smartphone/800/600",
        "category_slug": "smartphones",
    },
    {
        "slug": "usb-c-hub-7-in-1",
        "name": "USB-C Hub 7-in-1",
        "description": "HDMI, USB-A, SD card, and fast charging in one dock",
        "price": 34.99,
        "stock_quantity": 55,
        "image_url": "https://picsum.photos/seed/usb-c-hub-7-in-1/800/600",
        "category_slug": "accessories",
    },
    {
        "slug": "laptop-stand-adjustable",
        "name": "Adjustable Laptop Stand",
        "description": "Ergonomic aluminum stand with adjustable height",
        "price": 24.99,
        "stock_quantity": 65,
        "image_url": "https://picsum.photos/seed/laptop-stand-adjustable/800/600",
        "category_slug": "accessories",
    },
    {
        "slug": "webcam-1080p",
        "name": "1080p HD Webcam",
        "description": "Full HD webcam with built-in noise-cancelling mic",
        "price": 44.99,
        "stock_quantity": 40,
        "image_url": "https://picsum.photos/seed/webcam-1080p/800/600",
        "category_slug": "accessories",
    },
    {
        "slug": "wireless-charging-pad",
        "name": "Wireless Charging Pad",
        "description": "15W fast wireless charging for Qi-enabled devices",
        "price": 19.99,
        "stock_quantity": 70,
        "image_url": "https://picsum.photos/seed/wireless-charging-pad/800/600",
        "category_slug": "accessories",
    },
    {
        "slug": "screen-protector-tempered-glass",
        "name": "Tempered Glass Screen Protector",
        "description": "9H hardness scratch-resistant protection, pack of 2",
        "price": 9.99,
        "stock_quantity": 120,
        "image_url": "https://picsum.photos/seed/screen-protector-tempered-glass/800/600",
        "category_slug": "accessories",
    },
    {
        "slug": "phone-case-shockproof",
        "name": "Shockproof Phone Case",
        "description": "Military-grade drop protection with slim profile",
        "price": 16.99,
        "stock_quantity": 90,
        "image_url": "https://picsum.photos/seed/phone-case-shockproof/800/600",
        "category_slug": "accessories",
    },
    {
        "slug": "2-in-1-convertible-laptop",
        "name": "2-in-1 Convertible Laptop",
        "description": "Touchscreen laptop that folds into tablet mode",
        "price": 899.00,
        "stock_quantity": 14,
        "image_url": "https://picsum.photos/seed/2-in-1-convertible-laptop/800/600",
        "category_slug": "laptops",
    },
    {
        "slug": "kids-volume-limited-headphones",
        "name": "Kids Volume-Limited Headphones",
        "description": "Safe listening levels with durable, colorful design",
        "price": 22.99,
        "stock_quantity": 45,
        "image_url": "https://picsum.photos/seed/kids-volume-limited-headphones/800/600",
        "category_slug": "headphones",
    },
    {
        "slug": "foldable-smartphone",
        "name": "Foldable Smartphone",
        "description": "Book-style folding display with multitasking support",
        "price": 1799.00,
        "stock_quantity": 5,
        "image_url": "https://picsum.photos/seed/foldable-smartphone/800/600",
        "category_slug": "smartphones",
    },
    {
        "slug": "portable-ssd-1tb",
        "name": "Portable SSD 1TB",
        "description": "Compact external drive with USB-C high-speed transfer",
        "price": 89.99,
        "stock_quantity": 38,
        "image_url": "https://picsum.photos/seed/portable-ssd-1tb/800/600",
        "category_slug": "accessories",
    },
    {
        "slug": "ergonomic-wireless-keyboard",
        "name": "Ergonomic Wireless Keyboard",
        "description": "Split-key design to reduce wrist strain during typing",
        "price": 54.99,
        "stock_quantity": 32,
        "image_url": "https://picsum.photos/seed/ergonomic-wireless-keyboard/800/600",
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

