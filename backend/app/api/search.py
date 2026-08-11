import json

import numpy as np
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.product import Product
from app.schemas.product import ProductResponse
from app.core.embeddings import embed_query

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("/products", response_model=list[ProductResponse])
def smart_search(q: str, limit: int = 20, db: Session = Depends(get_db)):
    if not q or not q.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Query khaali nahi ho sakti")

    query_vector = np.array(embed_query(q), dtype=np.float32)

    products = (
        db.query(Product)
        .filter(Product.is_active == True, Product.embedding.isnot(None))
        .all()
    )
    if not products:
        return []

    # Sab products ki embeddings ko ek hi matrix mein load karo (loop nahi)
    vectors = np.array([json.loads(p.embedding) for p in products], dtype=np.float32)

    # Cosine similarity — ek hi bulk operation mein sab products ke sath
    query_norm = query_vector / (np.linalg.norm(query_vector) + 1e-8)
    vector_norms = vectors / (np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-8)
    scores = vector_norms @ query_norm  # matrix-vector multiply — ye hi speed ka raaz hai

    top_indices = np.argsort(-scores)[:limit]
    return [products[i] for i in top_indices]