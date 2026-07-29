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
under the 5-layer KCG Components pattern.

Per the Feat C addendum (2026-07-10), each mount SHALL also
expose two additional top-level attribute blocks in addition to
the 5 Dagster assets: a `cognify` block configuring the per-
subject Cognee dataset (`cianfhoghlaim_lc_<subject>`) and a
`langfuse_callbacks` block configuring the canonical trace name
(`agent.<module_slug>.<verb>`). Both blocks are populated by the
L5 Component at scaffold time — operator-managed defs.yaml files
MUST keep both blocks in sync with the canonical naming rule.

The `ROUTING_KEYWORDS` map at
`cianfhoghlaim/agents/routing_keywords.py` SHALL expose a seed
bucket for each of the 8 subjects with at least the NCCA canonical
name (`gaeilge`, `mathematics`, `applied_mathematics`,
`chemistry`, `computer_science`, `english`, `geography`,
`history`); the full bucket is appended by
`CelticAgentOpsComponent._append_routing_keywords()` at scaffold
time.

#### Scenario: math_agent mounts on L5 + routes by keyword + has cognify + langfuse blocks

- **GIVEN** `defs/5_agent_ops/adk/math_agent/defs.yaml`
- **WHEN** `dg list defs | grep math_agent` runs
- **THEN** the 5 math_agent assets are visible in the
  output
- **AND** `ROUTING_KEYWORDS["math_agent"]` contains
  `"mathematics"`
- **AND** `defs.yaml.attributes.cognify.dataset` equals
  `"cianfhoghlaim_lc_mathematics"`
- **AND** `defs.yaml.attributes.langfuse_callbacks.trace_name`
  equals `"agent.math.explain"`

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

### Requirement: Letta memory wired at agent construction time

The system SHALL bind the ``LettaMemoryService`` (from
`cianfhoghlaim/storage/letta_memory.py`) at module-construction
time on every one of the 8 NCCA subject agents. The wire-up
SHALL be exposed as the module-level ``<slug>_agent_wire``
attribute holding a ``WireSubjectAgent`` instance with the
``memory_backend_kind`` field set to either
``"protocol"`` (when ``get_default_backend()`` was reachable) or
``None`` (when the protocol could not be imported).

The wire-up MUST NOT pull in `google.genai`, `litellm`, or
`baml` at module-import time (the underlying imports are lazy).

#### Scenario: math_agent_wire is populated at import time

- **GIVEN** `python3 -c "from cianfhoghlaim.agents.tuatha import math_agent"`
- **WHEN** the import resolves
- **THEN** `math_agent.math_agent_wire.baml_prefix == "Math"`
- **AND** `math_agent.math_agent_wire.subject.cognee_dataset == "cianfhoghlaim_lc_mathematics"`
- **AND** no `ImportError` is raised during construction

### Requirement: Langfuse callbacks wired at agent construction time

The system SHALL bind the Langfuse tracer (from
`cianfhoghlaim/observability/langfuse_config.py`) at module-
construction time on every one of the 8 NCCA subject agents, via
the module-level ``<slug>_agent_open_trace`` function. The function
opens a trace with the canonical name
``agent.<module_slug>.<verb>`` (default verb = ``"explain"``).

When the ``langfuse`` package is not installed the function MUST
return a no-op context manager that yields ``None`` — it MUST NOT
raise.

#### Scenario: gael_agent_open_trace uses the canonical trace name

- **GIVEN** `from cianfhoghlaim.agents.tuatha import gael_agent`
- **WHEN** `gael_agent.gael_agent_open_trace(verb="explain")`
  is entered
- **THEN** the trace name (in normal Langfuse environments)
  equals `"agent.gael.explain"`
- **AND** when Langfuse is unavailable the context exits cleanly
  and yields `None`

### Requirement: Cognify emit step pushes to cianfhoghlaim_lc_<subject>

The system SHALL push every LLM response of the 8 NCCA subject
agents into the canonical Cognee dataset
``cianfhoghlaim_lc_<subject>``, where ``<subject>`` is the
canonical NCCA subject slug (not the file-name slug). The emit
hook is exposed as the module-level
``<slug>_agent_emit_to_cognee(response, query)`` async function
and returns the top-5 closest historical responses for the
given query.

When the ``cognee`` package is not installed the function MUST
return ``[]`` without raising.

