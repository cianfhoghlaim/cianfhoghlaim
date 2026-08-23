# Spec Delta: meaisinfoghlaim-ocr-htr

## ADDED Requirements

### Requirement: BIEP v2 4-path OCR ensemble SHALL perform real VLM calls

The system SHALL invoke 4 paths in parallel via `asyncio.gather()` for every incoming PDF row in the `lc5_<subject>_scanned_pdfs_ingested` asset.

**WHEN** the `biiep_ocr_ensemble` Dagster asset materializes with at least 1 scanned PDF row from `lc5_<subject>_scanned_pdfs_ingested`
**THEN** the 4-path ensemble SHALL fire all 4 calls in parallel within `asyncio.gather()`
**AND** the asset body SHALL return `{rows_landed: N, ragas_passed: bool, ragas_score: float, voted_path: str}` where N >= 1
**AND** the `biiep_ocr_ensemble_ragas_check` asset check SHALL pass when `ragas_score >= 0.70`

#### Scenario: Ensemble processes a scanned PDF via all 4 paths

- **WHEN** the operator runs `dagster asset materialize --select biiep_ocr_ensemble`
- **AND** `md:cianfhoghlaim.bronze.ireland_leaving_cert.lc5_documents` has at least 1 row where `is_scanned=True`
- **THEN** the asset materializes with `rows_landed >= 1`
- **AND** the `biiep_ocr_ensemble_ragas_check` asset check passes

#### Scenario: Ensemble returns ragas_passed=True when no scanned PDFs exist

- **WHEN** `md:cianfhoghlaim.bronze.ireland_leaving_cert.lc5_documents` has 0 rows where `is_scanned=True`
- **THEN** the asset returns `{rows_landed: 0, ragas_passed: True, ragas_score: 1.0, voted_path: None}`

### Requirement: PDF→text extraction SHALL detect scanned-vs-digital at the file level

The shared `extract_pdf_text()` helper in `dlt_sources/british_isles/ireland/education/_pdf_text.py` SHALL call `is_scanned_pdf(path)` from `meaisinfoghlaim/backends/scanned_detector.py` BEFORE returning the text-layer extraction.

**WHEN** a PDF row is detected as scanned
**THEN** the DLT source `_row()` SHALL emit `is_scanned=True` + `image_ratio` + `recommended_backend` + `page_count` columns

#### Scenario: Scanned PDF detection returns is_scanned=True for image-only PDFs

- **WHEN** `is_scanned_pdf()` is called with a PDF whose `pymupdf.get_text()` returns empty text across all pages
- **THEN** the returned `ScannedPDFReport` has `is_scanned=True`
- **AND** `recommended_backend` is `qwen3-vl-8b` (if image_ratio > 0.5) or `docling-serve` (if image_ratio <= 0.5)

#### Scenario: Digital PDF detection returns is_scanned=False for text-layer PDFs

- **WHEN** `is_scanned_pdf()` is called with a PDF whose `pymupdf.get_text()` returns > 50 chars across pages
- **THEN** the returned `ScannedPDFReport` has `is_scanned=False`

### Requirement: OCR results table SHALL be persisted to MotherDuck

The `md:cianfhoghlaim.ocr_results` table SHALL exist with the canonical schema:

```sql
CREATE TABLE IF NOT EXISTS cianfhoghlaim.ocr_results (
    document_id   VARCHAR PRIMARY KEY,
    content_hash  VARCHAR NOT NULL,
    model_used    VARCHAR NOT NULL,
    confidence    DOUBLE  NOT NULL,
    raw_text      TEXT    NOT NULL,
    latency_ms    INTEGER NOT NULL,
    success       BOOLEAN NOT NULL,
    created_at    TIMESTAMP NOT NULL DEFAULT now()
)
```

#### Scenario: Migration script creates the ocr_results table

- **WHEN** the operator runs `uv run python scripts/migrate_ocr_results_table.py`
- **THEN** the script connects to `md:cianfhoghlaim`
- **AND** runs `CREATE SCHEMA IF NOT EXISTS cianfhoghlaim.cianfhoghlaim`
- **AND** runs `CREATE TABLE IF NOT EXISTS cianfhoghlaim.cianfhoghlaim.ocr_results (...)`

## ADDED Requirements

### Requirement: `_run_path_baml()` SHALL call the real BAML function

The `_run_path_baml()` method in `meaisinfoghlaim/ocr/ensemble/ensembled_extractor.py` SHALL:

1. Call `_call_docling(pdf_path, self.docling_url)` to get the raw text
2. Call `from baml_client.baml_client.sync_client import b` to import the BAML client
3. Invoke `getattr(b, baml_function)(text=_docling_text)` (e.g. `b.ExtractCurriculumSyllabus(text=...)`)
4. Serialise the typed result to JSON via `result.model_dump_json()`

**WHEN** a PDF is processed
**THEN** the BAML path SHALL emit a real `EnsemblePathOutput(raw_response=<baml_output_json>, confidence_score=0.85, schema_valid=True)`

#### Scenario: BAML path returns real Pydantic JSON

- **WHEN** the BIEP v2 ensemble processes a PDF
- **AND** the BAML function `ExtractCurriculumSyllabus(text=<docling_text>, subject="chemistry")` is invoked
- **THEN** the result is a Pydantic model with `.model_dump_json()` method
- **AND** `EnsemblePathOutput.raw_response` contains the JSON string
