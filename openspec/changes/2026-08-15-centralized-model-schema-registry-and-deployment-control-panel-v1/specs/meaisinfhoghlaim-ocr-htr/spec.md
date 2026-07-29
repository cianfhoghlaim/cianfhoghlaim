# Spec delta: `meaisinfhoghlaim-ocr-htr`

This delta is part of the openspec change
`2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1`.
It registers the existing OCR/HTR spec to consume the new
`MODEL_REGISTRY.filter(family="ocr_vision")` instead of the legacy
`VISION_MODELS` direct reference.

## ADDED Requirements

### Requirement: OCR/HTR spec consumes MODEL_REGISTRY.filter(family="ocr_vision")

The system SHALL update `openspec/specs/meaisinfhoghlaim-ocr-htr/spec.md`
to reference `MODEL_REGISTRY.filter(family="ocr_vision")` rather than
the legacy `VISION_MODELS` direct reference. The 24-model 4-backend
contract (LITELLM / MLX / TRANSFORMERS / LLAMASWAP) MUST be preserved.

#### Scenario: OCR/HTR references MODEL_REGISTRY

- **GIVEN** the `MODEL_REGISTRY` populated
- **WHEN** the operator reads
  `openspec/specs/meaisinfhoghlaim-ocr-htr/spec.md`
- **THEN** the spec references
  `MODEL_REGISTRY.filter(family="ocr_vision")` for the 24-model list
- **AND** the 24-model 4-backend contract is preserved