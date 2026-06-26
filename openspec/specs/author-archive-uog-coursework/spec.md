# author-archive-uog-coursework Specification

## Purpose
TBD - created by archiving change author-archive-uog-coursework. Update Purpose after archive.
## Requirements
### Requirement: BAML extraction per UoG module

The system MUST provide one BAML function per UoG module that takes
the raw text + filename + file_type and returns a
`UoGModuleExtraction` record. Each function MUST set the `subject`
field to the matching `UoGSubject` enum value.

#### Scenario: Mathematics module

- **WHEN** a file in `leabharlann/ollscoil_na_gaillimhe/mata/` is extracted
- **THEN** the BAML function `ExtractUoGMathModule` is called
- **AND** the returned record has `subject = MATA`
- **AND** the `key_equations` field contains any LaTeX strings from
  the artefact (cryptography proofs, statistics equations, etc.)

#### Scenario: Irish module with bilingual content

- **WHEN** a file in `leabharlann/ollscoil_na_gaillimhe/irish/` is extracted
- **AND** the artefact contains significant Irish (Gaeilge) prose
- **THEN** the returned record has `subject = IRISH`
- **AND** `language = GA` or `MIXED`
- **AND** `has_gaelic_content = true`

#### Scenario: Personal record from achievement subdir

- **WHEN** a file in `cian_mac_an_déisigh_uí_liatháin/achievement/` is extracted
- **THEN** the BAML function `ExtractPersonalRecord` is called
- **AND** the `subdir` argument is `"achievement"`
- **AND** the returned record has `subject = PERSONAL`

### Requirement: DLT source per UoG module

The system MUST provide one DLT source per UoG module at
`sruth/oideachais/dlt_sources/leabharlann/olscoil_<module>.py`. Each
source MUST expose a `_documents` resource (the filesystem scan)
and an `_extraction` resource (the BAML extraction).

#### Scenario: Mata filesystem scan

- **WHEN** the `mata_source()` DLT source is loaded
- **THEN** the `mata_documents` resource yields one row per file in
  `leabharlann/ollscoil_na_gaillimhe/mata/`
- **AND** the row's `account` is `"uog_mata"`
- **AND** the row's `file_hash` is the sha256 of the file contents

#### Scenario: Personal records identity exclusion

- **WHEN** the `personal_records_source()` DLT source is loaded
- **AND** `INCLUDE_IDENTITY_RECORDS` env var is not set to `"true"`
- **THEN** the `personal_records` resource only yields rows from
  `achievement/` and `teaching/` subdirs
- **AND** no rows from `identity/` are yielded

#### Scenario: Personal records with identity override

- **WHEN** the `personal_records_source()` DLT source is loaded
- **AND** `INCLUDE_IDENTITY_RECORDS=true`
- **THEN** the `personal_records` resource yields rows from
  `achievement/`, `teaching/`, AND `identity/`

### Requirement: Dagster assets per UoG module

The system MUST provide two Dagster assets per UoG module:
`<module>_raw` (the filesystem scan) and `<module>_extraction`
(the BAML extraction). The mata, software, education, and
personal_records assets MUST be partitioned on their sub-directory.
The irish asset is unpartitioned (the irish/ tree is flat).

#### Scenario: Mata partition

- **WHEN** the `author_archive_uog_mata_raw` asset is materialised
  with partition key `"cs402_cryptography"`
- **THEN** the DLT source runs over
  `leabharlann/ollscoil_na_gaillimhe/mata/cs402_cryptography/`
- **AND** the returned MaterializeResult has `partition = "cs402_cryptography"`

#### Scenario: Education partition

- **WHEN** the `author_archive_uog_education_raw` asset is materialised
  with partition key `"1bme1"`
- **THEN** the DLT source runs over
  `leabharlann/ollscoil_na_gaillimhe/education/1bme1/`

### Requirement: Personal records identity subdir is private

The system MUST treat the `identity/` subdir of
`cian_mac_an_déisigh_uí_liatháin/` as private records (medical,
disability, vetting) and MUST NOT ingest it by default. The
operator MAY override this with the
`INCLUDE_IDENTITY_RECORDS=true` env var OR by passing
`include_identity=True` to the `personal_records_source()` DLT source.

#### Scenario: Default identity exclusion

- **WHEN** the `author_archive_personal_records_raw` asset is materialised
  with partition key `"identity"`
- **THEN** the asset returns 0 rows
- **AND** logs a warning that the identity subdir is excluded

#### Scenario: Identity override for legal disclosure

- **WHEN** the `INCLUDE_IDENTITY_RECORDS=true` env var is set
- **AND** the `author_archive_personal_records_raw` asset is materialised
  with partition key `"identity"`
- **THEN** the asset returns the identity subdir files

### Requirement: UoGModuleExtraction storage shape

The `UoGModuleExtraction` BAML class MUST have the following fields:

- `subject` (UoGSubject) — MATA / SOFTWARE / IRISH / EDUCATION / PERSONAL
- `document_kind` (UoGDocumentKind) — ASSIGNMENT / EXAM / LECTURE_NOTES /
  PLACEMENT / CODE_PROJECT / ACTION_RESEARCH / TRANSCRIPT / DIPLOMA /
  REFERENCE / SCANNED_PAGE / OTHER
- `course_code` (string?) — e.g. "MA335", "CT511", "GA101", "ED305"
- `module_title` (string) — module / paper title
- `programme_stage` (UoGStage) — UNDERGRADUATE / PGCE / MASTERS / PHD /
  PROFESSIONAL / UNKNOWN
- `academic_year` (string?) — e.g. "2020-2021"
- `language` (UoGLanguage) — EN / GA / MIXED / UNKNOWN
- `key_topics` (string[]) — 3-7 topical tags
- `key_equations` (string[]) — 0-N LaTeX strings
- `has_gaelic_content` (bool) — true for IRISH with Gaeilge prose
- `requires_handwriting_ocr` (bool) — true for .pages or scanned PDFs
- `word_count` (int?) — approximate word count
- `confidence` (float) — BAML extraction confidence 0.0-1.0

#### Scenario: Storage of a cryptography assignment

- **WHEN** the BAML `ExtractUoGMathModule` function returns a record
  for a cryptography assignment
- **THEN** the record has `subject = MATA`, `document_kind = ASSIGNMENT`,
  `course_code = "MA335"`, `module_title = "Cryptography"`,
  `key_equations = ["m = c^d mod n", "phi(n) = (p-1)(q-1)"]`,
  `key_topics = ["RSA", "modular arithmetic", "Euclidean algorithm"]`,
  `language = EN`, `has_gaelic_content = false`,
  `requires_handwriting_ocr = false`, `confidence = 0.92`

