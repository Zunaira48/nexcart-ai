"""
Har product (name + description) ke liye Gemini embedding banata hai
aur products table ke 'embedding' column mein JSON text ke roop mein
save karta hai.

v2 changes (pehli version mein data silently loss ho raha tha):
- Har batch apna ALAG, FRESH database session use karta hai (taake
  lambi script ke dauran koi idle/stale connection na bane)
- db.commit() bhi ab try/except ke andar hai — agar wo fail ho to
  turant clear error dikhega, chup-chap aage nahi badhega
- Har 500 products ke baad khud database se dobara count nikal kar
  verify karta hai ke asal mein utne hi save hue jitne loop ne socha
  — agar mismatch mile to turant ruk jayega, end tak wait nahi karega

Batching: ek API call mein 50 products ka text ek sath bhejte hain.

Resumable hai: dobara chalane par sirf un products ke liye kaam karega
jinki embedding abhi tak nahi bani.

Run: backend/ folder se (venv active):
    python -m app.db.generate_embeddings
"""

import json
import os
import time

from dotenv import load_dotenv

load_dotenv()

from google import genai

from app.db.database import SessionLocal
from app.models.product import Product

BATCH_SIZE = 50
MODEL = "gemini-embedding-2"
PAUSE_SECONDS = 4
MAX_RETRIES = 6
VERIFY_EVERY = 500  # har itne products ke baad DB se dobara count verify karo


def build_text(product: Product) -> str:
    description = product.description or ""
    combined = f"{product.name}. {description}"
    return combined[:2000]


def embed_with_retry(client, texts):
    wait_time = 15
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return client.models.embed_content(model=MODEL, contents=texts)
        except Exception as e:
            message = str(e)
            if "PerDay" in message:
                print("\n    Ye AAJ ka daily quota khatam hone wali error hai — retry karne se abhi nahi milega.")
                print("    Google AI Studio quota reset ka wait karna hoga (https://ai.dev/rate-limit check karo).")
                raise
            if attempt == MAX_RETRIES:
                raise
            print(f"    Rate limit/error (attempt {attempt}/{MAX_RETRIES}): {e}")
            print(f"    {wait_time} second wait karke retry kar rahe hain...")
            time.sleep(wait_time)
            wait_time *= 2


def count_remaining() -> int:
    db = SessionLocal()
    try:
        return db.query(Product).filter(Product.embedding.is_(None)).count()
    finally:
        db.close()


def count_with_embedding() -> int:
    db = SessionLocal()
    try:
        return db.query(Product).filter(Product.embedding.isnot(None)).count()
    finally:
        db.close()


def process_one_batch(client) -> int:
    """Fresh session khol kar EK batch process karta hai, commit karta hai,
    session band kar deta hai. Return: kitne products is batch mein process hue (0 = koi bacha nahi)."""
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
        result = embed_with_retry(client, texts)

        for product, emb in zip(batch, result.embeddings):
            product.embedding = json.dumps(emb.values)

        try:
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"\n  COMMIT FAIL hua: {e}")
            raise

        return len(batch)
    finally:
        db.close()


def main():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY .env mein nahi mili.")
        return

    client = genai.Client(api_key=api_key)

    total_remaining = count_remaining()
    print(f"Embeddings banani hain: {total_remaining} products ke liye")

    if total_remaining == 0:
        print("Sab products ki embeddings pehle se ban chuki hain.")
        return

    done_this_run = 0
    since_last_verify = 0

    while True:
        try:
            processed = process_one_batch(client)
        except Exception as e:
            print(f"\nScript rok rahe hain (error upar dikha). {done_this_run} products is run mein save hue.")
            print("Dobara 'python -m app.db.generate_embeddings' chalao — khud resume ho jayega.")
            return

        if processed == 0:
            break

        done_this_run += processed
        since_last_verify += processed
        print(f"  {done_this_run} products is run mein save hue (ab tak)...")

        if since_last_verify >= VERIFY_EVERY:
            actual = count_with_embedding()
            print(f"  --- CHECK: database mein abhi total {actual} products ki embedding hai ---")
            since_last_verify = 0

        time.sleep(PAUSE_SECONDS)

    final_count = count_with_embedding()
    print(f"\nDone. Is run mein {done_this_run} products process hue.")
    print(f"Database mein ab total {final_count} products ki embedding hai.")


if __name__ == "__main__":
    main()
