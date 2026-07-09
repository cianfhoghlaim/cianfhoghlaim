# Meaisínfhoghlaim Agent Frameworks Capability

## Purpose

`meaisinfhoghlaim-agent-frameworks` is a capability of the Cianfhoghlaim
platform. The corresponding source code lives at
`cianfhoghlaim/agents/` (12 specialised agents) and
`cianfhoghlaim/agents/{adk,agno}/` (the application-layer CopilotKit / AG-UI
facades). See `docs/00_index.md` for the quadrant map and
`docs/00-core/CLAUDE.md` for the project identity.

This spec was created by the `openspec-consolidation-and-readme-refresh`
change and supersedes the old `agent-frameworks` spec (which described
the Agno + Google ADK + LiteLLM framework, 253 lines).

## Background

The meaisinfhoghlaim agent framework is the model layer for the
Cianfhoghlaim platform. The 12 specialised agents in
`cianfhoghlaim/agents/` cover the full Irish + UK + pan-Celtic
education surface:

- **Root Agent** — orchestrator that routes to the 6+ specialised agents
  via LiteLLM with fallback chains
- **Curriculum Agent** — Irish + UK curriculum queries via LanceDB
  vector search + DuckDB
- **Translation Agent** — Irish ↔ English translation via OPUS-MT,
  M2M100, NLLB-200
- **Corpus Agent** — Celtic language corpus search via Duchas, Canuint,
  Terma, GAOIS
- **Geospatial Agent** — school boundaries + maps via DuckDB Spatial
- **Statistics Agent** — cross-nation education stats via
  NationComparison
- **Research Agent** — multi-source web research via Google ADK
  SequentialAgent
- **Curriculum Comparison Agent** — compares curricula across nations
  (Ireland, NI, England, Scotland, Wales, Crown Dependencies)
- **Bunchloch Research Agent** — research agent specialised for the
  bunchloch MacBook M4 environment
- **AG-UI Curriculum Agent** — AG-UI streaming agent for the
  oideachais web app
- **Corpus Agent** (variant) — corpus search with custom Irish
  language resources
- **Site Analysis Agent** — firecrawl + browserbase MCP-driven site
  audits

The 2 application-layer facades (`cianfhoghlaim/agents/{adk,agno}/`) wrap
these specialised agents for the front-end CopilotKit / AG-UI.
## Requirements
### Requirement: 12 specialised agents

The system SHALL provide 12 specialised agents in
`cianfhoghlaim/agents/` covering the Irish + UK + pan-Celtic
education surface.

#### Scenario: Root agent routes to specialists

- **GIVEN** a user query "what is the Irish curriculum for ga101?"
- **WHEN** the query is dispatched to the Root Agent
- **THEN** the Root Agent routes to the Curriculum Agent
- **AND** the Curriculum Agent returns the ga101 Primary Irish
  curriculum data

### Requirement: Agno + Google ADK + LiteLLM framework

The system SHALL use Agno (>=2.0.0) + Google ADK (>=1.0.0) + LiteLLM
as the agent framework.

#### Scenario: LiteLLM routing

- **GIVEN** the Root Agent is configured with `model="kimi-k2.6"` via
  LiteLLM
- **WHEN** the agent makes an LLM call
- **THEN** LiteLLM routes the call to the kimi-k2.6 model via the
  OpenCode Go API (`OPENAI_BASE_URL`)

#### Scenario: Fallback chain

- **GIVEN** the primary model (`kimi-k2.6`) is unavailable
- **WHEN** the agent makes an LLM call
- **THEN** LiteLLM falls back to the next model in the chain
  (`glm-5.1`, then `minimax-m2.5`, then `mimo-v2.5`, then
  `deepseek-v4-flash`)

### Requirement: Knowledge graph integration

The system SHALL integrate the agents with the Cognee + Graphiti +
LanceDB knowledge graph stack.

#### Scenario: Cognee knowledge base

- **GIVEN** a Curriculum Agent configured with a Cognee knowledge
  base
- **WHEN** a curriculum question is asked
- **THEN** the agent retrieves relevant context from Cognee via
  `cognee.search()` and incorporates it into the response

### Requirement: Observability stack

The system SHALL trace every agent call with Langfuse + MLflow + RAGAS
+ Logfire + Datadog (see `agent-observability` spec).

#### Scenario: Agent call traced

- **GIVEN** a Curriculum Agent is invoked
- **WHEN** the agent generates a response
- **THEN** Langfuse captures the input, output, metadata, and session
  information