The 5 subjects whose Cognee datasets differ from the
historical `cianfhoghlaim_<subject>` naming convention are
now consistent with `agent-memory-systems`.

#### Scenario: chem_agent emits to cianfhoghlaim_lc_chemistry

- **GIVEN** `chem_agent.chem_agent_open_trace` has been called for a query
- **WHEN** `chem_agent.chem_agent_emit_to_cognee(<response>, <query>)` runs
- **AND** the `cognee` package is installed
- **THEN** the response is added to the `cianfhoghlaim_lc_chemistry` dataset
- **AND** the returned hits come from the same dataset with
  `top_k = 5`

#### Scenario: emit_to_cognee is graceful on missing cognee

- **GIVEN** the `cognee` package is not installed
- **WHEN** `chem_agent.chem_agent_emit_to_cognee("resp", "q")` runs
- **THEN** the function returns `[]`
- **AND** no exception is raised

### Requirement: StorageBackend Protocol enforced on subject agents

The system SHALL enforce the `MemoryBackend` Protocol contract on
the 8 NCCA subject agents: no subject agent module MAY import
`cianfhoghlaim.storage.graphiti_client` or
`cianfhoghlaim.storage.falkordb_client` directly. Every subject
agent MUST depend on the abstraction via
`from cianfhoghlaim.storage.memf import get_default_backend`.

#### Scenario: no direct graphiti_client / falkordb_client imports

- **GIVEN** any of the 8 `<slug>_agent.py` modules at
  `cianfhoghlaim/agents/tuatha/`
- **WHEN** `grep -n "graphiti_client\|falkordb_client" <agent>.py`
  runs
- **THEN** the output SHALL be empty (0 matches)
- **AND** the subject agents import
  `from cianfhoghlaim.storage.memf import get_default_backend` when
  they need a concrete backend

### Requirement: 8 per-subject ADK specialists resolve to `agents/tuatha/<slug>_agent.py` and dispatch via `select_optimal_for_m4_max`

The system SHALL wire the 8 NCCA subject specialists in the ADK root
agent (`agents/adk/root_agent.py`) to the canonical
per-subject modules at `agents/tuatha/<slug>_agent.py`,
where `<slug>` is one of
`math`, `appm`, `chem`, `geog`, `hist`, `engl`, `gael`, `comp`.

The canonical module paths SHALL be exposed as
`cianfhoghlaim.agents.tuatha.<slug>_agent` (Python module imports)
— NOT the legacy phantom path
`cianfhoghlaim.agents.meaisinfhoghlaim.educational.<slug>_agent`,
which does not exist on disk.

The canonical M4-Max dispatch helper SHALL be
`select_optimal_for_m4_max()` from
`cianfhoghlaim.meaisinfhoghlaim.models.registry`. The legacy
name `get_default_for_m4_max()` is preserved as a deprecated
back-compat alias that emits `DeprecationWarning` and delegates to
`select_optimal_for_m4_max()`.

#### Scenario: root_agent dispatches a Mathematics query to the tuatha math_agent

- **GIVEN** the ADK `RootAgent` is constructed
- **AND** `RootAgent._get_agent(AgentDomain.MATH)` is called
- **WHEN** the per-subject wrapper's `_ensure_loaded()` runs
- **THEN** it imports `cianfhoghlaim.agents.tuatha.math_agent`
- **AND** the module imports resolve without `ModuleNotFoundError`
- **AND** the attribute lookup for the math specialist agent succeeds

#### Scenario: the 8 canonical module paths are all importable

- **WHEN** `python -c "from importlib import import_module; [import_module(f'cianfhoghlaim.agents.tuatha.{s}_agent') for s in ['math', 'appm', 'chem', 'geog', 'hist', 'engl', 'gael', 'comp']]"`
- **THEN** the command exits 0 with no `ModuleNotFoundError`
- **AND** all 8 modules resolve to physical files under
  `agents/tuatha/`

#### Scenario: select_optimal_for_m4_max is the canonical M4-Max helper

- **WHEN** `from cianfhoghlaim.meaisinfhoghlaim.models.registry import select_optimal_for_m4_max`
- **THEN** the import succeeds
- **AND** `select_optimal_for_m4_max()` returns `"gemma-4-26B-A4B"`

