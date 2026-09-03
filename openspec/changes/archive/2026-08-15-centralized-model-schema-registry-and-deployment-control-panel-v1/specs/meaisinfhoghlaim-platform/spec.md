# Spec delta: `meaisinfhoghlaim-platform`

This delta is part of the openspec change
`2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1`.
It registers the canonical model-registry home at
`meaisinfhoghlaim/models/registry.py:MODEL_REGISTRY`.

## ADDED Requirements

### Requirement: Canonical model-registry home is meaisinfhoghlaim/models/registry.py:MODEL_REGISTRY

The system SHALL register the canonical model-registry home at
`meaisinfhoghlaim/models/registry.py:MODEL_REGISTRY`. The legacy
`meaisinfhoghlaim/ocr/models/registry.py` shim (which emits
`DeprecationWarning`) SHALL be deprecated; consumers SHALL migrate to
the canonical home.

#### Scenario: Legacy shim is deprecated

- **GIVEN** the new `MODEL_REGISTRY` populated
- **WHEN** the operator imports
  `from meaisinfhoghlaim.ocr.models.registry import VISION_MODELS`
- **THEN** the import emits a `DeprecationWarning`
- **AND** the migration guide directs consumers to
  `from meaisinfhoghlaim.models.registry import MODEL_REGISTRY, VISION_MODELS`