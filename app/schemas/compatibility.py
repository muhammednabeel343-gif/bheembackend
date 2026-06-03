from typing import Optional
from pydantic import BaseModel


class SystemScanResponse(BaseModel):
    cpu: str
    gpu: str
    ram_gb: int
    storage_gb: int
    operating_system: Optional[str] = None

    class Config:
        from_attributes = True


class SaveSystemScanRequest(BaseModel):
    cpu: str
    gpu: str
    ram_gb: int
    storage_gb: int
    operating_system: Optional[str] = None
    game_id: Optional[int] = None


class UserSpecsResponse(BaseModel):
    cpu: str
    gpu: str
    ram_gb: int
    storage_gb: int
    operating_system: Optional[str] = None

    class Config:
        from_attributes = True


class CompatibilityCheckResponse(BaseModel):
    cpu_pass: bool
    gpu_pass: bool
    ram_pass: bool
    storage_pass: bool


class FpsEstimateResponse(BaseModel):
    low: int
    medium: int
    high: int
    ultra: int


class CompatibilityResponse(BaseModel):
    minimum_requirements: dict
    user_specs: UserSpecsResponse
    checks: CompatibilityCheckResponse
    compatibility_percentage: int
    status: str
    estimated_fps: FpsEstimateResponse

    class Config:
        from_attributes = True


class SimulatorRequest(BaseModel):
    game_id: int
    cpu: str
    gpu: str
    ram_gb: int
    storage_gb: int
