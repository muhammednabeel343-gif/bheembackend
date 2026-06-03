from typing import List
from pydantic import BaseModel


class FavoriteCreate(BaseModel):
    game_id: int


class FavoriteItem(BaseModel):
    id: int
    game_id: int
    name: str
    genre: str | None = None
    image_url: str | None = None

    class Config:
        from_attributes = True


class FavoriteListResponse(BaseModel):
    favorites: List[FavoriteItem]
