# Agents Quadrant — Agent Instructions

> **The Cianfhoghlaim Agent Fleet — the 12-agent fleet + 8 NCCA
> subject specialists + 3 educational agents.** A polyglot agent
> platform spanning 5 frameworks (Custom + ADK + Agno + Pipecat +
> CopilotKit), with the centralized wiring layer
> (`agents/wiring.py` + `agents/agent_registry.py`), the 5-layer
> observability stack (`agents/observability_hooks.py`), the
> 5-backend memory layer (`agents/memory_layer.py`), and the 4
> shared async dispatchers (`agents/_workflow_handlers.py`).

> **Wiring parity landed 2026-08-14** — the agent fleet is now
> wired through a single canonical surface
> (`AGENT_REGISTRY`) with the same conventions as
> `agents/tuatha/wiring.py:SubjectAgentWiring` (which was the
> reference template).

## Priority quick reference

The 8 priority skills, the 4 priority commands, the 4 priority
compose stacks, and the 4 priority openspec specs at a glance.
**Read this first**; the rest of the file is the full 12-agent
routing.

### Priority skills (10 of 53)

| Skill | When to load |
|:--|:--|
| [`agent-fleet-orchestration`](../.agents/skills/agent-fleet-orchestration/SKILL.md) | The 12-agent fleet wiring + the 5-framework runtime + the LiteLLM routing keyword map |
| [`agent-memory-systems`](../.agents/skills/agent-memory-systems/SKILL.md) | Cognee + Graphiti + LanceDB + FalkorDB + Memgraph memory backends |
| [`agent-observability`](../.agents/skills/agent-observability/SKILL.md) | Langfuse + Logfire + MLflow + RAGAS + structlog observability stack |
| [`agent-runtime-and-attribution`](../.agents/skills/agent-runtime-and-attribution/SKILL.md) | Agent runtime + attribution patterns |
| [`agentic-frontend-frameworks`](../.agents/skills/agentic-frontend-frameworks/SKILL.md) | CopilotKit + AG-UI + TanStack Start |
| [`agent-registry`](../.agents/skills/agent-registry/SKILL.md) | The canonical agent registry pattern |
| [`agent-platform-cluster`](../.agents/skills/agent-platform-cluster/SKILL.md) | The 8-stack agent cluster on bunchloch + arm1-oci |
| [`agno`](../.agents/skills/agno/SKILL.md) | Agno multi-agent orchestration |
| [`google-adk`](../.agents/skills/google-adk/SKILL.md) | Google Agent Development Kit |
| [`dignified-python`](../.agents/skills/dignified-python/SKILL.md) | Production Python standards |

### Priority commands

```bash
# The 12-agent fleet
python -c "from cianfhoghlaim.agents import AGENT_REGISTRY; print(len(AGENT_REGISTRY))"
# 12

# The 8 NCCA subject specialists (back-compat via tuatha/wiring.py)
python -c "from cianfhoghlaim.agents.tuatha import math_agent; print(math_agent)"

# The 5-layer observability contract
python -c "from cianfhoghlaim.agents.observability_hooks import verify_5_layer_contract; print(verify_5_layer_contract())"

# The 5-backend memory layer
python -c "from cianfhoghlaim.agents.memory_layer import get_default_memory_layer; l = get_default_memory_layer(); print(l.kind)"

# OpenSpec workflow
openspec list --specs
openspec validate <change-id> --strict
openspec archive <change-id> --yes
```

### Priority openspec specs (4 of 48)

| Spec | One-liner |
|:--|:--|
| `meaisinfhoghlaim-agent-frameworks` | The 12-agent fleet + the 8 NCCA subject specialists + the centralized wiring |
| `agent-observability` | The 5-layer observability stack |
| `agent-memory-systems` | The 5-backend memory layer |
| `agent-platform-cluster` | The 8-stack agent cluster IaC |

### Priority mise tasks

```bash
mise run agents:smoke         # 3 test files + reproducer
mise run agents:audit         # direct-import audit + registry validation
mise run lint:skills          # validate .agents/skills/ metadata
```

## Overview

`agents/` is the **agent fleet** sub-package of the Cianfhoghlaim
monorepo. It houses:

