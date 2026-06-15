from pydantic import BaseModel
from typing import Dict, Any, Optional, List


class ExplanationRequest(BaseModel):
    game_id: Optional[int]
    game_requirements: Dict[str, Any]
    system_profile: Dict[str, Any]


class ExplanationResponse(BaseModel):
    summary: str
    details: Dict[str, Any]


class UpgradeRequest(BaseModel):
    system_profile: Dict[str, Any]
    target_goal: Optional[str] = None


class UpgradeOption(BaseModel):
    component: str
    current: Any
    suggested: Any
    cost_estimate: Optional[str] = None
    expected_gain_pct: Optional[float] = None


class UpgradeResponse(BaseModel):
    bottleneck: str
    options: List[UpgradeOption]
