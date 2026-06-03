from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Project Bheem API"
    database_url: str = Field(..., env="DATABASE_URL")
    secret_key: str = Field("your-secret-key-change-this-in-production", env="SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    cors_origins: str = Field("", env="CORS_ORIGINS")

    class Config:
        env_file = ".env"

    @property
    def cors_origins_list(self) -> List[str]:
        value = (self.cors_origins or "").strip()
        if not value:
            return []
        if value.startswith("[") and value.endswith("]"):
            import json
            return json.loads(value)
        return [item.strip() for item in value.split(",") if item.strip()]


settings = Settings()
