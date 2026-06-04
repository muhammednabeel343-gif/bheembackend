from datetime import date
from typing import Optional, Any
from pydantic import BaseModel


class GameBase(BaseModel):
    name: str
    description: Optional[str] = None
    genre: Optional[str] = None
    release_date: Optional[str] = None
    image_url: Optional[str] = None
    publisher: Optional[str] = None


class GameCreate(GameBase):
    cpu: Optional[str] = None
    gpu: Optional[str] = None
    ram_gb: Optional[int] = None
    storage: Optional[int] = None
    directx: Optional[str] = None
    operating_system: Optional[str] = None


class GameUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    genre: Optional[str] = None
    release_date: Optional[str] = None
    image_url: Optional[str] = None
    publisher: Optional[str] = None
    cpu: Optional[str] = None
    gpu: Optional[str] = None
    ram_gb: Optional[int] = None
    storage: Optional[int] = None
    directx: Optional[str] = None
    operating_system: Optional[str] = None


class GameResponse(BaseModel):
    id: int
    name: str
    genre: Optional[str] = None
    publisher: Optional[str] = None
    release_date: Optional[str] = None
    image_url: Optional[str] = None
    cpu: Optional[str] = None
    gpu: Optional[str] = None
    ram_gb: Optional[int] = None
    directx: Optional[str] = None
    operating_system: Optional[str] = None
    storage: Optional[int] = None

    class Config:
        from_attributes = True


class GameListResponse(BaseModel):
    games: list[GameResponse]
    total: int
    page: int
    limit: int