#### Scenario: get_default_for_m4_max back-compat alias emits DeprecationWarning

- **WHEN** `from cianfhoghlaim.meaisinfhoghlaim.models.registry import get_default_for_m4_max`
- **AND** `get_default_for_m4_max()` is called with
  `warnings.simplefilter('error', DeprecationWarning)` active
- **THEN** a `DeprecationWarning` is raised
- **AND** the warning message references `select_optimal_for_m4_max` as the replacement

#### Scenario: no phantom `meaisinfhoghlaim.educational` paths remain in `root_agent.py`

- **WHEN** `grep -nE "meaisinfhoghlaim\.educational" agents/adk/root_agent.py`
- **THEN** the output SHALL be empty (0 matches)

### Requirement: 12-agent fleet wiring via `agents/wiring.py` + `agent_registry.py`

The system SHALL provide a centralized wiring layer for the 12
main agents (root_agent + 8 ADK + 3 Agno) at
`agents/wiring.py` (the `AgentFleetWiring` dataclass) and
`agents/agent_registry.py` (the `AGENT_REGISTRY` dict).

The `AgentFleetWiring` dataclass SHALL expose the following fields
per agent: `agent_name`, `module_path`, `framework`,
`baml_prefix`, `langfuse_trace_name`, `cognee_dataset`,
`letta_agent_id`, `litellm_routing_key`.

The `AGENT_REGISTRY` dict SHALL contain exactly 12 entries
mapping `agent_name` → `AgentFleetWiring` instance, and the
8 NCCA subject agents (gael, math, appm, chem, comp, engl,
geog, hist) SHALL be re-exported through the same dispatch
surface (back-compat alias via `agents/tuatha/wiring.py`).

#### Scenario: `AGENT_REGISTRY` has exactly 12 entries

- **GIVEN** the 12 agents are wired via `agents/wiring.py`
- **WHEN** `python -c "from cianfhoghlaim.agents import AGENT_REGISTRY; print(len(AGENT_REGISTRY))"`
- **THEN** the output SHALL be 12
- **AND** the keys SHALL be: `root_agent`, `curriculum_agent`,
  `translation_agent`, `corpus_agent`, `research_agent`,
  `education_research_agent`, `bunchloch_research_agent`,
  `geospatial_agent`, `statistics_agent`,
  `curriculum_comparison_agent`, `agui_curriculum_agent`,
  `mcp_curriculum_agent`

#### Scenario: 8 NCCA subject agents are re-exported through the same dispatch surface

- **GIVEN** the 8 NCCA subject agents are wired via `agents/tuatha/wiring.py`
- **WHEN** `python -c "from cianfhoghlaim.agents import AGENT_REGISTRY; ncca = [k for k in AGENT_REGISTRY if k in ['gael_agent', 'math_agent', 'appm_agent', 'chem_agent', 'comp_agent', 'engl_agent', 'geog_agent', 'hist_agent']]; print(len(ncca))"`
- **THEN** the output SHALL be 8
- **AND** the 8 NCCA agents SHALL be reachable via the same
  `AGENT_REGISTRY` dispatch surface (back-compat alias)

#### Scenario: `AgentFleetWiring` exposes all 8 fields per agent

- **GIVEN** an `AgentFleetWiring` instance for `curriculum_agent`
- **WHEN** `wiring = AGENT_REGISTRY["curriculum_agent"]`
- **THEN** the following attributes SHALL be non-None:
  - `agent_name == "curriculum_agent"`
  - `module_path` is a valid Python module path
  - `framework` is one of `{"Custom", "ADK", "Agno", "Pipecat", "CopilotKit"}`
  - `baml_prefix` is a non-empty string
  - `langfuse_trace_name` matches `^agent\.[a-z_]+\.[a-z_]+$`
  - `cognee_dataset` matches `^oideachais_lc_[a-z_]+$`
  - `letta_agent_id` is a non-empty string
  - `litellm_routing_key` is a non-empty string

### Requirement: 4 shared async dispatchers via `agents/_workflow_handlers.py`

The system SHALL provide 4 shared async dispatcher functions in
`agents/_workflow_handlers.py`:

- `dispatch_study_plan(ctx: StudyPlanContext) -> dict`
- `dispatch_deep_research(query: ResearchQuery) -> dict`
- `dispatch_literature_review(query: LiteratureReviewQuery) -> dict`
- `dispatch_summary(content: str, max_tokens: int) -> dict`

