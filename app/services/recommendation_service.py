from typing import List, Optional
from app.schemas.recommendations_schemas import RecommendationItem, RecommendationsResponse
from app.database import SessionLocal
from app.models.game import Game
from app.services.compatibility_service import get_latest_user_scan, compute_compatibility_report


class RecommendationService:
    def __init__(self, client=None):
        self.client = client

    def recommend_for_user(self, user_id: Optional[int] = None, limit: int = 8) -> RecommendationsResponse:
        """Return top `limit` recommended games for a user.

        If `user_id` is not provided or no system scan exists, fall back to a simple popularity mock.
        """
        if not user_id:
            # fallback mock list
            items = [
                RecommendationItem(game_id=101 + i, name=f"Mock Game {i+1}", compatibility=90 - i, genres=["Action", "RPG"]) for i in range(limit)
            ]
            return RecommendationsResponse(recommendations=items)

        db = SessionLocal()
        try:
            scan = get_latest_user_scan(db, user_id)
            if not scan:
                # no scan for user; fallback
                return self.recommend_for_user(None, limit)

            games = db.query(Game).all()
            results: List[RecommendationItem] = []
            for g in games:
                req = g.requirements[0] if g.requirements else None
                if not req:
                    # assume medium compatibility for games without explicit requirements
                    score = 60.0
                else:
                    report = compute_compatibility_report(req, scan)
                    score = float(report.get("compatibility_percentage", 0))

                genres = [g.genre] if g.genre else []
                results.append(RecommendationItem(game_id=g.id, name=g.name, compatibility=score, genres=genres))

            results.sort(key=lambda x: x.compatibility, reverse=True)
            return RecommendationsResponse(recommendations=results[:limit])

        finally:
            db.close()

    def recommend_for_game(self, game_id: int, limit: int = 8) -> RecommendationsResponse:
        """Recommend games similar to `game_id` by genre and basic heuristics.

        This uses simple similarity on `genre` and falls back to mock data when necessary.
        """
        db = SessionLocal()
        try:
            base = db.query(Game).filter(Game.id == game_id).first()
            if not base:
                # fallback mock
                items = [RecommendationItem(game_id=201 + i, name=f"Similar Game {i+1}", compatibility=85 - i, genres=["Action"]) for i in range(limit)]
                return RecommendationsResponse(recommendations=items)

            # find other games in same genre
            others = db.query(Game).filter(Game.genre == base.genre, Game.id != base.id).limit(limit).all()
            items = []
            for o in others:
                # naive compatibility score based on availability of requirements
                score = 75.0
                if o.requirements and base.requirements:
                    score = 80.0
                items.append(RecommendationItem(game_id=o.id, name=o.name, compatibility=score, genres=[o.genre] if o.genre else []))

            if not items:
                items = [RecommendationItem(game_id=301 + i, name=f"Similar Game {i+1}", compatibility=70 - i, genres=[base.genre or "Unknown"]) for i in range(limit)]

            return RecommendationsResponse(recommendations=items[:limit])
        finally:
            db.close()


__all__ = ["RecommendationService"]
