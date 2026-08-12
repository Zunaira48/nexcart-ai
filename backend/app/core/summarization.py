"""
Product reviews padh kar ek chhota AI summary banata hai — jaise koi
dost jo saari reviews padh ke tumhe 2-3 lines mein bata de log kya
keh rahe hain.

Embeddings wale model se ALAG model use hota hai yahan — isko naya
text LIKHNA hai, sirf compare nahi karna (isliye "generative" model).
Ye endpoint kam baar chalta hai (sirf naya/missing summary hone par),
isliye free tier ka daily quota yahan masla nahi banega.
"""

import json
import re

from google import genai

from app.core.config import settings

SUMMARY_MODEL = "gemini-flash-lite-latest"

_client = None


def get_client():
    global _client
    if _client is None:
        if not settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY .env mein nahi mili.")
        _client = genai.Client(api_key=settings.gemini_api_key)
    return _client


def generate_review_summary(product_name: str, comments: list[str], ratings: list[int]) -> dict:
    client = get_client()

    reviews_text = "\n".join(f"- ({r} star) {c}" for r, c in zip(ratings, comments) if c)
    avg_rating = sum(ratings) / len(ratings) if ratings else 0

    prompt = f"""You are summarizing customer reviews for an e-commerce product.

Product: {product_name}
Average rating: {avg_rating:.1f} / 5
Number of reviews: {len(ratings)}

Reviews:
{reviews_text}

Respond with ONLY valid JSON (no markdown, no code fences), in this exact shape:
{{
  "summary": "a 2-3 sentence natural summary of what customers are saying overall",
  "sentiment": "positive" | "mixed" | "negative",
  "pros": ["short phrase", "short phrase"],
  "cons": ["short phrase", "short phrase"]
}}

Keep pros/cons to at most 3 each, only include real, recurring points from the reviews. If there are no clear cons, return an empty list for cons."""

    response = client.models.generate_content(model=SUMMARY_MODEL, contents=prompt)
    raw = response.text.strip()
    raw = re.sub(r"^```(?:json)?|```$", "", raw, flags=re.MULTILINE).strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {}

    # Agar Gemini ne kisi bhi key ko chhod diya ho, safe defaults de do
    # (crash hone ke bajaye) — taake response hamesha valid rahe.
    data.setdefault("summary", "Summary generate nahi ho saki, dobara try karo.")
    data.setdefault("sentiment", "mixed")
    data.setdefault("pros", [])
    data.setdefault("cons", [])

    return data