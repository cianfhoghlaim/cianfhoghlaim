# Spec Delta — agent-observability

This delta adds 2 new requirements to the existing
`agent-observability` capability. Existing requirements are
preserved unchanged.

## ADDED Requirements

### Requirement: 5-layer observability hooks via `agents/observability_hooks.py`

The system SHALL provide a shared `agents/observability_hooks.py`
module containing the 5-layer observability wiring:

- **Layer 1**: `LangfuseLogger` — wraps the canonical
  `cianfhoghlaim.observability.langfuse_config.langfuse_trace`
  context manager with per-agent `trace_name` injection.
- **Layer 2**: `LogfireSpan` — wraps the canonical
  `cianfhoghlaim.observability.logfire_config.logfire_span`
  with per-agent span metadata.
- **Layer 3**: `MLflowTracker` — wraps the canonical
  `cianfhoghlaim.observability.mlflow_tracker.log_run`
  with per-agent experiment tagging.
- **Layer 4**: `RAGASScorer` — Dagster asset_check for
  RAGAS trace-based metrics.
- **Layer 5**: `structlogLogger` — structured JSON logging
  with per-agent context.

The `attach_observability(wiring)` function SHALL wire the
5 layers for a given `AgentFleetWiring` instance.

#### Scenario: `attach_observability` wires all 5 layers

- **GIVEN** an `AgentFleetWiring` for `curriculum_agent`
- **WHEN** `wire = attach_observability(wiring)`
- **THEN** the returned `wire` SHALL have:
  - `langfuse_wired=True` and `langfuse_trace_name` populated
  - `logfire_wired=True` and `logfire_span_name` populated
  - `mlflow_wired=True` and `mlflow_experiment_name` populated
  - `ragas_scorer_wired=True` and `ragas_dataset_name` populated
  - `structlog_wired=True` and `structlog_context` populated

#### Scenario: 5-layer observability contract verified

- **GIVEN** the 12 agents are wired via `agents/observability_hooks.py`
- **WHEN** `python -c "from cianfhoghlaim.agents.observability_hooks import verify_5_layer_contract; print(verify_5_layer_contract())"`
- **THEN** the output SHALL be `True`
- **AND** all 12 agents SHALL have all 5 layers wired

### Requirement: Observability contract verification

The system SHALL provide a `verify_observability_contract(agent_name)`
function that asserts the 5-layer observability contract for
a given agent. The function SHALL return `True` if all 5
layers are wired, `False` otherwise.

The `verify_observability_contract()` function (no args) SHALL
return a dict mapping `agent_name → bool` for all 12 agents.

#### Scenario: `verify_observability_contract` returns True for a wired agent

- **GIVEN** the `curriculum_agent` is wired via
  `agents/observability_hooks.py`
- **WHEN** `verify_observability_contract("curriculum_agent")`
- **THEN** the function SHALL return `True`

#### Scenario: `verify_observability_contract` returns a dict for all 12 agents

- **GIVEN** the 12 agents are wired via `agents/observability_hooks.py`
- **WHEN** `verify_observability_contract()`
- **THEN** the result SHALL be a dict with 12 keys
- **AND** all 12 values SHALL be `True`