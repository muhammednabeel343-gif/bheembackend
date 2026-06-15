from typing import Optional
from pydantic import BaseModel, ConfigDict


class SystemScanResponse(BaseModel):
    cpu: str
    gpu: str
    ram_gb: int
    storage_gb: int
    operating_system: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


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

    model_config = ConfigDict(from_attributes=True)


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


class AIInsightsResponse(BaseModel):
    gpu_analysis: Optional[str] = None
    cpu_analysis: Optional[str] = None
    ram_analysis: Optional[str] = None
    storage_analysis: Optional[str] = None
    os_analysis: Optional[str] = None
    expected_experience: Optional[str] = None
    recommended_settings: list = []
    tips: list = []
    warnings: list = []

    model_config = ConfigDict(from_attributes=True)


class CompatibilityResponse(BaseModel):
    minimum_requirements: dict
    user_specs: UserSpecsResponse
    checks: CompatibilityCheckResponse
    compatibility_percentage: int
    status: str
    estimated_fps: FpsEstimateResponse
    ai_insights: Optional[AIInsightsResponse] = None

    model_config = ConfigDict(from_attributes=True)


class SimulatorRequest(BaseModel):
    game_id: int
    cpu: str
    gpu: str
    ram_gb: int
    storage_gb: int
    operating_system: str = "Windows"
