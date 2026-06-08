from pydantic import BaseModel


class OSCreate(BaseModel):
    name: str


class OSResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True
