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

    # Step 1: SIRF id + embedding fetch karo — poori product row nahi
    # (naam, description, image_url waghera abhi zaroori nahi) — ye hi
    # sabse bada memory-saving change hai.
    rows = (
        db.query(Product.id, Product.embedding)
        .filter(Product.is_active == True, Product.embedding.isnot(None))
        .all()
    )
    if not rows:
        return []

    ids = [r.id for r in rows]
    vectors = np.array([json.loads(r.embedding) for r in rows], dtype=np.float32)

    query_norm = query_vector / (np.linalg.norm(query_vector) + 1e-8)
    vector_norms = vectors / (np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-8)
    scores = vector_norms @ query_norm

    top_indices = np.argsort(-scores)[:limit]
    top_ids = [ids[i] for i in top_indices]

    # Step 2: ab sirf top N (jaise 20) products ki POORI detail fetch karo
    products = db.query(Product).filter(Product.id.in_(top_ids)).all()
    products_by_id = {p.id: p for p in products}
    return [products_by_id[i] for i in top_ids if i in products_by_id]