"""Task factory — builds CrewAI Task instances from YAML config."""

from __future__ import annotations

import logging
from typing import Any

from crewai import Agent, Task

from content_crew.config import load_tasks_config

logger = logging.getLogger(__name__)


def _build_task(
    name: str,
    spec: dict[str, Any],
    agent: Agent,
    context: list[Task] | None = None,
) -> Task:
    kwargs: dict[str, Any] = {
        "description": spec["description"].strip(),
        "expected_output": spec["expected_output"].strip(),
        "agent": agent,
    }
    if context:
        kwargs["context"] = context
    logger.debug("Creating task '%s' for agent '%s'", name, agent.role)
    return Task(**kwargs)


def create_tasks(
    agents: dict[str, Agent],
    *,
    config: dict[str, Any] | None = None,
) -> list[Task]:
    """
    Create the sequential task chain: research → writer → social.

    Context wiring ensures each downstream task receives prior outputs.
    """
    tasks_cfg = config or load_tasks_config()

    research = _build_task(
        "research_task",
        tasks_cfg["research_task"],
        agents["research_agent"],
    )
    writer = _build_task(
        "writer_task",
        tasks_cfg["writer_task"],
        agents["writer_agent"],
        context=[research],
    )
    social = _build_task(
        "social_task",
        tasks_cfg["social_task"],
        agents["social_agent"],
        context=[writer],
    )
    return [research, writer, social]
