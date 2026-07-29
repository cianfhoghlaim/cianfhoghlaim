# Spec delta: `centralized-model-registry`

This delta is part of the openspec change
`2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1`.
The 4 ADDED Requirements were already added to the canonical
`centralized-model-registry` spec by the parallel-session work. This
delta adds ONE new requirement: the audit-on-commit CI gate.

## ADDED Requirements

### Requirement: Registry audit is a CI gate

The system SHALL run `mise run lint:registry` in the `.forgejo/workflows/`
CI on every commit. The CI gate SHALL fail any commit that introduces
a hardcoded model string outside the `MODEL_REGISTRY` whitelist
(detected via `scripts/registry_audit.py --strict`).

#### Scenario: hardcoded model string blocks PR

- **GIVEN** a PR adds `LlmAgent(model="custom-llama-3-70b")` to a Python file
- **WHEN** the CI runs `mise run lint:registry`
- **THEN** the audit SHALL flag the hardcoded model string
- **AND** the CI gate SHALL exit non-zero
- **AND** the PR SHALL be blocked from merge
