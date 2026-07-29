"""Model and output writer tests."""

from __future__ import annotations

from pathlib import Path

from content_crew.models import CrewRunResult, TaskArtifact
from content_crew.services import OutputWriter


def test_crew_run_result_mark_finished() -> None:
    result = CrewRunResult(run_id="abc123", topic="GenAI")
    assert result.finished_at is None
    result.mark_finished()
    assert result.finished_at is not None


def test_output_writer_creates_artifacts(tmp_path: Path) -> None:
    result = CrewRunResult(
        run_id="testrun01",
        topic="Latest Generative AI breakthroughs",
        final_output="social posts here",
        artifacts=[
            TaskArtifact(name="research_task", agent_role="Analyst", content="# Research"),
            TaskArtifact(name="writer_task", agent_role="Writer", content="# Blog"),
            TaskArtifact(name="social_task", agent_role="Social", content="**Post 1:** hi"),
        ],
    )
    out = OutputWriter(tmp_path).write(result)
    assert (out / "research_report.md").exists()
    assert (out / "blog_post.md").exists()
    assert (out / "social_posts.md").exists()
    assert (out / "final_output.md").exists()
    assert (out / "run_manifest.json").exists()
