from typing import List
from pathlib import Path
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings


_env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=_env_path, override=True)


class Settings(BaseSettings):
    app_name: str = "Project Bheem API"
    database_url: str = Field(..., env="DATABASE_URL")
    secret_key: str = Field("your-secret-key-change-this-in-production", env="SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    cors_origins: str = Field("http://localhost:5173,http://localhost:8000", env="CORS_ORIGINS")
    api_base_url: str = Field("http://127.0.0.1:8000", env="API_BASE_URL")

    @property
    def cors_origins_list(self) -> List[str]:
        value = (self.cors_origins or "http://localhost:5173").strip()
        if value.startswith("[") and value.endswith("]"):
            import json
            return json.loads(value)
        return [item.strip() for item in value.split(",") if item.strip()]


settings = Settings()
