from pydantic import BaseModel, ConfigDict


class OSCreate(BaseModel):
    name: str


class OSResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)
