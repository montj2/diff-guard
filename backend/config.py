"""Configuration management for DiffGuard.

Uses Pydantic BaseSettings so environment variables can configure runtime behavior.
Future: load policy file path, DB URL, provider-specific tuning, etc.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, HttpUrl

try:  # pragma: no cover - import guard
    from pydantic_settings import BaseSettings
except Exception:  # pragma: no cover - fallback
    from pydantic import BaseModel as BaseSettings  # type: ignore[assignment]


class Settings(BaseSettings):
    artifactory_url: HttpUrl | None = Field(default=None, validation_alias="ARTIFACTORY_URL")
    artifactory_token: str | None = Field(default=None, validation_alias="ARTIFACTORY_TOKEN")
    staging_repo: str = Field(default="npm-staging", validation_alias="STAGING_REPO")
    prod_repo: str = Field(default="npm-prod", validation_alias="PROD_REPO")
    quarantine_repo: str = Field(default="npm-quarantine", validation_alias="QUARANTINE_REPO")

    llm_provider: str = Field(default="openai", validation_alias="LLM_PROVIDER")
    llm_api_key: str | None = Field(default=None, validation_alias="LLM_API_KEY")

    policy_file: str = Field(default="policy.yaml", validation_alias="POLICY_FILE")

    log_level: Literal["debug", "info", "warning", "error"] = Field(default="info", validation_alias="LOG_LEVEL")
    request_timeout_seconds: int = Field(default=10, validation_alias="REQUEST_TIMEOUT_SECONDS")
    retry_attempts: int = Field(default=3, validation_alias="RETRY_ATTEMPTS")

    class Config:
        extra = "ignore"
        case_sensitive = False


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings instance.

    Returns:
        Settings: Application settings loaded from environment.
    """
    return Settings()
