from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.db.database import get_db
from app.models.product import Product
from app.models.user import User
from app.schemas.product import ProductCreate, ProductResponse
from app.core.security import require_role

router = APIRouter(prefix="/products", tags=["Products"])


from typing import Optional

from fastapi import Response

@router.get("/", response_model=list[ProductResponse])
def list_products(
    response: Response,
    db: Session = Depends(get_db),
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    skip: int = 0,
    limit: int = 20,
):
    query = (
        db.query(Product)
        .options(joinedload(Product.category))
        .filter(Product.is_active == True)
    )

    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    if category_id:
        query = query.filter(Product.category_id == category_id)

    if min_price is not None:
        query = query.filter(Product.price >= min_price)

    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    total_count = query.count()
    response.headers["X-Total-Count"] = str(total_count)

    return query.order_by(Product.id).offset(skip).limit(limit).all()

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = (
        db.query(Product)
        .options(joinedload(Product.category))
        .filter(Product.id == product_id, Product.is_active == True)
        .first()
    )
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product_in: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"])),
):
    new_product = Product(**product_in.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product