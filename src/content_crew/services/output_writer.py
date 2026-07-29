"""Persist crew artifacts to the outputs directory."""

from __future__ import annotations

import logging
import re
from pathlib import Path

from content_crew.models import CrewRunResult

logger = logging.getLogger(__name__)


def _slugify(value: str, max_len: int = 48) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return (slug or "run")[:max_len]


class OutputWriter:
    """Writes per-run artifacts (research, blog, social) and a JSON manifest."""

    ARTIFACT_NAMES = ("research_report", "blog_post", "social_posts")

    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def write(self, result: CrewRunResult) -> Path:
        run_dir = self.output_dir / f"{result.run_id}_{_slugify(result.topic)}"
        run_dir.mkdir(parents=True, exist_ok=True)

        for index, artifact in enumerate(result.artifacts):
            prefix = (
                self.ARTIFACT_NAMES[index]
                if index < len(self.ARTIFACT_NAMES)
                else artifact.name
            )
            path = run_dir / f"{prefix}.md"
            path.write_text(artifact.content.strip() + "\n", encoding="utf-8")
            logger.info("Wrote artifact: %s", path)

        final_path = run_dir / "final_output.md"
        final_path.write_text(result.final_output.strip() + "\n", encoding="utf-8")

        manifest_path = run_dir / "run_manifest.json"
        manifest_path.write_text(
            result.model_dump_json(indent=2) + "\n",
            encoding="utf-8",
        )
        logger.info("Run artifacts saved to %s", run_dir)
        return run_dir
