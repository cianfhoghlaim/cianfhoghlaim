# Spec delta: `meaisinfhoghlaim-platform`

This delta is part of the openspec change
`2026-08-15-cascading-registry-integration-v1`. It updates the
canonical model-registry home note to point at the new unified
`MODEL_REGISTRY` at `meaisinfhoghlaim/models/model_registry.py`.

## ADDED Requirements

### Requirement: meaisinfhoghlaim-platform MUST reference MODEL_REGISTRY as the canonical home

The system SHALL update `openspec/specs/meaisinfhoghlaim-platform/spec.md`
to reference the unified `MODEL_REGISTRY` at
`meaisinfhoghlaim/models/model_registry.py` (52 entries / 7 families)
as the canonical model-registry home. The legacy 22-entry
`VISION_MODELS` dict at `meaisinfhoghlaim/models/registry.py` is
preserved as the OCR/VLM subset view (`MODEL_REGISTRY.filter(family="ocr_vision")`).

#### Scenario: meaisinfhoghlaim-platform references MODEL_REGISTRY

- **GIVEN** the `MODEL_REGISTRY` populated with 52 entries
- **WHEN** the operator reads `meaisinfhoghlaim-platform/spec.md`
- **THEN** the spec references `MODEL_REGISTRY` at `meaisinfhoghlaim/models/model_registry.py`
- **AND** the 22-entry `VISION_MODELS` is marked as a subset view

#### Scenario: meaisinfhoghlaim-platform connects to schema_introspect helpers

- **GIVEN** the 5 schema introspection helpers in `notebooks/_shared/schema.py`
- **WHEN** the meaisinfhoghlaim-platform is queried for model + schema inventory
- **THEN** `list_dlt_sources()` + `list_cocoindex_apps()` + `list_baml_classes()` are the canonical API
- **AND** the count surfaces 1963 DLT sources + 92 CocoIndex Apps + 844 BAML classes