Each dispatcher SHALL route to the appropriate agent via the
`AGENT_REGISTRY` based on the `domain` field of the input
context, and SHALL gracefully degrade (returning `{}` or a
stub response) when the target agent is unavailable.

#### Scenario: `dispatch_study_plan` routes to the correct agent

- **GIVEN** a `StudyPlanContext` with `domain="curriculum"` and
  `subject="gaeilge"`
- **WHEN** `result = await dispatch_study_plan(ctx)`
- **THEN** the result SHALL contain a `lectionary` key
  (the per-subject study plan)
- **AND** the result SHALL contain a `progress` key
  (the per-student progress dict)

#### Scenario: `dispatch_deep_research` degrades gracefully when the agent is unavailable

- **GIVEN** the `research_agent` module is not importable
  (e.g. `agents/agno/research_agent.py` is missing)
- **WHEN** `result = await dispatch_deep_research(query)`
- **THEN** the result SHALL be `{}` (empty dict)
- **AND** no `ModuleNotFoundError` SHALL propagate

#### Scenario: 4 dispatchers AST-parse cleanly

- **GIVEN** `agents/_workflow_handlers.py`
- **WHEN** `python3 -c "import ast; ast.parse(open('agents/_workflow_handlers.py').read()); print('OK')"`
- **THEN** the command exits 0
- **AND** the AST SHALL contain exactly 4 `async def` definitions

### Requirement: Graceful degradation on missing dependency

The system SHALL NOT propagate `ImportError` or `ModuleNotFoundError`
when any of the 12 agents are loaded with missing dependencies
(Langfuse, Logfire, MLflow, Cognee, Graphiti, LanceDB, FalkorDB,
Memgraph, Letta, Pipecat, CopilotKit).

Each agent SHALL attach a `wire` field that reports which
dependencies were successfully wired against the current
Python environment. Missing-dependency warnings SHALL be
logged at `WARNING` level (not `ERROR`).

#### Scenario: 12 agents load with `wire` field populated

- **GIVEN** the 12 agents are wired via `agents/wiring.py`
- **WHEN** `python -c "from cianfhoghlaim.agents import AGENT_REGISTRY; [print(k, v.langfuse_wired, v.cognee_wired, v.memory_backend_kind) for k, v in AGENT_REGISTRY.items()]"`
- **THEN** the command exits 0
- **AND** each agent SHALL have a `wire` field with
  `langfuse_wired`, `cognee_wired`, `memory_backend_kind` set
- **AND** no `ImportError` or `ModuleNotFoundError` SHALL be raised

#### Scenario: missing-dep warnings are logged at WARNING level

- **GIVEN** the `langfuse` package is not installed
- **WHEN** `agents/wiring.py` initialises the 12 agents
- **THEN** each agent whose Langfuse probe fails SHALL log
  a `WARNING` message (not `ERROR`)
- **AND** the agent's `wire.langfuse_wired` SHALL be `False`

#### Scenario: 0 backend imports from agent modules

- **GIVEN** the 12 agents are wired via `agents/wiring.py`
- **WHEN** `grep -n "langfuse_client\|cognee_client\|letta_client\|graphiti_client\|falkordb_client\|memgraph_client" agents/{adk,agno}/<slug>_agent.py`
- **THEN** the output SHALL be empty (0 matches per agent)
- **AND** each agent module SHALL import at least one symbol
  from `agents/wiring.py` (the canonical wire-up module)

### Requirement: Per-subject agent workflows shipped for the 6 BIEP v1 LC subjects

The system SHALL ship 3 user-facing per-subject workflow handlers
for each of the 6 BIEP v1 Leaving Certificate subjects
(**Mathematics, Chemistry, Geography, Gaeilge, English, Computer
Science**) — 18 handlers in total — wired through the existing
`WireSubjectAgent` dataclass in
`agents/tuatha/wiring.py`.

The 3 per-subject handlers are:

1. **`make_study_plan_handler(ctx: StudyPlanContext) -> dict`** —
   produces a per-subject lectionary (a per-week list of NCCA LO +
   per-LO `Generate<Subject>FormativeItem` BAML call) + a
   per-student progress summary that downstream marimo notebooks +
   RAGAS evaluations can read.
