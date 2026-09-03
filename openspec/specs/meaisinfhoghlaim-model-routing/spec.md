# Meaisínfhoghlaim Model Routing

## Purpose

The model routing logic at `meaisinfhoghlaim/models/routing.py` — the routing function that decides which OCR/VLM/embedder model to invoke per request. Routes every model invocation through `MODEL_REGISTRY` (no hardcoded model strings).

## Requirements

### Requirement: All routing entries use model_for() lookup

The system SHALL route every model routing entry in `meaisinfhoghlaim/models/routing.py` through `MODEL_REGISTRY.model_for(family, role, language=None)`. No hardcoded model strings SHALL remain.

#### Scenario: All qwen3-vl-8b routing entries migrated to model_for

- **WHEN** `mise run lint:registry` is invoked
- **THEN** the audit SHALL flag any `qwen3-vl-8b` hardcoded reference in `meaisinfhoghlaim/models/routing.py`
- **AND** the audit SHALL verify every routing entry uses `model_for("ocr_vision", "default")` or equivalent
