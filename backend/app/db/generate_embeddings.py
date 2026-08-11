"""
Har product (name + description) ke liye LOCAL open-source model se
embedding banata hai — koi API call nahi, koi daily quota nahi, bilkul
free (model ek baar download hone ke baad offline bhi chalta hai).

Model: all-MiniLM-L6-v2 (384 dimensions) — chhota, tez, semantic search
ke liye industry-standard starter model.

Resumable hai: dobara chalane par sirf un products ke liye kaam karega
jinki embedding abhi tak nahi bani.

Run: backend/ folder se (venv active):
    python -m app.db.generate_embeddings
"""

import json

from sentence_transformers import SentenceTransformer

from app.db.database import SessionLocal
from app.models.product import Product

BATCH_SIZE = 200
MODEL_NAME = "all-MiniLM-L6-v2"


def build_text(product: Product) -> str:
    description = product.description or ""
    return f"{product.name}. {description}"[:2000]


def count_remaining() -> int:
    db = SessionLocal()
    try:
        return db.query(Product).filter(Product.embedding.is_(None)).count()
    finally:
        db.close()


def process_one_batch(model) -> int:
    db = SessionLocal()
    try:
        batch = (
            db.query(Product)
            .filter(Product.embedding.is_(None))
            .order_by(Product.id)
            .limit(BATCH_SIZE)
            .all()
        )
        if not batch:
            return 0

        texts = [build_text(p) for p in batch]
        vectors = model.encode(texts, show_progress_bar=False)

        for product, vec in zip(batch, vectors):
            product.embedding = json.dumps(vec.tolist())

        db.commit()
        return len(batch)
    finally:
        db.close()


def main():
    print("Local model load ho rahi hai (pehli baar thoda time lagega, phir tez hoga)...")
    model = SentenceTransformer(MODEL_NAME)

    total_remaining = count_remaining()
    print(f"Embeddings banani hain: {total_remaining} products ke liye")

    if total_remaining == 0:
        print("Sab products ki embeddings pehle se ban chuki hain.")
        return

    done = 0
    while True:
        processed = process_one_batch(model)
        if processed == 0:
            break
        done += processed
        print(f"  {done}/{total_remaining} products save hue...")

    print(f"\nDone. Total {done} products process hue.")


if __name__ == "__main__":
    main()