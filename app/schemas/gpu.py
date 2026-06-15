from pydantic import BaseModel, ConfigDict


class GPUCreate(BaseModel):
    name: str


class GPUResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)