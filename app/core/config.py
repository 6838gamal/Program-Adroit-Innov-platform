from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    APP_NAME: str = "AI Learning Platform"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    APP_URL: str = "http://localhost:8000"
    SECRET_KEY: str = "change-me-in-production"
    SESSION_COOKIE_NAME: str = "session"
    SESSION_MAX_AGE: int = 86400

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ai_learning"
    PGVECTOR_ENABLED: bool = True

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/auth/callback"
    GOOGLE_SCOPE: str = "openid email profile"

    # AI Provider
    AI_PROVIDER: str = "openai"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    AI_TUTOR_MAX_TOKENS: int = 1024
    AI_CODE_REVIEW_MAX_TOKENS: int = 2048
    AI_DEBUG_MAX_TOKENS: int = 1024

    # Code Runner
    RUNNER_URL: str = "http://runner:8001/run"
    RUNNER_TIMEOUT: int = 15
    RUNNER_MEMORY_LIMIT: str = "256m"
    RUNNER_CPU_LIMIT: str = "1.0"

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000"

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT: str = "60/minute"
    RATE_LIMIT_AI: str = "20/minute"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @field_validator("APP_DEBUG", mode="before")
    @classmethod
    def parse_bool(cls, v):
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes")
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
