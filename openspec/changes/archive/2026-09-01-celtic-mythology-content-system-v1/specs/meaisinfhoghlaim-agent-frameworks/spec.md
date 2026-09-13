## ADDED Requirements

### Requirement: Celtic Mythology Agent

The system SHALL provide `agents/meaisinfhoghlaim/educational/celtic_mythology_agent.py`
as an ADK agent with 8 tools (`extract_deity`, `extract_geis`,
`extract_ogham_inscription`, `extract_hero_cycle`, `extract_pent_elemental_affinity`,
`extract_mythology_quest`, `build_game_asset_from_lo`, `compose_mythology_narrative`).
The agent SHALL be registered in `agents/agent_registry.py:AGENT_REGISTRY`
with `framework="adk"`, `litellm_routing_key="mythology"`.

#### Scenario: Mythology agent queries Cúchulainn
- **WHEN** the user invokes `celtic_mythology_agent` with "Tell me about Cúchulainn"
- **THEN** the agent returns a `HeroCycle` Pydantic model

### Requirement: Irish History Agent

The system SHALL provide `agents/meaisinfhoghlaim/educational/irish_history_agent.py`
as an ADK agent with 6 tools for the 6 Irish dynastic families.

#### Scenario: Irish History agent queries a dynasty
- **WHEN** the user invokes `irish_history_agent` with "Tell me about Uí Liatháin"
- **THEN** the agent returns an `IrishDynasty` Pydantic model

### Requirement: Educational Geography Agent

The system SHALL provide `agents/meaisinfhoghlaim/educational/educational_geography_agent.py`
as an ADK agent with 10 tools covering the 4 syllabuses + GeoAI ops + map rendering.

#### Scenario: Geography agent queries LC unit 1.1
- **WHEN** the user invokes `educational_geography_agent` with "LC Geography Core Unit 1.1 learning outcomes"
- **THEN** the agent returns the 7 learning outcomes for the unit