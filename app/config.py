from typing import List, Optional
from pathlib import Path
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=_env_path, override=False)


class Settings(BaseSettings):
    app_name: str = "Project Bheem API"
    database_url: str = Field(..., json_schema_extra={"env": "DATABASE_URL"})
    secret_key: str = Field("your-secret-key-change-this-in-production", json_schema_extra={"env": "SECRET_KEY"})
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    api_base_url: Optional[str] = Field(None, json_schema_extra={"env": "API_BASE_URL"})
    cors_origins: Optional[str] = Field(None, json_schema_extra={"env": "CORS_ORIGINS"})

    # Cloudinary
    cloudinary_cloud_name: Optional[str] = Field(None, json_schema_extra={"env": "CLOUDINARY_CLOUD_NAME"})
    cloudinary_api_key: Optional[str] = Field(None, json_schema_extra={"env": "CLOUDINARY_API_KEY"})
    cloudinary_api_secret: Optional[str] = Field(None, json_schema_extra={"env": "CLOUDINARY_API_SECRET"})

    # OpenRouter (primary AI provider)
    openrouter_api_key: Optional[str] = Field(None, json_schema_extra={"env": "OPENROUTER_API_KEY"})
    openrouter_model: str = Field("meta-llama/llama-3.3-70b-instruct:free", json_schema_extra={"env": "OPENROUTER_MODEL"})

    # Legacy Gemini keys (kept for backward compat, not actively used)
    google_api_key: Optional[str] = Field(None, json_schema_extra={"env": "GOOGLE_API_KEY"})
    gemini_api_key: Optional[str] = Field(None, json_schema_extra={"env": "GEMINI_API_KEY"})
    google_project_id: Optional[str] = Field(None, json_schema_extra={"env": "GOOGLE_PROJECT_ID"})
    gemini_model: str = Field("meta-llama/llama-3.3-70b-instruct:free", json_schema_extra={"env": "GEMINI_MODEL"})

    enable_ai_features: bool = Field(False, json_schema_extra={"env": "ENABLE_AI_FEATURES"})
    ai_temperature_explanation: float = Field(0.3, json_schema_extra={"env": "AI_TEMPERATURE_EXPLANATION"})
    ai_max_tokens: int = Field(2048, json_schema_extra={"env": "AI_MAX_TOKENS"})
    ai_request_sample_rate: float = Field(1.0, json_schema_extra={"env": "AI_REQUEST_SAMPLE_RATE"})
    ai_max_calls_per_minute: int = Field(0, json_schema_extra={"env": "AI_MAX_CALLS_PER_MINUTE"})
    ai_fail_fast: bool = Field(False, json_schema_extra={"env": "AI_FAIL_FAST_ON_INVALID"})

    @property
    def cors_origins_list(self) -> List[str]:
        if self.cors_origins:
            value = self.cors_origins.strip()
        elif self.api_base_url:
            value = self.api_base_url.strip()
        else:
            # Include common dev ports (5173 and 5174) for Vite and React dev servers
            value = "http://localhost:5173,http://localhost:5174,http://localhost:3000,http://localhost,http://localhost:80,http://127.0.0.1:5173,http://127.0.0.1:5174"

        if value.startswith("[") and value.endswith("]"):
            import json
            return json.loads(value)
        return [item.strip() for item in value.split(",") if item.strip()]

    @property
    def ai_api_key(self) -> Optional[str]:
        """Return the active AI API key — OpenRouter preferred."""
        return self.openrouter_api_key or self.gemini_api_key or self.google_api_key

    @property
    def ai_enabled(self) -> bool:
        return bool(self.ai_api_key) or self.enable_ai_features


settings = Settings()
