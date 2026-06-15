from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class CartItemResponse(BaseModel):
    id: int
    user_id: int
    game_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CartItemWithGame(BaseModel):
    id: int
    game_id: int
    game_name: str
    price: float
    image_url: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CartResponse(BaseModel):
    items: List[CartItemWithGame]
    count: int
    total_amount: float

    model_config = ConfigDict(from_attributes=True)


class AddToCartRequest(BaseModel):
    game_id: int


class RemoveFromCartRequest(BaseModel):
    game_id: int
