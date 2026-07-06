# Meaisínfhoghlaim Agent Frameworks Capability

## Purpose

`meaisinfhoghlaim-agent-frameworks` is a capability of the Cianfhoghlaim
platform. The corresponding source code lives at
`sruth/meaisinfhoghlaim/agents/` (12 specialised agents) and
`sruth/oideachais/agents/{adk,agno}/` (the application-layer CopilotKit / AG-UI
facades). See `docs/00_index.md` for the quadrant map and
`docs/00-core/CLAUDE.md` for the project identity.

This spec was created by the `openspec-consolidation-and-readme-refresh`
change and supersedes the old `agent-frameworks` spec (which described
the Agno + Google ADK + LiteLLM framework, 253 lines).

## Background

The meaisinfhoghlaim agent framework is the model layer for the
Cianfhoghlaim platform. The 12 specialised agents in
`sruth/meaisinfhoghlaim/agents/` cover the full Irish + UK + pan-Celtic
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

The 2 application-layer facades (`sruth/oideachais/agents/{adk,agno}/`) wrap
these specialised agents for the front-end CopilotKit / AG-UI.
## Requirements
### Requirement: 12 specialised agents

The system SHALL provide 12 specialised agents in
`sruth/meaisinfhoghlaim/agents/` covering the Irish + UK + pan-Celtic
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
`sruth/oideachais/agents/{adk,agno}/` for the oideachais web app.

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

## Cross-references

- [`sruth/meaisinfhoghlaim/agents/`](../../sruth/meaisinfhoghlaim/agents/) (the 12 specialised agents)
- [`sruth/oideachais/agents/adk/`](../../sruth/oideachais/agents/adk/) (the Google ADK facade)
- [`sruth/oideachais/agents/agno/`](../../sruth/oideachais/agents/agno/) (the Agno facade)
- [`.agents/skills/agno/SKILL.md`](../../.agents/skills/agno/SKILL.md)
- [`.agents/skills/google-adk/SKILL.md`](../../.agents/skills/google-adk/SKILL.md)
- [`.agents/skills/ai-engineer/SKILL.md`](../../.agents/skills/ai-engineer/SKILL.md)
- [`.agents/skills/celtic-language-ai/SKILL.md`](../../.agents/skills/celtic-language-ai/SKILL.md)
- [`openspec/specs/meaisinfhoghlaim-platform/spec.md`](meaisinfhoghlaim-platform/spec.md) (the quadrant overview)
- [`openspec/specs/agent-observability/spec.md`](../agent-observability/spec.md) (the observability stack)
- [`openspec/specs/agent-memory-systems/spec.md`](../agent-memory-systems/spec.md) (the memory systems)
