"""
Application configuration using Pydantic Settings.
Loads environment variables with validation.
"""
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "SabiTax"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    # Database (NeonDB PostgreSQL)
    database_url: str

    # JWT Authentication
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # AI Assistant (NexusBert)
    nexusbert_api_url: str = "https://nexusbert-sabitax.hf.space"
    nexusbert_api_key: str = ""

    # Bank Integration (Optional)
    mono_secret_key: str = ""
    okra_secret_key: str = ""

    # CORS Origins
    cors_origins: str = "*"

    @property
    def async_database_url(self) -> str:
        """Convert standard PostgreSQL URL to async version."""
        url = self.database_url
        
        # asyncpg does not support sslmode or channel_binding query parameters
        if "?" in url:
            url = url.split("?")[0]
            
        # Handle NeonDB/Postgres protocols
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("neondb://"):
             # SQLAlchemy doesn't natively support neondb:// scheme, but it's usually just an alias for postgres
            return url.replace("neondb://", "postgresql+asyncpg://", 1)
            
        return url

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins into list."""
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()  # type: ignore[call-arg]
