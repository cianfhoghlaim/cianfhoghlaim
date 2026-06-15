# Spec Delta — `author-archive-baml-extraction` (new capability)

## Purpose

`author-archive-baml-extraction` is a capability of the Cianfhoghlaim platform. This document is the canonical capability spec; the corresponding BAML schema lives at `baml_src/author_archive.baml`. See `docs/00_index.md` for the quadrant map and `docs/00-core/CLAUDE.md` for the project identity.

Structured extraction of the Gemini Deep Research reports, University of Galway artefacts, and handwritten equations using BAML. The extracted rows feed the CocoIndex embedding flow and the DuckDB-side metadata tables. English-only for this change.

## ADDED Requirements

### Requirement: Gemini Report Extraction
The system SHALL extract structured fields from every Gemini Deep Research PDF using the BAML `ExtractGeminiReport` function.

#### Scenario: Function defined
- **GIVEN** `baml_src/author_archive.baml` is generated (`mise run baml:generate`)
- **WHEN** the function is invoked with `(pdf_text, file_name)` for a Gemini PDF
- **THEN** the BAML client SHALL return a `GeminiDeepResearchReport` instance with `topic: string`, `domain: GeminiDomain` (one of `law|medical|politics|technology|culture|other|identity|education`), `summary: string`, `key_findings: string[]`, `cited_urls: CitedUrl[]`, `gemini_account: string | null`, `research_date: date | null`

#### Scenario: Memoisation
- **GIVEN** the same `file_hash` has been extracted before
- **WHEN** the `author_archive_baml_extraction` Dagster asset materialises
- **THEN** the asset SHALL skip the BAML call and reuse the cached `GeminiDeepResearchReport` from the `author_archive.extraction_metadata` DuckDB table
- **AND** the cache key SHALL be `(file_hash, baml_function_name)`

### Requirement: University of Galway Artefact Extraction
The system SHALL extract structured fields from every University of Galway PDF and DOCX using the BAML `ExtractUoGArtifact` function.

#### Scenario: Function defined
- **GIVEN** `baml_src/author_archive.baml` is generated
- **WHEN** the function is invoked with `(pdf_text, file_name, file_type)` for a UoG document
- **THEN** the BAML client SHALL return a `UniversityOfGalwayArtifact` instance with `artifact_kind: UoGArtifactKind` (one of `assignment|exam|lecture_notes|action_research|placement|code_file|scanned_pages|presentation|transcript`), `course_code: string | null`, `module_title: string | null`, `stage: UoGStage` (one of `undergraduate|pgce|masters|phd|professional`), `language: UoGLanguage` (always `"en"` for this change), `key_topics: string[]`, `requires_handwriting_ocr: bool`

#### Scenario: Course code propagation
- **GIVEN** a UoG PDF whose path matches `([A-Z]{2,3})(\d{3,4})` (e.g. `ed305_assignment_1.pdf`)
- **WHEN** the `extraction_metadata` resource yields the row
- **THEN** the `course_code` column SHALL be populated by the dlt scanner (regex match) AND by the BAML extractor (semantic match); the BAML value SHALL win on conflict

### Requirement: Handwritten Equation Extraction
The system SHALL extract handwritten equations from OCR'd pages using the BAML `ExtractHandwrittenEquations` function.

#### Scenario: Function defined
- **GIVEN** `baml_src/author_archive.baml` is generated
- **WHEN** the function is invoked with `(ocr_text, file_name)` for a handwritten page
- **THEN** the BAML client SHALL return a `HandwrittenEquation[]` where each element has `latex: string`, `verbatim: string`, `context: string`, `confidence: float` (clamped 0.0-1.0)

#### Scenario: Empty OCR text
- **GIVEN** `ocr_text` is the empty string (OCR back-end not available on the workstation)
- **WHEN** the function is invoked
- **THEN** the function SHALL return an empty list
- **AND** the `author_archive_equations_index` Dagster asset SHALL skip that file

### Requirement: BAML Client Alias
The system SHALL use the canonical `extract_en` BAML client alias for all three functions.

#### Scenario: Client alias registration
- **GIVEN** `baml_src/clients.baml` and `baml_src/generators.baml` are updated
- **WHEN** `mise run baml:generate` runs
- **THEN** the BAML compiler SHALL emit a Python client with `b.ExtractGeminiReport`, `b.ExtractUoGArtifact`, and `b.ExtractHandwrittenEquations` functions
- **AND** the default `client_name` for these functions SHALL be `extract_en` (pointing at `litellm/gemini-2.0-flash`)
- **AND** a fallback `client_name` `extract_en_strong` SHALL be available (pointing at `litellm/anthropic/claude-sonnet-4-20250514`) for difficult extractions

#### Scenario: Test coverage
- **GIVEN** `baml_src/author_archive.baml` defines `test ExtractGeminiReportTest`, `test ExtractUoGArtifactTest`, and `test ExtractHandwrittenEquationsTest`
- **WHEN** `mise run baml:test` runs
- **THEN** the existing 30+ BAML tests SHALL still pass
- **AND** the 3 new tests SHALL pass against a deterministic fixture (`gemini_sample.txt`, `uog_sample.txt`, `equation_sample.txt`) committed under `baml_src/fixtures/`

## MODIFIED Requirements

*(None.)*

## REMOVED Requirements

*(None.)*
