# Architecture

This document expands on the README diagrams and explains design choices for a production-shaped CrewAI content pipeline.

## Design goals

1. **Declarative agents/tasks** — role text lives in YAML so product/content owners can iterate without touching Python.
2. **Thin orchestration** — `ContentCrew` only wires factories, validates credentials, runs `kickoff`, and persists artifacts.
3. **Deterministic CI** — `--dry-run` / `CONTENT_CREW_DRY_RUN=true` exercises the full path without billed LLM or Serper calls.
4. **Auditable outputs** — every run produces Markdown artifacts plus a JSON manifest.

## Control flow

```mermaid
stateDiagram-v2
  [*] --> ValidateEnv: CLI run
  ValidateEnv --> DryRun: dry_run?
  ValidateEnv --> BuildCrew: live
  DryRun --> Persist: fixture artifacts
  BuildCrew --> Research: sequential[0]
  Research --> Write: context forwarded
  Write --> Social: context forwarded
  Social --> Persist: final + task outputs
  Persist --> [*]
```

## Agent responsibilities

```mermaid
mindmap
  root((Content Crew))
    research_agent
      Web search via Serper
      Structured briefing
      Source citations
      Trends and impact
    writer_agent
      Narrative structure
      Tech-savvy audience
      Fidelity to research
      Markdown blog post
    social_agent
      Compression
      Platform tone
      Hashtags
      CTA to read more
```

## Context passing

CrewAI tasks declare `context=[prior_task]` so the writer and social agents receive prior raw outputs rather than re-deriving them. That mirrors how a human editorial desk hands a brief → draft → social cutdown.

```mermaid
flowchart TD
  RT["research_task.output"] -->|injected as context| WT["writer_task"]
  WT["writer_task.output"] -->|injected as context| ST["social_task"]
  ST --> FO["crew.kickoff return value<br/>(final task output)"]
```

## Configuration precedence

```mermaid
flowchart LR
  DEF["settings.yaml defaults"] --> ENV["Environment / .env<br/>CONTENT_CREW_* · OPENAI_* · SERPER_*"]
  ENV --> CLI["CLI flags<br/>--dry-run · --topic · --verbose"]
  CLI --> RUN["Effective runtime Settings"]
```

## Failure modes & mitigations

| Failure | Behavior |
| --- | --- |
| Missing `OPENAI_API_KEY` on live run | `RuntimeError` before `kickoff` |
| Missing `SERPER_API_KEY` | Warning; research agent runs with empty tool list |
| Tool init failure | Soft-fail; crew still builds |
| Downstream publisher outage | Irrelevant to core crew — artifacts remain on disk |

## Extension points

```mermaid
flowchart LR
  subgraph Stable["Keep stable"]
    ORCH["ContentCrew.kickoff"]
    MODEL["CrewRunResult"]
    WRITER["OutputWriter"]
  end

  subgraph Swap["Swap / extend"]
    YAML["agents.yaml / tasks.yaml"]
    TOOLS["tools/*"]
    PROC["Process.sequential → hierarchical"]
    SINK["New sinks: CMS, Slack, S3"]
  end

  YAML --> ORCH
  TOOLS --> ORCH
  PROC --> ORCH
  ORCH --> MODEL --> WRITER --> SINK
```

## Why not a single notebook?

Notebooks are excellent for exploration. This layout is aimed at:

- reproducible installs (`pyproject.toml` / pins),
- a real CLI for operators,
- unit-testable factories and persistence,
- clear seams for adding agents without rewriting the demo cell.
