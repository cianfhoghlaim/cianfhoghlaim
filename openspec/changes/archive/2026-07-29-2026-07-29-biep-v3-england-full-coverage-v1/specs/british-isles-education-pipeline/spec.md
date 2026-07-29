## MODIFIED Requirements

### Requirement: England pipeline covers all 276 cohorts via the registry

The system SHALL provide a single generic England DLT pipeline
(`dlt/british_isles/england/education/england_jurisdiction_pipeline.py`)
that reads the canonical registry
(`cianfhoghlaim.education._registry.subjects` filtered by
`jurisdiction='england'`) and materialises every England cohort
(≥276 rows: 43 GCSE + 49 A-Level × 3 boards AQA + OCR + Edexcel).

The pipeline SHALL NOT introduce per-board per-subject Python files.
The 3 board-specific BAML functions
(`ExtractAQAQualSpec` / `ExtractOCRQualSpec` / `ExtractEdexcelQualSpec`)
are deprecated in favour of the generic
`ExtractUKQualSpec(board: AwardingBody, ...)`.

#### Scenario: England pipeline emits 276 rows

- **WHEN** `seed_registry()` is run + the lakehouse stack is healthy
- **THEN** the `england_jurisdiction_pipeline()` returns a DLT pipeline
  that materialises ≥276 rows to the
  `cianfhoghlaim.education.england.<stage>.<board>.<subject>` namespace
- **AND** the companion notebook Tab 2 shows `england >= 276`

#### Scenario: Generic ExtractUKQualSpec handles all 3 boards

- **WHEN** a Dagster asset invokes `b.ExtractUKQualSpec(board="aqa", ...)` /
  `(board="ocr", ...)` / `(board="edexcel", ...)`
- **THEN** the BAML client dispatches to the corresponding per-board
  extraction function
- **AND** the result is the canonical `AQAQualSpec` / `OCRQualSpec` /
  `EdexcelQualSpec` Pydantic class

#### Scenario: 3 generic England Dagster assets replace per-board assets

- **WHEN** `dg list assets | grep england_` runs
- **THEN** exactly 4 entries are listed (the same 4 as Ireland:
  ingestion + extraction + embedding + asset_check)
- **AND** zero per-board per-subject assets are present
  (`eng_aqa_mathematics_*`, etc.)