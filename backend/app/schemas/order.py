from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from datetime import datetime


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    unit_price: Decimal
    quantity: int

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    id: int
    status: str
    total: Decimal
    created_at: datetime
    items: list[OrderItemResponse]

    model_config = ConfigDict(from_attributes=True)