from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from datetime import datetime
from typing import Optional

from app.schemas.category import CategoryResponse


class ProductCreate(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    price: Decimal
    stock_quantity: int = 0
    image_url: Optional[str] = None
    category_id: int


class ProductResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str]
    price: Decimal
    stock_quantity: int
    image_url: Optional[str]
    is_active: bool
    created_at: datetime
    category: CategoryResponse

    model_config = ConfigDict(from_attributes=True)
class ProductUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    stock_quantity: Optional[int] = None
    image_url: Optional[str] = None
    category_id: Optional[int] = None
    is_active: Optional[bool] = None

    