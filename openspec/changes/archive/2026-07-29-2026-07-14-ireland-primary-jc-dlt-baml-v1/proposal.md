# Ireland Primary + Junior Cycle DLT + BAML v1

## Why

The `ireland-primary-jc-dlt-baml` capability covers the 2
non-Leaving-Cert educational stages — Primary (ages 4-12, 5-6 year-old
students in Junior/Senior Infants) and Junior Cycle (ages 12-15) — with
stage-specific DLT sources and BAML extraction schemas. The pre-v4
`cianfhoghlaim-pipeline` used a generic per-stage BAML schema that
mis-extracted Primary (which has 4 "areas", not subjects, and 8 year
levels) and Junior Cycle (which has its own short-cycle syllabus
structure distinct from Senior Cycle / Leaving Cert).

This change ships **Phase 1** of the capability — the canonical DLT
source + BAML extractor + Dagster cron assets for the combined Primary
+ JC pipeline. Together with the BIEP v1 flagship (which covers Senior
Cycle / Leaving Cert for 15-18 year-old students), the 3 specs cover
the full K-12 → university pipeline:

| Stage | Age | Capability |
|:--|:--|:--|
| Primary | 4-12 (5-6yo infants + 6-12yo) | `ireland-primary-jc-dlt-baml` (this) |
| Junior Cycle | 12-15 | `ireland-primary-jc-dlt-baml` (this) |
| Senior Cycle / Leaving Cert | 15-18 | `british-isles-education-pipeline` |

## What changes

### 1. 3 new DLT sources

- **`dlt/british_isles/ireland/education/primary.py`**
  (already shipped by the v4 dlt consolidation in commit `24f671f43`)
  — 12 NCCA Primary curriculum areas × EN + GA, with
  `use_local_scrapes=true` reading from `/stedding/ingest_queue/primary/`.
- **`dlt/british_isles/ireland/education/junior_cycle.py`**
  (already shipped in commit `24f671f43`) — 18 NCCA Junior Cycle
  subjects + 16 short courses + CBAs, with `use_local_scrapes=true`
  reading from `/stedding/ingest_queue/junior_cycle/`.
- **`dlt/british_isles/ireland/education/primary_jc_combined.py`**
  (**new**) — the canonical cross-stage DLT source for the combined
  Primary + JC ingestion loop. Walks `/stedding/ingest_queue/{primary,
  junior_cycle}/` and emits one row per (stage, subject, language)
  tuple via 3 dlt resources (`primary_jc_unified` +
  `primary_jc_subjects` + `primary_jc_strands`). Honours
  `USE_LOCAL_SCRAPES=true`.

Each source follows the existing BIEP v1 pattern (per
`ncca.py + examinations.py + gov_ie_circulars.py`):
- `@dlt.resource(name=..., write_disposition="merge", primary_key=["url"])`
- Uses structlog for observability
- Honours `USE_LOCAL_SCRAPES=true` (default) to read from the local
  scrape cache (`/stedding/ingest_queue/<stage>/`)

### 2. 2 new stage-specific BAML schemas

- **`baml/education/primary/primary_extraction.baml`**
  (**new**) — the canonical Primary schema with:
  - `PrimaryYearLevel` enum (the 8 NCCA Primary year levels)
  - `PrimaryArea` enum (the 4 spec-mandated areas: ENGLISH / GAEILGE
    / MATHEMATICS / SESE)
  - `PrimaryMathsStrand` enum (5 Mathematics strands)
  - `PrimaryLearningOutcomeStage` + `PrimaryStrandStage` +
    `PrimaryAreaSpecStage` Pydantic classes
  - `ExtractPrimaryArea` BAML function (uses the canonical `ExtractEn`
    client → `minimax-m3`)
