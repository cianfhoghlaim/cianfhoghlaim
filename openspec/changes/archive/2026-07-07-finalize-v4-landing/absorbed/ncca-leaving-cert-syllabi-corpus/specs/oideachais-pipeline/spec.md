## ADDED Requirements

### Requirement: NCCA leaving-cert syllabi corpus enumeration
The system SHALL enumerate, for each of the 8 priority Leaving Certificate subjects (mathematics, applied-mathematics, chemistry, geography, history, english, gaeilge, computer-science) and each of the 2 languages (en, ga), the canonical currently-taught syllabus PDF URL hosted on `curriculumonline.ie`. The system MUST emit a `curriculumonline_syllabi` dlt resource with one row per (subject, language, pdf_url) tuple and a SHA-256 content hash for downstream dedup. The system SHALL document any (subject, language) combination where no syllabus exists (e.g. gaeilge in en, or where the GA-equivalent is the same as the EN PDF) in the resource output rather than silently omitting it.

#### Scenario: Both EN and GA syllabi exist
- **WHEN** the curriculumonline_syllabi source is materialised for `subject="english"`, `language="en"`
- **THEN** the resource yields exactly one row pointing to `curriculumonline.ie/getmedia/.../SCSEC14_English_Syllabus.pdf`
- **AND** materialising again with `language="ga"` yields zero rows with a `(subject, language, status="ga_uses_en")` provenance record
- **AND** both rows carry a stable `sha256` value computed from the PDF bytes (only the EN row, the GA row is a status provenance record)

#### Scenario: GA version does not exist
- **WHEN** the curriculumonline_syllabi source is materialised for `subject="gaeilge"`, `language="en"`
- **THEN** the resource yields zero rows
- **AND** a `(subject, language, status="not_available")` provenance record is written to the `source_provenance` resource
- **AND** the asset partition `(gaeilge, en)` is registered as `no-op` in the Dagster metadata so downstream does not block

#### Scenario: Cloudflare bot challenge triggers fallback
- **WHEN** Firecrawl returns a Cloudflare challenge page for a subject
- **THEN** the system SHALL fall back to `USE_LOCAL_SCRAPES=true` and serve the cached scrape from `stedding/ingest_queue/curriculumonline.ie/`
- **AND** if neither live nor cache yields a PDF URL, the system SHALL yield a `(subject, language, status="scrape_failed")` provenance record and continue rather than crashing

### Requirement: NCCA leaving-cert syllabi corpus download
The system SHALL provide a Dagster asset `lc_syllabus_download` with `MultiPartitionsDefinition(subject × language)` that, for a given (subject, language) partition, downloads each PDF URL emitted by the curriculumonline_syllabi source into `stedding/ingest_queue/curriculumonline.ie/{subject}/{lang}/{filename}.pdf`. The system MUST compute and store the SHA-256 of the downloaded file alongside the bytes, and MUST be idempotent — re-materialising a partition with unchanged upstream content SHALL be a no-op (no rewrite, no new Dagster run history entry beyond `UP_TO_DATE`). The system MUST emit Dagster `MaterializeResult` metadata with `url`, `filename`, `size_bytes`, `sha256`, `skipped` (bool), `http_status` (int).

#### Scenario: First-time download of a syllabus
- **WHEN** the `(mathematics, en)` partition is materialised for the first time
- **THEN** the file `stedding/ingest_queue/curriculumonline.ie/mathematics/en/SCSEC25_Maths_syllabus_examination-2015_English.pdf` exists on disk
- **AND** its SHA-256 matches the value emitted in the dlt resource
- **AND** the MaterializeResult metadata reports `size_bytes`, `http_status=200`, `skipped=false`

#### Scenario: Re-materialisation with unchanged content
- **WHEN** the `(mathematics, en)` partition is re-materialised and the upstream URL still returns identical bytes
- **THEN** the file on disk is NOT rewritten
- **AND** the MaterializeResult metadata reports `skipped=true`
- **AND** the Dagster run is recorded as `UP_TO_DATE` rather than `REEXECUTED`

#### Scenario: Upstream changes content
- **WHEN** NCCA republishes the syllabus PDF (new SHA-256) and the `(mathematics, en)` partition is re-materialised
- **THEN** the file on disk is overwritten with the new bytes
- **AND** the MaterializeResult metadata reports `skipped=false`, `sha256=<new hash>`

### Requirement: BAML syllabus level-section extraction
The system SHALL provide a BAML function `ExtractSyllabusStructure(pdf: Pdf, subject: str, language: str) -> SyllabusStructure` that parses a combined Leaving Certificate syllabus PDF and returns its logical level sections (Foundation, Ordinary, Higher — only the levels the subject is examined at). The system MUST identify the page range, chapter count, and topic count for each level section, and SHALL return the subject overview and assessment overview as plain text. The function MUST be implemented as a pure BAML function using the `ExtractEnStrong` client (or `ExtractGaStrong` for Irish-language syllabi) and MUST NOT perform any I/O.

#### Scenario: Mathematics syllabus has 3 levels
- **WHEN** `ExtractSyllabusStructure` is called with the Mathematics EN syllabus PDF
- **THEN** the returned `SyllabusStructure.level_sections` contains exactly 3 entries: one for Foundation, one for Ordinary, one for Higher
- **AND** each entry includes a non-empty `page_range` and `learning_outcomes` list

#### Scenario: English syllabus has 2 levels
- **WHEN** `ExtractSyllabusStructure` is called with the English EN syllabus PDF
- **THEN** the returned `level_sections` contains exactly 2 entries (Ordinary, Higher)
- **AND** no Foundation entry is present

#### Scenario: Gaeilge syllabus is in Irish
- **WHEN** `ExtractSyllabusStructure` is called with the Gaeilge GA syllabus PDF
- **THEN** the function uses the `ExtractGaStrong` client
- **AND** the returned `subject_overview` and `assessment_overview` strings are in Irish
- **AND** the returned level sections correctly identify the Gnáthleibhéal / Árdleibhéal / Bonnleibhéal labels