2. **`discuss_exam_paper_handler(exam_paper_id: str) -> dict`** —
   loads the past-paper items + matching `*_marking_scheme_lookup`
   entries by `lo_code` + emits a per-LO discussion crosswalk + a
   flat `analysis` summary.
3. **`explain_marking_scheme_handler(marking_scheme_id: str) ->
   dict`** — loads the NCCA marking-scheme text + the related past-
   paper items + generates an exemplar practice item via
   `*_formative_item_generate_tool` + optionally scores a sample
   attempt via `*_response_score_tool`.

The 3 handlers consume the existing per-subject tool callables
(`*_syllabus_lookup_tool`, `*_past_paper_lookup_tool`,
`*_marking_scheme_lookup_tool`, `*_formative_item_generate_tool`,
`*_response_score_tool`) that the existing 8 NCCA subject agents
already export (they were wired in T4 + Feat C).

The 3 handlers SHALL be exposed on the existing
`<slug>_agent_wire` (`WireSubjectAgent`) dataclass — via 3 new
`Callable | None` fields (`study_plan_handler`,
`exam_paper_handler`, `marking_scheme_handler`) added with default
`None`. The fields are filled at module-load time via
`dataclasses.replace(wire_subject_agent(_X_WIRING), ...)` calls in
each of the 6 per-subject agent modules.

The shared async dispatcher functions live in
`agents/tuatha/_workflow_handlers.py` so the 3
handler bodies are not duplicated across the 6 per-subject modules
(`build_subject_workflow_handlers(wiring, syllabus, past_paper,
marking_scheme, formative_item, response_score)` returns a
`SubjectWorkflowHandlers` triple; `attach_subject_workflow_handlers
(wire, handlers)` returns a new `WireSubjectAgent` with the 3
callables attached).

The 2 out-of-scope NCCA subjects (Applied Mathematics + History)
remain unwired for these handlers (they are deliberately excluded
per the user's locked plan — the BIEP flagship is the
6-subject LC pipeline, not the 8-subject NCCA surface). When a
future change wants to extend the per-subject workflow surface
to those subjects it SHALL add the analogous `make_*_handler` +
`discuss_*_handler` + `explain_*_handler` functions to the
respective `appm_agent.py` / `hist_agent.py` modules using the
same `_workflow_handlers` factory.

#### Scenario: `WireSubjectAgent` exposes the 3 new handler fields

- **GIVEN** the
      `agents/tuatha/wiring.py` module
- **WHEN** an agent runs
      `python3 -c "from cianfhoghlaim.agents.tuatha.wiring import WireSubjectAgent; print(sorted(WireSubjectAgent.__dataclass_fields__))"`
- **THEN** the printed field names SHALL contain exactly these 3 new
      ones (in any order):
      - `study_plan_handler`
      - `exam_paper_handler`
      - `marking_scheme_handler`
- **AND** the 3 new fields SHALL default to `None` (back-compat
      with the T4 smoke tests that construct `WireSubjectAgent`
      without handlers).

#### Scenario: All 6 in-scope per-subject agents attach the 3 handlers

- **GIVEN** any of the 6 in-scope subjects
      (`mathematics`, `chemistry`, `geography`, `gaeilge`,
      `english`, `computer_science`)
- **WHEN** an agent imports the corresponding
      `*_agent.py` module
- **THEN** the `<slug>_agent_wire` instance SHALL expose
      non-`None` `study_plan_handler` + `exam_paper_handler` +
      `marking_scheme_handler` callables.

#### Scenario: `make_study_plan_handler` returns a per-subject lectionary

- **GIVEN** `from cianfhoghlaim.agents.tuatha import math_agent`
- **WHEN** an agent invokes
      `await math_agent.make_study_plan_handler(StudyPlanContext(level="lc_hl", topic="differentiation", weeks=3))`
- **THEN** the returned dict SHALL contain:
      - `subject == "mathematics"`
      - `level == "lc_hl"`
      - `weeks == 3`
      - `lectionary` list of length 3, each entry with the keys
        `week`, `lo_code`, `topic`, `difficulty`,
        `formative_item`
      - `progress` dict with `agent == "agent.math.explain"` + the
        Langfuse trace-name convention.

#### Scenario: `discuss_exam_paper_handler` returns a per-subject discussion

