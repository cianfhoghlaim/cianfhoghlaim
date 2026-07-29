# Spec Delta — meaisinfhoghlaim-agent-frameworks

This delta adds 3 new requirements to the existing
`meaisinfhoghlaim-agent-frameworks` capability. Existing requirements
are preserved unchanged.

## ADDED Requirements

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