"""Typer CLI for the Content Generation Crew."""

from __future__ import annotations

import json

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from content_crew import __version__
from content_crew.config import get_settings
from content_crew.crew import run_pipeline
from content_crew.logging_setup import setup_logging

app = typer.Typer(
    name="content-crew",
    help="Production multi-agent content pipeline (research → write → social) powered by CrewAI.",
    add_completion=False,
    no_args_is_help=True,
)
console = Console()


@app.callback()
def main(
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable debug logging.",
    ),
) -> None:
    settings = get_settings()
    level = "DEBUG" if verbose else settings.log_level
    setup_logging(level)


@app.command("version")
def version_cmd() -> None:
    """Print package version."""
    console.print(__version__)


@app.command("run")
def run_cmd(
    topic: str = typer.Option(
        "Latest Generative AI breakthroughs",
        "--topic",
        "-t",
        help="Topic to research and turn into content.",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Skip live LLM/tool calls; emit fixture artifacts.",
    ),
    no_persist: bool = typer.Option(
        False,
        "--no-persist",
        help="Do not write artifacts under outputs/.",
    ),
    json_out: bool = typer.Option(
        False,
        "--json",
        help="Print the run manifest as JSON instead of rich panels.",
    ),
) -> None:
    """Execute the sequential research → writer → social crew."""
    base = get_settings()
    settings = base.model_copy(update={"dry_run": True}) if dry_run else base

    mode = "[yellow]dry-run[/yellow]" if settings.dry_run else "[green]live[/green]"
    console.print(
        Panel.fit(
            f"[bold]Content Crew[/bold] v{__version__}\n"
            f"Topic: [cyan]{topic}[/cyan]\n"
            f"Mode: {mode}",
            title="Kickoff",
        )
    )

    result = run_pipeline(topic, settings=settings, persist=not no_persist)

    if json_out:
        console.print_json(result.model_dump_json())
        return

    for artifact in result.artifacts:
        console.print(
            Panel(
                Markdown(artifact.content),
                title=f"{artifact.name} — {artifact.agent_role}",
                border_style="blue",
            )
        )

    console.print(
        Panel(
            Markdown(result.final_output),
            title="Final Output (Social)",
            border_style="green",
        )
    )

    out_dir = result.metadata.get("output_dir")
    if out_dir:
        console.print(f"[dim]Artifacts written to[/dim] {out_dir}")


@app.command("doctor")
def doctor_cmd() -> None:
    """Validate environment configuration without running the crew."""
    settings = get_settings()
    checks = {
        "OPENAI_API_KEY": bool(settings.openai_api_key),
        "SERPER_API_KEY": bool(settings.serper_api_key),
        "OPENAI_MODEL_NAME": settings.openai_model_name,
        "OUTPUT_DIR": str(settings.resolve_output_dir()),
        "DRY_RUN": settings.dry_run,
    }
    console.print(Panel(json.dumps(checks, indent=2), title="Environment"))
    if not settings.openai_api_key and not settings.dry_run:
        console.print(
            "[yellow]Warning:[/yellow] OPENAI_API_KEY missing — live runs will fail. "
            "Use --dry-run or set the key in .env."
        )
        raise typer.Exit(code=1)
    console.print("[green]Doctor checks passed.[/green]")


if __name__ == "__main__":
    app()
