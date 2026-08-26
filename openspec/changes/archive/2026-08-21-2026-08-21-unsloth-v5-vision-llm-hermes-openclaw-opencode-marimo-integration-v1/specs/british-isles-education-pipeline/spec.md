## ADDED Requirements

### Requirement: The 6 BIEP LC subjects have a 10-way OCR/VLM comparison surface

The British-Isles Education Pipeline SHALL expose a marimo notebook (`notebooks/30_unsloth_vision_compare.py`) that lets the operator compare 10 backends — 6 Unsloth VLMs from `MODEL_REGISTRY.filter(family="ocr_vision")` + 4 classical OCR backends (Docling, dots-ocr, OlmOCR, PaddleOCR) — against the 6 BIEP LC subjects' PDFs (Mathematics, Chemistry, Geography, Gaeilge, English, Computer Science). The notebook is human-driven only (no Dagster asset wiring).

#### Scenario: 10-way comparison of 4 backends on a BIEP PDF

- **GIVEN** the marimo notebook is opened at `m.cianfhoghlaim.ie/unsloth-compare`
- **WHEN** the operator selects 4 backends (e.g. Qwen3-VL-8B, GLM-4.6V-Flash, Docling, OlmOCR) and 1 Gaeilge PDF
- **THEN** the notebook sends 4 requests in parallel via the ocr-router :8090 gateway
- **AND** displays the 4 outputs side-by-side with latency, tokens (for VLMs) / regions (for classical), and the model's published KL-divergence benchmark (for VLMs) or CER/WER (for classical OCR)
- **AND** the operator can filter by `ModelCapability` (DENSE_OCR / GROUNDING / TABLES / LATEX / REASONING / MULTILINGUAL / GAELIC / DIAGRAM)
- **AND** the comparison results export to `stedding/eval_results/unsloth_compare_{model_role}_{pdf_hash}.json`
- **AND** the notebook imports `from notebooks._shared.schema import list_pipelines` for the PDF picker
- **AND** `mise run lint:registry` exits 0 with no hardcoded model strings in the notebook

#### Scenario: Notebook is human-driven, not a Dagster asset

- **WHEN** the BIEP spec is audited for asset health
- **THEN** the notebook does NOT appear in `orchestration/defs/4_asset_generation/` or `5_agent_ops/`
- **AND** no Dagster sensor monitors `stedding/eval_results/`
- **AND** the notebook is launched only via the marimo UI or `mise run notebook:unsloth-compare`
- **AND** the outputs are still readable by future Dagster assets (no write-side schema change)

#### Scenario: Notebook uses the canonical MODEL_REGISTRY

- **WHEN** the notebook is rendered
- **THEN** the model picker is populated from `MODEL_REGISTRY.filter(family="ocr_vision")` (no hardcoded model strings)
- **AND** `mise run lint:registry` exits 0 with no hardcoded model strings in the notebook
- **AND** the notebook imports `from notebooks._shared.schema import list_pipelines, list_dlt_sources` for the PDF picker
