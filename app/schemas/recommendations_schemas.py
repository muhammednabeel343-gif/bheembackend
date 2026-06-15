from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class RecommendationItem(BaseModel):
    game_id: int
    name: str
    compatibility: float
    genres: List[str]
    reason: Optional[str] = None


class RecommendationsResponse(BaseModel):
    recommendations: List[RecommendationItem]


class RecommendationReasonResponse(BaseModel):
    game_id: int
    reason: str


class ProfileInsightsResponse(BaseModel):
    user_id: Optional[int]
    avg_compatibility: float
    favorite_genres: List[str]
    strengths: List[str]
    weaknesses: List[str]
    recommended_games: List[RecommendationItem]
