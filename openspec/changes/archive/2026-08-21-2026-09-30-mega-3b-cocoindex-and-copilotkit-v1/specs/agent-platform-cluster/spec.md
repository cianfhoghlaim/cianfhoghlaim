## ADDED Requirements

### Requirement: agent_ui_bridge.py wires ADK to CopilotKit AG-UI

The system SHALL provide `agents/integrations/agent_ui_bridge.py`
that wires any Google ADK `LlmAgent` to the CopilotKit AG-UI protocol.

The bridge wraps `ag-ui-adk.ADKAgent` + `CopilotKitRuntime` (per the
`docs/copilotkit/examples/showcases/adk-dashboard/agent/agent.py`
pattern).

#### Scenario: agent_ui_bridge exposes ADK agents to CopilotKit

- **GIVEN** the 12 ADK agents at `agents/adk/*.py`
- **WHEN** the operator runs `from agents.integrations.agent_ui_bridge import register_adk_agent; register_adk_agent(agent)`
- **THEN** the helper emits the AG-UI registration event so the
  CopilotKit UI can route to it via `CopilotRuntime.agents[name]`

### Requirement: BuiltInPlanner via make_planner_agent helper

The system SHALL ensure that every ADK agent uses the canonical
`make_planner_agent()` helper (per the 2026-08-18-mega-3-fast-follow-v1
change FF.3) instead of hand-writing `BuiltInPlanner(...)`.

#### Scenario: Every ADK agent uses the canonical planner helper

- **WHEN** `mise run lint:adk-builtin-planner-coverage` runs
- **THEN** every ADK agent that has a planner MUST use the
  `make_planner_agent()` helper (per FF.3)
- **AND** the lint returns `OK: 12/12 agents with planner`

### Requirement: 12 ADK agents use output_schema (Pydantic)

The system SHALL auto-generate `output_schema` (Pydantic) for all 12
ADK agents via the `BAMLFunctionTool` integration helper (from the
2026-08-26-mega-3a-baml-and-adk-v1 change).

#### Scenario: Every ADK agent uses BAML-generated Pydantic classes

- **WHEN** the operator runs
  `python -c "from baml_client.types import *; from agents.adk.curriculum_agent import CurriculumAgentOutput; print(issubclass(CurriculumAgentOutput, BaseModel))"`
- **THEN** the agent's `output_schema` is a BAML-generated Pydantic
  class
- **AND** no `BaseModel` re-declaration exists in `agents/adk/*.py`