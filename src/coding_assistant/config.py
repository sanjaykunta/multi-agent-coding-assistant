from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables and .env."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "local"
    log_level: str = "INFO"
    llm_provider: Literal["local", "fake", "vertex"] = "local"
    google_cloud_project: str | None = None
    google_cloud_location: str = "global"
    gemini_model: str = "gemini-2.5-flash"
    llm_timeout_seconds: int = Field(default=90, ge=5, le=300)
    max_agent_iterations: int = Field(default=2, ge=1, le=5)
    workspace_root: Path = Path("./sample_workspace")


@lru_cache
def get_settings() -> Settings:
    return Settings()
