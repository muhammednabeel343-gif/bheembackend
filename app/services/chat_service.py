"""
chat_service.py
Hybrid AI chat engine:
  1. Classify the question (compatibility / upgrade / recommendation / profile / general)
  2. For project-data questions: generate a local answer from real DB data
  3. If Gemini is available: use it to polish the local answer into natural language
  4. For general gaming knowledge: use Gemini directly; fall back to a quota message
  5. Persist every turn to the database so history survives page reloads
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.config import settings
from app.models.chat import ChatMessage, ChatSession
from app.models.user import User
from app.services.context_builder_service import ContextBuilderService
from app.services.gemini_service import GeminiService
from app.services.local_ai_service import LocalAIService
from app.services.question_classifier import (
    QuestionCategory,
    QuestionType,
    classify,
    classify_category,
)

logger = logging.getLogger(__name__)

MAX_HISTORY_IN_PROMPT = 12

# Shown in the assistant bubble when Gemini is down for GENERAL questions only
_GENERAL_QUOTA_MSG = (
    "AI gaming knowledge features are temporarily unavailable because the AI quota "
    "has been reached. GameReady can still answer **compatibility**, **FPS**, "
    "**upgrade**, and **recommendation** questions using local system data.\n\n"
    "Try asking:\n"
    "- *Can my PC run Elden Ring?*\n"
    "- *What should I upgrade?*\n"
    "- *Recommend games for my system.*\n"
    "- *Analyze my gaming profile.*"
)


class ChatService:
    def __init__(self, db: Session, user: User):
        self.db = db
        self.user = user
        self._gemini = GeminiService()
        self._context = ContextBuilderService(db, user)
        self._local = LocalAIService(db, user)

    # ------------------------------------------------------------------
    # Session management
    # ------------------------------------------------------------------

    def list_sessions(self) -> List[ChatSession]:
        return (
            self.db.query(ChatSession)
            .filter(ChatSession.user_id == self.user.id)
            .order_by(desc(ChatSession.updated_at))
            .all()
        )

    def create_session(self, title: str = "New Chat") -> ChatSession:
        session = ChatSession(user_id=self.user.id, title=title[:200])
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_session(self, session_id: int) -> Optional[ChatSession]:
        return (
            self.db.query(ChatSession)
            .filter(ChatSession.id == session_id, ChatSession.user_id == self.user.id)
            .first()
        )

    def rename_session(self, session_id: int, title: str) -> Optional[ChatSession]:
        session = self.get_session(session_id)
        if not session:
            return None
        session.title = title[:200]
        self.db.commit()
        self.db.refresh(session)
        return session

    def delete_session(self, session_id: int) -> bool:
        session = self.get_session(session_id)
        if not session:
            return False
        self.db.delete(session)
        self.db.commit()
        return True

    # ------------------------------------------------------------------
    # Messages
    # ------------------------------------------------------------------

    def get_messages(self, session_id: int) -> List[ChatMessage]:
        session = self.get_session(session_id)
        return session.messages if session else []

    def _save_message(self, session_id: int, role: str, content: str) -> ChatMessage:
        msg = ChatMessage(session_id=session_id, role=role, content=content)
        self.db.add(msg)
        session = self.get_session(session_id)
        if session:
            session.updated_at = datetime.now(timezone.utc)
            self.db.add(session)
        self.db.commit()
        self.db.refresh(msg)
        return msg

    def _auto_title(self, session: ChatSession, first_message: str) -> None:
        if session.title == "New Chat":
            title = first_message[:60].strip()
            if title:
                session.title = title
                self.db.add(session)
                self.db.commit()

    # ------------------------------------------------------------------
    # Core: send_message
    # ------------------------------------------------------------------

    def send_message(self, session_id: int, user_message: str) -> dict:
        if not user_message or not user_message.strip():
            raise ValueError("Message must not be empty.")

        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found.")

        user_msg = self._save_message(session_id, "user", user_message.strip())
        self._auto_title(session, user_message.strip())

        answer, ai_available = self._generate_answer(session_id, user_message.strip())

        assistant_msg = self._save_message(session_id, "assistant", answer)

        return {
            "user_message": user_msg,
            "assistant_message": assistant_msg,
            "ai_available": ai_available,
        }

    # ------------------------------------------------------------------
    # Hybrid answer generation
    # ------------------------------------------------------------------

    def _generate_answer(self, session_id: int, message: str) -> tuple[str, bool]:
        """
        Returns (answer_text, ai_was_used).

        Pipeline:
          PROJECT → local GameReady data + optional Gemini polish
          GAMING  → OpenRouter knowledge for general gaming questions
          UNRELATED → refusal message, no OpenRouter call
        """
        q_category = classify_category(message)
        q_type = classify(message)
        logger.info(
            "[Chat] Q-category: %s | Q-type: %s | msg: %.80s",
            q_category,
            q_type,
            message,
        )

        if q_category == QuestionCategory.UNRELATED:
            return (
                "I am GameReady AI and specialize in gaming, PC hardware, compatibility analysis, FPS estimates, upgrades, game recommendations, and GameReady platform features.",
                True,
            )

        if q_type == QuestionType.GENERAL:
            return self._handle_general(message, session_id)

        return self._handle_project_data(q_type, message, session_id)

    # ------------------------------------------------------------------
    # GENERAL: pure Gemini, quota-aware
    # ------------------------------------------------------------------

    def _handle_general(self, message: str, session_id: int) -> tuple[str, bool]:
        history_text = self._build_history_text(session_id)
        prompt = self._build_general_prompt(message, history_text)
        try:
            answer = self._gemini.ask(prompt, temperature=0.5).strip()
            if not answer:
                answer = "I couldn't generate a response. Please try again."
            return answer, True
        except Exception as exc:
            logger.warning("[Chat] Gemini unavailable for general Q: %s", exc)
            return _GENERAL_QUOTA_MSG, False

    # ------------------------------------------------------------------
    # PROJECT DATA: local first, Gemini polish if available
    # ------------------------------------------------------------------

    def _handle_project_data(
        self, q_type: QuestionType, message: str, session_id: int
    ) -> tuple[str, bool]:
        # Step 1: generate a complete local answer (never fails)
        local_answer = self._local.answer(q_type, message)

        # Step 2: try Gemini polish
        try:
            polished = self._polish_with_gemini(q_type, message, local_answer, session_id)
            return polished, True
        except Exception as exc:
            logger.info("[Chat] Gemini polish skipped (%s), using local answer.", exc)
            return local_answer, False

    def _polish_with_gemini(
        self, q_type: QuestionType, message: str, local_data: str, session_id: int
    ) -> str:
        """Ask Gemini to turn structured local data into natural prose."""
        history_text = self._build_history_text(session_id)

        type_instructions = {
            QuestionType.COMPATIBILITY: (
                "You are presenting a gaming compatibility report. "
                "Keep all numbers, percentages, and FPS values EXACTLY as shown. "
                "Present the data clearly and encourage the user."
            ),
            QuestionType.UPGRADE: (
                "You are giving hardware upgrade advice. "
                "Keep all component names and scores EXACTLY as shown. "
                "Be concise and practical."
            ),
            QuestionType.RECOMMENDATION: (
                "You are recommending games. "
                "Keep all game names and compatibility scores EXACTLY as shown. "
                "Be enthusiastic and helpful."
            ),
            QuestionType.PROFILE: (
                "You are describing the user's gaming profile. "
                "Keep all stats and hardware details EXACTLY as shown. "
                "Be encouraging and insightful."
            ),
        }

        instruction = type_instructions.get(q_type, "Present the information clearly and naturally.")

        parts = [
            instruction,
            "",
            "The following data was computed from the user's real system specs and game database:",
            "",
            "---",
            local_data,
            "---",
        ]
        if history_text:
            parts += ["", f"Recent conversation:\n{history_text}"]
        parts += [
            "",
            f"User asked: {message}",
            "",
            "Present this data in a friendly, natural response. "
            "Do NOT invent new numbers. Do NOT add specs not in the data. "
            "Keep markdown formatting (bold, tables, lists) intact.",
        ]

        result = self._gemini.ask("\n".join(parts), temperature=0.3).strip()
        return result or local_data

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_history_text(self, session_id: int) -> str:
        messages = self.get_messages(session_id)
        # Exclude the message we just saved (last one is the user's current message)
        recent = messages[-MAX_HISTORY_IN_PROMPT:-1] if len(messages) > 1 else []
        if not recent:
            return ""
        lines = []
        for m in recent:
            role = "User" if m.role == "user" else "Assistant"
            lines.append(f"{role}: {m.content[:400]}")
        return "\n".join(lines)

    def _build_general_prompt(self, message: str, history_text: str) -> str:
        """
        For general gaming knowledge questions.
        The master system prompt is already injected by GeminiService._call().
        We only need to provide user context + conversation history + the question.
        """
        context_text = self._context.build_context()
        parts = []

        if context_text:
            parts.append(f"User Context:\n{context_text}")

        if history_text:
            parts.append(f"Conversation so far:\n{history_text}")

        parts.append(f"User: {message}")

        return "\n\n".join(parts)
