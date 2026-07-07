# Spec Delta: meaisinfhoghlaim-platform

## MODIFIED Requirements

### Requirement: OCR Model Registry Location (v4) — 20-entry trim for M4 Max

The system SHALL expose the OCR model registry at `cianfhoghlaim/ocr/models/registry.py`. The registry SHALL list **at least 20 vision models** (the 24-entry v4 registry trimmed of 4 models that don't fit on M4 48 GB: qwen3-vl-235b-a22b 130GB, glm-4.6v-full 107GB, qwen3.6-35b-a3b-mtp 22GB marginal, gemma-4-31B 19GB marginal). The legacy 9×6 model registry at `sruth/meaisinfhoghlaim/ocr/model_registry.py` is REPLACED (gpt_4o, claude_3_5_sonnet, llama_3_2_vision, uccix_13b are removed; classical OCR stacks stay separate as Docker compose).

The 20 models SHALL be served via 3 backends per the per-model backend URL strategy:
- **llama-swap :8080** (Unsloth Q4_K_M, dynamic-load 1 model at a time) for the 15 GGUF models
- **mlx-omni :10240** (Apple Silicon MLX) for the 5 MLX community variants
- **transformers :5000** (PyTorch) for the 4 specialist models (molmo2-4b, molmo2-8b, deepseek-ocr-2, olmocr-2-7b-1025)

#### Scenario: A Dagster asset materialises on the M4 Max

- **GIVEN** a developer runs `mise run dagster:oideachais` on the M4 Max
- **WHEN** the `pdf_processing_syllabus` Dagster asset materialises
- **THEN** Stage 1 dispatches to `gemma-4-26B-A4B` (the M4 default) via llama-swap
- **AND** the model loads in ~15s (Unsloth GGUF Q4_K_M, 14GB resident)
- **AND** Stage 5 chunks into 12 topic chunks + 8 figure chunks + 12 BGE-M3 embeddings
- **AND** Stage 6 writes to `ducklake://oideachais.assets.official_documents.syllabi.mathematics.2024` + creates 20 Cognee nodes + 1 Graphiti episode
- **AND** the marimo dashboard at `/dashboards/pdf-processing?subject=mathematics&year=2024` renders within 60 seconds
