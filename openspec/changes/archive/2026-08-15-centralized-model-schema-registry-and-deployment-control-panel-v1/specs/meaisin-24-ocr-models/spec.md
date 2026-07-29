# Spec delta: `meaisin-24-ocr-models`

This delta is part of the openspec change
`2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1`.
It extends the existing 24-model OCR/VLM registry to be a subset of
the new `centralized-model-registry` `MODEL_REGISTRY`, preserving the
existing 2-axis partition (scope × model).

## ADDED Requirements

### Requirement: 24-model OCR/VLM registry is a subset view of MODEL_REGISTRY

The system SHALL expose the existing 22-entry `VISION_MODELS` as a
subset view of the new `MODEL_REGISTRY` via
`MODEL_REGISTRY.filter(family="ocr_vision")`. The 24-model 2-axis
partition (scope × model) MUST be preserved.

#### Scenario: VISION_MODELS is a subset view

- **GIVEN** the new `MODEL_REGISTRY` at
  `meaisinfhoghlaim/models/registry.py`
- **WHEN** the operator runs
  `python3 -c "from meaisinfhoghlaim.models.registry import VISION_MODELS, MODEL_REGISTRY; assert VISION_MODELS == MODEL_REGISTRY.filter(family='ocr_vision')"`
- **THEN** the assertion passes and the exit code is `0`

#### Scenario: 2-axis partition is preserved

- **GIVEN** the existing 24-model 2-axis partition (scope × model)
- **WHEN** the `ocr_model_<key>_documents_ingested` asset materialises
- **THEN** the partition key is `(scope="meaisin_ocr_vlm_<model_key>",
  model="v4")` (unchanged from the existing contract)