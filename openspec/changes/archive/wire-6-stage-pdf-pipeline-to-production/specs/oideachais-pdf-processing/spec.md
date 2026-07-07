# Spec Delta: oideachais-pdf-processing

## MODIFIED Requirements

### Requirement: 6-stage PDF processing pipeline is wired to production

The 6-stage pipeline at `cianfhoghlaim/assets/_oideachais_dagster_defs/assets/pdf_processing/pipeline.py` MUST use the real ML model calls (not stubs) for Stages 1, 2, 3, 4, 5, 6. Specifically:

- **Stage 1 (OCR)** — MUST call `litellm.completion()` against
  the v4 Unsloth GGUF served by llama-swap (per
  `select_ocr_backend()` in `cianfhoghlaim/ocr/models/registry.py`)
- **Stage 2 (Diagram detection)** — MUST call Granite-Docling 258M
  via the `transformers` backend AND Molmo2-8B for figure pointing
- **Stage 3 (BAML extraction)** — MUST call the regenerated
  `baml_client` for `ExtractLeavingCertSyllabus`,
  `ExtractPastPaper`, and `ExtractMarkingScheme`
- **Stage 4 (Topic validation)** — MUST load the NCCA taxonomy
  from `ducklake://oideachais.assets.official_documents.syllabus.<subject>`
- **Stage 5 (Semantic chunking)** — MUST embed with BGE-M3
  (1024-dim) in batches of 100+ and write to
  `lancedb://oideachais.pdf_processing_chunks`
- **Stage 6 (Lakehouse)** — MUST write to DuckLake + Cognee cognify
  + Graphiti episode append

The pipeline MUST be wrapped in the `trace_pipeline()` observability
context manager (per `observability.py`) which logs to Langfuse +
MLflow + Logfire and posts RAGAS-style BAML extraction quality scores.

The 3 Dagster assets (`pdf_processing_syllabus`,
`pdf_processing_past_paper`, `pdf_processing_marking_scheme`) MUST be
registered in the v4 code-location
(`cianfhoghlaim/assets/_oideachais_dagster_defs/defs.yaml`).

#### Scenario: The 6-stage pipeline processes a real NCCA syllabus

- **GIVEN** a 50-page NCCA mathematics syllabus PDF is uploaded to
  `stedding/ingest_queue/ncca.ie/`
- **WHEN** the `pdf_processing_syllabus` Dagster asset materialises
- **THEN** Stage 1 dispatches to `gemma-4-26B-A4B` (the M4 default)
  via llama-swap and produces per-page text
- **AND** Stage 2 detects 8 figure regions via Granite-Docling + 8
  bounding boxes via Molmo2-8B
- **AND** Stage 3 calls `b.ExtractLeavingCertSyllabus()` and produces
  12 `SyllabusTopic` records
- **AND** Stage 4 validates all 12 topics against the NCCA taxonomy
  (≥95% pass rate)
- **AND** Stage 5 chunks into 12 topic chunks + 8 figure chunks +
  12 BGE-M3 embeddings → 32 chunks in LanceDB
- **AND** Stage 6 writes to `ducklake://oideachais.assets.official_documents.syllabi.mathematics.2024`
  + creates 20 Cognee nodes + 1 Graphiti episode
- **AND** the marimo dashboard at `/dashboards/pdf-processing?subject=mathematics&year=2024` renders within 60 seconds
- **AND** the Langfuse trace shows all 6 stages with their durations
- **AND** the MLflow run logs 30+ metrics (per stage + RAGAS)
- **AND** the Logfire event logs the pipeline completion