- **GIVEN** `from cianfhoghlaim.agents.tuatha import chem_agent`
- **WHEN** an agent invokes
      `await chem_agent.discuss_exam_paper_handler("chemistry.paper2")`
- **THEN** the returned dict SHALL contain:
      - `subject == "chemistry"`
      - `exam_paper_id == "chemistry.paper2"`
      - `items` list (possibly empty if BAML client not
        generated in the dev env)
      - `marking_schemes` list (per matched `lo_code`)
      - `analysis.items_discussed` + `analysis.marking_schemes_crosswalked`
        numeric fields.
- **AND** the handler SHALL NOT raise when BAML is unavailable —
      it returns the dict with empty `items` + a graceful
      `analysis` summary.

#### Scenario: `explain_marking_scheme_handler` returns a per-subject explanation

- **GIVEN** `from cianfhoghlaim.agents.tuatha import gael_agent`
- **WHEN** an agent invokes
      `await gael_agent.explain_marking_scheme_handler("LC-GAEL-LO-3.1")`
- **THEN** the returned dict SHALL contain:
      - `subject == "gaeilge"`
      - `marking_scheme_id == "LC-GAEL-LO-3.1"`
      - `scheme` (the marking-scheme lookup result — may have
        an `error` key if LO not found in the local DB)
      - `rationale.explanation_en` (the canonical Irish-med
        rationale template)
      - `rationale.explanation_ga` (the secondary Irish-language
        rationale)
      - `exemplar_formative_item` (the BAML-generated practice
        item — may have an `error` key if BAML client not
        generated)
      - `related_past_paper_items` (truncated to 5).

#### Scenario: The 18 handlers consume `Generate<Subject>FormativeItem`

- **GIVEN** any of the 6 per-subject BAML files at
      `baml/education/subjects/qpack_<subject>.baml`
- **WHEN** an agent runs
      `grep -E "^function" baml/education/subjects/qpack_<subject>.baml`
- **THEN** the output SHALL include the
      `Generate<Subject>FormativeItem` function (used by the
      per-subject `*_formative_item_generate_tool` that each
      handler delegates to).
- **AND** the BAML file SHALL contain at least 5 `function`
      declarations total (the canonical 6: `QuestPack`,
      `Extract<Subject>LOStatement`, optional `Extract<Subject>GaStatement`,
      `FormativeItem`, `Score<Subject>FormativeResponse`,
      `Validate<Subject>QuestPack`).

### Requirement: 8 NCCA ADK specialists as A2UI surface emitters

The system SHALL register the 8 NCCA ADK specialists at
`agents/tuatha/{math,chem,geog,gael,engl,comp,appm,hist}_agent.py`
as CopilotKit dispatch targets that emit A2UI operations
(`createSurface` / `updateComponents` / `updateDataModel`) when
responding to user queries. The 18 per-subject workflow handlers
(`_workflow_handlers.py::make_study_plan_handler` /
`discuss_exam_paper_handler` / `explain_marking_scheme_handler` × 6
subjects) SHALL be the dispatcher entry points.

This requirement is the canonical link between the agent fleet and
the A2UI surface generation described in
`openspec/changes/2026-07-18-british-isles-portal-activation-v3/specs/cianfhoghlaim-leaving-cert-portal/spec.md`
R18.

#### Scenario: A user opens a Mathematics page

- **GIVEN** the user is on `/en/subjects/mathematics/`
- **WHEN** they ask the CopilotKit sidebar for a study plan
- **THEN** `math_agent` is dispatched
- **AND** `make_study_plan_handler` invokes the BAML `WebStudyPlan`
- **AND** the agent emits an A2UI `createSurface` operation
- **AND** the client mounts the `<StudyPlanCard>` from the catalog

#### Scenario: A user asks Gaeilge agent for a past paper discussion (in Irish)

- **GIVEN** the user is on `/ga/subjects/gaeilge/`
- **WHEN** they type "déan plé ar Pháipéar 2 2024" (discuss Paper 2 2024)
- **THEN** `gael_agent` is dispatched
- **AND** `discuss_exam_paper_handler` invokes `b.WebExamPaperDiscussion(subject="gaeilge", paper_year=2024, paper_level="LC_HL", paper_language="ga", question_text="...")`
- **AND** the agent emits an A2UI `createSurface` with bilingual EN+GA labels

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
