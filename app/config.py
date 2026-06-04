from typing import List
from pathlib import Path
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings


# Safe .env path calculation: config.py is at backend/app/config.py
# parent = backend/app, parent.parent = backend/
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=_env_path, override=True)


class Settings(BaseSettings):
    app_name: str = "Project Bheem API"
    database_url: str = Field(..., env="DATABASE_URL")
    secret_key: str = Field("your-secret-key-change-this-in-production", env="SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    api_base_url: str = Field(..., env="API_BASE_URL")
    cors_origins: str = Field(None, env="CORS_ORIGINS")

    @property
    def cors_origins_list(self) -> List[str]:
        # Use API_BASE_URL as fallback if CORS_ORIGINS not set
        value = (self.cors_origins or self.api_base_url).strip()
        if value.startswith("[") and value.endswith("]"):
            import json
            return json.loads(value)
        return [item.strip() for item in value.split(",") if item.strip()]


settings = Settings()
