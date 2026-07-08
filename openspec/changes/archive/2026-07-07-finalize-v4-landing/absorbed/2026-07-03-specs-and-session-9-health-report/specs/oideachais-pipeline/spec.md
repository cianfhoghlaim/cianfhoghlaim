## ADDED Requirements

### Requirement: LC5-subject pipeline + Gemini 6-corpus pipeline

The `oideachais-pipeline` capability SHALL include 2 new pipelines:

1. **LC5-subject pipeline** (per
   `openspec/changes/2026-07-03-leaving-cert-5-subject-pipeline-with-diagrams/`):
   41 PDFs + 2 JPGs across chemistry / computer_science / gaeilge /
   geography / mathematics. Organised into 5 DAGs each with 7 stages
   (VLM/OCR → DuckLake → LanceDB → Cognee → Graphiti → FalkorDB).

2. **Gemini 6-corpus pipeline** (per
   `openspec/changes/2026-07-03-gemini-6-corpus-pipeline/`):
   224 PDFs across law / medical / politics / culture / technology /
   other. Organised into 6 DAGs each with 7 stages.

#### Scenario: LC5 ingests 72 PDFs total (5 subjects × EN/GA + 1 JPG + duplicates)

- **WHEN** `dagster asset materialize --select 'lc5_*_ingested'`
- **THEN** the sum of rows from `lc5_chemistry_ingested`,
  `lc5_computer_science_ingested`, `lc5_gaeilge_ingested`,
  `lc5_geography_ingested`, `lc5_mathematics_ingested` SHALL be
  **72** (41 PDFs + 1 JPG + 30 `_2026-06-30` duplicate copies)

#### Scenario: Gemini ingests 224 PDFs across 6 corpora

- **WHEN** `dagster asset materialize --select 'gemini_*_ingested'`
- **THEN** the sum SHALL be 224 (57 law + 54 medical + 47 politics
  + 30 culture + 24 technology + 12 other; verified 2026-07-04)

#### Scenario: Both pipelines share the v4 OCR/VLM registry

- **GIVEN** both pipelines are deployed
- **WHEN** a PDF is ingested
- **THEN** `select_ocr_backend(pdf_path)` (LC5) or the
  `gemini_corpus_source._classify_pdf(pdf_path)` heuristic
  (Gemini) SHALL return a v4 registry model key
- **AND** the chosen model SHALL be loaded from llama-swap :8080
  (Unsloth GGUF) or inline via the dagster image's 12 Python packages

#### Scenario: The cross-subject FalkorDB graph spans 11 datasets

- **GIVEN** both pipelines are deployed
- **WHEN** the L3 cognify DAGs run
- **THEN** the resulting FalkorDB graph SHALL contain 11 datasets
  (5 LC + 6 Gemini) and support cross-corpus queries between them
