## ADDED Requirements

### Requirement: All hardcoded model strings across the platform route through MODEL_REGISTRY

The system SHALL route every model invocation through `MODEL_REGISTRY.model_for(family, role, language=None)` or `MODEL_REGISTRY.filter(family=...)`. No hardcoded model strings (e.g., `gpt-4o-mini`, `minimax-m3`, `chatterbox`, `gemini-2.5-pro`) SHALL remain outside the registry whitelist. The `mise run lint:registry` CI gate SHALL fail any commit that introduces a hardcoded model string.

This requirement was added in the
`2026-07-29-complete-remaining-model-registry-migrations-v1` change
(per issue #141 follow-up to the deferred Phase 1.3-1.10 + 1.12-1.19
from `2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1`).

#### Scenario: New model added via registry, not code

- **GIVEN** a new `text_llm` model is added to `MODEL_REGISTRY`
- **WHEN** the operator runs `mise run lint:registry`
- **THEN** the audit SHALL pass (no hardcoded strings)
- **AND** every agent that calls `model_for("text_llm", "default")`
  SHALL pick up the new model automatically (no code changes)

#### Scenario: Operator disables a model via deployment-choice.yaml

- **GIVEN** `deployment-choice.yaml` has `disabled_models: ["minimax-m3"]`
- **WHEN** the agent runtime starts
- **THEN** `model_for("text_llm", "default")` SHALL return the next
  enabled model in the family
- **AND** the audit log at `stedding/deployment-control-panel/audit.log`
  SHALL record the disabled model with timestamp
