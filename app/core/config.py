from __future__ import annotations

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "openclaw-control-api"
    app_env: str = "development"
    app_port: int = 8088
    log_level: str = "INFO"
    allowed_origins: str = "http://localhost:3000"

    database_url: str = "postgresql+psycopg2://openclaw:openclaw@postgres:5432/openclaw_control"
    redis_url: str = "redis://redis:6379/0"
    use_redis: bool = False

    ingest_api_token: str = ""

    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24

    admin_default_username: str = "admin"
    admin_default_password: str = "change-me-now"

    @field_validator("allowed_origins")
    @classmethod
    def _normalize_origins(cls, value: str) -> str:
        return ",".join([item.strip() for item in value.split(",") if item.strip()])

    def allowed_origins_list(self) -> list[str]:
        return [item.strip() for item in self.allowed_origins.split(",") if item.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
