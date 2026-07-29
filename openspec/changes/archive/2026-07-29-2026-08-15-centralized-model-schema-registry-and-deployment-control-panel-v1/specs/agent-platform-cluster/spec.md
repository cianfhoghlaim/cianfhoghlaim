# Spec delta: `agent-platform-cluster`

This delta is part of the openspec change
`2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1`.
The other 9 ADDED Requirements were already added to the canonical
`agent-platform-cluster` spec by the parallel-session work. This delta
adds ONE new requirement: the deployment-choice.yaml enablement file
that the central change registers.

## ADDED Requirements

### Requirement: deployment-choice.yaml is the canonical enablement file

The system SHALL provide a `deployment-choice.yaml` file at the
repo root that records which families in `MODEL_REGISTRY` are
enabled for production (default: all). The file SHALL have the
shape:

```yaml
enabled_families:
  - ocr_vision
  - text_llm
  - embedder
  - image_gen
  - voice
  - translation
enabled_jurisdictions:
  - ireland
  - england
disabled_families: []
disabled_models: []
```

#### Scenario: deployment-choice.yaml is read at startup

- **WHEN** the agent runtime (hermes / openclaw / openchamber) starts
- **THEN** it SHALL read `deployment-choice.yaml`
- **AND** the runtime SHALL only call `MODEL_REGISTRY.model_for(...)`
  for families in `enabled_families`
- **AND** if `deployment-choice.yaml` is missing, the runtime SHALL
  default to all-families-enabled + log a warning
