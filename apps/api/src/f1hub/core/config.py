"""
F1 Intelligence Hub - Configuration Management

This module handles all application configuration using Pydantic Settings.
Environment variables are loaded from .env file and validated at startup.
"""

from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ========================================================================
    # Application
    # ========================================================================
    APP_NAME: str = "F1 Intelligence Hub"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = Field(default="development", pattern="^(development|staging|production)$")
    DEBUG: bool = Field(default=True)
    LOG_LEVEL: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")

    # ========================================================================
    # API
    # ========================================================================
    API_HOST: str = Field(default="0.0.0.0")
    API_PORT: int = Field(default=8000, ge=1024, le=65535)
    API_RELOAD: bool = Field(default=True)
    API_PREFIX: str = "/api/v1"

    # Security
    SECRET_KEY: str = Field(
        default="dev-secret-key-change-in-production",
        min_length=32,
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, ge=1)

    # CORS
    CORS_ORIGINS: str = Field(default="http://localhost:3000")

    @field_validator("CORS_ORIGINS")
    @classmethod
    def parse_cors_origins(cls, v: str) -> List[str]:
        """Parse comma-separated CORS origins into a list."""
        if v == "*":
            return ["*"]
        return [origin.strip() for origin in v.split(",") if origin.strip()]

    # ========================================================================
    # Database
    # ========================================================================
    DATABASE_URL: str = Field(
        default="postgresql://f1hub:f1hub_dev_password@localhost:5432/f1hub"
    )

    # Connection pool settings
    DB_POOL_SIZE: int = Field(default=5, ge=1)
    DB_MAX_OVERFLOW: int = Field(default=10, ge=0)
    DB_POOL_RECYCLE: int = Field(default=3600, ge=300)  # 1 hour
    DB_ECHO: bool = Field(default=False)

    # ========================================================================
    # Redis & Celery
    # ========================================================================
    REDIS_URL: str = Field(default="redis://localhost:6379/0")

    CELERY_BROKER_URL: str | None = None
    CELERY_RESULT_BACKEND: str | None = None

    @field_validator("CELERY_BROKER_URL", mode="before")
    @classmethod
    def set_celery_broker(cls, v: str | None, info) -> str:
        """Default Celery broker to REDIS_URL if not set."""
        return v or info.data.get("REDIS_URL", "redis://localhost:6379/0")

    @field_validator("CELERY_RESULT_BACKEND", mode="before")
    @classmethod
    def set_celery_backend(cls, v: str | None, info) -> str:
        """Default Celery result backend to REDIS_URL if not set."""
        return v or info.data.get("REDIS_URL", "redis://localhost:6379/0")

    CELERY_TASK_TRACK_STARTED: bool = Field(default=True)
    CELERY_TASK_TIME_LIMIT: int = Field(default=1800, ge=60)  # 30 minutes
    CELERY_TASK_SOFT_TIME_LIMIT: int = Field(default=1500, ge=60)  # 25 minutes

    # ========================================================================
    # MinIO / S3
    # ========================================================================
    MINIO_ENDPOINT: str = Field(default="localhost:9000")
    MINIO_ROOT_USER: str = Field(default="minioadmin")
    MINIO_ROOT_PASSWORD: str = Field(default="minioadmin")
    MINIO_BUCKET: str = Field(default="f1hub")
    MINIO_USE_SSL: bool = Field(default=False)

    # ========================================================================
    # FastF1
    # ========================================================================
    FASTF1_CACHE_DIR: str = Field(default="./data/fastf1_cache")

    # ========================================================================
    # OpenAI (for Phase 3 LLM features)
    # ========================================================================
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = Field(default="gpt-4o-mini")
    OPENAI_EMBEDDING_MODEL: str = Field(default="text-embedding-3-small")
    OPENAI_MAX_TOKENS: int = Field(default=2000)
    OPENAI_TEMPERATURE: float = Field(default=0.7)

    # ========================================================================
    # Feature Flags
    # ========================================================================
    ENABLE_SWAGGER_UI: bool = Field(default=True)
    ENABLE_REDOC: bool = Field(default=True)

    # ========================================================================
    # Computed Properties
    # ========================================================================
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == "production"

    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list."""
        return self.CORS_ORIGINS if isinstance(self.CORS_ORIGINS, list) else [self.CORS_ORIGINS]


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Uses lru_cache to ensure Settings is only instantiated once.
    This is important for performance and to avoid re-reading .env files.

    Returns:
        Settings: Cached settings instance
    """
    return Settings()


# Convenience export
settings = get_settings()
