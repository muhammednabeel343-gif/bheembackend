"""
gemini_service.py  (powered by OpenRouter)

Uses the OpenAI-compatible /chat/completions endpoint.
System prompt is injected as a proper `system` role message so every
model respects it, regardless of which fallback is used.
"""
from __future__ import annotations

import logging
from typing import Optional

from app.config import settings

logger = logging.getLogger(__name__)

OPENROUTER_BASE = "https://openrouter.ai/api/v1"

# -----------------------------------------------------------------------
# MASTER SYSTEM PROMPT
# Injected as `{"role": "system", ...}` on every single request.
# -----------------------------------------------------------------------
SYSTEM_PROMPT = """You are GameReady AI — an expert gaming compatibility assistant built into the GameReady platform.

YOUR IDENTITY:
- You are part of GameReady, a platform that helps gamers check PC compatibility, get FPS estimates, find upgrade paths, and discover games their system can run.
- You are knowledgeable, friendly, and always helpful.
- You speak directly to the user by name when their profile is available.

YOUR CAPABILITIES:
1. Game Compatibility — Check if a user's PC can run specific games, show FPS estimates at different settings.
2. Upgrade Advice — Identify hardware bottlenecks and suggest the best upgrades for the user's budget/goals.
3. Game Recommendations — Suggest games the user's system can run, filtered by genre or preference.
4. Gaming Profile Analysis — Summarize the user's system tier, favourite genres, and scan history.
5. General Gaming Knowledge — Explain PC gaming concepts (DLSS, ray tracing, VRAM, etc.), compare games, discuss hardware.

STRICT RULES — NEVER BREAK THESE:
- NEVER invent hardware specs, FPS numbers, or compatibility scores. Only use data explicitly provided in the context.
- If the user has no saved system scan, tell them to go to "My System" to save their specs first.
- If data is provided in structured form (tables, scores, FPS values), preserve those exact numbers in your reply.
- Do NOT pretend to be any other AI (GPT, Gemini, Claude, etc.). You are GameReady AI.
- Keep responses focused only on gaming, PC hardware, compatibility analysis, upgrades, game recommendations, and GameReady platform features.
- If a user asks anything outside those topics, respond with a brief, polite refusal.
- You are NOT a general-purpose AI assistant.
- Format responses with markdown: use **bold**, headers (##, ###), bullet lists, and tables where appropriate.
- Be concise but thorough. Avoid filler phrases like "Great question!" or "Certainly!".

TONE:
- Enthusiastic about gaming but professional.
- Encouraging — help users understand their system's strengths.
- Practical — give actionable advice, not vague generalities.
"""

# Free models in priority order (verified on OpenRouter)
_FALLBACK_MODELS = [
    "meta-llama/llama-3.3-70b-instruct:free",
    "qwen/qwen3-coder:free",
    "openai/gpt-oss-120b:free",
    "nousresearch/hermes-3-llama-3.1-405b:free",
    "meta-llama/llama-3.2-3b-instruct:free",
]


class GeminiService:
    """Name kept for backward compatibility. Now powered by OpenRouter."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        **_kwargs,
    ):
        self.api_key = api_key or settings.openrouter_api_key or settings.ai_api_key
        self.model = model or settings.openrouter_model

    def ask(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Send prompt with system context. Auto-falls back through free models on quota errors."""
        if not prompt or not prompt.strip():
            return ""
        if not self.api_key:
            raise RuntimeError("No OpenRouter API key configured (OPENROUTER_API_KEY).")

        models = [self.model] + [m for m in _FALLBACK_MODELS if m != self.model]
        last_exc: Exception = RuntimeError("No models tried.")

        for model in models:
            try:
                text = self._call(prompt, model, temperature, max_tokens)
                if model != self.model:
                    logger.info("[OpenRouter] Fallback model used: %s", model)
                return text
            except RuntimeError as exc:
                last_exc = exc
                if any(kw in str(exc).lower() for kw in ("quota", "429", "rate", "limit", "overloaded", "unavailable")):
                    logger.warning("[OpenRouter] %s rate-limited, trying next...", model)
                    continue
                raise

        raise RuntimeError(f"All AI models exhausted. Last error: {last_exc}") from last_exc

    def _call(
        self,
        prompt: str,
        model: str,
        temperature: Optional[float],
        max_tokens: Optional[int],
    ) -> str:
        try:
            import httpx
        except ImportError as exc:
            raise RuntimeError("httpx required: pip install httpx") from exc

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://gameready.app",
            "X-Title": "GameReady AI",
        }

        # Proper system + user message split
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt},
            ],
            "temperature": temperature if temperature is not None else settings.ai_temperature_explanation,
            "max_tokens": max_tokens or settings.ai_max_tokens,
        }

        try:
            resp = httpx.post(
                f"{OPENROUTER_BASE}/chat/completions",
                json=payload,
                headers=headers,
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json()
            choices = data.get("choices", [])
            if choices:
                return str(choices[0].get("message", {}).get("content", "")).strip()
            raise RuntimeError(f"Unexpected OpenRouter response: {data}")

        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            try:
                err_msg = exc.response.json().get("error", {}).get("message", str(exc))
            except Exception:
                err_msg = str(exc)
            if status in (429, 503, 529):
                raise RuntimeError(f"quota/rate on {model}: {err_msg}") from exc
            raise RuntimeError(f"OpenRouter HTTP {status} on {model}: {err_msg}") from exc

        except httpx.TimeoutException as exc:
            raise RuntimeError(f"OpenRouter timed out on {model}") from exc

        except Exception as exc:
            raise RuntimeError(f"OpenRouter call failed on {model}: {exc}") from exc
