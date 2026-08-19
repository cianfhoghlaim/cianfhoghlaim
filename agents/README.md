# Agents

> **The Cianfhoghlaim Agent Fleet.** A polyglot agent platform spanning
> 5 frameworks (Custom + Google ADK + Agno + Pipecat + CopilotKit),
> with a centralized wiring layer, a 5-layer observability stack, and
> a 5-backend memory layer.

## What this is

`agents/` hosts the `AGENT_REGISTRY` — 13 root-level agents (routed
via `agents/agent_registry.py`) plus the 8 NCCA Leaving Cert subject
specialists (`agents/tuatha/`), each backed by LiteLLM model routing,
BAML structured extraction, and a shared observability/memory layer.
It's the runtime that answers a user's question by picking the right
specialist, calling it with the right tools, and recording the trace.

## Architecture

```
        user question
              │
              ▼
       root_agent (routing)
              │
   ┌──────────┼──────────────────────┐
   ▼          ▼                      ▼
curriculum_*  research_* / corpus_*  tuatha/ (8 NCCA subjects)
   │              │                      │
   └──────────────┴──────────┬───────────┘
                              ▼
                   agents/wiring.py (shared setup)
                    ├─ LiteLLM model routing (model_for())
                    ├─ BAML structured extraction
                    ├─ observability_hooks.py (Langfuse/Logfire/MLflow/RAGAS/structlog)
                    └─ memory_layer.py (Cognee/Graphiti/LanceDB/FalkorDB/Memgraph)
```

Each agent is a thin framework wrapper (ADK `LlmAgent`, Agno `Agent`,
or a custom dispatcher) over the same shared wiring — the framework
choice is per-agent, the plumbing underneath it is not.

## Implementation decisions

- **5 frameworks, not 1** — ADK for structured multi-tool agents
  (curriculum, research), Agno for the education team's multi-agent
  coordination, Pipecat for voice, CopilotKit for the web-embedded
  agent surface, and a lightweight custom dispatcher (`root_agent`)
  for pure routing. No single framework covers all four shapes well;
  picking per-agent avoided forcing voice/web/batch agents into one
  framework's assumptions.
- **LiteLLM for model routing, not per-agent client code** — every
  agent calls `model_for(family, role)` (see
  `.agents/skills/centralized-registry/SKILL.md`) rather than
  hardcoding a model string, so a model swap is a registry edit, not
  a 60-file grep-and-replace.
- **`AGENT_REGISTRY` as the single source of truth** — `agents/tuatha/wiring.py`
  registers the 8 NCCA subject agents into the same dict the 13 root
  agents live in, so anything that walks the fleet (tests, docs
  generators, the drift linter) sees one list, not two.

## Layout

| Path | Purpose |
|:--|:--|
| `agents/agent_registry.py` | The `AGENT_REGISTRY` dict (13 root agents) |
| `agents/adk/` | Google ADK agent implementations |
| `agents/agno/` | Agno education-team multi-agent coordination |
| `agents/tuatha/` | The 8 NCCA subject specialists + subject router |
| `agents/api/` | Hono API routes exposing agents to the web apps |
| `agents/tools/` | 9 shared tool modules |
| `agents/wiring.py` | Centralized model/BAML/observability/memory setup |
| `agents/memory_layer.py` | The 5-backend memory layer |
| `agents/observability_hooks.py` | The 5-layer observability stack |
| `agents/meaisinfhoghlaim/` | OCR/HTR-specific agent sub-package |

## Run it

```bash
uv run python -c "from agents.agent_registry import AGENT_REGISTRY; print(len(AGENT_REGISTRY))"
mise run agents:audit   # AGENT_REGISTRY validation for the fleet
```

For the full quadrant overview (routing keywords, per-agent status,
how to add a new agent, how to reproduce the fleet from zero), see
[`AGENTS.md`](AGENTS.md), [`STATUS.md`](STATUS.md),
[`DEVELOPMENT.md`](DEVELOPMENT.md), and [`REPRODUCER.md`](REPRODUCER.md).

## Take it independently

The cleanest single-file entry point to clone this pattern for another
domain is `agents/meaisinfhoghlaim/educational/celtic_morphology_agent.py`
(~210 LoC, 4 trivial tool wrappers, no manifest, no web dependency).
Rename the tool functions and BAML imports, point `model_for()` at
your own registry, and it runs standalone. See
[`docs/CHOP_AND_CHANGE_GUIDE.md`](../docs/CHOP_AND_CHANGE_GUIDE.md#2-agents--the-agent-fleet-umbrella)
for the fuller per-file breakdown.

## Known gaps

- The installed `google-adk` version's Pydantic validation is stricter
  than some agents were written against — `agents/adk/research_agent.py`'s
  `output_schema` (a bare `list[SearchQuery]`) currently fails
  validation at agent-construction time. Declared as a real dependency
  as of 2026-08-19; the schema itself hasn't been fixed yet.
- `agents/tuatha/README.md` (881 lines) still describes the pre-v7
  `sruth/` namespaces and is self-dated 2026-06-15; the current,
  accurate doc for this game/MMO surface is [`tuatha/README.md`](../tuatha/README.md)
  at the repo root.

## Cross-References

- The main agent architecture: [`AGENTS.md`](AGENTS.md)
- The skills library: [`.agents/skills/`](../.agents/skills/)
- The canonical exceptions: [`agents/exceptions.py`](exceptions.py)
- The Pydantic v2 base models: [`agents/pydantic_models.py`](pydantic_models.py)

### Sub-package AGENTS.md

- [`agents/api/AGENTS.md`](api/AGENTS.md) — the Hono API routes
- [`agents/tools/AGENTS.md`](tools/AGENTS.md) — the 9 tool modules
- [`agents/meaisinfhoghlaim/AGENTS.md`](meaisinfhoghlaim/AGENTS.md) — the OCR/HTR sub-package
- [`agents/tuatha/AGENTS.md`](tuatha/AGENTS.md) — the 8 NCCA subject specialists
