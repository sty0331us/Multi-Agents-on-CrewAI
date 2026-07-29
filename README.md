# Multi-Agents on CrewAI

Production-oriented **multi-agent content pipeline** built with [CrewAI](https://www.crewai.com/). Three specialized agents collaborate in a **sequential process** to turn a topic into researched insight, a publishable blog post, and platform-ready social copy.

| Agent | Role | Responsibility |
| --- | --- | --- |
| `research_agent` | Senior Research Analyst | Web research + structured briefing with sources |
| `writer_agent` | Tech Content Strategist | Research → engaging tech blog post |
| `social_agent` | Social Media Strategist | Blog → 2–3 LinkedIn / X posts |

---

## Learning objectives

After working through this project you will be able to:

- Leverage CrewAI to automate multi-agent workflows for intelligent content generation.
- Understand CrewAI’s core building blocks — **agents**, **tasks**, **tools**, and **processes** — and how they compose into a sequential pipeline.
- Implement a real collaboration pattern: technical research → reader-friendly content → social distribution.
- Extend the same pattern to marketing, education, and research-automation domains.

---

## Architecture

### System context

```mermaid
flowchart TB
  subgraph External["External services"]
    LLM["LLM Provider<br/>(OpenAI via LiteLLM)"]
    SERPER["Serper.dev<br/>Web Search API"]
  end

  subgraph App["Content Crew application"]
    CLI["CLI / API entry<br/>content-crew run"]
    CFG["Config layer<br/>agents.yaml · tasks.yaml · settings.yaml · .env"]
    ORCH["ContentCrew orchestrator"]
    OUT["OutputWriter<br/>outputs/run_id/"]
  end

  USER["Operator / CI"] --> CLI
  CLI --> CFG
  CLI --> ORCH
  ORCH --> LLM
  ORCH --> SERPER
  ORCH --> OUT
  OUT --> ART["Artifacts<br/>research_report.md<br/>blog_post.md<br/>social_posts.md<br/>run_manifest.json"]
```

### Sequential multi-agent pipeline

```mermaid
flowchart LR
  IN["Input<br/>topic"] --> T1

  subgraph Crew["Crew · Process.sequential"]
    direction LR
    T1["research_task"] --> T2["writer_task"] --> T3["social_task"]

    A1["research_agent<br/>Senior Research Analyst"] -. assigned .-> T1
    A2["writer_agent<br/>Tech Content Strategist"] -. assigned .-> T2
    A3["social_agent<br/>Social Media Strategist"] -. assigned .-> T3

    TOOL["SerperDevTool"] -. tools .-> A1
  end

  T1 -->|"context: research brief"| T2
  T2 -->|"context: blog draft"| T3
  T3 --> FINAL["Final output<br/>social posts"]
```

### Sequence diagram — end-to-end collaboration

How a single `content-crew run --topic "..."` call flows through the sequential CrewAI pipeline: research with Serper, writing with research context, social cutdown with blog context, then artifact persistence.

```mermaid
sequenceDiagram
  autonumber
  actor Op as Operator
  participant CLI as content-crew CLI
  participant CFG as Config YAML and env
  participant CC as ContentCrew
  participant Crew as Crew sequential
  participant RA as research_agent
  participant Serper as SerperDevTool
  participant LLM as LLM Provider
  participant WA as writer_agent
  participant SA as social_agent
  participant OW as OutputWriter
  participant FS as outputs run directory

  Op->>CLI: run with topic input
  CLI->>CFG: Load settings, agents, tasks
  CFG-->>CLI: Runtime Settings and YAML specs
  CLI->>CC: kickoff(topic)

  CC->>CC: Validate credentials or dry-run
  CC->>Crew: Build agents and tasks

  Note over Crew,RA: Phase 1 research_task
  Crew->>RA: Execute research_task(topic)
  loop Until research brief is sufficient
    RA->>LLM: Reason about search plan
    LLM-->>RA: Thought and tool call
    RA->>Serper: search_query
    Serper-->>RA: Organic results and snippets
  end
  RA->>LLM: Synthesize sourced research report
  LLM-->>RA: Final research brief
  RA-->>Crew: research_task.output

  Note over Crew,WA: Phase 2 writer_task with research context
  Crew->>WA: Execute writer_task with research context
  WA->>LLM: Draft blog from research brief
  LLM-->>WA: Markdown blog post
  WA-->>Crew: writer_task.output

  Note over Crew,SA: Phase 3 social_task with blog context
  Crew->>SA: Execute social_task with blog context
  SA->>LLM: Compress blog into 2-3 posts
  LLM-->>SA: LinkedIn or X social copy
  SA-->>Crew: social_task.output

  Crew-->>CC: CrewOutput final social posts
  CC->>OW: Persist CrewRunResult
  OW->>FS: research_report.md
  OW->>FS: blog_post.md
  OW->>FS: social_posts.md
  OW->>FS: final_output.md
  OW->>FS: run_manifest.json
  OW-->>CC: output_dir path
  CC-->>CLI: CrewRunResult
  CLI-->>Op: Rich panels and artifact path
```

### Component map (repository)

```mermaid
flowchart TB
  subgraph config_pkg["config/"]
    AY["agents.yaml"]
    TY["tasks.yaml"]
    SY["settings.yaml"]
  end

  subgraph src_pkg["src/content_crew/"]
    CLI2["cli.py"]
    CREW["crew.py"]
    AG["agents/"]
    TK["tasks/"]
    TL["tools/search.py"]
    SV["services/output_writer.py"]
    MD["models/outputs.py"]
    CF["config.py"]
  end

  CLI2 --> CREW
  CREW --> AG
  CREW --> TK
  AG --> TL
  AG --> AY
  TK --> TY
  CREW --> SY
  CREW --> SV
  CREW --> MD
  CF --> AY
  CF --> TY
  CF --> SY
```

### Data / artifact flow

```mermaid
flowchart TD
  TOPIC["topic: string"] --> R1["research_report.md"]
  R1 --> R2["blog_post.md"]
  R2 --> R3["social_posts.md"]
  R3 --> R4["final_output.md"]
  R1 & R2 & R3 & R4 --> M["run_manifest.json<br/>run_id · timings · metadata"]
```

---

## Project structure

```text
Multi-Agents-on-CrewAI/
├── config/
│   ├── agents.yaml          # Roles, goals, backstories
│   ├── tasks.yaml           # Descriptions, expected outputs, context chain
│   └── settings.yaml        # Crew / LLM / output defaults
├── src/content_crew/
│   ├── cli.py               # Typer CLI (run, doctor, version)
│   ├── crew.py              # ContentCrew orchestrator
│   ├── config.py            # Pydantic settings + YAML loaders
│   ├── agents/              # Agent factory
│   ├── tasks/               # Task factory + context wiring
│   ├── tools/               # Serper search tool wiring
│   ├── services/            # Artifact persistence
│   └── models/              # Run result schemas
├── outputs/                 # Per-run artifacts (gitignored contents)
├── tests/                   # Unit tests + dry-run pipeline tests
├── docs/architecture.md     # Extended design notes
├── .env.example
├── pyproject.toml
├── requirements.txt
└── Makefile
```

This layout separates **declarative config** (who the agents are / what they do) from **imperative orchestration** (how the crew is built and executed), which is the usual pattern for systems you expect to evolve beyond a notebook demo.

---

## CrewAI building blocks (how they map here)

| Concept | In this project | Notes |
| --- | --- | --- |
| **Agent** | `config/agents.yaml` → `agents/` | Role, goal, backstory; research agent owns search tools |
| **Task** | `config/tasks.yaml` → `tasks/` | Description + expected output; writer/social receive prior context |
| **Tool** | `tools/search.py` → `SerperDevTool` | Live web search for the research agent |
| **Process** | `Process.sequential` | Strict order: research → write → social |
| **Crew** | `ContentCrew` in `crew.py` | Assembles agents/tasks and calls `kickoff(inputs={"topic": …})` |

---

## Setup

### Prerequisites

- Python **3.10–3.12**
- An OpenAI API key (or compatible key routed through LiteLLM)
- A [Serper](https://serper.dev) API key for live web research (optional for `--dry-run`)

### Install

```bash
cd Multi-Agents-on-CrewAI
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -U pip
pip install -e ".[dev]"
cp .env.example .env               # then edit API keys
```

Pinned stack (aligned with the lab versions you shared):

| Package | Version |
| --- | --- |
| `crewai` | `0.80.0` |
| `crewai-tools` | `0.38.0` |
| `langchain` | `0.3.20` |
| `langchain-community` | `0.3.19` |

> **Note:** Installing `crewai` and `crewai-tools` together can pull transitive upgrades. Prefer `pip install -e ".[dev]"` from this repo so pins in `pyproject.toml` / `requirements.txt` stay authoritative. Restart your shell/kernel after install if packages were upgraded in-place.

---

## Usage

### Validate environment

```bash
content-crew doctor
```

### Live run

```bash
content-crew run --topic "Latest Generative AI breakthroughs"
# or
make run TOPIC="Latest Generative AI breakthroughs"
```

### Dry run (no LLM / Serper calls — CI & local smoke tests)

```bash
content-crew run --topic "Latest Generative AI breakthroughs" --dry-run
# or
make dry-run
```

### Programmatic API

```python
from content_crew.crew import run_pipeline

result = run_pipeline("Latest Generative AI breakthroughs")
print(result.final_output)
print(result.metadata["output_dir"])
```

Equivalent CrewAI core (what the orchestrator builds):

```python
crew = Crew(
    agents=[research_agent, writer_agent, social_agent],
    tasks=[research_task, writer_task, social_task],
    process=Process.sequential,
    verbose=True,
)
result = crew.kickoff(inputs={"topic": "Latest Generative AI breakthroughs"})
```

---

## Outputs

Each run writes a directory under `outputs/`:

```text
outputs/<run_id>_<topic-slug>/
├── research_report.md
├── blog_post.md
├── social_posts.md
├── final_output.md
└── run_manifest.json
```

`run_manifest.json` includes `run_id`, timestamps, topic, dry-run flag, and per-task artifacts for auditing or downstream publishing jobs.

---

## Testing & quality

```bash
make test        # pytest (includes dry-run pipeline)
make lint        # ruff
make typecheck   # mypy
```

Live LLM integration tests are intentionally out of scope for the default suite so CI stays deterministic and free.

---

## Extending the system

Practical next steps that keep the architecture intact:

1. **New domain** — duplicate agent/task YAML entries (e.g. `educator_agent`) and append a task to the sequential chain.
2. **Hierarchical process** — switch `process` in `settings.yaml` / `crew.py` to `Process.hierarchical` and designate a manager agent.
3. **More tools** — add file I/O, scrapers, or vector retrieval beside Serper in `tools/`.
4. **Publishing adapters** — consume `outputs/*/run_manifest.json` from a CMS, Slack, or scheduling worker.
5. **Observability** — hook OpenTelemetry exporters already pulled in by CrewAI for production traces.

See [docs/architecture.md](docs/architecture.md) for deeper design rationale and Mermaid views of extension points.

---

## License

MIT
