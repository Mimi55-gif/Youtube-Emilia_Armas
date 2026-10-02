from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./frame.db"
    secret_key: str = "local-development-key-change-before-deploy"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    upload_dir: str = "backend/uploads"
    max_video_mb: int = 100
    max_image_mb: int = 10
    aws_region: str = "us-east-1"
    s3_video_bucket: str = ""
    s3_thumbnail_bucket: str = ""
    s3_public_base_url: str = ""

    model_config = SettingsConfigDict(env_file=Path(__file__).resolve().parents[1] / ".env", extra="ignore")

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
