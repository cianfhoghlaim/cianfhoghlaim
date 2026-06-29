# Spec Delta: meaisinfhoghlaim-platform

## MODIFIED Requirements

### Requirement: OCR Model Registry Location (v4) — IMPLEMENTED

The system SHALL expose the OCR model registry at `cianfhoghlaim/ocr/models/registry.py` (the v4 location, per Q4 2026). The registry MUST list **at least 24 vision models** covering the 6 VLM families + 6 specialist OCR families per the `meaisinfhoghlaim-ocr-htr` spec), **6 classical OCR Docker stacks**, and **3 text-only models** for the agent fleet. The legacy 9×6 model registry at `sruth/meaisinfhoghlaim/ocr/model_registry.py` is REPLACED. The 24+ entry registry uses **Unsloth-first fallback chains** (each model has `unsloth_id` → `mlx_id` → `upstream_id` keys).

The registry MUST NOT include cloud-API-only models (no OpenAI, no Anthropic). All entries must have at least one local inference path (Unsloth GGUF, mlx-community, or upstream safetensors on M4 Max 48 GB / arm1-oci).

#### Scenario: Dagster OCR dispatch uses the v4 registry

- **WHEN** Dagster materialises an Ireland Leaving Cert exam paper asset
- **THEN** the OCR dispatch MUST read from `cianfhoghlaim/ocr/models/registry.py:VISION_MODELS`
- **AND** the model MUST run on `llama-swap` (GGUF), `mlx-omni` (MLX), or `transformers` per the entry's `backend` field
- **AND** `get_default_for_m4_max()` MUST return `gemma-4-26B-A4B` (the Tier 2 default)
- **AND** the dispatch MUST prefer the `unsloth_id` over the `upstream_id`

### Requirement: 6-stage PDF processing pipeline

The system SHALL expose a 6-stage PDF processing pipeline at `cianfhoghlaim/assets/_oideachais_dagster_defs/assets/pdf_processing/`. The pipeline processes NCCA syllabus PDFs, SEC past paper PDFs, and SEC marking-scheme PDFs through the 6 stages:

1. **OCR (VLM dispatch)** — selects optimal (model, backend) pair from VISION_MODELS
2. **Diagram detection** — Granite-Docling DocTags + Molmo2-8B pointing
3. **BAML extraction** — schema-validated LLM extraction via litellm
4. **Topic validation** — fuzzy-match against NCCA taxonomy
5. **Semantic chunking** — CocoIndex v1 + BGE-M3 embedder
6. **Lakehouse + Cognee + Graphiti** — write to DuckLake + cognify + temporal episode

The pipeline is exposed via FastAPI at `cianfhoghlaim/agents/api/_oideachais_api/routes/pdf_processing.py` and visualised in marimo at `cianfhoghlaim/notebooks/meaisinfhoghlaim/marimo/03_pdf_processing.py`.

See `oideachais-pdf-processing/spec.md` for the full 6-stage specification.

#### Scenario: A leaving_cert asset triggers the 6-stage pipeline

- **GIVEN** a 2024 LC Irish past paper PDF is uploaded to `stedding/ingest_queue/examinations.ie/`
- **WHEN** the `pdf_processing_past_paper` Dagster asset materialises
- **THEN** the 6-stage pipeline at `cianfhoghlaim/assets/_oideachais_dagster_defs/assets/pdf_processing/pipeline.py` is invoked
- **AND** the 6 stages run in sequence with intermediate state written to `motherduck://oideachais.pdf_processing.{subject}.{year}.{paper}.*` tables
