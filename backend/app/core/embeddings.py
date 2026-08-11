"""
Search query ke liye Gemini se embedding banata hai, aur do vectors
(query vs product) ke beech similarity nikalta hai.

SEARCH_DIMENSIONS = 768: full embedding 3072 numbers ki hoti hai, lekin
Gemini ke embedding models "Matryoshka" tarah trained hote hain — matlab
pehle 768 numbers akele bhi ek valid (thoda kam precise) embedding hote
hain. Kam numbers = tez comparison, kam memory — 19000 products ke liye
zaroori hai.
"""

import json
import math
import os

from google import genai

QUERY_MODEL = "gemini-embedding-2"
SEARCH_DIMENSIONS = 768

_client = None


def get_client():
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY .env mein nahi mili.")
        _client = genai.Client(api_key=api_key)
    return _client


def embed_query(text: str) -> list[float]:
    client = get_client()
    result = client.models.embed_content(model=QUERY_MODEL, contents=[text])
    return result.embeddings[0].values[:SEARCH_DIMENSIONS]


def load_product_vector(embedding_json: str) -> list[float]:
    return json.loads(embedding_json)[:SEARCH_DIMENSIONS]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)