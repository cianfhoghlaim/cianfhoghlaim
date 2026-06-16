## ADDED Requirements

The `meaisinfhoghlaim-agent-frameworks` capability is created by this
change. The full Requirements + Scenarios are in the canonical spec at
`openspec/specs/meaisinfhoghlaim-agent-frameworks/spec.md`.

### Requirement: 12 specialised agents

The system SHALL provide 12 specialised agents in
`meaisinfhoghlaim/agents/` covering the Irish + UK + pan-Celtic
education surface.

#### Scenario: Root agent routes to specialists

- **WHEN** a user query "what is the Irish curriculum for ga101?" is dispatched
- **THEN** the Root Agent routes to the Curriculum Agent
- **AND** the Curriculum Agent returns the ga101 Primary Irish curriculum data

### Requirement: Agno + Google ADK + LiteLLM framework

The system SHALL use Agno (>=2.0.0) + Google ADK (>=1.0.0) + LiteLLM
as the agent framework.

#### Scenario: LiteLLM routing

- **WHEN** the agent makes an LLM call
- **THEN** LiteLLM routes the call to the configured model

#### Scenario: Fallback chain

- **WHEN** the primary model is unavailable
- **THEN** LiteLLM falls back to the next model in the chain

### Requirement: Knowledge graph integration

The system SHALL integrate the agents with the Cognee + Graphiti +
LanceDB knowledge graph stack.

#### Scenario: Cognee knowledge base

- **WHEN** a curriculum question is asked
- **THEN** the agent retrieves relevant context from Cognee

### Requirement: Application-layer facades

The system SHALL provide 2 application-layer agent facades in
`oideachais/agents/{adk,agno}/`.

#### Scenario: CopilotKit AG-UI streaming

- **WHEN** a user issues a query in the oideachais web app CopilotKit chat
- **THEN** the response is streamed to the client via AG-UI
