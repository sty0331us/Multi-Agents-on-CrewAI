"""Config and YAML loading tests."""

from __future__ import annotations

from content_crew.config import (
    load_agents_config,
    load_app_settings,
    load_tasks_config,
    project_root,
)


def test_project_root_contains_config() -> None:
    assert (project_root() / "config" / "agents.yaml").exists()


def test_agents_yaml_has_three_agents() -> None:
    agents = load_agents_config()
    assert set(agents) >= {"research_agent", "writer_agent", "social_agent"}
    for name in ("research_agent", "writer_agent", "social_agent"):
        assert "role" in agents[name]
        assert "goal" in agents[name]
        assert "backstory" in agents[name]


def test_tasks_yaml_context_chain() -> None:
    tasks = load_tasks_config()
    assert "research_task" in tasks
    assert tasks["writer_task"]["context"] == ["research_task"]
    assert tasks["social_task"]["context"] == ["writer_task"]


def test_settings_yaml_process_is_sequential() -> None:
    settings = load_app_settings()
    assert settings["crew"]["process"] == "sequential"
