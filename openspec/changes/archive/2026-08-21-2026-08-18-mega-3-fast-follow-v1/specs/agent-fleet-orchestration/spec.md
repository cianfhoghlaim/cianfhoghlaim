## ADDED Requirements

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