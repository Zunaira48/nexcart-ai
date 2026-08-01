from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.db.database import get_db
from app.models.cart import CartItem
from app.models.product import Product
from app.models.user import User
from app.schemas.cart import CartItemCreate, CartItemUpdate, CartResponse
from app.core.security import get_current_user

router = APIRouter(prefix="/cart", tags=["Cart"])


def _build_cart_response(db: Session, user_id: int) -> CartResponse:
    items = (
        db.query(CartItem)
        .options(joinedload(CartItem.product))
        .filter(CartItem.user_id == user_id)
        .order_by(CartItem.id)
        .all()
    )
    total = sum((item.product.price * item.quantity for item in items), Decimal("0"))
    return CartResponse(items=items, total=total)


@router.get("/", response_model=CartResponse)
def get_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _build_cart_response(db, current_user.id)


@router.post("/items", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
def add_to_cart(
    item_in: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = db.query(Product).filter(Product.id == item_in.product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    existing = (
        db.query(CartItem)
        .filter(CartItem.user_id == current_user.id, CartItem.product_id == item_in.product_id)
        .first()
    )

    if existing:
        existing.quantity += item_in.quantity
    else:
        db.add(
            CartItem(
                user_id=current_user.id,
                product_id=item_in.product_id,
                quantity=item_in.quantity,
            )
        )

    db.commit()
    return _build_cart_response(db, current_user.id)


@router.put("/items/{item_id}", response_model=CartResponse)
def update_cart_item(
    item_id: int,
    item_in: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = (
        db.query(CartItem)
        .filter(CartItem.id == item_id, CartItem.user_id == current_user.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")

    if item_in.quantity < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Quantity must be at least 1"
        )

    item.quantity = item_in.quantity
    db.commit()
    return _build_cart_response(db, current_user.id)


@router.delete("/items/{item_id}", response_model=CartResponse)
def remove_cart_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = (
        db.query(CartItem)
        .filter(CartItem.id == item_id, CartItem.user_id == current_user.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")

    db.delete(item)
    db.commit()
    return _build_cart_response(db, current_user.id)