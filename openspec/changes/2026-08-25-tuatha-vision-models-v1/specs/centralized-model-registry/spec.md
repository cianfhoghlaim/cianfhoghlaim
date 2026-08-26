# Spec Delta: centralized-model-registry

## ADDED Requirements

### Requirement: The 2 Qwen3-VL entries are registered under ocr_vision

The system SHALL expose `qwen3-vl-8b` (role: `tier2_medium`) and
`qwen3-vl-4b` (role: `tier3_light`) in `MODEL_REGISTRY[family="ocr_vision"]`
so the capture pipeline can resolve them via
`model_for("ocr_vision", "tier2_medium")` etc.

#### Scenario: The M4-Max host selects qwen3-vl-8b for the Hades extractor

- **WHEN** the operator runs the pipeline on an M4-Max macOS host
- **THEN** `MODEL_REGISTRY.resolve("ocr_vision", "tier2_medium")` SHALL
  return `"qwen3-vl-8b"`.
