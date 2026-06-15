from typing import Optional
from app.schemas.recommendations_schemas import ProfileInsightsResponse, RecommendationItem


class ProfileInsightsService:
    def __init__(self, client=None):
        self.client = client

    def insights_for_user(self, user_id: Optional[int] = None) -> ProfileInsightsResponse:
        # Mock insights
        recs = [RecommendationItem(game_id=301 + i, name=f"Insight Game {i+1}", compatibility=80 + i, genres=["RPG"]) for i in range(3)]
        return ProfileInsightsResponse(
            user_id=user_id,
            avg_compatibility=78.5,
            favorite_genres=["Action", "RPG"],
            strengths=["GPU-bound games", "Action titles"],
            weaknesses=["Simulation/VR"],
            recommended_games=recs,
        )


__all__ = ["ProfileInsightsService"]