- **`baml/education/junior_cycle/junior_cycle_extraction.baml`**
  (**new**) — the canonical Junior Cycle schema with:
  - `JCYearLevel` enum (YEAR_1 / YEAR_2 / YEAR_3, no TY in v1)
  - `JCSubject` enum (the 24 NCCA JC subjects)
  - `JCScienceStrand` enum (4 Science strands)
  - `JCLevel` enum (ORDINARY / LEVEL_1_LP / LEVEL_2_LP)
  - `JCLearningOutcomeStage` + `JCStrandStage` +
    `JCSubjectSpecStage` Pydantic classes
  - `ExtractJCSubjectSpec` BAML function

The legacy canonical Primary + JC schemas (at
`baml/education/stages/primary.baml` and `baml/education/stages/
junior_cycle.baml`, shipped in commit `54c21dd52`) remain unchanged —
they're consumed by the per-subject loops in
`dlt/british_isles/ireland/education/primary.py` +
`junior_cycle.py`. The new stage-specific schemas add the
spec-required `Stage` suffix to all class names to avoid collision
with the legacy classes.

### 3. 3 new Dagster cron assets (Layer 1 Ingestion)

Per the BIEP v1 `CelticIngestionComponent` pattern (per the English
wiring from commit `ccd1a7e18`):

- **`orchestration/defs/1_ingestion/curriculum/primary/defs.yaml`**
  — daily 04:00 UTC cron, partitions: 4 areas × EN+GA (8 partitions)
- **`orchestration/defs/1_ingestion/curriculum/junior_cycle/defs.yaml`**
  — Monday-only 04:00 UTC cron, partitions: 24 subjects × EN+GA (48 partitions)
- **`orchestration/defs/1_ingestion/curriculum/primary_jc_combined/defs.yaml`**
  — daily 05:00 UTC cron, partitions: 2 stages × EN+GA (4 partitions)

All 3 use `use_local_scrapes=true` and include an `asset_check_*` for
minimum row counts.

### 4. 1 MODIFIED spec delta

Adds 1 ADDED Requirement to the existing `ireland-primary-jc-dlt-baml`
spec documenting Phase 1 completeness.

## Verified

- All 3 DLT sources AST-parse cleanly (the 2 existing files + the new
  `primary_jc_combined.py`)
- All 2 new BAML files have **zero** parse errors under
  `mise run baml:generate` (the 6 remaining errors in
  `baml_src/processing/_shared/video_kg.baml` are from another parallel
  agent's dirty state, not from this change)
- All 3 new `defs.yaml` cron assets are valid YAML
- The 1 MODIFIED spec delta is well-formed

## Out of scope (Phase 2+)

- Live web scraping (Phase 1 honours `USE_LOCAL_SCRAPES=true` only)
- CocoIndex v1 Apps for Primary + JC embeddings (the
  `cic/cocoindex/primary_embedding.py` + `junior_cycle_embedding.py`
  files referenced by the spec are deferred to Phase 2)
- Per-stage marimo dashboards in `orchestration/defs/4_asset_generation/
  marimo_dashboards/`
- Transition Year (TY) outcomes in the JC extractor (v1 covers
  Year 1 + Year 2 + Year 3 only)

## Cross-references

- [`british-isles-education-pipeline` spec](../specs/british-isles-education-pipeline/spec.md)
  — the flagship BIEP v1 (covers the 6 LC subjects, Senior Cycle only)
- [`ireland-primary-jc-dlt-baml` spec](../specs/ireland-primary-jc-dlt-baml/spec.md)
  — the capability spec this change implements
- [`cianfhoghlaim-pipeline` spec](../specs/cianfhoghlaim-pipeline/spec.md)
  — the parent 5-stage capability (5 stages × EN + GA)
- Commit `24f671f43` — `refactor(dlt): rename british_isles/en/ → england/`
  (shipped the existing primary.py + junior_cycle.py)
- Commit `54c21dd52` — `fix(baml): resolve 50 out-of-scope field: type errors`
  (shipped the existing stages/primary.baml + stages/junior_cycle.baml)
- Commit `667635dfd` — `feat(baml): single minimax-m3 text generator`
  (canonical BAML client setup)
- Commit `ccd1a7e18` — `feat(biep): complete Phase 1.1 English wiring`
  (canonical CelticIngestionComponent pattern for defs.yaml)