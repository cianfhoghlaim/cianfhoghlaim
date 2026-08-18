## ADDED Requirements

### Requirement: agent_registry.py (the canonical 12-agent registry)

The system SHALL provide `agents/adk/agent_registry.py` that
registers the 12 ADK agents + the 4 stage agents (lc_subject_agent,
jc_subject_agent, alevel_subject_agent, gcse_subject_agent) + their
BAMLFunctionTool-wrapped tools.

The registry exposes `AGENT_REGISTRY: dict[str, AgentWiring]` so the
`agents.integrations/agent_ui_bridge.py` can wire any agent via
`AGENT_REGISTRY["<agent_name>"]`.

#### Scenario: agent_registry exposes all 16 agents

- **GIVEN** the 12 baseline ADK agents + the 4 stage agents
- **WHEN** the operator runs
  `python -c "from agents.adk.agent_registry import AGENT_REGISTRY; print(len(AGENT_REGISTRY))"`
- **THEN** the output is `>= 16`

### Requirement: A2A Protocol for the 12-agent fleet

The system SHALL adopt the A2A Protocol (Agent-to-Agent) so the 12
ADK agents can call each other via a standardised message format.

The A2A Protocol is exposed at `/api/a2a/<agent_name>` and the
`agent_ui_bridge` registers all 12 agents with the A2A router.

#### Scenario: Agent A can call Agent B via A2A

- **GIVEN** 12 ADK agents are registered with the A2A router
- **WHEN** the `curriculum_agent` calls the
  `bunchloch_research_agent` via A2A
- **THEN** the A2A router routes the message + returns the result