- **12 main agents** (the canonical agent fleet)
  - 1 Custom agent (`root_agent`)
  - 8 ADK agents (`curriculum_agent`, `translation_agent`,
    `corpus_agent`, `research_agent`, `geospatial_agent`,
    `statistics_agent`, `curriculum_comparison_agent`,
    `mcp_curriculum_agent`)
  - 3 Agno agents (`education_research_agent`,
    `bunchloch_research_agent`, `agui_curriculum_agent`)
  - 5 framework stubs (Pipecat + CopilotKit + 3 future frameworks)

- **8 NCCA subject specialists** at `agents/tuatha/<slug>_agent.py`
  - `gael_agent`, `math_agent`, `appm_agent`, `chem_agent`,
    `comp_agent`, `engl_agent`, `geog_agent`, `hist_agent`
  - The 8 are re-exported through the canonical `AGENT_REGISTRY`
    via `agents/tuatha/wiring.py:register_ncca_subjects_in_agent_registry()`

- **3 educational agents** at `agents/meaisinfhoghlaim/educational/`
  - `academic_history_agent`, `celtic_grammar_agent`,
    `celtic_morphology_agent`

- **The OCR/HTR/alignment sub-package** at
  `agents/meaisinfhoghlaim/` — 10 OCR backends across 4 ensemble
  patterns + 3 alignment primitives. See
  [`agents/meaisinfhoghlaim/AGENTS.md`](meaisinfhoghlaim/AGENTS.md).

- **The Hono API routes** at `agents/api/` — 8 route categories +
  3 endpoint patterns. See [`agents/api/AGENTS.md`](api/AGENTS.md).

- **The tools layer** at `agents/tools/` — 9 tool modules for
  curriculum search, corpus lookup, geospatial analysis, statistics
  computation, terminology lookup, etc. See
  [`agents/tools/AGENTS.md`](tools/AGENTS.md).

- **The centralized wiring layer** (added by the
  `2026-08-14-agents-fleet-wiring-parity-v1` change):
  - `agents/wiring.py` — `AgentFleetWiring` dataclass + `wire_agent`
  - `agents/agent_registry.py` — `AGENT_REGISTRY` dict (12 + 8 entries)
  - `agents/_workflow_handlers.py` — 4 shared async dispatchers
  - `agents/observability_hooks.py` — 5-layer observability stack
  - `agents/memory_layer.py` — 5-backend memory layer
  - `agents/exceptions.py` — canonical `AgentError` hierarchy
  - `agents/pydantic_models.py` — 4 Pydantic v2 base models

## The 12 agents (the fleet)

| Agent | Framework | Speciality | Langfuse trace tag | Cognee dataset |
|:--|:--|:--|:--|:--|
| `root_agent` | Custom | The query router + orchestrator | `agent.root.route` | `oideachais_root` |
| `curriculum_agent` | ADK | The 5-nation curriculum search (NCCA + CfE + CfW + CCEA + SQA) | `agent.curriculum.search` | `oideachais_curriculum` |
| `translation_agent` | ADK | The 6-Celtic-language translation | `agent.translation.translate` | `oideachais_translation` |
| `corpus_agent` | ADK | The Dúchas + Gaois + UD + Canúint + Téarma corpus search | `agent.corpus.search` | `oideachais_corpus` |
| `research_agent` | ADK | The long-form research + citations | `agent.research.deep` | `oideachais_research` |
| `education_research_agent` | Agno | The cross-nation education policy research (LoopAgent) | `agent.education_research.policy` | `oideachais_education_research` |
| `bunchloch_research_agent` | Agno | The M4 MacBook-local research (SequentialAgent) | `agent.bunchloch_research.local` | `oideachais_bunchloch_research` |
| `geospatial_agent` | ADK | The LSOA / Data Zone spatial analysis | `agent.geospatial.spatial` | `oideachais_geospatial` |
| `statistics_agent` | ADK | The education metrics + benchmarking | `agent.statistics.benchmark` | `oideachais_statistics` |
| `curriculum_comparison_agent` | ADK | The cross-nation curriculum mapping | `agent.curriculum_comparison.map` | `oideachais_curriculum_comparison` |
| `agui_curriculum_agent` | Agno | The AG-UI streaming curriculum agent (CopilotKit consumer) | `agent.agui_curriculum.stream` | `oideachais_agui_curriculum` |
| `mcp_curriculum_agent` | ADK | The MCP-server-bridged curriculum agent (for external clients) | `agent.mcp_curriculum.bridge` | `oideachais_mcp_curriculum` |