- **AND** MLflow logs the agent run as an experiment
- **AND** RAGAS evaluates the response (faithfulness, answer relevance,
  context precision, context recall)

### Requirement: Application-layer facades

The system SHALL provide 2 application-layer agent facades in
`cianfhoghlaim/agents/{adk,agno}/` for the oideachais web app.

#### Scenario: CopilotKit AG-UI streaming

- **GIVEN** a user issues a query in the oideachais web app CopilotKit
  chat
- **WHEN** the facade routes to the Curriculum Agent
- **THEN** the response is streamed to the client via AG-UI

### Requirement: ADK package init SHALL resolve cleanly

The `from cianfhoghlaim.agents.adk import <name>` path SHALL resolve all `LlmAgent` instances declared in `__all__` without raising `ImportError` or `pydantic_core.ValidationError`.

#### Scenario: research_agent imports cleanly under google-genai v2.13+

- **WHEN** the user runs `from cianfhoghlaim.agents.adk.research_agent import ResearchFeedback, SearchQuery`
- **AND** the installed `google-genai` version is `>=2.13`
- **THEN** the import SHALL NOT raise `pydantic_core._pydantic_core.ValidationError` on `ThinkingConfig`
- **AND** the import SHALL NOT raise `ImportError` for any name declared in `research_agent.__all__`

#### Scenario: package init resolves all exports

- **WHEN** the user runs `from cianfhoghlaim.agents.adk import dev_env_demo_agent`
- **THEN** `dev_env_demo_agent` SHALL be a `google.adk.agents.LlmAgent` instance
- **AND** it SHALL have all 8 dev-env tools wired
- **AND** it SHALL NOT have raised any error during import

#### Scenario: stale name imports are removed

- **WHEN** the user inspects `cianfhoghlaim/agents/adk/__init__.py:118-127`
- **THEN** the imports from `research_agent` SHALL only contain names declared in `research_agent.__all__`
- **AND** stale names (`ResearchReport`, `compose_report`, `conduct_research`, `evaluate_research`, `execute_research`, `generate_search_queries`) SHALL be absent

### Requirement: 8 NCCA subject agent definitions wired to Layer 5

The system SHALL mount each of the 8 NCCA subject agents
(`gael_agent`, `math_agent`, `appm_agent`, `chem_agent`,
`comp_agent`, `engl_agent`, `geog_agent`, `hist_agent`) at
`cianfhoghlaim/orchestration/defs/5_agent_ops/adk/<slug>_agent/defs.yaml`
under the 5-layer KCG Components pattern. Each mount consumes
the `CelticAgentOpsComponent` and emits 5 Dagster assets per agent:
`agent_health_<slug>_agent`, `agent_routing_<slug>_agent`,
`agent_memory_<slug>_agent`, `agent_event_<slug>_agent`,
`agent_trace_<slug>_agent`.

The `ROUTING_KEYWORDS` map at
`cianfhoghlaim/agents/routing_keywords.py` SHALL expose a seed
bucket for each of the 8 subjects with at least the NCCA canonical
name (`gaeilge`, `mathematics`, `applied_mathematics`,
`chemistry`, `computer_science`, `english`, `geography`,
`history`); the full bucket is appended by
`CelticAgentOpsComponent._append_routing_keywords()` at scaffold
time.

#### Scenario: math_agent mounts on L5 + routes by keyword

- **GIVEN** `defs/5_agent_ops/adk/math_agent/defs.yaml`
- **WHEN** `dg list defs | grep math_agent` runs
- **THEN** the 5 math_agent assets are visible in the
  output
- **AND** `ROUTING_KEYWORDS["math_agent"]` contains
  `"mathematics"`

### Requirement: OCR adapter wiring to the standard eval harness

The system SHALL wire the 4 `OCRAdapter` concrete implementations
at `cianfhoghlaim/meaisinfhoghlaim/backends/adapters.py`
(`PaddleOCRAdapter`, `DoclingAdapter`, `DotsOCRAdapter`,
`UnstractAdapter`) to `meaisinfhoghlaim/evaluation/compare.py`
via the `_run_classical_eval()` helper. The
`_CLASSICAL_ADAPTER_FOR_STACK` mapping MUST resolve every
`ClassicalOCRStack.stack_name` to one of the 4 adapters.

`compare_ocr_models()` SHALL remain the canonical entry point
for end-to-end multi-model OCR comparisons.

