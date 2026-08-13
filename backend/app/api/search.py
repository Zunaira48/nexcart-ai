import json

import numpy as np
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.product import Product
from app.schemas.product import ProductResponse
from app.core.embeddings import embed_query

router = APIRouter(prefix="/search", tags=["Search"])

# In-memory cache — ek baar load hone ke baad dobara DB se nahi mangwana
# padta har request pe, jab tak process restart na ho.
_vector_cache = {"ids": None, "vectors": None}


def get_cached_vectors(db: Session):
    if _vector_cache["ids"] is None:
        rows = (
            db.query(Product.id, Product.embedding)
            .filter(Product.is_active == True, Product.embedding.isnot(None))
            .all()
        )
        _vector_cache["ids"] = [r.id for r in rows]
        _vector_cache["vectors"] = np.array(
            [json.loads(r.embedding) for r in rows], dtype=np.float16
        )
    return _vector_cache["ids"], _vector_cache["vectors"]


@router.get("/products", response_model=list[ProductResponse])
def smart_search(q: str, limit: int = 20, db: Session = Depends(get_db)):
    if not q or not q.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Query khaali nahi ho sakti")

    query_vector = np.array(embed_query(q), dtype=np.float16)

    ids, vectors = get_cached_vectors(db)
    if not ids:
        return []

    query_norm = query_vector / (np.linalg.norm(query_vector) + 1e-8)
    vector_norms = vectors / (np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-8)
    scores = vector_norms.astype(np.float32) @ query_norm.astype(np.float32)

    top_indices = np.argsort(-scores)[:limit]
    top_ids = [ids[i] for i in top_indices]

    products = db.query(Product).filter(Product.id.in_(top_ids)).all()
    products_by_id = {p.id: p for p in products}
    return [products_by_id[i] for i in top_ids if i in products_by_id]