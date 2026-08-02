from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime
from typing import Optional


class ReviewerResponse(BaseModel):
    id: int
    full_name: str

    model_config = ConfigDict(from_attributes=True)


class ReviewCreate(BaseModel):
    rating: int
    comment: Optional[str] = None

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, value: int) -> int:
        if value < 1 or value > 5:
            raise ValueError("Rating must be between 1 and 5")
        return value


class ReviewResponse(BaseModel):
    id: int
    rating: int
    comment: Optional[str]
    created_at: datetime
    user: ReviewerResponse

    model_config = ConfigDict(from_attributes=True)