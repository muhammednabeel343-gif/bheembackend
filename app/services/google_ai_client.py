import time
import threading
import random
from typing import Optional, Any, Dict
from app.services.ai_metrics import metrics


class GoogleAIClient:
    """Lightweight wrapper for Google Generative AI calls.

    - Uses the real `google.generativeai` library when available and enabled.
    - Falls back to a safe mock response when the library or API key is not present.
    - Provides simple retry and minimum-interval rate limiting to protect downstream systems.
    """

    def __init__(self, api_key: Optional[str] = None, project_id: Optional[str] = None, *,
                 enable: bool = False, mock: bool = False, model: Optional[str] = None,
                 min_interval_seconds: float = 0.1, max_retries: int = 3):
        self.api_key = api_key
        self.project_id = project_id
        self.model = model
        self.enable = bool(enable)
        self.mock = bool(mock) or (not self.enable)
        self.min_interval_seconds = float(min_interval_seconds)
        self.max_retries = int(max_retries)

        self._lock = threading.Lock()
        self._last_call_ts = 0.0
        # Simple rate limiting / cost-control
        self.sample_rate = 1.0
        self.max_calls_per_minute = 0
        self._calls_lock = threading.Lock()
        self._window_start = time.time()
        self._calls_in_window = 0

        try:
            import google.generativeai as ggen  # type: ignore
            self._ggen = ggen
            # If API key provided, attempt to configure the library
            try:
                if self.api_key and hasattr(self._ggen, "configure"):
                    # Typical usage: google.generativeai.configure(api_key=...)
                    try:
                        self._ggen.configure(api_key=self.api_key)
                    except Exception:
                        # some versions expect different configuration call
                        try:
                            self._ggen.configure(api_key=self.api_key, project_id=self.project_id)
                        except Exception:
                            pass
            except Exception:
                pass
        except Exception:
            self._ggen = None
            # keep mock mode if library not present
            self.mock = True

        # Try to pick up cost-control from environment if available (best-effort)
        try:
            from app.config import settings
            self.sample_rate = float(getattr(settings, 'ai_request_sample_rate', 1.0) or 1.0)
            self.max_calls_per_minute = int(getattr(settings, 'ai_max_calls_per_minute', 0) or 0)
        except Exception:
            pass

    def _throttle(self):
        with self._lock:
            now = time.time()
            elapsed = now - self._last_call_ts
            if elapsed < self.min_interval_seconds:
                time.sleep(self.min_interval_seconds - elapsed)
            self._last_call_ts = time.time()

    def generate_text(self, prompt: str, temperature: Optional[float] = None,
                      max_tokens: Optional[int] = None, model: Optional[str] = None) -> Dict[str, Any]:
        """Generate text from prompt. Returns a dict with `text` key on success.

        This method is deterministic when `mock=True` and safe to call in tests.
        """
        if self.mock:
            return {"text": f"[MOCK] Response for prompt: {prompt[:120]}"}

        # Note: Sampling removed. Heuristic fallback in ChatbotService handles quota exhaustion gracefully.
        # All requests attempt real API call; quota is the natural limiting factor.

        # Simple per-minute rate limit: raise to allow caller retry/handle
        if self.max_calls_per_minute and self.max_calls_per_minute > 0:
            now = time.time()
            with self._calls_lock:
                # reset window if needed
                if now - self._window_start >= 60.0:
                    self._window_start = now
                    self._calls_in_window = 0

                if self._calls_in_window >= self.max_calls_per_minute:
                    metrics.incr_failed()
                    raise RuntimeError("GoogleAIClient rate limit exceeded")
                self._calls_in_window += 1
        metrics.incr_attempt()

        # Best-effort real call with retries and throttling
        attempt = 0
        last_exc = None
        while attempt < self.max_retries:
            attempt += 1
            try:
                self._throttle()
                if not self._ggen:
                    raise RuntimeError("google.generativeai not available")

                # Attempt to call a generative method if available; keep call generic
                # Use attribute checks to avoid hard dependency on library API shape
                # Preferred modern surface: google.generativeai.generate
                if hasattr(self._ggen, "generate"):
                    # Some versions use generate(input=...), others use different names
                    try:
                        kwargs = {
                            "input": prompt,
                            "temperature": temperature or 0.3,
                            "max_output_tokens": max_tokens or 512,
                        }
                        if model:
                            kwargs["model"] = model
                        resp = self._ggen.generate(**kwargs)
                        text = getattr(resp, "output_text", None) or getattr(resp, "text", None) or str(resp)
                    except TypeError:
                        # fallback to simpler call signature
                        resp = self._ggen.generate(prompt)
                        text = getattr(resp, "output_text", None) or getattr(resp, "text", None) or str(resp)
                elif hasattr(self._ggen, "responses") and hasattr(self._ggen.responses, "generate"):
                    kwargs = {"text": prompt}
                    if model:
                        kwargs["model"] = model
                    resp = self._ggen.responses.generate(**kwargs)
                    text = getattr(resp, "output_text", None) or getattr(resp, "text", None) or str(resp)
                elif hasattr(self._ggen, "GenerativeModel"):
                    gen_model = self._ggen.GenerativeModel(model or self.model)
                    chat = gen_model.start_chat()
                    resp = chat.send_message(prompt)
                    text = getattr(resp, "text", None) or getattr(resp, "output_text", None) or str(resp)
                else:
                    raise RuntimeError("Unsupported google.generativeai API surface")

                metrics.incr_success()
                return {"text": text}
            except Exception as exc:  # broad catch to allow retries
                last_exc = exc
                error_name = type(exc).__name__
                message = str(exc) or ""
                if error_name == "ResourceExhausted" or "quota" in message.lower():
                    raise RuntimeError(
                        "AI request failed due to API quota exhaustion. Please try again later."
                    ) from exc
                backoff = 0.5 * (2 ** (attempt - 1))
                time.sleep(backoff)
                continue

        metrics.incr_failed()
        raise RuntimeError("GoogleAIClient failed after retries") from last_exc

    def generate_structured_response(self, prompt: str, schema: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Generate a structured response following a simple schema.

        In mock mode this returns a placeholder structure with the schema keys present.
        """
        if self.mock:
            # Create placeholders for each key
            return {k: f"[MOCK:{k}]" for k in schema.keys()}

        # For real mode, call generate_text and attempt to parse JSON-like output
        text_resp = self.generate_text(prompt, temperature=kwargs.get("temperature"),
                                       max_tokens=kwargs.get("max_tokens"))
        text = text_resp.get("text", "")
        # Best-effort: attempt to parse JSON from the response
        try:
            import json
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            pass

        # Fallback: return raw text under a single key
        return {"raw": text}

    def validate(self, timeout: int = 5) -> Dict[str, Any]:
        """Validate that the client is able to contact the backend/service.

        Returns a dictionary with `ok` boolean and optional `detail`.
        In mock mode this returns ok=True and mode=mock.
        """
        if self.mock:
            return {"ok": True, "mode": "mock"}

        # Perform a lightweight generate_text call and treat success as validation
        try:
            resp = self.generate_text("healthcheck", max_tokens=16)
            text = resp.get("text") if isinstance(resp, dict) else None
            if not text:
                return {"ok": False, "detail": "empty response"}
            return {"ok": True, "mode": "real", "sample": text[:200]}
        except Exception as e:
            return {"ok": False, "detail": str(e)}


__all__ = ["GoogleAIClient"]
