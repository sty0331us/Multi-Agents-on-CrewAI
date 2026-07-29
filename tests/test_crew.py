"""Crew dry-run pipeline tests (no live LLM calls)."""

from __future__ import annotations

from content_crew.config import Settings
from content_crew.crew import ContentCrew, run_pipeline


def test_dry_run_pipeline(dry_settings: Settings) -> None:
    result = run_pipeline(
        "Latest Generative AI breakthroughs",
        settings=dry_settings,
        persist=True,
    )
    assert result.dry_run is True
    assert len(result.artifacts) == 3
    assert result.artifacts[0].name == "research_task"
    assert result.artifacts[1].name == "writer_task"
    assert result.artifacts[2].name == "social_task"
    assert "Generative AI" in result.final_output or "generative" in result.final_output.lower()
    assert result.metadata.get("output_dir")


def test_live_run_requires_api_key(tmp_path) -> None:  # type: ignore[no-untyped-def]
    settings = Settings(
        CONTENT_CREW_DRY_RUN=False,
        CONTENT_CREW_OUTPUT_DIR=str(tmp_path),
        OPENAI_API_KEY=None,
    )
    crew = ContentCrew(settings=settings)
    try:
        crew.kickoff("topic", persist=False)
        raised = False
    except RuntimeError as exc:
        raised = True
        assert "OPENAI_API_KEY" in str(exc)
    assert raised
