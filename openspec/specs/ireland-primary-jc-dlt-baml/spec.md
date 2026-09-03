# Ireland Primary + Junior Cycle DLT + BAML Capability

## Purpose

`ireland-primary-jc-dlt-baml` is a capability of the Cianfhoghlaim
platform. It complements `cianfhoghlaim-pipeline` (which covers all 5
educational stages with a generic per-stage BAML extraction) by focusing
on the **Primary + Junior Cycle** stages specifically — the 2
non-Leaving-Cert stages — with stage-specific DLT sources and BAML
extraction schemas tailored to (a) the Primary Curriculum (4 areas:
English, Gaeilge, Mathematics, SESE), and (b) the 24 Junior Cycle
subjects.

The corresponding source code lives at:

- `cianfhoghlaim/dlt/british_isles/ireland/education/primary/` (Primary DLT sources per area + per language EN/GA)
- `cianfhoghlaim/dlt/british_isles/ireland/education/junior_cycle/` (Junior Cycle DLT sources per subject + per language)
- `cianfhoghlaim/baml/education/primary/` (Primary BAML extraction schemas)
- `cianfhoghlaim/baml/education/junior_cycle/` (Junior Cycle BAML extraction schemas)
- `cianfhoghlaim/cocoindex/primary_embedding.py` + `cianfhoghlaim/cocoindex/junior_cycle_embedding.py` (CocoIndex v1 Apps)
- `cianfhoghlaim/orchestration/defs/2_materials/primary/` +
  `cianfhoghlaim/orchestration/defs/2_materials/junior_cycle/` (Dagster assets)

## Background

The pre-v4 `cianfhoghlaim-pipeline` had a single BAML schema covering all
5 stages and a per-subject loop. The Primary + Junior Cycle stages have
different shape from Senior Cycle / Leaving Cert: Primary uses
4 "areas" not subjects, and Junior Cycle has its own short-cycle
syllabus structure (Year 1 + Year 2 + Year 3 + Optional TYs). The
generic BAML schema mis-extracted these. This capability provides
stage-specific BAML extraction so the Primary + JC pipelines run
without leaking Senior-Cycle assumptions.
## Requirements
### Requirement: Primary stage DLT sources

The system SHALL provide DLT sources for the 4 Primary curriculum
areas: English, Gaeilge, Mathematics, SESE (Science + Geography +
History; called "Social, Environmental and Scientific Education").
Each area SHALL have an EN source + a GA source (8 sources total)
at `cianfhoghlaim/dlt/british_isles/ireland/education/primary/`.

#### Scenario: Primary EN Gaeilge ingestion

- **WHEN** the developer runs `dagster asset materialize primary_gaeilge_en`
- **THEN** the source SHALL fetch the Primary Gaeilge curriculum pages
  from `curriculumonline.ie` + `ncca.ie`
- **AND** yield one row per Primary Gaeilge area + per Primary school year (Junior Infants through 6th Class)

#### Scenario: Primary Mathematics SESE

- **WHEN** the developer runs `dagster asset materialize primary_mathematics_en` + `primary_sese_en`
- **THEN** both sources materialise
- **AND** yield rows with `area ∈ {MATHEMATICS, SESE}` per Primary year

### Requirement: Junior Cycle DLT sources (24 subjects)

The system SHALL provide DLT sources for the 24 Junior Cycle subjects
(English, Gaeilge, Mathematics, History, Geography, Science, Business
Studies, French, German, Spanish, Italian, Russian, Japanese, Arabic,
Music, Art, Home Economics, Wood Technology, Metalwork, Technical
Graphics, Materials Technology Wood, Materials Technology Metal,
Engineering, Coding). Each subject SHALL have an EN source + a GA
source at `cianfhoghlaim/dlt/british_isles/ireland/education/junior_cycle/`
(48 sources total).

#### Scenario: Junior Cycle English ingestion

- **WHEN** the developer runs `dagster asset materialize junior_cycle_english`
- **THEN** the source SHALL fetch the Junior Cycle English spec from
  `curriculumonline.ie` + `ncca.ie/junior-cycle/`
- **AND** yield 1 row per JC English learning outcome (Year 1 + Year 2 + Year 3 strand)

#### Scenario: Gaeilge-specific Junior Cycle

- **WHEN** the developer runs `dagster asset materialize junior_cycle_gaeilge_ga`
- **THEN** the source SHALL fetch the JC Gaeilge GA spec from
  `curriculumonline.ie/ga/` + `ncca.ie/junior-cycle/gaeilge/`
- **AND** yield rows in `GA_classified` records only (no EN sibling)

### Requirement: Stage-specific BAML schemas

The system SHALL provide stage-specific BAML extraction schemas at
`cianfhoghlaim/baml/education/primary/` and
`cianfhoghlaim/baml/education/junior_cycle/`. Each schema SHALL NOT
reuse the Senior Cycle / Leaving Cert schema (no learning outcomes
array, no exam paper layout, no marking scheme).

#### Scenario: Primary Mathematics extraction

