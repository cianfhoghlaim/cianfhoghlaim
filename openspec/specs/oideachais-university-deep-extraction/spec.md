# oideachais-university-deep-extraction Specification

## Purpose
TBD - created by archiving change 2026-07-15-oideachais-university-deep-extraction-v1. Update Purpose after archive.
## Requirements
### Requirement: Phase 1 ship — Tertiary 18+ DLT + BAML loop is functionally complete

The `cianfhoghlaim-university-deep-extraction` capability SHALL be considered Phase 1 complete once all 5 Tertiary 18+ DLT sources (`universities` + `tus` + `qqi_awards` + `cao` + `solas`), the 5+ Pydantic classes + 4+ enums + 5+ functions in `baml/education/university/university_extraction.baml`, and the 1 Layer 1 Ingestion `defs.yaml` cron asset at `orchestration/defs/1_ingestion/university/defs.yaml` (containing 5 `CelticIngestionComponent` entries — one per DLT source) are present, AST-parse cleanly, and the BAML file generates zero parse errors attributable to the Tertiary 18+ content under `mise run baml:generate`.

#### Scenario: 5 Tertiary 18+ DLT sources ship at the canonical paths

- **GIVEN** the 2026-07-15-cianfhoghlaim-university-deep-extraction-v1 change has landed
- **WHEN** `ls dlt/british_isles/ireland/university/{universities,tus,qqi_awards,cao,solas}.py` is run
- **THEN** all 5 files exist
- **AND** each AST-parses cleanly under `uv run python3 -c "import ast; ast.parse(open('<file>').read())"`
- **AND** each follows the canonical BIEP v1 dlt pattern: `@dlt.resource(name="tertiary_<area>", write_disposition="merge", primary_key=["<id>"])`, structlog observability, honors `USE_LOCAL_SCRAPES=true` (default) to read from `/stedding/ingest_queue/university/<area>/`
- **AND** each `@dlt.source(name="ireland_tertiary_<area>")` aggregator emits at least 2 dlt resources (the registry view + the per-(institution, faculty/campus/award) view)

#### Scenario: 5+ Pydantic classes + 4+ enums + 5+ BAML functions ship in the extended university_extraction.baml

- **GIVEN** the change has landed
- **WHEN** `baml/education/university/university_extraction.baml` is read
- **THEN** it defines **at least 5 new Pydantic classes**: `University` (the 8 universities) + `TU` (the 5 TUs) + `QQIAward` (the 10 QQI awards) + `CAOChoice` (a CAO course choice) + `SOLASCourse` (a SOLAS PLC / apprenticeship)
- **AND** it defines **at least 4 new enums**: `UniversityType` (TRADITIONAL / SPECIALIST / TECHNOLOGICAL / PRIVATE) + `QQILevel` (NFQ_6 / NFQ_7 / NFQ_8 / NFQ_9 / NFQ_10) + `CAOField` (ARTS_HUMANITIES / BUSINESS_LAW / SCIENCE / COMPUTING_ENGINEERING / MEDICINE_HEALTH / EDUCATION / MUSIC_PERFORMING / AGRICULTURE_VET) + `SOLASPath` (PLC / APPRENTICESHIP / YOUTHREACH / ADULT_LITERACY / VTOS / COMMUNITY_TRAINING)
- **AND** it defines **at least 5 new BAML functions** (`ExtractUniversityInfo` + `ExtractTuInfo` + `ExtractQQIAward` + `ExtractCAOChoice` + `ExtractSOLASCourse`) that each returns one of the 5 new Pydantic classes
- **AND** all 5 new functions route through the canonical `ExtractEn` LiteLLM client (which resolves to `minimax-m3` per commit `667635dfd` — the single text generator)
- **AND** `mise run baml:generate` exits with **zero** parse errors attributable to the new Tertiary 18+ content (errors in other files — e.g. the parallel agent's `baml/processing/_shared/video_kg.baml` — are out of scope)

#### Scenario: 1 Layer 1 Ingestion cron asset ships at the canonical path

- **GIVEN** the change has landed
- **WHEN** `ls orchestration/defs/1_ingestion/university/defs.yaml` is run
- **THEN** the file exists
- **AND** it is valid YAML under `uv run python3 -c "import yaml; yaml.safe_load(open('<file>').read())"`
- **AND** it contains **exactly 5** `CelticIngestionComponent` entries (one per DLT source: `ireland_tertiary_universities` + `ireland_tertiary_tus` + `ireland_tertiary_qqi` + `ireland_tertiary_cao` + `ireland_tertiary_solas`)
- **AND** each entry uses `use_local_scrapes=true` and at least 1 `asset_check_*` for minimum row counts (per the BIEP v1 wiring pattern from commit `ccd1a7e18`)
- **AND** each entry's cron schedule is daily 06:00 UTC (slightly later than primary_jc_combined's 05:00 to avoid clashing)
- **AND** each entry's tags include `[biep, tertiary, university, ingestion]`

