"""Shared pytest fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

from content_crew.config import Settings


@pytest.fixture
def tmp_output_dir(tmp_path: Path) -> Path:
    out = tmp_path / "outputs"
    out.mkdir()
    return out


@pytest.fixture
def dry_settings(tmp_output_dir: Path) -> Settings:
    return Settings(
        CONTENT_CREW_DRY_RUN=True,
        CONTENT_CREW_OUTPUT_DIR=str(tmp_output_dir),
        CONTENT_CREW_VERBOSE=False,
        CONTENT_CREW_LOG_LEVEL="WARNING",
        OPENAI_API_KEY=None,
        SERPER_API_KEY=None,
    )
