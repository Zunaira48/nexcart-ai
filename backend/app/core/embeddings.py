"""
Search query ke liye local (offline) model se vector banata hai, aur
product vectors ke saath cosine similarity nikalta hai. Koi API call
nahi — isliye ye function bilkul free, unlimited, aur fast hai.
"""

import json
import math

from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"

_model = None


def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def embed_query(text: str) -> list[float]:
    model = get_model()
    return model.encode([text])[0].tolist()


def load_product_vector(embedding_json: str) -> list[float]:
    return json.loads(embedding_json)


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)