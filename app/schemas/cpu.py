from pydantic import BaseModel

class CPUCreate(BaseModel):
    name: str

class CPUResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True