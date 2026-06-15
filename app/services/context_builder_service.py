"""
context_builder_service.py
Builds rich context text for Gemini prompts AND exposes structured data
for the local AI engine.
"""
from __future__ import annotations

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models.user import User
from app.services.compatibility_service import (
    get_latest_user_scan,
    get_all_user_scans,
    get_cpu_score,
    get_gpu_score,
)
from app.services.favorite_service import list_user_favorites


def _format_requirement(requirement) -> str:
    if not requirement:
        return "No requirement details available."
    return (
        f"{requirement.cpu} / {requirement.gpu} / "
        f"{requirement.ram_gb}GB RAM / {requirement.storage_gb}GB storage / "
        f"OS: {requirement.operating_system or 'Unknown'}"
    )


def _format_game_summary(game) -> str:
    if not game:
        return "Unknown game"
    release_date = game.release_date.isoformat() if getattr(game, "release_date", None) else "Unknown"
    requirement = game.requirements[0] if getattr(game, "requirements", None) else None
    requirements_text = _format_requirement(requirement)
    return (
        f"{game.name} ({game.genre or 'Unknown genre'}) - Released: {release_date}. "
        f"Requirements: {requirements_text}"
    )


class ContextBuilderService:
    def __init__(self, db: Session, user: User):
        self.db = db
        self.user = user

    # ------------------------------------------------------------------
    # Structured data — used by LocalAIService and hybrid pipeline
    # ------------------------------------------------------------------

    def get_structured(self) -> Dict[str, Any]:
        """Return all user data as a plain dict for programmatic use."""
        scan = get_latest_user_scan(self.db, self.user.id)
        scans = get_all_user_scans(self.db, self.user.id)
        favorites = list_user_favorites(self.db, self.user.id)

        result: Dict[str, Any] = {
            "user": {"id": self.user.id, "username": self.user.username},
            "system": None,
            "favorites": [],
            "scan_history": [],
        }

        if scan:
            result["system"] = {
                "cpu": scan.cpu,
                "gpu": scan.gpu,
                "ram_gb": scan.ram_gb,
                "storage_gb": scan.storage_gb,
                "operating_system": scan.operating_system,
                "compatibility_score": scan.compatibility_score,
                "cpu_score": get_cpu_score(scan.cpu),
                "gpu_score": get_gpu_score(scan.gpu),
            }

        result["favorites"] = [
            {
                "name": f.game.name,
                "genre": f.game.genre,
            }
            for f in favorites
            if f.game
        ]

        result["scan_history"] = [
            {
                "game": s.game.name if s.game else None,
                "compatibility_score": s.compatibility_score,
                "cpu": s.cpu,
                "gpu": s.gpu,
                "ram_gb": s.ram_gb,
                "storage_gb": s.storage_gb,
                "os": s.operating_system,
            }
            for s in scans[:10]
        ]

        return result

    # ------------------------------------------------------------------
    # Plain text context — used by Gemini prompt construction
    # ------------------------------------------------------------------

    def build_context(self) -> str:
        sections: List[str] = [
            self._build_profile_section(),
            self._build_system_section(),
            self._build_favorites_section(),
            self._build_recent_scans_section(),
            self._build_game_insights_section(),
        ]
        return "\n\n".join(s for s in sections if s)

    def _build_profile_section(self) -> str:
        return (
            "User Profile:\n"
            f"- Username: {self.user.username}\n"
            f"- Email: {self.user.email}\n"
            "Use this to personalize answers and recommend games."
        )

    def _build_system_section(self) -> str:
        scan = get_latest_user_scan(self.db, self.user.id)
        if not scan:
            return "System Profile: No saved system scan available."
        return (
            "System Profile:\n"
            f"- CPU: {scan.cpu}\n"
            f"- GPU: {scan.gpu}\n"
            f"- RAM: {scan.ram_gb} GB\n"
            f"- Storage: {scan.storage_gb} GB\n"
            f"- OS: {scan.operating_system or 'Unknown'}\n"
            f"- Last compatibility score: {scan.compatibility_score:.1f}%\n"
        )

    def _build_favorites_section(self) -> str:
        favorites = list_user_favorites(self.db, self.user.id)
        if not favorites:
            return "Favorites: No favorite games saved."
        items = [
            f"- {f.game.name} ({f.game.genre or 'Unknown genre'})"
            f" - Released: {f.game.release_date.isoformat() if f.game.release_date else 'Unknown'}"
            for f in favorites[:5]
        ]
        return "Favorites:\n" + "\n".join(items)

    def _build_recent_scans_section(self) -> str:
        scans = get_all_user_scans(self.db, self.user.id)
        if not scans:
            return "Recent Scan History: No scan history available."
        items = []
        for scan in scans[:5]:
            game_name = scan.game.name if scan.game else "System-only scan"
            items.append(
                f"- {game_name}: {scan.compatibility_score:.1f}% compatibility, "
                f"{scan.ram_gb}GB RAM, {scan.storage_gb}GB storage, {scan.operating_system or 'Unknown OS'}"
            )
        return "Recent Scan History:\n" + "\n".join(items)

    def _build_game_insights_section(self) -> str:
        favorites = list_user_favorites(self.db, self.user.id)
        favorite_games = [f.game for f in favorites if f.game][:3]
        scans = get_all_user_scans(self.db, self.user.id)
        recent_games = []
        for scan in scans:
            if scan.game and scan.game not in favorite_games and len(recent_games) < 3:
                recent_games.append(scan.game)

        items = [f"- {_format_game_summary(g)}" for g in favorite_games + recent_games]
        if not items:
            return "Game Insights: No favorite or scanned games available."
        return "Game Insights:\n" + "\n".join(items)
