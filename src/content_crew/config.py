"""Configuration loading and runtime settings."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def project_root() -> Path:
    """Return the repository root (two levels above this package)."""
    # src/content_crew/config.py → parents: content_crew, src, repo
    return Path(__file__).resolve().parents[2]


def config_dir() -> Path:
    return project_root() / "config"


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in {path}, got {type(data).__name__}")
    return data


class Settings(BaseSettings):
    """Environment-backed application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    log_level: str = Field(default="INFO", alias="CONTENT_CREW_LOG_LEVEL")
    output_dir: str = Field(default="outputs", alias="CONTENT_CREW_OUTPUT_DIR")
    verbose: bool = Field(default=True, alias="CONTENT_CREW_VERBOSE")
    dry_run: bool = Field(default=False, alias="CONTENT_CREW_DRY_RUN")

    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_model_name: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL_NAME")
    serper_api_key: str | None = Field(default=None, alias="SERPER_API_KEY")

    def resolve_output_dir(self) -> Path:
        path = Path(self.output_dir)
        if not path.is_absolute():
            path = project_root() / path
        path.mkdir(parents=True, exist_ok=True)
        return path


@lru_cache
def get_settings() -> Settings:
    return Settings()


def load_agents_config() -> dict[str, Any]:
    return load_yaml(config_dir() / "agents.yaml")


def load_tasks_config() -> dict[str, Any]:
    return load_yaml(config_dir() / "tasks.yaml")


def load_app_settings() -> dict[str, Any]:
    return load_yaml(config_dir() / "settings.yaml")
