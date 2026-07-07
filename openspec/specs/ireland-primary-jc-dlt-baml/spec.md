# Ireland Primary + Junior Cycle DLT + BAML Capability

## Purpose

`ireland-primary-jc-dlt-baml` is a capability of the Cianfhoghlaim
platform. It complements `oideachais-pipeline` (which covers all 5
educational stages with a generic per-stage BAML extraction) by focusing
on the **Primary + Junior Cycle** stages specifically — the 2
non-Leaving-Cert stages — with stage-specific DLT sources and BAML
extraction schemas tailored to (a) the Primary Curriculum (4 areas:
English, Gaeilge, Mathematics, SESE), and (b) the 24 Junior Cycle
subjects.

The corresponding source code lives at:

- `cianfhoghlaim/dlt/british_isles/ie/education/primary/` (Primary DLT sources per area + per language EN/GA)
- `cianfhoghlaim/dlt/british_isles/ie/education/junior_cycle/` (Junior Cycle DLT sources per subject + per language)
- `cianfhoghlaim/baml/education/primary/` (Primary BAML extraction schemas)
- `cianfhoghlaim/baml/education/junior_cycle/` (Junior Cycle BAML extraction schemas)
- `cianfhoghlaim/cocoindex/primary_embedding.py` + `cianfhoghlaim/cocoindex/junior_cycle_embedding.py` (CocoIndex v1 Apps)
- `cianfhoghlaim/orchestration/defs/2_materials/primary/` +
  `cianfhoghlaim/orchestration/defs/2_materials/junior_cycle/` (Dagster assets)

## Background

The pre-v4 `oideachais-pipeline` had a single BAML schema covering all
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
at `cianfhoghlaim/dlt/british_isles/ie/education/primary/`.

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
source at `cianfhoghlaim/dlt/british_isles/ie/education/junior_cycle/`
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

## Cross-references

- [`oideachais-pipeline`](../oideachais-pipeline/spec.md) — the parent capability (5 stages; Senior Cycle + Leaving Cert covered there)
- [`oideachais-baml-schemas`](../oideachais-baml-schemas/spec.md) — the BAML extraction library
- [`british-isles-education-pipeline`](../british-isles-education-pipeline/spec.md) — the flagship BIEP v1 (covers the 6 LC subjects, not Primary/JC)

## Migrated from: *(none)*
