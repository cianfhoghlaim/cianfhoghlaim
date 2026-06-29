# Spec Delta — `oideachais-baml-schemas` (modified)

## Purpose

`oideachais-baml-schemas` is a capability of the Cianfhoghlaim platform.
The corresponding source code lives at `baml_src/` (8 BAML files) and
`baml_client/` (the auto-generated Python client). See `docs/00_index.md`
for the quadrant map and `docs/00-core/CLAUDE.md` for the project
identity.

This delta adds the new `university_extraction.baml` file to the
canonical BAML surface (5 BAML classes + 4 BAML functions + 4
deterministic tests) and extends the "Runtime deterministic evals"
requirement with 3 new evals for the university extraction path. Per
the `oideachais-university-deep-extraction` spec, these new functions
target the *website* side of the University of Galway scrape (the
existing `ExtractUoGArtifact` in `author_archive.baml` covers the
*personal-archive* side).

## MODIFIED Requirements

### Requirement: Author-archive extraction (UoG + Gemini + Zotero)

The system SHALL extract structured records from the 3 author-archive
corpora (UoG artefacts, Gemini deep research reports, Zotero papers)
PLUS the new `university_extraction.baml` file (5 classes + 4
functions for course / module / programme / reading-list descriptors)
on the *website* side (per the `oideachais-university-deep-extraction`
spec).

#### Scenario: Module descriptor extracted from UoG module page

- **GIVEN** a module page markdown blob (e.g. `https://www.universityofgalway.ie/.../ct516-deep-learning/`)
- **WHEN** the `ExtractModuleDescriptor` BAML function is called
- **THEN** the function returns a `ModuleDescriptor` with the module code, title, ECTS, semester, programme codes, learning outcomes, assessment breakdown, prerequisite modules, lecturers, and recommended reading
- **AND** the function routes through the canonical `ExtractEn` LiteLLM client (no direct Firecrawl call)

#### Scenario: Reading list extracted with ISBN-13 validation

- **GIVEN** a module page markdown blob with a "Recommended reading" section
- **WHEN** the `ExtractReadingList` BAML function is called
- **THEN** the function returns a `ReadingListItem[]` with format (`ISBN_13 | DOI | URL`), title, authors, year
- **AND** the deterministic eval `reading_list_isbn13_format` rejects any record where `format = "ISBN_13"` and the `isbn_13` field doesn't match `^\d{13}$`

#### Scenario: BAML client is missing

- **GIVEN** the BAML client is not yet generated (the `baml_client/` directory is empty)
- **WHEN** the `uog_extract_modules` Dagster asset runs
- **THEN** the asset SHALL log a warning and return 0 rows (graceful degradation, per the `university_of_galway_source` pattern in `leabharlann/`)
- **AND** the asset run SHALL NOT fail

### Requirement: Runtime deterministic evals (extended for university extraction)

The system SHALL provide 6 deterministic Python evals (the existing set)
PLUS 3 new evals for the university extraction path:

7. **`course_code_format_regex_match`** — every `CourseDescriptor.course_code` SHALL match `^[A-Z]{2,4}\d{3,4}$` (e.g. `MA335`, `CT511`, `HDSD`)
8. **`programme_ects_sum`** — `sum(ProgrammeDescriptor.modules[*].ects)` SHALL equal `ProgrammeDescriptor.total_ects` within ±1
9. **`module_count_within_programme`** — `ProgrammeDescriptor.modules` SHALL contain 6-20 modules for a full undergraduate or master's programme (a 1-module or 100-module programme is flagged as suspect)

#### Scenario: Course code format validation

- **GIVEN** a `CourseDescriptor` with `course_code = "MA335"`
- **WHEN** the `course_code_format_regex_match` eval runs
- **THEN** the eval returns `passed = true`

#### Scenario: Course code format rejection

- **GIVEN** a `CourseDescriptor` with `course_code = "math-335"` (lowercase + dash)
- **WHEN** the `course_code_format_regex_match` eval runs
- **THEN** the eval returns `passed = false`
- **AND** the eval's `message` field SHALL be `"course_code 'math-335' does not match ^[A-Z]{2,4}\\d{3,4}$"`
- **AND** the auto-retry loop SHALL re-invoke `ExtractCourseDescriptor` with a stronger prompt

#### Scenario: Programme ECTS sum fails — auto-retry triggers

- **GIVEN** a `ProgrammeDescriptor` with `total_ects = 90` but 8 modules whose `ects` sum to `120`
- **WHEN** the `programme_ects_sum` eval runs
- **THEN** the eval returns `passed = false`
- **AND** the asset_check fires
- **AND** the auto-retry loop re-invokes `ExtractProgrammeDescriptor` with a stronger prompt that emphasises the ECTS sum