#### Scenario: K-12 → university pipeline is now complete across 4 specs

- **GIVEN** the BIEP v1 flagship has shipped (covering Senior Cycle / Leaving Cert 15-18yo via `british-isles-education-pipeline`)
- **AND** the `ireland-primary-jc-dlt-baml` Phase 1 has shipped (covering Primary 4-12yo + Junior Cycle 12-15yo via the 2026-07-14 dispatch)
- **AND** the `cianfhoghlaim-university-deep-extraction` Phase 1 has shipped (covering Tertiary 18+ via this change)
- **WHEN** the 4 capability specs are listed
- **THEN** they collectively cover the full K-12 → university pipeline for the Republic of Ireland:
  - Primary (5-6yo infants + 6-12yo) ← `ireland-primary-jc-dlt-baml`
  - Junior Cycle (12-15yo) ← `ireland-primary-jc-dlt-baml`
  - Senior Cycle / Leaving Cert (15-18yo) ← `british-isles-education-pipeline`
  - Tertiary 18+ (universities + TUs + QQI + CAO + SOLAS) ← `cianfhoghlaim-university-deep-extraction` (this change)
- **AND** no student age bracket (NFQ 1-10) is left uncovered in the canonical spec catalogue
- **AND** the 4 specs collectively index **8 universities** + **5 TUs** + **10 QQI awards** + **4 CAO rounds** + **16 ETBs** for the Tertiary 18+ stage

#### Scenario: Tertiary 18+ registry view complements per-university deep extraction

- **GIVEN** the existing per-university deep extraction schema at `baml/education/university/university_extraction.baml` (CourseDescriptor / ModuleDescriptor / ProgrammeDescriptor / ReadingListItem + 4 functions)
- **AND** the new Tertiary 18+ registry schema in the same file (University / TU / QQIAward / CAOChoice / SOLASCourse + 4 enums + 5 functions)
- **WHEN** the BAML client is generated
- **THEN** the 5 new classes + 4 new enums + 5 new functions all coexist with the existing 4 classes + 4 enums + 4 functions in the same file
- **AND** no class name or enum name collides with the existing per-university ones (e.g. `CourseDescriptor` vs `University` — different naming conventions)
- **AND** the registry view (`University.institution_id` + `TU.tu_id`) is joinable with the per-university view (`CourseDescriptor.course_code`) via the `institution_id` foreign key for downstream cross-stage analytics

#### Scenario: NFQ 1-5 pre-tertiary coverage is preserved (no double-counting)

- **GIVEN** the upstream `ireland-primary-jc-dlt-baml` + `british-isles-education-pipeline` specs cover NFQ 1-5 (pre-tertiary: Primary + JC + LC)
- **AND** this change's `qqi_awards.py` covers NFQ 6-10 only (Tertiary 18+)
- **WHEN** the `QQILevel` enum is enumerated
- **THEN** it defines **exactly 5 values** (`NFQ_6` / `NFQ_7` / `NFQ_8` / `NFQ_9` / `NFQ_10`)
- **AND** it does NOT define `NFQ_1` / `NFQ_2` / `NFQ_3` / `NFQ_4` / `NFQ_5` (those are covered by the upstream specs and would cause double-counting)
- **AND** the 5 NFQ levels partition cleanly: 5 TUs + 8 universities collectively award NFQ 6-10 via their programmes

