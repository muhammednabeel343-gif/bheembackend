from typing import List, Optional
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
    # Optional: API_BASE_URL can be set in environment, or derived from request at runtime
    api_base_url: Optional[str] = Field(None, env="API_BASE_URL")
    # Optional: CORS origins, will use api_base_url as fallback if not set
    cors_origins: Optional[str] = Field(None, env="CORS_ORIGINS")
    
    # Cloudinary configuration for image storage
    cloudinary_cloud_name: Optional[str] = Field(None, env="CLOUDINARY_CLOUD_NAME")
    cloudinary_api_key: Optional[str] = Field(None, env="CLOUDINARY_API_KEY")
    cloudinary_api_secret: Optional[str] = Field(None, env="CLOUDINARY_API_SECRET")

    @property
    def cors_origins_list(self) -> List[str]:
        # Use CORS_ORIGINS if set, otherwise use API_BASE_URL, or default to localhost
        if self.cors_origins:
            value = self.cors_origins.strip()
        elif self.api_base_url:
            value = self.api_base_url.strip()
        else:
            # Default for local development
            value = "http://localhost:5173"
        
        if value.startswith("[") and value.endswith("]"):
            import json
            return json.loads(value)
        return [item.strip() for item in value.split(",") if item.strip()]


settings = Settings()
