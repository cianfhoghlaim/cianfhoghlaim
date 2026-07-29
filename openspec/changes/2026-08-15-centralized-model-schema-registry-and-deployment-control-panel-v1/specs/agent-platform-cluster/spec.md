# Spec delta: `agent-platform-cluster`

This delta is part of the openspec change
`2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1`.
It registers the new `MODEL_REGISTRY` as the LiteLLM config source
and removes the legacy hardcoded LiteLLM aliases.

## ADDED Requirements

### Requirement: LiteLLM config is regenerated from MODEL_REGISTRY

The system SHALL regenerate
`bonneagar/stacks/litellm/config/config.yaml` from `MODEL_REGISTRY`
on every `mise run cic:meaisin:litellm-regenerate`. The 5 M3
chokepoint aliases (`kimi/k2`, `glm/5.1`, `minimax/m2.5`, `mimo/2.5`,
`deepseek/flash`) + the 24 `local/vision/*` entries SHALL all be
derived from `MODEL_REGISTRY`.

#### Scenario: LiteLLM config is generated from MODEL_REGISTRY

- **GIVEN** the `MODEL_REGISTRY` populated
- **WHEN** the operator runs
  `mise run cic:meaisin:litellm-regenerate`
- **THEN** `bonneagar/stacks/litellm/config/config.yaml` is regenerated
  from `MODEL_REGISTRY`
- **AND** the file contains no hand-edited model_list entries
- **AND** the 5 ghost-model references (`qwen3-vl-235b-a22b`,
  `glm-4.6v-full`, `qwen3.6-35b-a3b-mtp`, `gemma-4-31B`,
  `gemma-3-27b-it`) are removed