from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Project Bheem API"
    database_url: str = Field(..., env="DATABASE_URL")
    secret_key: str = Field("your-secret-key-change-this-in-production", env="SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    cors_origins: List[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:5174",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:5174",
        ],
        env="CORS_ORIGINS",
    )

    class Config:
        env_file = ".env"


settings = Settings()
