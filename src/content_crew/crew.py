"""Crew orchestration — wires agents, tasks, and the sequential process."""

from __future__ import annotations

import logging
import uuid
from typing import TYPE_CHECKING, Any

from content_crew.config import Settings, get_settings, load_app_settings
from content_crew.models import CrewRunResult, TaskArtifact
from content_crew.services import OutputWriter

if TYPE_CHECKING:
    from crewai import Crew

logger = logging.getLogger(__name__)

# Fixture payloads used when CONTENT_CREW_DRY_RUN=true (no LLM / tool calls).
_DRY_RUN_ARTIFACTS: tuple[tuple[str, str, str], ...] = (
    (
        "research_task",
        "Senior Research Analyst",
        (
            "# Research Report (dry-run)\n\n"
            "## Executive Summary\n"
            "Generative AI advanced rapidly with multimodal models, agentic systems, "
            "and enterprise adoption across retail, healthcare, and finance.\n\n"
            "## Key Breakthroughs\n"
            "- Multimodal LLMs (text, image, code, video)\n"
            "- Autonomous agent frameworks\n"
            "- Efficiency gains in training and inference\n\n"
            "## Sources\n"
            "- Example: https://example.com/genai-trends\n"
        ),
    ),
    (
        "writer_task",
        "Tech Content Strategist",
        (
            "# Generative AI Breakthroughs: From Hype to Production (dry-run)\n\n"
            "Generative AI moved from demos to durable enterprise workflows. "
            "Organizations now ship assistants, copilots, and domain-specific models "
            "that reshape how teams write, analyze, and decide.\n\n"
            "Adoption leaders report measurable gains in customer support resolution, "
            "developer productivity, and knowledge work acceleration — while still "
            "wrestling with evaluation, safety, and cost controls.\n"
        ),
    ),
    (
        "social_task",
        "Social Media Strategist",
        (
            "**Post 1:** Generative AI is shifting from experiment to operating system "
            "for knowledge work. Multimodal models + agents are reshaping support, "
            "dev, and analytics. #GenerativeAI #AI\n\n"
            "**Post 2:** Enterprise gen-AI isn't just chatbots — it's copilots, "
            "workflow automation, and domain models with real ROI. Worth a deeper look. "
            "#TechTrends #FutureOfWork\n"
        ),
    ),
)


class ContentCrew:
    """
    Production façade around a CrewAI sequential pipeline:

        research_agent → writer_agent → social_agent
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.app_settings = load_app_settings()
        self._crew: Crew | None = None

    def build(self) -> Crew:
        """Construct (or return cached) Crew instance."""
        if self._crew is not None:
            return self._crew

        from crewai import Crew, Process

        from content_crew.agents import create_all_agents
        from content_crew.tasks import create_tasks

        agents = create_all_agents(serper_api_key=self.settings.serper_api_key)
        tasks = create_tasks(agents)
        crew_cfg = self.app_settings.get("crew", {})

        verbose = self.settings.verbose
        if "verbose" in crew_cfg:
            verbose = bool(crew_cfg["verbose"])

        self._crew = Crew(
            agents=list(agents.values()),
            tasks=tasks,
            process=Process.sequential,
            verbose=verbose,
            memory=bool(crew_cfg.get("memory", False)),
        )
        logger.info(
            "Built crew '%s' with %d agents / %d tasks (process=sequential)",
            crew_cfg.get("name", "content_generation_crew"),
            len(agents),
            len(tasks),
        )
        return self._crew

    def kickoff(self, topic: str, *, persist: bool = True) -> CrewRunResult:
        """
        Execute the sequential pipeline for ``topic``.

        When ``settings.dry_run`` is True, returns fixture artifacts without
        calling remote LLMs or tools — useful for CI and local smoke tests.
        """
        run_id = uuid.uuid4().hex[:12]
        result = CrewRunResult(
            run_id=run_id,
            topic=topic,
            dry_run=self.settings.dry_run,
            metadata={
                "model": self.settings.openai_model_name,
                "verbose": self.settings.verbose,
            },
        )

        if self.settings.dry_run:
            logger.warning("DRY RUN enabled — skipping live CrewAI execution")
            result.artifacts = [
                TaskArtifact(name=n, agent_role=r, content=c)
                for n, r, c in _DRY_RUN_ARTIFACTS
            ]
            result.final_output = result.artifacts[-1].content
            result.mark_finished()
        else:
            self._validate_credentials()
            crew = self.build()
            logger.info("Starting crew kickoff for topic=%r (run_id=%s)", topic, run_id)
            crew_output = crew.kickoff(inputs={"topic": topic})
            result.final_output = str(crew_output)
            result.artifacts = self._extract_artifacts(crew)
            result.mark_finished()
            logger.info("Crew kickoff completed (run_id=%s)", run_id)

        if persist:
            writer = OutputWriter(self.settings.resolve_output_dir())
            out_dir = writer.write(result)
            result.metadata["output_dir"] = str(out_dir)

        return result

    def _validate_credentials(self) -> None:
        if not self.settings.openai_api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is required for live runs. "
                "Copy .env.example to .env or set CONTENT_CREW_DRY_RUN=true."
            )

    @staticmethod
    def _extract_artifacts(crew: Any) -> list[TaskArtifact]:
        artifacts: list[TaskArtifact] = []
        for task in crew.tasks:
            output = getattr(task, "output", None)
            content = ""
            if output is not None:
                content = str(getattr(output, "raw", None) or output)
            agent = task.agent
            role = getattr(agent, "role", "unknown") if agent else "unknown"
            name = getattr(task, "description", "task")[:64]
            artifacts.append(
                TaskArtifact(
                    name=name.replace("\n", " ").strip(),
                    agent_role=str(role),
                    content=content or "(empty task output)",
                )
            )
        labels = ("research_task", "writer_task", "social_task")
        if len(artifacts) == 3:
            for artifact, label in zip(artifacts, labels, strict=True):
                artifact.name = label
        return artifacts


def run_pipeline(
    topic: str,
    *,
    settings: Settings | None = None,
    persist: bool = True,
) -> CrewRunResult:
    """Convenience entrypoint used by the CLI and external callers."""
    return ContentCrew(settings=settings).kickoff(topic, persist=persist)