- **WHEN** the BAML function `ExtractPrimaryMathematics` is called on a Primary Mathematics Curriculum page
- **THEN** the function SHALL return a `PrimaryCurriculumSpec` record
- **AND** the `strand` field SHALL be one of `NUMBER`, `ALGEBRA`,
  `SHAPE_SPACE`, `MEASURE`, `DATA`
- **AND** the `year_level` field SHALL be one of
  `JUNIOR_INFANTS`, `SENIOR_INFANTS`, `FIRST`, `SECOND`,
  `THIRD`, `FOURTH`, `FIFTH`, `SIXTH`

#### Scenario: Junior Cycle Science extraction

- **WHEN** the BAML function `ExtractJuniorCycleScience` is called
- **THEN** the function SHALL return a `JCCurriculumSpec` record
- **AND** the `strand` field SHALL be one of the 4 JC Science strands
- **AND** the `learning_outcomes` list SHALL carry outcomes per Year
  (Year 1 + Year 2 + Year 3 only, no TY outcomes in v1)

### Requirement: Phase 1 ship — Primary + JC DLT loop is functionally complete

The `ireland-primary-jc-dlt-baml` capability SHALL be considered Phase 1 complete once all 3 DLT sources (`primary` + `junior_cycle` + `primary_jc_combined`), both stage-specific BAML extractor functions (`ExtractPrimaryArea` + `ExtractJCSubjectSpec`), and all 3 Layer 1 Ingestion `defs.yaml` cron assets (one per source) are present, AST-parse cleanly, and the BAML files generate zero parse errors under `mise run baml:generate`.

#### Scenario: 3 DLT sources ship at the canonical paths

- **GIVEN** the 2026-07-14-ireland-primary-jc-dlt-baml-v1 change has landed
- **WHEN** `ls dlt/british_isles/ireland/education/{primary,junior_cycle,primary_jc_combined}.py` is run
- **THEN** all 3 files exist
- **AND** each AST-parses cleanly under `uv run python3 -c "import ast; ast.parse(open('<file>').read())"`
- **AND** each follows the canonical BIEP v1 dlt pattern: `@dlt.resource(name=..., write_disposition="merge", primary_key=["url"])`, structlog observability, honours `USE_LOCAL_SCRAPES=true` (default) to read from `/stedding/ingest_queue/<stage>/`

#### Scenario: 2 stage-specific BAML schemas ship at the canonical paths

- **GIVEN** the change has landed
- **WHEN** `ls baml/education/{primary, junior_cycle}/*_extraction.baml` is run
- **THEN** both files exist (`primary_extraction.baml` + `junior_cycle_extraction.baml`)
- **AND** `mise run baml:generate` exits with 0 errors attributable to these 2 files
- **AND** each defines exactly 1 BAML function (`ExtractPrimaryArea` /
  `ExtractJCSubjectSpec`) that returns a stage-specific Pydantic class
  (`PrimaryAreaSpecStage` / `JCSubjectSpecStage`) constrained to the
  spec-mandated year levels (Primary: 8 NCCA year levels, JC: Year 1 +
  Year 2 + Year 3 only, no TY)
- **AND** each function uses the canonical `ExtractEn` client (which
  routes to `minimax-m3` per commit `667635dfd`)

#### Scenario: 3 Layer 1 Ingestion cron assets ship at the canonical paths

- **GIVEN** the change has landed
- **WHEN** `ls orchestration/defs/1_ingestion/curriculum/{primary,junior_cycle,primary_jc_combined}/defs.yaml` is run
- **THEN** all 3 defs.yaml files exist
- **AND** each is valid YAML under `uv run python3 -c "import yaml; yaml.safe_load(open('<file>').read())"`
- **AND** each uses the `CelticIngestionComponent` type with `use_local_scrapes=true` and at least 1 asset_check (per the BIEP v1 wiring pattern from commit `ccd1a7e18`)

#### Scenario: K-12 → university pipeline is now complete across 3 specs

- **GIVEN** the BIEP v1 flagship has shipped (covering Senior Cycle / Leaving Cert 15-18yo via `british-isles-education-pipeline`)
- **AND** the `ireland-primary-jc-dlt-baml` Phase 1 has shipped (covering Primary 4-12yo + Junior Cycle 12-15yo via this change)
- **WHEN** the 3 capability specs are listed
- **THEN** they collectively cover the full K-12 → university pipeline:
  - Primary (5-6yo infants + 6-12yo) ← `ireland-primary-jc-dlt-baml` (this change)
  - Junior Cycle (12-15yo) ← `ireland-primary-jc-dlt-baml` (this change)
  - Senior Cycle / Leaving Cert (15-18yo) ← `british-isles-education-pipeline` (BIEP v1 flagship)
- **AND** no student age bracket is left uncovered in the canonical spec catalogue

#### Scenario: BAML class-name collision with the legacy stages/ schemas is avoided

