from fastapi import APIRouter, Depends, HTTPException
from app.services.recommendation_service import RecommendationService
from app.services.profile_insights_service import ProfileInsightsService
from typing import Optional

router = APIRouter()


@router.get("/api/recommendations")
def get_recommendations(user_id: Optional[int] = None, limit: int = 8):
    svc = RecommendationService()
    return svc.recommend_for_user(user_id, limit).dict()


@router.get("/api/recommendations/{game_id}")
def get_recommendations_for_game(game_id: int, limit: int = 8):
    svc = RecommendationService()
    return svc.recommend_for_game(game_id, limit).dict()


@router.get("/api/profile/{user_id}/insights")
def get_profile_insights(user_id: int):
    svc = ProfileInsightsService()
    return svc.insights_for_user(user_id).dict()
