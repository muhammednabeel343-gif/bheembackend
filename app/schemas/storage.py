from pydantic import BaseModel


class StorageCreate(BaseModel):
    size: int


class StorageResponse(BaseModel):
    id: int
    size: int

    class Config:
        from_attributes = True