- **GIVEN** the legacy canonical Primary + JC schemas at `baml/education/stages/primary.baml` + `stages/junior_cycle.baml` define classes named `PrimaryLearningOutcome` / `PrimaryStrand` / `JCSubjectSpec`
- **WHEN** the new stage-specific schemas at `baml/education/primary/primary_extraction.baml` + `junior_cycle/junior_cycle_extraction.baml` are evaluated
- **THEN** all 3 classes use the `Stage` suffix (`PrimaryLearningOutcomeStage` / `PrimaryStrandStage` / `PrimaryAreaSpecStage` / `JCLearningOutcomeStage` / `JCStrandStage` / `JCSubjectSpecStage`)
- **AND** no class name collides with the legacy canonical names
- **AND** the legacy canonical schemas remain unchanged (consumed by `dlt/.../primary.py` + `junior_cycle.py`)

### Requirement: Junior Cycle BAML extraction (per-subject)

The system SHALL provide 4 BAML extraction functions at
`baml_src/british_isles/ireland/education/junior_cycle/`:

- `ExtractJCCurriculum(subject, language, year, text) -> JCCurriculumSpec`
- `ExtractCBADescriptor(text) -> CBATask`
- `ExtractJCShortCourse(text) -> JCShortCourse`
- `ExtractJCExamPaper(text) -> JCExamPaper`

The 18 NCCA Junior Cycle subjects (`english`, `gaeilge`, `mathematics`,
`irish_history`, `geography`, `science`, `business_studies`, `french`,
`german`, `spanish`, `italian`, `home_economics`, `music`, `art`,
`technology`, `engineering`, `graphics`, `wood_technology`) SHALL each have
an EN source and a GA source at
`dlt/british_isles/ireland/education/junior_cycle_subjects/`
(36 sources total), and the 16 short courses SHALL each have a single source
(English-only is canonical, but the source SHALL emit rows tagged with
`language="en"` and optionally `language="ga"` if a GA spec exists).

#### Scenario: JC English GA extraction

- **WHEN** the developer runs `dagster asset materialize jc_english_ga_extracted`
- **THEN** the BAML function `b.ExtractJCCurriculum(subject="english", language="ga", year=1, text=...)` is invoked
- **AND** the resulting `JCCurriculumSpec` carries `language="ga"`, `subject="english"`, `year=YEAR_1`
- **AND** the row lands in `cianfhoghlaim.education.british_isles.ireland.junior_cycle.english.ga`
- **AND** the corresponding LanceDB table `cianfhoghlaim.jc.english.year_1_ga` is populated by the CocoIndex App

#### Scenario: JC Coding short-course

- **WHEN** the developer runs `dagster asset materialize jc_short_course_coding_extracted`
- **THEN** the BAML function `b.ExtractJCShortCourse(text=...)` is invoked
- **AND** the resulting `JCShortCourse` carries `course_slug="coding"`, `language="en"`, `hours > 0`, `learning_outcomes[]` non-empty

#### Scenario: CBA descriptor extraction

- **WHEN** the developer runs `dagster asset materialize jc_cba_english_1_extracted`
- **THEN** the BAML function `b.ExtractCBADescriptor(text=...)` is invoked
- **AND** the resulting `CBATask` carries `subject="english"`, `cba_id="english_cba_1"`, `weighting > 0`
- **AND** the row lands in `cianfhoghlaim.education.british_isles.ireland.junior_cycle.cbas.english.1`

### Requirement: Primary + Junior Cycle tabs on the central portal

The system SHALL publish the Primary + JC tabs on the central portal
(`portal.cianfhoghlaim.ie/en/primary` + `/junior-cycle`) populated
from the stage-specific BAML extraction files
(`baml/education/stages/primary.baml` + `junior_cycle.baml` +
`baml/education/primary/primary_extraction.baml` +
`baml/education/junior_cycle/junior_cycle_extraction.baml`) and the
CocoIndex apps (`primary_embedding.py` + `junior_cycle_embedding.py`).

This requirement is the canonical link between the Primary + JC data
pipeline and the new central portal entry described in
`openspec/changes/2026-07-18-british-isles-portal-activation-v3/specs/cianfhoghlaim-leaving-cert-portal/spec.md`
R17 + R19.

#### Scenario: A user opens the Primary tab

- **GIVEN** the user clicks "Primary" on the central portal
- **WHEN** the page loads
- **THEN** 4 cards render: English / Gaeilge / Mathematics / SESE
- **AND** each card shows the learning outcomes extracted by `ExtractPrimaryLearningOutcomes`

#### Scenario: A user opens the Junior Cycle tab

- **GIVEN** the user clicks "Junior Cycle" on the central portal
- **WHEN** the page loads
- **THEN** 24 JC subject cards render in a grid
- **AND** each card shows the assessment components + CBA tasks extracted by `ExtractJCSpec`

## Cross-references

- [`cianfhoghlaim-pipeline`](../cianfhoghlaim-pipeline/spec.md) — the parent capability (5 stages; Senior Cycle + Leaving Cert covered there)
- [`cianfhoghlaim-baml-schemas`](../cianfhoghlaim-baml-schemas/spec.md) — the BAML extraction library
- [`british-isles-education-pipeline`](../british-isles-education-pipeline/spec.md) — the flagship BIEP v1 (covers the 6 LC subjects, not Primary/JC)

## Migrated from: *(none)*
