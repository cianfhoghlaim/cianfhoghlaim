# Spec Delta: meaisinfhoghlaim-ocr-htr

## MODIFIED Requirements

### Requirement: 20-entry vision model registry with Unsloth-first priority (post-M4-fit trim)

The system SHALL maintain a 20-entry v4 registry trimmed from 24 entries to fit on the M4 Max 48 GB unified memory. The 4 models removed are:

- **`qwen3-vl-235b-a22b`** (130 GB) — doesn't fit on M4 48 GB
- **`glm-4.6v-full`** (107 GB) — doesn't fit on M4 48 GB
- **`qwen3.6-35b-a3b-mtp`** (22 GB marginal) — use `qwen3.6-27b-mtp` (16 GB) instead
- **`gemma-4-31B`** (19 GB marginal) — use `gemma-4-26B-A4B` (14 GB) instead

The 20 remaining models all fit on the M4 Max 48 GB unified memory with the llama-swap dynamic-loader pattern (1 model + 1 mmproj in VRAM at a time).

The litellm gateway SHALL route 5 MLX community variants via `mlx-omni:10240` (Apple Silicon-optimized), 15 GGUF models via `llama-swap:8080` (Unsloth Q4_K_M), and 4 specialist models via `transformers:5000` (PyTorch).

#### Scenario: A developer adds a new Gemma 4 size that fits on M4

- **GIVEN** a developer adds a new Gemma 4 size variant to
  `cianfhoghlaim/ocr/models/registry.py:VISION_MODELS`
- **WHEN** the registry is imported
- **THEN** the registry MUST have ≥21 entries
- **AND** the entry's `m4_max_48gb_fit` MUST be `True`
- **AND** the entry's `arm1_oci_required` MUST be `False`
- **AND** the entry's `notes` MUST include "v4 — fits on M4 Max 48 GB"

#### Scenario: A developer tries to add a 100B+ model

- **GIVEN** a developer adds a 100B+ model variant to the registry
- **WHEN** `python scripts/validate_litellm_config.py` is run
- **THEN** the validation reports the model as "too large for M4 48 GB"
- **AND** the commit is blocked (exit code 1) — unless the entry's
  `available: bool = False` (a placeholder for future Modal deployment)
