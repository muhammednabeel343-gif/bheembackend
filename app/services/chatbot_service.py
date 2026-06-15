import threading
from typing import List, Dict
from sqlalchemy.orm import Session
from app.models.user import User
from app.services.gemini_service import GeminiService
from app.services.context_builder_service import ContextBuilderService
from app.config import settings


class ChatbotService:
    _session_memory: dict[int, List[Dict[str, str]]] = {}
    _lock = threading.Lock()

    def __init__(self, db: Session, user: User):
        self.db = db
        self.user = user
        self.gemini = GeminiService()
        self.context_builder = ContextBuilderService(db, user)

    def _ensure_memory(self) -> None:
        with self._lock:
            if self.user.id not in self._session_memory:
                self._session_memory[self.user.id] = []

    def get_history(self) -> List[Dict[str, str]]:
        self._ensure_memory()
        with self._lock:
            return list(self._session_memory[self.user.id])

    def reset_history(self) -> None:
        with self._lock:
            self._session_memory[self.user.id] = []

    def record_message(self, role: str, content: str) -> None:
        self._ensure_memory()
        with self._lock:
            self._session_memory[self.user.id].append({"role": role, "content": content})
            if len(self._session_memory[self.user.id]) > 12:
                self._session_memory[self.user.id] = self._session_memory[self.user.id][-12:]

    def _build_history_section(self) -> str:
        history = self.get_history()
        if not history:
            return ""

        lines = ["Conversation history:"]
        for message in history:
            role = message["role"].capitalize()
            lines.append(f"{role}: {message['content']}")
        return "\n".join(lines)

    def _heuristic_answer(self, message: str, context_text: str) -> str:
        """Generate a contextual answer using heuristic rules when Gemini is unavailable.
        
        This extracts game names and system info from context to provide realistic answers.
        """
        msg_lower = message.lower()
        
        # Try to extract game name from common question patterns
        game_name = None
        patterns = [
            r"run\s+(.*?)\?",  # "run Elden Ring?"
            r"play\s+(.*?)\?",  # "play Cyberpunk?"
            r"(.*?)\s+compatible",  # "Baldur's Gate compatible?"
            r"(.*?)\s+fps",  # "Elden Ring fps"
        ]
        import re
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                game_name = match.group(1).strip()
                break
        
        # Extract system info from context if available
        has_system_profile = "System Profile:" in context_text and "CPU:" in context_text
        has_scan_history = "Recent Scan History:" in context_text
        
        # Compatibility question with specific game
        if any(word in msg_lower for word in ["compatible", "can i run", "will run", "will it run"]):
            if game_name:
                return (
                    f"Based on your system profile, {game_name} should be playable. "
                    f"To get exact FPS estimates and optimal graphics settings, "
                    f"please run a compatibility scan for this game in the GameReady system analyzer. "
                    f"This will check your specific hardware against the game's requirements."
                )
            else:
                return (
                    "To check game compatibility, name a specific title (e.g., 'Can I run Baldur's Gate 3?') "
                    "and I'll assess your system specs against its requirements. "
                    "For detailed FPS estimates, run a compatibility scan in the analyzer."
                )
        
        # FPS/Performance question
        elif any(word in msg_lower for word in ["fps", "performance", "framerate", "frames"]):
            if game_name:
                return (
                    f"FPS for {game_name} depends on your exact GPU, resolution, and settings. "
                    f"Run a compatibility scan for specific performance predictions. "
                    f"Generally, modern AAA games expect 60+ FPS at 1080p with mid-range GPUs."
                )
            else:
                return (
                    "FPS varies greatly by game, resolution, and graphics settings. "
                    "Modern AAA titles typically target 60+ FPS at 1080p. "
                    "Use the compatibility scanner to get exact predictions for specific games."
                )
        
        # Upgrade/bottleneck question
        elif any(word in msg_lower for word in ["upgrade", "improve", "bottleneck", "better"]):
            if has_system_profile:
                return (
                    "Based on your current system, I recommend identifying your bottleneck first. "
                    "Run a compatibility scan for games you want to play—it will highlight which component limits performance. "
                    "Typically GPU upgrades offer the best FPS improvement for gaming."
                )
            else:
                return (
                    "I can identify your hardware bottleneck once you complete a system scan. "
                    "The scanner will compare your CPU, GPU, and RAM against modern game requirements "
                    "and suggest the most impactful upgrade path."
                )
        
        # Recommendation question
        elif any(word in msg_lower for word in ["recommend", "suggest", "which game", "what game", "like"]):
            if has_scan_history:
                return (
                    "Based on your scan history and favorites, I can recommend compatible games in your preferred genres. "
                    "Check the Recommendations section in your profile, or mark more games as favorites "
                    "to get better personalized suggestions."
                )
            else:
                return (
                    "I can recommend games compatible with your system. "
                    "Complete a compatibility scan first so I understand your hardware capabilities, "
                    "then tell me your favorite genres or game titles."
                )
        
        # Library/favorites question
        elif any(word in msg_lower for word in ["favorite", "library", "played", "wishlist"]):
            return (
                "Manage your game library and favorites in the GameReady dashboard. "
                "Mark games as favorites to get personalized compatibility insights and upgrade recommendations. "
                "Your library helps me understand what games you're interested in."
            )
        
        # Default fallback
        else:
            return (
                "I'm GameReady AI, your gaming compatibility expert. "
                "I can help with: game compatibility checks, FPS estimates, hardware upgrade advice, and game recommendations. "
                "Name a game or ask about your system to get started!"
            )

    # ------------------------------------------------------------------
    # Strict project-data mode helpers
    # ------------------------------------------------------------------
    def _classify_question(self, message: str) -> str:
        """Classify the user's question into allowed categories or 'disallowed'.

        Returns one of: 'system_specs', 'can_run', 'fps', 'upgrade',
        'compatible_games', 'recommend_games', 'profile_insights',
        'compatibility_history', 'disallowed', 'unknown'.
        """
        m = message.lower()
        # Disallowed: clear negative list of subject keywords
        disallowed_keywords = [
            "dlss",
            "ray tracing",
            "cristiano",
            "who is",
            "write python",
            "write code",
            "solve",
            "math",
            "joke",
            "world war",
            "history",
        ]
        for kw in disallowed_keywords:
            if kw in m:
                return "disallowed"

        # Allowed patterns
        if any(x in m for x in ["what are my system specs", "my system specs", "system specs", "what is my system"]) or any(x in m for x in ["my cpu", "my gpu", "my ram"]):
            return "system_specs"
        if any(x in m for x in ["can i run", "will run", "compatible", "can my pc run"]):
            return "can_run"
        if any(x in m for x in ["fps", "framerate", "frames"]):
            return "fps"
        if any(x in m for x in ["upgrade", "improve", "bottleneck"]):
            return "upgrade"
        if any(x in m for x in ["which games", "which game", "compatible games", "games are compatible", "library"]):
            return "compatible_games"
        if any(x in m for x in ["recommend", "recommend games", "recommendation", "suggest games"]):
            return "recommend_games"
        if any(x in m for x in ["profile", "profile insights", "my profile", "show my profile"]):
            return "profile_insights"
        if any(x in m for x in ["history", "scan history", "compatibility history", "my scans"]):
            return "compatibility_history"

        return "unknown"

    def _can_answer_with_project_data(self, category: str, message: str) -> bool:
        """Decide whether the question can be answered using only GameReady project data.

        Uses structured data from ContextBuilderService and simple heuristics.
        """
        structured = self.context_builder.get_structured()

        # Disallowed cannot be answered
        if category == "disallowed":
            return False

        # If unknown, require explicit system or scan data to proceed
        if category == "unknown":
            # We only answer unknown if there is a saved system or scan
            return bool(structured.get("system") or structured.get("scan_history"))

        # For system specs, require a saved system
        if category == "system_specs":
            return bool(structured.get("system"))

        # For can_run / fps / upgrade / compatible_games / recommend_games,
        # require a saved system and at least one game in favorites or scan history
        if category in ("can_run", "fps", "upgrade", "compatible_games", "recommend_games"):
            has_system = bool(structured.get("system"))
            # check if user referenced a specific game in the message and if it's present in favorites or scans
            import re
            match = re.search(r"can i run\s+([\w\s\'\-]+)\??", message, re.IGNORECASE)
            if match:
                game_name = match.group(1).strip().lower()
                # search favorites and scan_history for the game name
                in_favorites = any(game_name in (f.get("name") or "").lower() for f in structured.get("favorites", []))
                in_scans = any(game_name in (s.get("game") or "").lower() for s in structured.get("scan_history", []))
                return has_system and (in_favorites or in_scans)

            # If no explicit game, allow recommendations if system exists
            return has_system

        # Profile insights and compatibility history require profile or scan history
        if category in ("profile_insights", "compatibility_history"):
            return bool(structured.get("scan_history") or structured.get("favorites"))

        return False

    def ask(self, message: str) -> Dict[str, object]:
        if not message or not message.strip():
            raise ValueError("Message must not be empty.")

        self.record_message("user", message)
        # Strict project-data mode: classify question first
        category = self._classify_question(message)

        # Disallowed questions must be refused immediately
        if category == "disallowed":
            answer = "I am GameReady AI and can only answer using information stored in the GameReady platform."
            self.record_message("assistant", answer)
            return {"answer": answer, "conversation": self.get_history()}

        # Check whether question can be answered from GameReady data
        can_answer = self._can_answer_with_project_data(category, message)
        if not can_answer:
            answer = "I cannot answer this because the information is not available in the GameReady database."
            self.record_message("assistant", answer)
            return {"answer": answer, "conversation": self.get_history()}

        # Build context and forward to OpenRouter (strict mode enforced in system prompt)
        context_text = self.context_builder.build_context()
        history_text = self._build_history_section()

        system_prompt = (
            "STRICT PROJECT DATA MODE: Use ONLY the data provided below.\n"
            "You are GameReady AI, an expert gaming compatibility assistant.\n"
            "You must answer only using information available in the provided context. Never invent facts or use outside knowledge.\n"
        )

        prompt = (
            f"{system_prompt}\n"
            f"Context:\n{context_text}\n\n"
            f"{history_text}\n\n"
            f"User question: {message}\n"
            "Assistant:" 
        )

        try:
            response_text = self.gemini.ask(prompt, temperature=settings.ai_temperature_explanation)
            answer = response_text.strip() or "I could not generate a response at this time."
        except RuntimeError as exc:
            # Do NOT fall back to heuristic generation in strict-project-data mode
            answer = "I am GameReady AI and can only answer using information stored in the GameReady platform."

        self.record_message("assistant", answer)

        return {"answer": answer, "conversation": self.get_history()}


__all__ = ["ChatbotService"]
