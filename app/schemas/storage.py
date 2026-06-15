from pydantic import BaseModel, ConfigDict


class StorageCreate(BaseModel):
    size: int


class StorageResponse(BaseModel):
    id: int
    size: int

    model_config = ConfigDict(from_attributes=True)