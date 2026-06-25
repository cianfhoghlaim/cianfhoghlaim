# Spec Delta — `author-archive-filesystem` (new capability)

## Purpose

`author-archive-filesystem` is a capability of the Cianfhoghlaim platform. This document is the canonical capability spec; the corresponding source code lives at `sruth/oideachais/dlt_sources/author_archive/`. See `docs/00_index.md` for the quadrant map and `docs/00-core/CLAUDE.md` for the project identity.

End-to-end filesystem ingestion of the personal archive directories `author_cian_deacy_lyons_mac_an_déisigh_uí_liatháin/gemini_deep_research/` and `author_cian_deacy_lyons_mac_an_déisigh_uí_liatháin/university_of_galway/`, with hash-based incremental discovery, content extraction (pymupdf for PDF, python-docx for DOCX), and DuckLake partitioning by `account` and `domain`.

## ADDED Requirements

### Requirement: Gemini Deep Research Filesystem Ingestion
The system SHALL discover and ingest every PDF in `author_cian_deacy_lyons_mac_an_déisigh_uí_liatháin/gemini_deep_research/` into the `author_archive_gemini_documents` DuckLake table.

#### Scenario: First-run full scan
- **GIVEN** the `author_archive_gemini_deep_research_raw` Dagster asset has not been materialised
- **WHEN** the asset is materialised
- **THEN** the `gemini_deep_research_source()` DLT source SHALL walk every `.pdf` under `gemini_deep_research/` recursively
- **AND** each discovered file SHALL be hashed (SHA-256) and tagged with `account="gemini_deep_research"`, `domain=<one of culture|law|medical|politics|technology|other|identity>`, `file_path`, `file_name`, `file_size`, `modified_at`
- **AND** the resulting rows SHALL be written to `oideachais.author_archive_gemini.documents` with `primary_key=["file_hash"]` and `write_disposition="merge"`

#### Scenario: Inline citation extraction
- **GIVEN** a Gemini PDF is being scanned
- **WHEN** the `gemini_citations` column is populated
- **THEN** PyMuPDF link annotations + first-page heading regex SHALL be used to extract a list of `(url, anchor_text)` tuples
- **AND** the resulting list SHALL be stored as a JSON column on the same row as the source PDF

#### Scenario: Incremental re-run
- **GIVEN** the `author_archive_gemini_deep_research_raw` asset has been materialised at least once
- **WHEN** the asset is re-materialised
- **THEN** only files whose SHA-256 has changed (or are newly added) SHALL be re-loaded
- **AND** the `FileHashTracker` (`sruth/oideachais/dlt_sources/author_archive/_scanner.py`) SHALL be the source of truth for the file-hash ledger

### Requirement: University of Galway Filesystem Ingestion
The system SHALL discover and ingest every supported file in `author_cian_deacy_lyons_mac_an_déisigh_uí_liatháin/university_of_galway/` into the `author_archive_uog_documents` DuckLake table.

#### Scenario: Multi-format discovery
- **GIVEN** the `author_archive_university_of_galway_raw` Dagster asset is materialised
- **WHEN** the source walks the directory
- **THEN** it SHALL yield one row per supported file (`.pdf`, `.docx`, `.doc`, `.pages`, `.pptx`, `.xlsx`, `.py`, `.ipynb`, `.js`, `.ts`, `.java`)
- **AND** each row SHALL be tagged with `account="university_of_galway"`, `domain=<one of education|irish|mata|past|software_development>`, and a `course_code` when the path matches `([A-Z]{2,3})(\d{3,4})`

#### Scenario: Handwriting flag
- **GIVEN** a file under `university_of_galway/mata/` or `university_of_galway/past/` is scanned
- **WHEN** the file extension is `.pages`, `.heic`, or the PDF appears to be scanned (image-only)
- **THEN** the row SHALL include `requires_handwriting_ocr=true`
- **AND** a separate `handwritten_pages` resource SHALL yield one row per such file (de-duplicated against the `all_documents` resource by `file_hash`)

#### Scenario: Content extraction
- **GIVEN** a PDF or DOCX file is being scanned
- **WHEN** the `pdf_documents` or `word_documents` resource yields the row
- **THEN** the text content SHALL be extracted with pymupdf or python-docx
- **AND** the extracted text SHALL be stored in a `full_text` JSON column
- **AND** the `detected_language` column SHALL be set to `"en"` (English-only) by the `_scanner.detect_language` heuristic

### Requirement: DuckLake Destination and Partitioning
The system SHALL write all three filesystem sources to the shared DuckLake destination configured by `sruth/oideachais/dlt_utils/destinations.py:118`.

#### Scenario: Local DuckLake
- **GIVEN** `DLT_ENVIRONMENT=local` (default) and `USE_DUCKLAKE=true`
- **WHEN** any `author_archive_*_raw` asset materialises
- **THEN** the destination SHALL be the local DuckLake on Garage S3 (`s3://ducklake/sruth/oideachais/`) with the PostgreSQL catalog at `localhost:5433`

#### Scenario: DuckDB fallback for tests
- **GIVEN** `USE_DUCKLAKE=false`
- **WHEN** the test suite runs
- **THEN** the destination SHALL be a local DuckDB file (`./.dlt/test_author_archive.duckdb`)

### Requirement: Multi-Account Account Label
The system SHALL support multiple accounts even in Phase 1 (filesystem only), so that adding a Google Takeout account in Phase 2 requires no schema change.

#### Scenario: Single-account Phase 1
- **GIVEN** only the UoG and Gemini directories exist on the workstation
- **WHEN** the assets materialise
- **THEN** every row SHALL have an `account` column with one of `"university_of_galway" | "gemini_deep_research" | "<account_label>"` (the last form is reserved for Phase 2 takeout accounts)

## MODIFIED Requirements

*(None — this is a new capability.)*

## REMOVED Requirements

*(None.)*
