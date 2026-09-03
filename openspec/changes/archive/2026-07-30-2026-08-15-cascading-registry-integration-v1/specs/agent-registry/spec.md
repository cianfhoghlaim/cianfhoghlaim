# Spec delta: `agent-registry`

This delta is part of the openspec change
`2026-08-15-cascading-registry-integration-v1`. It updates the
12-agent fleet spec to consume `MODEL_REGISTRY.resolve()` for each
agent's `litellm_routing_key`.

## ADDED Requirements

### Requirement: 12-agent fleet MUST consume MODEL_REGISTRY.resolve() for litellm_routing_key

The system SHALL update `agents/agent_registry.py:39-184` so that
each agent's `litellm_routing_key` resolves through
`MODEL_REGISTRY.resolve("text_llm", role=<key>)`. The 12 agents in
the `AGENT_REGISTRY` are: `root_agent`, `curriculum_agent`,
`translation_agent`, `corpus_agent`, `research_agent`,
`education_research_agent`, `bunchloch_research_agent`, `geospatial_agent`,
`statistics_agent`, `curriculum_comparison_agent`,
`agui_curriculum_agent`, `mcp_curriculum_agent`.

#### Scenario: Each agent's litellm_routing_key resolves through the registry

- **GIVEN** the `MODEL_REGISTRY` populated with the `text_llm` family (13 entries)
- **WHEN** the operator reads `agents/agent_registry.py:39-184`
- **THEN** each agent's `litellm_routing_key` resolves via
  `MODEL_REGISTRY.resolve("text_llm", role=<agent_name>)`
- **AND** the resolved model key is one of the canonical 13 entries (minimax-m3, qwen3.6-27b-mtp, etc.)

#### Scenario: 12-agent fleet connects to the deployment control panel

- **GIVEN** the 5-tab marimo control panel at `notebooks/00_control_panel.py`
- **WHEN** an operator toggles an agent's `litellm_routing_key` off
- **THEN** `deployment-choice.yaml:enabled_models[<agent_key>]` is set to `false`
- **AND** the agent's `make_litellm_agent()` call falls back to the fallback model
