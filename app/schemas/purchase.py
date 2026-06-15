from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class PurchasedGameResponse(BaseModel):
    id: int
    user_id: int
    game_id: int
    game_name: str
    image_url: Optional[str] = None
    genre: Optional[str] = None
    purchase_date: datetime

    model_config = ConfigDict(from_attributes=True)


class UserLibraryResponse(BaseModel):
    games: list
    total_count: int

    model_config = ConfigDict(from_attributes=True)


class IsPurchasedResponse(BaseModel):
    is_purchased: bool
    purchase_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
