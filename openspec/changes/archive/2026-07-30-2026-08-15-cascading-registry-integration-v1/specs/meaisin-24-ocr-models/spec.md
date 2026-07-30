# Spec delta: `meaisin-24-ocr-models`

This delta is part of the openspec change
`2026-08-15-cascading-registry-integration-v1` (a follow-up to
`2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1`).
It updates the 24-model OCR/VLM registry spec to consume the new
unified `MODEL_REGISTRY` (post-2026-08-15) instead of the legacy
`VISION_MODELS` dict.

## ADDED Requirements

### Requirement: meaisin-24-ocr-models MUST consume MODEL_REGISTRY.filter(family="ocr_vision")

The system SHALL update `openspec/specs/meaisin-24-ocr-models/spec.md`
to reference `MODEL_REGISTRY.filter(family="ocr_vision")` rather than
the legacy `VISION_MODELS` direct reference. The 24-model 4-backend
contract (LITELLM / MLX / TRANSFORMERS / LLAMASWAP) MUST be preserved.

#### Scenario: meaisin-24-ocr-models references MODEL_REGISTRY

- **GIVEN** the `MODEL_REGISTRY` populated (52 entries / 7 families)
- **WHEN** the operator reads `openspec/specs/meaisin-24-ocr-models/spec.md`
- **THEN** the spec references `MODEL_REGISTRY.filter(family="ocr_vision")` for the 24-model list
- **AND** the 24-model 4-backend contract is preserved

#### Scenario: meaisin-24-ocr-models connects to the centralized-registry skill

- **GIVEN** the `centralized-registry` skill at `.agents/skills/centralized-registry/SKILL.md`
- **WHEN** a subagent needs to add a new OCR/VLM model
- **THEN** the skill's `model_for("ocr_vision", role)` API is the canonical entry point
- **AND** the 24-model registry is a subset view of the unified `MODEL_REGISTRY`
