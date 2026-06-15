"""
local_ai_service.py
Generates fully local, data-driven responses for every question type
without requiring Gemini.  Always returns a meaningful answer.
"""
from __future__ import annotations

import re
from typing import Optional, List

from sqlalchemy.orm import Session

from app.data.cpu_benchmarks import CPU_BENCHMARKS
from app.data.gpu_benchmarks import GPU_BENCHMARKS
from app.models.user import User
from app.services.compatibility_service import (
    compute_compatibility_report,
    get_cpu_score,
    get_gpu_score,
    get_latest_user_scan,
    get_all_user_scans,
)
from app.services.favorite_service import list_user_favorites
from app.services.question_classifier import QuestionType


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find_game_in_db(db: Session, name_hint: str):
    """Best-effort fuzzy game lookup by partial name."""
    from app.models.game import Game
    hint = name_hint.strip().lower()
    games = db.query(Game).all()
    # exact first
    for g in games:
        if g.name.lower() == hint:
            return g
    # partial
    for g in games:
        if hint in g.name.lower() or g.name.lower() in hint:
            return g
    return None


def _extract_game_name(message: str) -> Optional[str]:
    """Pull a potential game name out of common question patterns."""
    patterns = [
        r"(?:can (?:i|my (?:pc|system|laptop)) (?:run|play))\s+(.+?)(?:\?|$)",
        r"(?:will (?:it|my (?:pc|system)) (?:run|play))\s+(.+?)(?:\?|$)",
        r"(?:run|play)\s+(.+?)\s+(?:on my|with my|at)",
        r"(?:compatible with|compatibility (?:of|for))\s+(.+?)(?:\?|$)",
        r"(?:fps (?:for|in|on))\s+(.+?)(?:\?|$)",
        r"(?:performance (?:for|in|on))\s+(.+?)(?:\?|$)",
        r"(.+?)\s+(?:compatible|compatibility|fps|framerate)(?:\?|$)",
    ]
    for pat in patterns:
        m = re.search(pat, message, re.IGNORECASE)
        if m:
            candidate = m.group(1).strip().strip("?").strip()
            if 2 < len(candidate) < 80:
                return candidate
    return None


def _gpu_tier(score: int) -> str:
    if score >= 90: return "flagship"
    if score >= 80: return "high-end"
    if score >= 65: return "mid-range"
    if score >= 45: return "entry-level"
    return "budget"


def _cpu_tier(score: int) -> str:
    if score >= 90: return "top-tier"
    if score >= 75: return "strong"
    if score >= 55: return "mid-range"
    if score >= 40: return "entry-level"
    return "budget"


