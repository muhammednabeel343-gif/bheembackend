from typing import List
from pydantic import BaseModel, ConfigDict


class FavoriteCreate(BaseModel):
    game_id: int


class FavoriteItem(BaseModel):
    id: int
    game_id: int
    name: str
    genre: str | None = None
    image_url: str | None = None

    model_config = ConfigDict(from_attributes=True)


class FavoriteListResponse(BaseModel):
    favorites: List[FavoriteItem]
