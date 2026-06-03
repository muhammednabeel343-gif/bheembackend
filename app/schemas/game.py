from datetime import date
from typing import List, Optional

from pydantic import BaseModel, HttpUrl


class RequirementResponse(BaseModel):
    id: int
    cpu: str
    gpu: str
    ram_gb: int
    storage_gb: int
    directx: Optional[str] = None
    operating_system: Optional[str] = None

    class Config:
        from_attributes = True


class GameListItem(BaseModel):
    id: int
    name: str
    genre: str
    image_url: Optional[HttpUrl] = None
    is_favorite: bool = False

    class Config:
        from_attributes = True


class GameDetail(BaseModel):
    id: int
    name: str
    genre: str
    publisher: Optional[str] = None
    release_date: Optional[date] = None
    image_url: Optional[HttpUrl] = None

    requirements: List[RequirementResponse] = []

    is_favorite: bool = False

    class Config:
        from_attributes = True


class GameListResponse(BaseModel):
    games: List[GameListItem]
    total: int
    page: int
    limit: int