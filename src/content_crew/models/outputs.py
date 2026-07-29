"""Structured result models for crew outputs."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class TaskArtifact(BaseModel):
    """Output captured from a single crew task."""

    name: str
    agent_role: str
    content: str
    status: str = "completed"


class CrewRunResult(BaseModel):
    """Full run result persisted to disk as a manifest + artifacts."""

    run_id: str
    topic: str
    process: str = "sequential"
    started_at: str = Field(default_factory=utc_now_iso)
    finished_at: str | None = None
    dry_run: bool = False
    final_output: str = ""
    artifacts: list[TaskArtifact] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def mark_finished(self) -> None:
        self.finished_at = utc_now_iso()
