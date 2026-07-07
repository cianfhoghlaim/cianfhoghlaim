# Spec Delta: oideachais-pdf-processing

## MODIFIED Requirements

### Requirement: 6-stage PDF processing pipeline uses 20 v4 models that fit on M4 Max

The 6-stage pipeline at `cianfhoghlaim/assets/_oideachais_dagster_defs/assets/pdf_processing/pipeline.py` MUST use the 20 v4 models that fit on M4 Max 48 GB unified memory. The 4 models removed from the v4 registry (qwen3-vl-235b-a22b 130GB, glm-4.6v-full 107GB, qwen3.6-35b-a3b-mtp 22GB marginal, gemma-4-31B 19GB marginal) are documented in `openspec/changes/deploy-v4-ocr-vlm-on-m4-max/proposal.md` as "too large for M4 48 GB; use a smaller alternative".

For each of the 6 stages, the litellm gateway routes to the appropriate backend:
- **GGUF models** → `http://llama-swap:8080/v1` (Unsloth Q4_K_M)
- **MLX community variants** → `http://mlx-omni:10240/v1` (Apple Silicon MLX)
- **Specialists** (molmo2-*, deepseek-ocr-2, olmocr-2-7b-1025) → `http://transformers:5000/v1` (PyTorch)

The human-review Gradio HF Space at `spaces/oideachais-pdf-review/` runs on HuggingFace Spaces ZeroGPU (free tier), using the v4 Unsloth GGUFs `unsloth/gemma-3-4b-it-GGUF` (suggested correction) and `unsloth/gemma-4-26B-A4B-it-GGUF` (explanation).

#### Scenario: The 6-stage pipeline runs on the M4 Max

- **GIVEN** a 50-page NCCA mathematics syllabus PDF is uploaded to
  `stedding/ingest_queue/ncca.ie/`
- **WHEN** the `pdf_processing_syllabus` Dagster asset materialises
- **THEN** Stage 1 dispatches to `gemma-4-26B-A4B` (the M4 default) via llama-swap
- **AND** the OCR completes in ~90 seconds (Unsloth GGUF, 14GB resident, Apple Silicon GPU)
- **AND** Stage 2 detects 8 figure regions via Granite-Docling DocTags + 8 bounding boxes via Molmo2-8B
- **AND** Stage 3 calls `b.ExtractLeavingCertSyllabus()` and produces 12 `SyllabusTopic` records
- **AND** Stage 4 validates all 12 topics against the NCCA taxonomy (≥95% pass rate)
- **AND** Stage 5 chunks into 12 topic chunks + 8 figure chunks + 20 BGE-M3 embeddings → 40 chunks in LanceDB
- **AND** Stage 6 writes to `ducklake://oideachais.assets.official_documents.syllabi.mathematics.2024` + creates 28 Cognee nodes + 1 Graphiti episode
- **AND** the marimo dashboard renders the 6-stage status within 60 seconds
