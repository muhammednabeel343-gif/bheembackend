from pydantic import BaseModel, ConfigDict

class CPUCreate(BaseModel):
    name: str

class CPUResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)