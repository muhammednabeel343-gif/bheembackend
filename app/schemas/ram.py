from pydantic import BaseModel, ConfigDict


class RAMCreate(BaseModel):
    size: int


class RAMResponse(BaseModel):
    id: int
    size: int

    model_config = ConfigDict(from_attributes=True)