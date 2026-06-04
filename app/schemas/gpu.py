from pydantic import BaseModel


class GPUCreate(BaseModel):
    name: str


class GPUResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True