The 12 are registered in `agents/agent_registry.AGENT_REGISTRY`.
The 8 NCCA subject agents are re-exported through the same surface
via `agents/tuatha/wiring.py:register_ncca_subjects_in_agent_registry()`.

## The 5 frameworks (the runtime)

| Framework | Implementation | Used by |
|:--|:--|:--|
| Custom | `agents/adk/root_agent.py` (the query router + LiteLLM) | `root_agent` |
| ADK | `google.adk.agents.LlmAgent` (via `cianfhoghlaim.agents.adk.*`) | `curriculum_agent`, `translation_agent`, `corpus_agent`, `research_agent`, `geospatial_agent`, `statistics_agent`, `curriculum_comparison_agent`, `mcp_curriculum_agent` |
| Agno | `agents/agno/team.py` (the EducationTeam) | `education_research_agent`, `bunchloch_research_agent`, `agui_curriculum_agent` |
| Pipecat | `agents/voice_agent.py` (the real-time audio transport) | (the voice agent is not in the 12 above; it's a separate voice channel — deferred) |
| CopilotKit | `agents/adk/agui_curriculum_agent.py` (the AG-UI consumer) | (the CopilotKit consumer is the front-end; it's not an agent — deferred) |

The 5 frameworks share the LiteLLM gateway at
`litellm.cianfhoghlaim.ie:4000` as the single LLM proxy.

## The 5-layer observability stack

| Layer | Class | Wraps |
|:--|:--|:--|
| 1 | `LangfuseLogger` | `cianfhoghlaim.observability.langfuse_config.langfuse_trace` |
| 2 | `LogfireSpan` | `cianfhoghlaim.observability.logfire_config.logfire_span` |
| 3 | `MLflowTracker` | `cianfhoghlaim.observability.mlflow_tracker.log_run` |
| 4 | `RAGASScorer` | `cianfhoghlaim.observability.ragas_scorer.score` |
| 5 | `structlogLogger` | `logging.Logger(f"agent.{agent_name}")` |

The `attach_observability(wire)` function wires all 5 layers for a
given `WireAgent` instance. The `verify_5_layer_contract()`
function verifies the contract for all 12 agents.

## The 5-backend memory layer

| Backend | Cascade order | Port | Use case |
|:--|:--|--:|:--|
| Cognee | 1 | 8000 | Structured knowledge (entities + relationships) |
| Graphiti | 2 | 8001 | Temporal knowledge graph (bi-temporal) |
| LanceDB | 3 | 8002 | Vector RAG (HNSW) |
| FalkorDB | 4 | 8003 | Vector + graph hybrid (Redis-compatible) |
| Memgraph | 5 | 7687 | Production graph (Cypher + MAGE) |

The `get_default_memory_layer()` cached factory resolves to the
first available backend in cascade order. If all 5 are unreachable,
falls back to the in-memory `InMemoryMemoryLayer`.

## The 4 shared async dispatchers

| Dispatcher | Routes to | Returns |
|:--|:--|:--|
| `dispatch_study_plan(ctx)` | `curriculum_agent` + 1 NCCA subject agent | `{lectionary, progress}` |
| `dispatch_deep_research(query)` | `research_agent` / `education_research_agent` / `bunchloch_research_agent` | `{answer, citations, sources, agent}` |
| `dispatch_literature_review(query)` | `corpus_agent` + `research_agent` | `{corpus_hits, citations, years}` |
| `dispatch_summary(req)` | `corpus_agent` / `translation_agent` / `statistics_agent` | `{summary, tokens_used, agent}` |

Each dispatcher routes to the appropriate agent via the
`AGENT_REGISTRY` based on the `domain` field, and degrades
gracefully (returns `{}` or stub) when the target agent is unavailable.

## Quick routing — "I want to add X, where do I go?"

| If you want to... | Look at... |
|:--|:--|
| Add a new agent to the 12-agent fleet | `agents/wiring.py` (the wiring dataclass) + `agents/agent_registry.py` (the registry) + `agents/_workflow_handlers.py` (the dispatchers) |
| Modify the 5-layer observability stack | `agents/observability_hooks.py` |
| Modify the 5-backend memory layer | `agents/memory_layer.py` |
| Add a new exception type | `agents/exceptions.py` |
| Add a new Pydantic base model | `agents/pydantic_models.py` |
| Add a new async dispatcher | `agents/_workflow_handlers.py` |
| Modify the routing keyword map | `agents/routing_keywords.py` (the 12-bucket seed) |
| Modify the 8 NCCA subject specialists | `agents/tuatha/<slug>_agent.py` (back-compat via `agents/tuatha/wiring.py`) |
| Modify the 3 educational agents | `agents/meaisinfhoghlaim/educational/<slug>_agent.py` |
| Add a new OCR backend | `meaisinfhoghlaim/ocr/registry.py` (the 10-backends registry) |
| Add a new API route | `agents/api/routes/` (the 8 route categories) |
| Add a new tool module | `agents/tools/` (the 9 tool modules) |
| Deploy the agent fleet | `bonneagar/komodo/procedures/deploy-agent-fleet-{bunchloch,arm1-oci,arm1-oci-cci}.toml` (added by this change) |
| Reproduce the agent fleet from zero | `scripts/reproducers/agents-fleet-reproducer.sh` |

## openspec specs that govern agents

The 4 openspec specs for the agents quadrant are:

- `meaisinfhoghlaim-agent-frameworks` — the 12-agent fleet + the 8 NCCA subject specialists + the centralized wiring
- `agent-observability` — the 5-layer observability stack
- `agent-memory-systems` — the 5-backend memory layer
- `agent-platform-cluster` — the 8-stack agent cluster IaC

Plus the shared specs (4):

- `agentic-frontend-frameworks` — TanStack Start + CopilotKit + AG-UI
- `agent-registry` — the canonical agent registry pattern
- `agent-runtime-and-attribution` — agent runtime + attribution
- `dagger-pipelines` — polyglot CI/CD via Dagger

## Related skills (in `.agents/skills/`)

- `agent-fleet-orchestration/SKILL.md` — the 12-agent fleet wiring
- `agent-memory-systems/SKILL.md` — the 5 memory backends
- `agent-observability/SKILL.md` — the 5-layer observability stack
- `agent-platform-cluster/SKILL.md` — the 8-stack agent cluster
- `agent-registry/SKILL.md` — the canonical agent registry pattern
- `agent-runtime-and-attribution/SKILL.md` — agent runtime + attribution
- `agentic-frontend-frameworks/SKILL.md` — CopilotKit + AG-UI + TanStack Start
- `agno/SKILL.md` — Agno multi-agent orchestration
- `google-adk/SKILL.md` — Google Agent Development Kit
- `dignified-python/SKILL.md` — production Python standards

## Cross-references

- [`agents/STATUS.md`](STATUS.md) — current state of each agent
- [`agents/DEVELOPMENT.md`](DEVELOPMENT.md) — how to add a new agent
- [`agents/REPRODUCER.md`](REPRODUCER.md) — how to reproduce the agent fleet
- [`agents/api/AGENTS.md`](api/AGENTS.md) — Hono routes layer
- [`agents/tools/AGENTS.md`](tools/AGENTS.md) — tools layer
- [`agents/meaisinfhoghlaim/AGENTS.md`](meaisinfhoghlaim/AGENTS.md) — OCR/HTR/alignment sub-package
- [`agents/tuatha/AGENTS.md`](tuatha/AGENTS.md) — NCCA subject specialists
- [`openspec/AGENTS.md`](../openspec/AGENTS.md) — openspec workflow
- [`../AGENTS.md`](../AGENTS.md) — root agent instructions

## Feedback loop (project → openspec → skill)

Per the `skills-as-project-docs` openspec convention, this quadrant
participates in the formal feedback loop:

1. **When an openspec change is archived**, the canonical skill
   gets a "Post-archive update: YYYY-MM-DD-..." note in its
   "Pair this skill with" section.
2. **When this quadrant changes a BAML extraction / DLT source
   / Dagster asset**, the corresponding skill (`baml/SKILL.md`,
   `dlt/SKILL.md`, `dagster/SKILL.md`) gets a 1-line addition
   to its "When to use this skill" section.
3. **When this quadrant's `STATUS.md` / `REFACTORING.md` /
   README.md changes**, the
   `data-engineering-pipeline-documentation/SKILL.md` gets a
   link to the new content.

The lint script `mise run lint:skills` enforces the 4 metadata
rules (frontmatter, name match, description length, line count)
on every skill in `.agents/skills/`.

## LiteLlm migration (NEW 2026-08-15)

Historical drift (RESOLVED 2026-08-15): the 32 `LlmAgent(model=config.model_name)` constructors in `agents/adk/*` were hardcoding `"gemini-2.0-flash"`, BYPASSING the KCG `minimax` 7-tier LiteLLM fallback alias (the Agent 06 P0-#1 drift finding). All 32 sites now route through `MODEL_REGISTRY`.

The new canonical surface is **`agents/adk/litellm_agent.py`** (129 LOC), which exposes two helpers:

```python
from agents.adk.litellm_agent import make_litellm_agent, litellm_model

# Option A: Construct an LlmAgent with explicit LiteLlm routing
agent = make_litellm_agent(
    name="my_agent",
    description="Routes through the KCG minimax LiteLLM gateway.",
    model_alias="minimax",  # the canonical 7-tier fallback
    temperature=0.7,
    max_output_tokens=8192,
    tools=[my_tool],
    instruction="...",
)

# Option B: Use the model wrapper directly with the canonical LlmAgent
from google.adk.agents import LlmAgent
agent = LlmAgent(
    name="my_agent",
    model=litellm_model("minimax"),
    description="...",
)
```

The two helpers read the LiteLLM gateway URL from `LITELLM_API_BASE` (defaults to `https://litellm.cianfhoghlaim.ie`) and the API key from `LITELLM_API_KEY` (injected by the Locket sidecar at runtime).

**To add a new agent**:

1. Add a new entry to `agents/agent_registry.py:AGENT_REGISTRY` with `framework`, `module_path`, `display_name`, `baml_prefix`, `langfuse_trace_name`, `cognee_dataset`, `letta_agent_id`, `litellm_routing_key`.
2. Create the agent file at `agents/adk/<name>_agent.py` with:
   ```python
   from .litellm_agent import make_litellm_agent
   my_agent = make_litellm_agent(
       name="my_agent",
       description="...",
       model_alias="curriculum",  # the canonical LiteLLM routing key
       tools=[...],
       instruction="...",
   )
   ```
3. The 12-agent fleet is auto-discovered via `agents/agent_registry.py:AGENT_REGISTRY` — no manual wiring needed.

**For LiteLlm alias resolution**: if you need to override the model, use the `model_alias` parameter — never hardcode a model string. The available aliases are defined in `bonneagar/stacks/litellm/config/config.yaml` and regenerated from `MODEL_REGISTRY` on every `mise run cic:meaisin:litellm-regenerate`.

## Model registry for agents (NEW 2026-08-15)

Every agent field that touches a model (the `model_name`, `irish_model`, `embedding_model`, `translation_models` dict on `AgentConfig`) now uses a lazy `default_factory` that resolves through `MODEL_REGISTRY`:

```python
from meaisinfhoghlaim.models import model_for

config = AgentConfig()  # all model fields resolve via MODEL_REGISTRY
config.model_name       # → "minimax-m3"  (was hardcoded "gemini-2.0-flash")
config.irish_model       # → "uccix-mistral-24b"
config.embedding_model   # → "BAAI/bge-m3"
```

The legacy `agents/adk/tuatha_config.py:AgentConfig` is deprecated (marked back-compat shim) — its `orchestrator_model` + `worker_model` + `fast_model` + `irish_model` + `multilingual_model` all resolve through `MODEL_REGISTRY` too.

---

**Last updated**: 2026-08-15 (added the LiteLlm migration section + the Model registry for agents section).
**Owner**: Build agent.