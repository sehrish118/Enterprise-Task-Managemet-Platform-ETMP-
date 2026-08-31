from functools import lru_cache

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_INSECURE_DEFAULTS = {"change-me-in-production", "secret", "changeme", ""}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ── App ──────────────────────────────────────────
    APP_NAME: str = "ETMP"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    UPLOAD_DIR: str = "uploads"

    # ── Database ─────────────────────────────────────
    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── Auth / JWT ───────────────────────────────────
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1400
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── SMTP / Email Settings ────────────────────────
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAILS_FROM_EMAIL: str | None = None
    FRONTEND_URL: str = "http://localhost:5173"
    GROQ_API_KEY: str = ""

    # ── CORS ─────────────────────────────────────────

    CORS_ORIGINS_RAW: str = Field(default="http://localhost:3000", alias="CORS_ORIGINS")

    @property
    def CORS_ORIGINS(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.CORS_ORIGINS_RAW.split(",")
            if origin.strip()
        ]

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @field_validator("DATABASE_URL")
    @classmethod
    def _validate_database_url(cls, v: str) -> str:
        if not v.startswith("postgresql+asyncpg://"):
            raise ValueError(
                "DATABASE_URL must use the 'postgresql+asyncpg://' scheme "
                "(asyncpg driver) — got a different scheme/driver."
            )
        return v

    @model_validator(mode="after")
    def _validate_production_secrets(self) -> "Settings":
        if self.is_production and self.JWT_SECRET_KEY in _INSECURE_DEFAULTS:
            raise ValueError(
                "JWT_SECRET_KEY is set to an insecure default value while "
                "APP_ENV=production. Refusing to start. Set a strong, "
                "randomly generated secret (e.g. `openssl rand -hex 32`)."
            )
        if self.is_production and self.DEBUG:
            raise ValueError("DEBUG must be false when APP_ENV=production.")
        return self


@lru_cache
# This caches settings object in memory. So, in entire project,
# when ever get_settings() will
# be called, we can fastly access the settings. No need to go into .env again and again.
def get_settings() -> Settings:

    return Settings()  # type: ignore[call-arg]


settings = get_settings()
