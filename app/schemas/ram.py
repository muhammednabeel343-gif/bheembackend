from pydantic import BaseModel


class RAMCreate(BaseModel):
    size: int


class RAMResponse(BaseModel):
    id: int
    size: int

    class Config:
        from_attributes = True