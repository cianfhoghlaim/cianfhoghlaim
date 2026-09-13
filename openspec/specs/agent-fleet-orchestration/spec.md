# agent-fleet-orchestration Specification

## Purpose
TBD - created by archiving change 2026-09-30-mega-3b-cocoindex-and-copilotkit-v1. Update Purpose after archive.

## Requirements

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

### Requirement: 12 ADK agents registered as CopilotKit agents

The system SHALL register the 12 ADK agents at `agents/adk/*.py` as
`CopilotRuntime.agents[name]` so the CopilotKit UI can route user
messages to any of the 12 agents via the AG-UI protocol.

The 12 agents are: `root_agent`, `curriculum_agent`,
`translation_agent`, `corpus_agent`, `research_agent`,
`education_research_agent`, `bunchloch_research_agent`,
`geospatial_agent`, `statistics_agent`, `curriculum_comparison_agent`,
`agui_curriculum_agent`, `mcp_curriculum_agent`.

#### Scenario: All 12 ADK agents are registered

- **GIVEN** the CopilotKit runtime at `web/apps/cianfhoghlaim/app.config.ts`
- **WHEN** the operator runs `ccc:search "register_adk_agent"` or
  inspects the CopilotRuntime initialization
- **THEN** the system has registered all 12 agents
- **AND** each agent has a corresponding route in `web/apps/cianfhoghlaim-web/src/routes/agents/<agent_name>/`

#### Scenario: CopilotKit UI routes to the right ADK agent

- **GIVEN** the user sends a message about "compare Irish and English LC mathematics syllabuses"
- **WHEN** the CopilotKit UI receives the message
- **THEN** the AG-UI protocol routes it to `curriculum_comparison_agent`
  (per the agent description match)
- **AND** the agent's tools (including the 6 LC-subject BAML
  functions) are exposed to the LLM
