# meaisinfhoghlaim-ocr-htr — Delta for meaisinfhoghlaim Unsloth-Priority Refactor v1

## ADDED Requirements

### Requirement: ocr/ensemble/ MUST use Gemma 4 vision as the Tier 1 primary

The system MUST require `meaisinfhoghlaim/ocr/ensemble/` to use the
Gemma 4 26B-A4B-vision path as the Tier 1 primary (per the v5 model
priority change). The 4-path ensemble paths are:

- `baml` (Docling-serve)
- `unstract` (Unstract API)
- `gemma4_vision` (Gemma 4 26B-A4B-vision via llama-swap) — was `qwen3_vl`
- `gemma4` (Gemma 4 26B-A4B text-only via Unsloth Studio)

#### Scenario: Gemma 4 vision is the Tier 1 primary

- **WHEN** the operator runs the BIEP v2 4-path ensemble
- **THEN** the `gemma4_vision` path uses
  `local/ocr/gemma-4-26B-A4B-vision` (NOT `qwen3-vl-8b`)
- **AND** the DuckLake landing emits `{baml_canonical, unstract_json,
  gemma4, gemma4}` partitions

### Requirement: backends/scanned_detector.py MUST default to Gemma 4 vision

The system MUST require `meaisinfhoghlaim/backends/scanned_detector.py`
to default to `gemma-4-26b-a4b-vision` as the recommended backend
for the `recommended_backend` field.

#### Scenario: scanned_detector recommends Gemma 4

- **WHEN** `is_scanned=True AND image_ratio > 0.5`
- **THEN** `recommended_backend = "gemma-4-26b-a4b-vision"`
  (was `qwen3-vl-8b`)

### Requirement: datasets/irish_processing.py MUST default to Gemma 4 chain

The system MUST require `meaisinfhoghlaim/datasets/irish_processing.py`
to use the Gemma 4 fallback chain as the default.

#### Scenario: Irish processing uses Gemma 4

- **WHEN** `process_with_fallback(image_bytes, "gemma-4-e4b-vision")`
  is called
- **THEN** the chain tries Gemma 4 E4B → Gemma 4 26B-A4B →
  molmo2-8b → olmocr-2-7b → paddleocr-vl
- **AND** no `qwen3-vl` entry is in the chain

### Requirement: training/modal_finetune MUST use Gemma 4 base

The system MUST require
`meaisinfhoghlaim/training/modal_finetune/finetune_unsloth_local.py`
to default to the Gemma 4 26B-A4B base model + QLoRA + GGUF
export pipeline (was qwen3.8 27B).

#### Scenario: training default base model is Gemma 4

- **WHEN** `finetune_unsloth_local.py` runs
- **THEN** `base_model_id` defaults to
  `cianfhoghlaim/irish-gemma-4-26b-a4b-instruct`
- **AND** the checkpoint directory is `./checkpoints/irish-gemma-4`
- **AND** the GGUF export is `unsloth/gemma-4-26b-a4b-it-GGUF`