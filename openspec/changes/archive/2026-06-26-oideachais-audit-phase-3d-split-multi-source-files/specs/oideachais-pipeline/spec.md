# Spec Delta — Round 11 Phase 3D

## ADDED Requirements

### Requirement: Country-First Layout — Multi-Source File Splitting

The system SHALL split all multi-source legacy DLT files so that each `@dlt.source` function
lives in its own canonical file at `dlt_sources/{nation}/{domain}/{entity}.py`.

#### Scenario: Each `@dlt.source` function lives in its own file

- **WHEN** a legacy file contains 2+ `@dlt.source` functions
- **THEN** the system SHALL split the file such that each `@dlt.source` function lives in its own file
- **AND** the system SHALL extract shared private helpers (non-`@dlt.source` functions and module constants) to a sibling `_helpers.py` file
- **AND** the system SHALL move the new files to the canonical `dlt_sources/{nation}/{domain}/{entity}.py` paths

#### Scenario: Per-source function blocks preserved with decorators

- **WHEN** a `@dlt.source` function contains nested `@dlt.resource` functions
- **THEN** the system SHALL preserve the source function and all its nested resource functions in the same output file
- **AND** the system SHALL preserve all decorators (`@dlt.source`, `@dlt.resource`, `@dlt.transformer`) and indentation

#### Scenario: Shared helpers extracted to private modules

- **WHEN** multiple split source files reference the same private helper function or module constant
- **THEN** the system SHALL extract the shared helper to a sibling `_helpers.py` file (e.g. `dlt_sources/ie/education/_oide_helpers.py`)
- **AND** the system SHALL rewrite intra-file references to import from the helper module

#### Scenario: Legacy multi-source files deleted after split

- **WHEN** all `@dlt.source` functions from a legacy multi-source file have been split
- **THEN** the system SHALL delete the legacy file
- **AND** the system SHALL update all importers

#### Scenario: Multi-source file mapping table

The following legacy multi-source files SHALL be split per source:

| Legacy | Splits into |
|:--|:--|
| `dlt_sources/ireland/oide.py` | `dlt_sources/ie/education/{oide, oide_subject, oide_gaeilge, oide_all_subjects}.py` |
| `dlt_sources/ireland/examinations.py` | `dlt_sources/ie/education/{examinations, sec_examinations_browser, leaving_certificate, junior_cycle_exams, mathematics_exams, science_subjects_exams}.py` |
| `dlt_sources/ireland/local_documents.py` | `dlt_sources/ie/culture/{local_education_documents, local_documents_by_subject}.py` |
| `dlt_sources/ireland/agentic_discovery.py` | `dlt_sources/ie/education/{agentic_discovery, deep_research}.py` |
| `dlt_sources/ireland/pdf_downloader.py` | `dlt_sources/ie/education/{pdf_downloads, exam_pdf_downloads}.py` |
| `dlt_sources/uk/england/national_curriculum.py` | `dlt_sources/en/education/{national_curriculum, aqa_qualifications, edexcel_qualifications, ocr_qualifications, all_exam_boards}.py` |
| `dlt_sources/uk/northern_ireland/ccea_curriculum.py` | `dlt_sources/ni/education/{ni_curriculum, ccea_qualifications, irish_medium_ni}.py` |
| `dlt_sources/uk/scotland/curriculum_for_excellence.py` | `dlt_sources/sct/education/{curriculum_for_excellence, sqa_qualifications, gaelic_curriculum}.py` |
| `dlt_sources/uk/wales/curriculum_for_wales.py` | `dlt_sources/wls/education/{curriculum_for_wales, wjec_qualifications, welsh_medium}.py` |
| `dlt_sources/celtic/canuint.py` | `dlt_sources/ie/culture/canuint/{pronunciation, search, audio_download, dialect_summary, word_alignment}.py` |
| `dlt_sources/celtic/duchas_images.py` | `dlt_sources/ie/culture/{duchas_images, hidden_heritages}.py` |
| `dlt_sources/celtic/gaois.py` | `dlt_sources/ie/culture/{logainm, tearma, ainm, gaois_combined}.py` |
| `dlt_sources/geospatial/met_office.py` | `dlt_sources/ie/statistics/{met_office, met_office_forecast}.py` |
| `dlt_sources/geospatial/cso_small_areas.py` | `dlt_sources/ie/statistics/{cso_small_areas, cso_education, cso_deprivation}.py` |
| `dlt_sources/geospatial/geohive.py` | `dlt_sources/ie/statistics/{geohive, geohive_deprivation}.py` |
| `dlt_sources/bunchloch/filesystem_source.py` | `dlt_sources/cross/bunchloch/{filesystem, filesystem_by_subject}.py` |