def _settings_for_score(compat_score: int) -> str:
    if compat_score >= 90: return "Ultra / 1440p+"
    if compat_score >= 75: return "High / 1080p"
    if compat_score >= 55: return "Medium / 1080p"
    if compat_score >= 40: return "Low / 900p"
    return "Minimum settings only"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class LocalAIService:
    def __init__(self, db: Session, user: User):
        self.db = db
        self.user = user

    def answer(self, question_type: QuestionType, message: str) -> str:
        dispatch = {
            QuestionType.COMPATIBILITY:  self._answer_compatibility,
            QuestionType.UPGRADE:        self._answer_upgrade,
            QuestionType.RECOMMENDATION: self._answer_recommendations,
            QuestionType.PROJECT_REVIEW: self._answer_project_review,
            QuestionType.PROFILE:        self._answer_profile,
            QuestionType.GREETING:       self._answer_greeting,
            QuestionType.GENERAL:        self._answer_general_fallback,
        }
        handler = dispatch.get(question_type, self._answer_general_fallback)
        return handler(message)

    def _answer_project_review(self, message: str) -> str:
        """
        Produce a lightweight repository review: list top-level folders/files,
        detect presence of frontend/backend, tests, and key manifests, and give
        actionable suggestions. This runs locally and does not call external AI.
        """
        from pathlib import Path
        root = Path(__file__).resolve().parents[3]

        lines = ["## Project Review", ""]

        # Top-level entries
        try:
            entries = sorted([p.name for p in root.iterdir() if not p.name.startswith('.')])
            lines += ["### Top-level files and folders", ""]
            for e in entries:
                lines.append(f"- {e}")
        except Exception as exc:
            lines.append(f"Could not list repository files: {exc}")

        # Check for common artifacts
        def exists(*parts):
            return (root.joinpath(*parts)).exists()

        lines += ["", "### Detected components", ""]
        components = []
        if exists('backend') or exists('app'):
            components.append("Backend (Python/ FastAPI likely)")
        if exists('frontend') or exists('package.json'):
            components.append("Frontend (JS/TS, Vite/React)")
        if exists('tests') or exists('backend/tests'):
            components.append("Tests present")
        if exists('requirements.txt') or exists('pyproject.toml'):
            components.append("Python dependency manifest")
        if exists('package.json'):
            components.append("Node dependency manifest (package.json)")
        if exists('README.md'):
            components.append("README")

        if components:
            for c in components:
                lines.append(f"- {c}")
        else:
            lines.append("- No common components detected")

        # Quick suggestions
        lines += ["", "### Suggestions", ""]
        lines += [
            "- Ensure `README.md` explains how to run backend and frontend locally.",
            "- Add a `requirements.txt` or `pyproject.toml` for Python dependencies.",
            "- Add tests covering key backend services and a basic frontend smoke test.",
            "- Include a CONTRIBUTING or DEVELOPMENT guide for maintainers.",
        ]

        return "\n".join(lines)

    def _answer_greeting(self, message: str) -> str:
        return (
            "Hello! I am GameReady AI, your specialist assistant for PC gaming compatibility, hardware upgrades, game recommendations, and GameReady platform features. "
            "Ask me about your system, your games, or how to improve your gaming experience."
        )

    # ------------------------------------------------------------------
    # COMPATIBILITY
    # ------------------------------------------------------------------

    def _answer_compatibility(self, message: str) -> str:
        scan = get_latest_user_scan(self.db, self.user.id)
        if not scan:
            return (
                "I don't have your system specs yet. "
                "Please go to **My System** and save your hardware first, "
                "then I can run an accurate compatibility check for any game."
            )

        game_name = _extract_game_name(message)
        game = _find_game_in_db(self.db, game_name) if game_name else None

        if game and game.requirements:
            req = game.requirements[0]
            report = compute_compatibility_report(req, scan)
            score = report["compatibility_percentage"]
            status = report["status"]
            fps = report["estimated_fps"]
            checks = report["checks"]

            lines = [
                f"## Compatibility: {game.name}",
                "",
                f"**Overall Score:** {score}% — {status}",
                "",
                "### Your System vs Requirements",
                f"| Component | Required | Your Spec | Status |",
                f"|-----------|----------|-----------|--------|",
                f"| CPU | {req.cpu} | {scan.cpu} | {'✅' if checks['cpu_pass'] else '⚠️'} |",
                f"| GPU | {req.gpu} | {scan.gpu} | {'✅' if checks['gpu_pass'] else '⚠️'} |",
                f"| RAM | {req.ram_gb} GB | {scan.ram_gb} GB | {'✅' if checks['ram_pass'] else '❌'} |",
                f"| Storage | {req.storage_gb} GB | {scan.storage_gb} GB | {'✅' if checks['storage_pass'] else '❌'} |",
                f"| OS | {req.operating_system or 'Any'} | {scan.operating_system or 'Unknown'} | {'✅' if checks['os_pass'] else '⚠️'} |",
                "",
                "### Expected FPS",
                f"- **Low settings:** {fps['low']} FPS",
                f"- **Medium settings:** {fps['medium']} FPS",
                f"- **High settings:** {fps['high']} FPS",
                f"- **Ultra settings:** {fps['ultra']} FPS",
                "",
                f"**Recommended settings:** {_settings_for_score(score)}",
            ]

            if score < 60:
                lines += [
                    "",
                    "⚠️ Your system struggles with this game's requirements. "
                    "Consider upgrading your GPU or RAM for a better experience.",
                ]
            elif score >= 90:
                lines += ["", "✅ Your system exceeds the requirements — expect a smooth experience!"]

            return "\n".join(lines)

        # Game not in DB — give benchmark-based assessment
        user_gpu_score = get_gpu_score(scan.gpu)
        user_cpu_score = get_cpu_score(scan.cpu)
        gpu_t = _gpu_tier(user_gpu_score)
        cpu_t = _cpu_tier(user_cpu_score)

        game_label = f"**{game_name}**" if game_name else "that game"
        lines = [
            f"## Compatibility Check: {game_name or 'General'}",
            "",
            f"Your system has a {gpu_t} GPU ({scan.gpu}) and a {cpu_t} CPU ({scan.cpu}) "
            f"with {scan.ram_gb} GB RAM.",
            "",
        ]

        if game_name:
            lines += [
                f"I don't have {game_label}'s exact requirements in my database yet. "
                "Based on your hardware tier:",
                "",
                f"- If {game_label} is a **AAA title (2020–2024)**: your system is likely {'capable' if user_gpu_score >= 70 else 'borderline'} at 1080p.",
                f"- If {game_label} is an **indie / older title**: you should run it comfortably.",
                "",
                "For exact FPS numbers, check the game's Steam page for requirements and compare "
                "against your specs on the **Compatible Games** page.",
            ]
        else:
            lines += [
                "Please specify a game title for a detailed compatibility report.",
                "Example: *Can my PC run Elden Ring?*",
            ]

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # UPGRADE
    # ------------------------------------------------------------------

    def _answer_upgrade(self, message: str) -> str:
        scan = get_latest_user_scan(self.db, self.user.id)
        if not scan:
            return (
                "To give upgrade advice I need your system specs. "
                "Please go to **My System** and save your hardware first."
            )

        gpu_score = get_gpu_score(scan.gpu)
        cpu_score = get_cpu_score(scan.cpu)
        ram_gb = scan.ram_gb or 0

        # Identify weakest component
        bottleneck = "GPU"
        if cpu_score < gpu_score - 20:
            bottleneck = "CPU"
        elif ram_gb < 16:
            bottleneck = "RAM"

        # Build GPU upgrade suggestions
        gpu_suggestions = []
        for name, score in sorted(GPU_BENCHMARKS.items(), key=lambda x: x[1]):
            if score > gpu_score + 10:
                gpu_suggestions.append(f"- **{name.upper()}** (score: {score}/100)")
            if len(gpu_suggestions) >= 3:
                break

        # Build CPU upgrade suggestions
        cpu_suggestions = []
        for name, score in sorted(CPU_BENCHMARKS.items(), key=lambda x: x[1]):
            if score > cpu_score + 10:
                cpu_suggestions.append(f"- **{name.upper()}** (score: {score}/100)")
            if len(cpu_suggestions) >= 3:
                break

        lines = [
            "## Upgrade Analysis",
            "",
            "### Your Current Build",
            f"- **GPU:** {scan.gpu} (score: {gpu_score}/100 — {_gpu_tier(gpu_score)})",
            f"- **CPU:** {scan.cpu} (score: {cpu_score}/100 — {_cpu_tier(cpu_score)})",
            f"- **RAM:** {ram_gb} GB {'✅' if ram_gb >= 16 else '⚠️ (16 GB recommended for modern games)'}",
            f"- **Storage:** {scan.storage_gb} GB",
            "",
            f"### 🎯 Primary Bottleneck: **{bottleneck}**",
            "",
        ]

        if bottleneck == "GPU":
            lines += [
                "Your GPU is the limiting factor for gaming performance. "
                "Upgrading it will give you the biggest FPS boost.",
                "",
                "**Suggested GPU upgrades:**",
            ] + gpu_suggestions

        elif bottleneck == "CPU":
            lines += [
                "Your CPU is holding back your GPU. A faster processor will improve "
                "1% lows and open-world game performance.",
                "",
                "**Suggested CPU upgrades:**",
            ] + cpu_suggestions

        else:
            lines += [
                "Your GPU and CPU are well-matched, but **16 GB RAM** is the sweet spot "
                "for modern AAA titles. Adding more RAM will reduce stutters and improve "
                "loading times.",
                "",
                "After upgrading RAM, consider:",
                "**GPU upgrades for more FPS:**",
            ] + gpu_suggestions

        lines += [
            "",
            "### Priority Order",
            f"1. **{bottleneck}** — biggest impact on your gaming experience",
            "2. RAM (if below 16 GB)",
            "3. SSD storage (if still on HDD)",
            "",
            "_Prices vary — check current deals on your preferred retailer._",
        ]

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # RECOMMENDATIONS
    # ------------------------------------------------------------------

    def _answer_recommendations(self, message: str) -> str:
        from app.models.game import Game

        scan = get_latest_user_scan(self.db, self.user.id)
        favorites = list_user_favorites(self.db, self.user.id)
        all_games = self.db.query(Game).all()

        if not all_games:
            return (
                "No games are in the database yet. "
                "Ask an admin to add games, then I can recommend titles for your system."
            )

        # Filter by genre preference if detectable
        msg_lower = message.lower()
        genre_hint = None
        genre_keywords = {
            "action": "Action",
            "rpg": "RPG",
            "action rpg": "Action RPG",
            "racing": "Racing",
            "shooter": "Shooter",
            "strategy": "Strategy",
            "adventure": "Action Adventure",
            "sports": "Sports",
            "simulation": "Simulation",
        }
        for kw, genre in genre_keywords.items():
            if kw in msg_lower:
                genre_hint = genre
                break

        # Score each game by compatibility with user system
        scored: list[tuple] = []
        for game in all_games:
            if not game.requirements:
                continue
            req = game.requirements[0]
            if scan:
                report = compute_compatibility_report(req, scan)
                compat = report["compatibility_percentage"]
                fps = report["estimated_fps"]["medium"]
            else:
                compat = 50
                fps = 30

            # Boost favorites
            fav_ids = {f.game_id for f in favorites}
            is_fav = game.id in fav_ids

            if genre_hint and game.genre:
                if genre_hint.lower() not in (game.genre or "").lower():
                    continue

            scored.append((compat, fps, is_fav, game))

        if not scored:
            return (
                f"No {'**' + genre_hint + '**' if genre_hint else ''} games found in the database "
                "that match your filter. Try a different genre or check the Game Library."
            )

        # Sort: favourites first, then by compatibility
        scored.sort(key=lambda x: (not x[2], -x[0], -x[1]))
        top = scored[:6]

        lines = [
            f"## Game Recommendations{' — ' + genre_hint if genre_hint else ''}",
            "",
        ]

        if not scan:
            lines += [
                "⚠️ _No system specs saved yet — showing all available games. "
                "Save your specs in **My System** for personalized compatibility scores._",
                "",
            ]

        for compat, fps, is_fav, game in top:
            status_emoji = "✅" if compat >= 70 else "⚠️" if compat >= 50 else "❌"
            fav_tag = " ⭐" if is_fav else ""
            lines += [
                f"### {status_emoji} {game.name}{fav_tag}",
                f"- **Genre:** {game.genre or 'Unknown'}",
                f"- **Compatibility:** {compat}%  |  **Est. FPS (Medium):** {fps}",
                f"- **Publisher:** {game.publisher or 'Unknown'}",
                "",
            ]

        lines += [
            "_Visit the **Game Library** to browse all available titles._",
        ]
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # PROFILE
    # ------------------------------------------------------------------

    def _answer_profile(self, message: str) -> str:
        scan = get_latest_user_scan(self.db, self.user.id)
        scans = get_all_user_scans(self.db, self.user.id)
        favorites = list_user_favorites(self.db, self.user.id)

        lines = [
            f"## Gaming Profile — {self.user.username}",
            "",
        ]

        # System overview
        if scan:
            gpu_score = get_gpu_score(scan.gpu)
            cpu_score = get_cpu_score(scan.cpu)
            lines += [
                "### 🖥️ System Overview",
                f"- **GPU:** {scan.gpu} ({_gpu_tier(gpu_score)})",
                f"- **CPU:** {scan.cpu} ({_cpu_tier(cpu_score)})",
                f"- **RAM:** {scan.ram_gb} GB",
                f"- **Storage:** {scan.storage_gb} GB",
                f"- **OS:** {scan.operating_system or 'Unknown'}",
                "",
                "### 🎯 System Tier",
            ]
            overall = (gpu_score * 0.6 + cpu_score * 0.4)
            if overall >= 85:
                tier, desc = "High-End Gaming Rig", "Can run virtually any game at Ultra settings."
            elif overall >= 65:
                tier, desc = "Mid-Range Gaming PC", "Great for most modern games at High settings."
            elif overall >= 45:
                tier, desc = "Entry-Level Gaming", "Handles older titles and lighter modern games well."
            else:
                tier, desc = "Budget / Older System", "Best suited for indie games and older titles."
            lines += [f"**{tier}** — {desc}", ""]
        else:
            lines += [
                "⚠️ No system specs saved. Go to **My System** to add your hardware.",
                "",
            ]

        # Favourites & genre analysis
        if favorites:
            fav_games = [f.game for f in favorites if f.game]
            genres = [g.genre for g in fav_games if g.genre]
            genre_counts: dict[str, int] = {}
            for g in genres:
                genre_counts[g] = genre_counts.get(g, 0) + 1

            lines += ["### 🎮 Favourite Games"]
            for fav in favorites[:5]:
                if fav.game:
                    lines.append(f"- {fav.game.name} ({fav.game.genre or 'Unknown genre'})")
            lines.append("")

            if genre_counts:
                top_genre = max(genre_counts, key=genre_counts.get)
                lines += [
                    "### 📊 Genre Preferences",
                    f"- **Top genre:** {top_genre}",
                ]
                for genre, count in sorted(genre_counts.items(), key=lambda x: -x[1]):
                    lines.append(f"- {genre}: {count} game{'s' if count > 1 else ''}")
                lines.append("")
        else:
            lines += [
                "### 🎮 Favourites",
                "No favourites saved yet. Star games in the Game Library to build your profile.",
                "",
            ]

        # Scan history summary
        game_scans = [s for s in scans if s.game_id]
        if game_scans:
            avg_compat = sum(s.compatibility_score for s in game_scans) / len(game_scans)
            lines += [
                "### 📈 Compatibility History",
                f"- **Games scanned:** {len(game_scans)}",
                f"- **Average compatibility:** {avg_compat:.0f}%",
            ]
            best = max(game_scans, key=lambda s: s.compatibility_score)
            if best.game:
                lines.append(f"- **Best match:** {best.game.name} ({best.compatibility_score:.0f}%)")
            lines.append("")

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # GENERAL FALLBACK (no Gemini available)
    # ------------------------------------------------------------------

    def _answer_general_fallback(self, message: str) -> str:
        return (
            "AI gaming knowledge features are temporarily unavailable because the AI quota "
            "has been reached. GameReady can still answer **compatibility**, **FPS**, "
            "**upgrade**, and **recommendation** questions using local system data.\n\n"
            "Try asking:\n"
            "- *Can my PC run Elden Ring?*\n"
            "- *What should I upgrade?*\n"
            "- *Recommend games for my system.*\n"
            "- *Analyze my gaming profile.*"
        )


__all__ = ["LocalAIService"]
