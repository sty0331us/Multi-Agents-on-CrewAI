"""Search tool helpers."""

from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


def build_search_tools(serper_api_key: str | None = None) -> list[Any]:
    """
    Return SerperDev search tools when an API key is available.

    Falls back to an empty tool list (agents still reason from LLM knowledge)
    so local/CI environments without Serper can still construct the crew.
    """
    api_key = serper_api_key or os.getenv("SERPER_API_KEY")
    if not api_key:
        logger.warning(
            "SERPER_API_KEY is not set — research agent will run without live web search."
        )
        return []

    # Ensure the tool's expected env var is present for crewai-tools
    os.environ.setdefault("SERPER_API_KEY", api_key)

    try:
        from crewai_tools import SerperDevTool

        tool = SerperDevTool()
        logger.info("SerperDevTool enabled for research agent")
        return [tool]
    except Exception as exc:  # noqa: BLE001 — soft-fail tool wiring
        logger.warning("Failed to initialize SerperDevTool: %s", exc)
        return []
