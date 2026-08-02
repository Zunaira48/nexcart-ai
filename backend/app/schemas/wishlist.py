from pydantic import BaseModel, ConfigDict

from app.schemas.product import ProductResponse


class WishlistItemResponse(BaseModel):
    id: int
    product: ProductResponse

    model_config = ConfigDict(from_attributes=True)