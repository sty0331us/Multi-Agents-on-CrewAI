"""Agent factory — builds CrewAI Agent instances from YAML config."""

from __future__ import annotations

import logging
from typing import Any

from crewai import Agent

from content_crew.config import load_agents_config
from content_crew.tools import build_search_tools

logger = logging.getLogger(__name__)


def _agent_kwargs(spec: dict[str, Any], *, tools: list[Any] | None = None) -> dict[str, Any]:
    kwargs: dict[str, Any] = {
        "role": spec["role"],
        "goal": spec["goal"].strip(),
        "backstory": spec["backstory"].strip(),
        "verbose": True,
        "allow_delegation": False,
    }
    if tools is not None:
        kwargs["tools"] = tools
    return kwargs


def create_research_agent(
    *,
    serper_api_key: str | None = None,
    allow_delegation: bool = False,
    config: dict[str, Any] | None = None,
) -> Agent:
    """Senior Research Analyst with optional Serper web search."""
    agents = config or load_agents_config()
    spec = agents["research_agent"]
    tools = build_search_tools(serper_api_key)
    kwargs = _agent_kwargs(spec, tools=tools)
    kwargs["allow_delegation"] = allow_delegation
    logger.debug("Creating research_agent with %d tool(s)", len(tools))
    return Agent(**kwargs)


def create_writer_agent(
    *,
    allow_delegation: bool = False,
    config: dict[str, Any] | None = None,
) -> Agent:
    """Tech Content Strategist — turns research into a blog post."""
    agents = config or load_agents_config()
    spec = agents["writer_agent"]
    kwargs = _agent_kwargs(spec)
    kwargs["allow_delegation"] = allow_delegation
    logger.debug("Creating writer_agent")
    return Agent(**kwargs)


def create_social_agent(
    *,
    allow_delegation: bool = False,
    config: dict[str, Any] | None = None,
) -> Agent:
    """Social Media Strategist — compresses blog content into posts."""
    agents = config or load_agents_config()
    spec = agents["social_agent"]
    kwargs = _agent_kwargs(spec)
    kwargs["allow_delegation"] = allow_delegation
    logger.debug("Creating social_agent")
    return Agent(**kwargs)


def create_all_agents(
    *,
    serper_api_key: str | None = None,
    config: dict[str, Any] | None = None,
) -> dict[str, Agent]:
    """Build the full agent roster keyed by logical name."""
    cfg = config or load_agents_config()
    return {
        "research_agent": create_research_agent(serper_api_key=serper_api_key, config=cfg),
        "writer_agent": create_writer_agent(config=cfg),
        "social_agent": create_social_agent(config=cfg),
    }
