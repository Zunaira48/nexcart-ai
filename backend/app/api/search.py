import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.product import Product
from app.schemas.product import ProductResponse
from app.core.embeddings import embed_query, cosine_similarity, load_product_vector

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("/products", response_model=list[ProductResponse])
def smart_search(q: str, limit: int = 20, db: Session = Depends(get_db)):
    if not q or not q.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Query khaali nahi ho sakti")

    query_vector = embed_query(q)

    products = (
        db.query(Product)
        .filter(Product.is_active == True, Product.embedding.isnot(None))
        .all()
    )

    scored = []
    for p in products:
        try:
            vec = load_product_vector(p.embedding)
        except (TypeError, ValueError, json.JSONDecodeError):
            continue
        scored.append((cosine_similarity(query_vector, vec), p))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in scored[:limit]]