#### Scenario: docling stack is wired through DoclingAdapter

- **GIVEN** a `ClassicalOCRStack(stack_name="docling", ...)`
- **WHEN** `_run_classical_eval(stack, corpus, document)` runs
- **THEN** `OCRAdapterRegistry.get("docling")` returns a
  `DoclingAdapter`
- **AND** `adapter.process_pdf(document)` is invoked
- **AND** the resulting `EvalSample` reports the adapter name
  in `model_id`

#### Scenario: adapter error produces well-formed EvalSample

- **WHEN** the adapter raises (Docker stack unreachable)
- **THEN** `EvalSample` is still emitted with
  `notes="adapter-error: <message>"`
- **AND** `cer=1.0`, `wer=1.0`, `fada_consistent=False`

### Requirement: Federated OCR Dagster asset materialises

The federated OCR subsystem SHALL be moved from
`meaisinfhoghlaim/process/irish_ocr_federated.py` (an orphaned
618-LOC file post-v4) to `meaisinfhoghlaim/federated/`, and
materialised as a Dagster asset `irish_ocr_federated_smoke` on a
30-minute cron cycle via the `CelticFederatedOcrComponent`. The
asset SHALL be a graceful smoke run (not a long-running server
thread) and SHALL surface any exception in the
`metadata.error` field rather than crashing the Dagster run.

#### Scenario: Asset materialises every 30 minutes

- **WHEN** the cron `*/30 * * * *` triggers
- **THEN** Dagster materialises `irish_ocr_federated_smoke`
- **AND** `metadata.status` is either `"ok"` or `"error"`
- **AND** `metadata.result` is JSON-encoded with the
  `run_federated_training(...)` return value or the exception
  message

### Requirement: MemoryBackend Protocol contract

Every memory backend (Graphiti, FalkorDB, InMemoryLanceDB) SHALL
implement the `MemoryBackend` protocol at
`cianfhoghlaim/storage/memf.py`. The protocol surface SHALL be
exactly:

- `async def add_episode(episode: Episode) -> str`
- `async def search(query: str, *, k: int = 10, **filters) -> list[SearchResult]`
- `async def get_node(node_id: str) -> Node | None`
- `async def close() -> None`
- `kind: ClassVar[str]`

Agent code SHALL depend on the protocol, not on any concrete
class. `get_default_backend()` SHALL be the canonical factory.

#### Scenario: get_default_backend() returns InMemoryLanceDBBackend when both backends are down

- **GIVEN** Graphiti is unreachable (TCP probe fails)
- **AND** FalkorDB is unreachable (TCP probe fails)
- **WHEN** `await get_default_backend()` is called
- **THEN** the result is an `InMemoryLanceDBBackend`
- **AND** `backend.kind == "in_memory_lancedb"`
- **AND** `isinstance(backend, MemoryBackend)` is True

#### Scenario: get_default_backend() probes fall through to FalkorDB on Graphiti 5xx

- **GIVEN** Graphiti is marked `DOWN_5XX`
- **AND** FalkorDB is reachable
- **WHEN** `await get_default_backend()` is called
- **THEN** the result is a `FalkorDBBackend`
- **AND** subsequent calls within the 30s cache TTL return the
  same instance

## Cross-references

- [`cianfhoghlaim/agents/`](../../cianfhoghlaim/agents/) (the 12 specialised agents)
- [`cianfhoghlaim/agents/adk/`](../../cianfhoghlaim/agents/adk/) (the Google ADK facade)
- [`cianfhoghlaim/agents/agno/`](../../cianfhoghlaim/agents/agno/) (the Agno facade)
- [`.agents/skills/agno/SKILL.md`](../../.agents/skills/agno/SKILL.md)
- [`.agents/skills/google-adk/SKILL.md`](../../.agents/skills/google-adk/SKILL.md)
- [`.agents/skills/ai-engineer/SKILL.md`](../../.agents/skills/ai-engineer/SKILL.md)
- [`.agents/skills/celtic-language-ai/SKILL.md`](../../.agents/skills/celtic-language-ai/SKILL.md)
- [`openspec/specs/meaisinfhoghlaim-platform/spec.md`](meaisinfhoghlaim-platform/spec.md) (the quadrant overview)
- [`openspec/specs/agent-observability/spec.md`](../agent-observability/spec.md) (the observability stack)
- [`openspec/specs/agent-memory-systems/spec.md`](../agent-memory-systems/spec.md) (the memory systems)
