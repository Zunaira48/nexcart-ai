"""
Search query ke liye vector banata hai — LIGHTWEIGHT library (fastembed,
onnxruntime-based) use karta hai, torch NAHI — taake Render ke free tier
(512 MB RAM) pe crash na ho. Same model (all-MiniLM-L6-v2), bas halka
runtime.
"""

import json

from fastembed import TextEmbedding

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_model = None


def get_model():
    global _model
    if _model is None:
        _model = TextEmbedding(model_name=MODEL_NAME)
    return _model


def embed_query(text: str) -> list[float]:
    model = get_model()
    vector = list(model.embed([text]))[0]
    return vector.tolist()


def load_product_vector(embedding_json: str) -> list[float]:
    return json.loads(embedding_json)