import json

from app.db.database import SessionLocal
from app.models.product import Product

db = SessionLocal()
try:
    total = db.query(Product).count()
    with_embedding = db.query(Product).filter(Product.embedding.isnot(None)).count()
    without_embedding = total - with_embedding

    print(f"Total products: {total}")
    print(f"With embedding:  {with_embedding}")
    print(f"Without embedding: {without_embedding}")

    sample = db.query(Product).filter(Product.embedding.isnot(None)).first()
    if sample:
        vec = json.loads(sample.embedding)
        print(f"\nSample product: {sample.name}")
        print(f"Embedding length: {len(vec)}")
        print(f"First 3 numbers: {vec[:3]}")
finally:
    db.close()
