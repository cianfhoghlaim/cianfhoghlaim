# Spec Delta — Multi-Stage DLT Sources (5 stages)

## MODIFIED Requirements

### Requirement: Curriculum Ingestion (multi-stage)

The system SHALL provide DLT sources for **all 5 stages of Irish education** (Aistear, Primary, Junior Cycle, Senior Cycle, Tertiary), with the same `USE_LOCAL_SCRAPES=true` cache-fallback pattern as the existing Ireland DLT sources.

#### Scenario: Aistear Source
- **GIVEN** `sruth/oideachais/data_platform/dlt_sources/ireland/aistear.py`
- **WHEN** the `@dlt.source aistear_curriculum` is invoked
- **THEN** it yields `AistearDocument` rows from the 14 source PDFs on `curriculumonline.ie/en/early-childhood/` and the `ncca.ie/en/early-childhood/` pages
- **AND** with `USE_LOCAL_SCRAPES=true`, it reads from `/stedding/ingest_queue/aistear/` cache instead of live scraping
- **AND** yields `Naionra` rows from `gaeloideachas.ie/directories/` (for the geospatial layer)

#### Scenario: Primary Source
- **GIVEN** `sruth/oideachais/data_platform/dlt_sources/ireland/primary.py`
- **WHEN** the `@dlt.source primary_curriculum` is invoked
- **THEN** it yields `PrimaryCurriculumArea` rows for each of the 12 curriculum areas × 4 stages
- **AND** deduplicates by content hash with `SourceProvenance` tracking

#### Scenario: Junior Cycle Source (Extended)
- **GIVEN** `sruth/oideachais/data_platform/dlt_sources/ireland/junior_cycle.py` (extension)
- **WHEN** the new `junior_cycle_cb_tasks` resource is invoked
- **THEN** it yields 2 `CBATask` rows per subject for 18 core + 16 short courses
- **AND** existing resources (`junior_cycle_subjects`, `junior_cycle_short_courses`) continue to work

#### Scenario: Senior Cycle Source (Extended)
- **GIVEN** `sruth/oideachais/data_platform/dlt_sources/ireland/senior_cycle.py` (extension)
- **WHEN** the new `lazy_extract_exam_paper` resource is invoked
- **THEN** it fires `baml.LazyExtractExamPaper` on-demand (only when the SPA opens a paper), respecting the per-session `ExtractionBudget`
- **AND** existing resources (`senior_cycle_subjects`, `leaving_certificate`, `junior_cycle_exams`) continue to work

#### Scenario: Tertiary Source
- **GIVEN** `sruth/oideachais/data_platform/dlt_sources/ireland/tertiary.py`
- **WHEN** the `@dlt.source tertiary_courses` is invoked
- **THEN** it yields `CAOCourse`, `MatriculationRequirement`, `QqiFetAward`, `Apprenticeship`, `ApplicationTimeline` rows from:
  - `cao.ie/courses/` (Skyvern/Stagehand for JS-heavy dropdowns)
  - `nui.ie/matriculation/`, `ucd.ie/matriculation/`, `tcd.ie/matriculation/`, `ul.ie/matriculation/`, `ucc.ie/matriculation/`, `maynoothuniversity.ie/matriculation/`
  - `atu.ie`, `tus.ie`, `setu.ie`, `mtu.ie` (IoT matriculation)
  - `qqi.ie` (FET awards)
  - `apprenticeship.ie` (apprenticeship listings)
- **AND** yields a `CAOGradeProfile` row per `(course_code, year)` with median points + median grades

## ADDED Requirements

### Requirement: 5-Stage Source Manifest
The system SHALL provide a manifest of all DLT sources per stage, indexed by stage slug.

#### Scenario: Stage Manifest Lookup
- **GIVEN** a stage slug (e.g., `tertiary`)
- **WHEN** `oideachais.data_platform.subjects.manifest.sources_for_stage('tertiary')` is called
- **THEN** the function returns the list of DLT source modules for that stage
