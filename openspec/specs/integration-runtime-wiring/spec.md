# integration-runtime-wiring Specification

## Purpose
The integration runtime wiring surface covers the agent runtime → tool integration across the Cianfhoghlaim monorepo. It defines 3 invariants: the runtime layer (orchestration/components/layer5_agent_ops.py), the tool layer (orchestration/components/layer1_ingestion.py + layer3_model_lifecycle.py), and the canonical adapter pattern (each tool exposes a single function-shaped entry point).

## Requirements
### Requirement: Marimo Integration Runtime Wired into 4 Stage Dashboards

The system SHALL wire the canonical `make_baml_chat_for_stage`
helper from `notebooks/_shared/marimo_integration_runtime.py`
into each of the 4 stage dashboards (LC + JC + A-Level + GCSE).
Each dashboard MUST import the helper and call
`make_baml_chat_for_stage(stage="<stage>", subject=None)`.

#### Scenario: LC dashboard exposes a BAML chat
- **WHEN** `notebooks/19_ireland_pipeline_dashboard.py` is rendered
- **THEN** a `mo.ui.chat` widget is displayed in the chat cell
  AND the chat is backed by the `LC6_FUNCTIONS` (5 canonical
  extraction functions)

#### Scenario: JC dashboard exposes a BAML chat
- **WHEN** `notebooks/19_junior_cycle_pipeline_dashboard.py` is rendered
- **THEN** a `mo.ui.chat` widget is displayed AND the chat is backed
  by the `JC_FUNCTIONS` (4 canonical extraction functions)

#### Scenario: A-Level dashboard exposes a BAML chat
- **WHEN** `notebooks/20_england_alevel_pipeline_dashboard.py` is rendered
- **THEN** a `mo.ui.chat` widget is displayed AND the chat is backed
  by the `QPACK_FUNCTIONS` (3 cross-stage functions)

#### Scenario: GCSE dashboard exposes a BAML chat
- **WHEN** `notebooks/20_england_gcse_pipeline_dashboard.py` is rendered
- **THEN** a `mo.ui.chat` widget is displayed AND the chat is backed
  by the `QPACK_FUNCTIONS`

### Requirement: Agent Registry Runtime Wired into Hono API

The system SHALL wire the canonical `agent_registry_runtime`
Python helpers into the Hono API at
`web/hono-api/src/routes/copilotkit/registry.ts`. The route
MUST expose 3 endpoints: `/config`, `/events`, `/agents`. Each
endpoint MUST delegate to the corresponding Python helper via a
subprocess call (using `execFile`, not `exec`, to avoid shell
injection).

#### Scenario: GET /api/copilotkit/registry/config returns the runtime config
- **WHEN** a client GETs `/api/copilotkit/registry/config`
- **THEN** the response is a JSON object with the keys `agents`,
  `tools`, `metadata` (sourced from
  `build_copilotkit_runtime_config()`)

#### Scenario: GET /api/copilotkit/registry/events returns the AG-UI events
- **WHEN** a client GETs `/api/copilotkit/registry/events`
- **THEN** the response is a JSON object with the keys `events`
  (a list) and `count` (the list length)

#### Scenario: GET /api/copilotkit/registry/agents returns the agent names
- **WHEN** a client GETs `/api/copilotkit/registry/agents`
- **THEN** the response is a JSON object with the keys `agents`
  (a list of names) and `count`

### Requirement: Phase 2 Integration Tests

The system SHALL provide 8 integration tests in
`tests/test_phase2_integration_wiring.py` that verify:

1. `make_baml_chat_for_stage` is callable for each of the 4 stages
2. Each of the 4 stage dashboards imports the helper

#### Scenario: All 8 Phase 2 tests pass
- **WHEN** `python -m pytest tests/test_phase2_integration_wiring.py -v` runs
- **THEN** 8/8 tests pass

