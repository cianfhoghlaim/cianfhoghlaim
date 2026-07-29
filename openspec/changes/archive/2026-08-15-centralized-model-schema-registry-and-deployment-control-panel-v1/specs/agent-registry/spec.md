# Spec delta: `agent-registry`

This delta is part of the openspec change
`2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1`.
It registers the 12-agent fleet's consumption of
`MODEL_REGISTRY.resolve(family, role)` for each agent's
`litellm_routing_key`.

## ADDED Requirements

### Requirement: 12-agent fleet consumes MODEL_REGISTRY.resolve() for litellm_routing_key

The system SHALL update `agents/agent_registry.py:39-184` so that
each agent's `litellm_routing_key` resolves through
`MODEL_REGISTRY.resolve("text_llm", role=<agent_key>)`. The 32
hardcoded `gemini-2.0-flash` sites in `agents/adk/*` SHALL be replaced
with `MODEL_REGISTRY.resolve(...)` calls.

#### Scenario: Each agent's litellm_routing_key resolves through the registry

- **GIVEN** the `MODEL_REGISTRY` populated with the `text_llm` family
- **WHEN** the operator runs
  `python3 -c "from agents.agent_registry import AGENT_REGISTRY; from meaisinfhoghlaim.models.registry import MODEL_REGISTRY; [print(k, MODEL_REGISTRY.resolve('text_llm', role=k)) for k in AGENT_REGISTRY]"`
- **THEN** the output prints every agent's resolved model key
- **AND** no hardcoded `gemini-2.0-flash` strings remain in
  `agents/adk/*.py`

#### Scenario: google-adk/SKILL.md drift signal is resolved

- **GIVEN** the drift signal at `google-adk/SKILL.md:403-419`
  ("32 LlmAgent(model=config.model_name) constructors hardcode
  gemini-2.0-flash ... BYPASSING the KCG minimax 7-tier LiteLLM
  fallback alias")
- **WHEN** the operator runs `mise run lint:registry`
- **THEN** the output contains `Found 0 hardcoded model strings in audited files`
- **AND** the drift signal is removed from `google-adk/SKILL.md`