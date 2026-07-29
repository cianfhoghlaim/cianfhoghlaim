# Spec delta: `dagster-5-layer-component-architecture`

This delta is part of the openspec change
`2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1`.
It registers the 5 KCG Components' (Ingestion / Materials / Model
Lifecycle / Asset Generation / Agent Operations) consumption of
`MODEL_REGISTRY` for the Model Lifecycle layer.

## ADDED Requirements

### Requirement: Model Lifecycle Component consumes MODEL_REGISTRY

The system SHALL update the 5-layer KCG Component architecture so
that the Model Lifecycle layer consumes `MODEL_REGISTRY` for its
CocoIndex v1 Apps + LLM routing + embedder configuration. The
Ingestion / Materials / Asset Generation / Agent Operations layers
remain unchanged.

#### Scenario: Model Lifecycle layer reads from MODEL_REGISTRY

- **GIVEN** the `MODEL_REGISTRY` populated
- **WHEN** the operator runs
  `mise run cocoindex:conformance`
- **THEN** the R1+R2+R3+R4 linter reports that every CocoIndex App
  imports `MODEL_REGISTRY` (or the legacy `VISION_MODELS` subset view)
- **AND** the L3 Component `defs.yaml` files reference
  `MODEL_REGISTRY.filter(family="ocr_vision")` for the embedder

#### Scenario: Dagster 1_ingestion cleanup is registered

- **GIVEN** the 619 empty placeholder YAMLs across
  `orchestration/defs/1_ingestion/european_nations/`,
  `orchestration/defs/1_ingestion/commonwealth/{canada,nigeria,australia}/`,
  `orchestration/defs/1_ingestion/american_nations/`
- **WHEN** the operator runs `mise run dagster:dev`
- **THEN** the empty YAMLs are not loaded
- **AND** the 10 per-jurisdiction `generic_<jur>_assets.py` files
  use the new `JurisdictionAssetsBase`