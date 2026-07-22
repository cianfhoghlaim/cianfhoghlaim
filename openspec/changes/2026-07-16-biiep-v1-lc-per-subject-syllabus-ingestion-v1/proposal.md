# 2026-07-16-biiep-v1-lc-per-subject-syllabus-ingestion-v1

## Why

The BIEP v1 specification (capspec `british-isles-education-pipeline`)
ships per-subject NCCA syllabus ingestion + per-subject BAML
extraction for the 6 priority Irish Leaving Certificate subjects
(Mathematics, Chemistry, Geography, Gaeilge, English, Computer
Science). The canonical `ExtractCurriculumSyllabus` function in
`baml/education/lc_extraction/curriculum_syllabus.baml` already
covers the cross-subject shape (SyllabusDocument, ModuleTopic[],
LcLearningOutcome[]), and the 6 qpack BAMLs at
`baml/education/subjects/qpack_<subject>.baml` each carry the
per-subject quest-pack generator. What was missing was:

1. **6 per-subject NCCA crawl DLT sources** — one
   `ncca_<subject>.py` per LC subject, with the canonical BIEP v1
   pattern (`@dlt.resource(name="<subject>_syllabus",
   write_disposition="merge", primary_key=["url"])`, the
   `named_destinations` factory, `USE_LOCAL_SCRAPES=true` honour,
   and the `default` BAML client).
2. **1 unified BAML extractor** at
   `baml/education/unified_extraction.baml` exposing
   `ExtractLC6Syllabus(subject, text, language) -> LCSyllabus` —
   the canonical dispatcher for the per-subject pipeline.
3. **6 per-subject L1 defs YAMLs** at
   `orchestration/defs/1_ingestion/curriculum/lc6/<subject>.yaml`
   — each wraps a `CelticIngestionComponent` with `source_id =
   filesystem.leaving_cert.<subject>`, daily 04:00 UTC cron, and
   per-subject partitions (subject × language = 2 partitions).

This is the foundation for the BIEP v1 agent + dashboard +
study-tool work (Picks 2-5): a single call site
(`b.ExtractLC6Syllabus(subject="mathematics", text=..., language="en")`)
replaces six different `b.ExtractCurriculumSyllabus(text)`
invocations and gives downstream agents one stable
discriminated `LCSyllabus` return shape.

## What Changes

Ships the per-subject NCCA syllabus ingestion + BAML extraction
pipeline for the 6 BIEP v1 LC subjects (Mathematics, Chemistry,
Geography, Gaeilge, English, Computer Science) — the user's
locked plan. Applied Mathematics + History are explicitly out of
scope per the user.

- **NEW**: 6 per-subject NCCA crawl DLT sources at
  `dlt/british_isles/ireland/education/ncca_<subject>.py`
  - `ncca_mathematics.py` — Mathematics LC syllabus crawler
  - `ncca_chemistry.py` — Chemistry LC syllabus crawler
  - `ncca_geography.py` — Geography LC syllabus crawler
  - `ncca_gaeilge.py` — Gaeilge LC syllabus crawler
  - `ncca_english.py` — English LC syllabus crawler
  - `ncca_computer_science.py` — Computer Science LC syllabus crawler

  Each ships the canonical BIEP v1 dlt pattern:
  `@dlt.resource(name="<subject>_syllabus", write_disposition="merge",
  primary_key=["url"])`, the `named_destinations` factory (the
  `warehouse` named destination), `USE_LOCAL_SCRAPES=true` honour
  to read from `stedding/ingest_queue/ncca/<subject>/<lang>/`, and
  the `default` BAML client (minimax-m3 per `667635dfd`).

- **NEW**: `dlt/common/named_destinations.py` — the
  canonical named destination registry (warehouse / lakehouse /
  local_duckdb) used by the 6 per-subject sources.

- **NEW**: `baml/education/unified_extraction.baml` —
  the unified LC6 BAML extractor exposing:
  - `ExtractLC6Syllabus(subject, text, language) -> LCSyllabus`
  - 6 per-subject thin wrappers
    (`ExtractMathSyllabus`, `ExtractChemSyllabus`, `ExtractGeogSyllabus`,
    `ExtractGaelSyllabus`, `ExtractEnglSyllabus`, `ExtractCompSyllabus`)
  - The `LCSyllabus` discriminated Pydantic class (extends the
    canonical `SyllabusDocument` with the per-subject discriminator)
  - Routes to the `Default` client (minimax-m3 per `667635dfd`)

- **EXISTING (verified)**: 6 qpack BAMLs at
  `baml/education/subjects/qpack_<subject>.baml`
  Each carries the canonical `<Subject>Syllabus` pipeline:
  `Generate<Subject>QuestPack(syllabus: LeavingCertSyllabus, ...)` +
  `Extract<Subject>LOStatement(paragraph)` + per-subject formatters.
  The Math prefix is `Math*` (per `49e0259a0`); the others use
  `Engl*` / `Chem*` / `Geog*` / `Gael*` / `Comp*`.

- **NEW**: 6 per-subject L1 ingestion defs YAMLs at
  `orchestration/defs/1_ingestion/curriculum/lc6/<subject>.yaml`
  Each wraps a `CelticIngestionComponent` with:
  - `source_id: filesystem.leaving_cert.<subject>`
  - `domain: curriculum`, `nation: ie`, `subject: <subject>`
  - `automation: on_cron`, `automation_cron: "0 4 * * *"` (daily 04:00 UTC)
  - `state_backed: true`, `state_refresh_interval: monthly`
  - `partitions`: subject × language (2 partitions per subject = 12 total)

- **MODIFIED**: 1 ADDED requirement on the
  `british-isles-education-pipeline` capspec documenting the
  per-subject NCCA syllabus ingestion + BAML extraction pipeline.

## Dependencies

This change is **part of** the BIEP v1 multi-change batch:
- 2026-07-06-british-isles-education-pipeline-v1 (the canonical
  v1 capspec — already archived)
- 2026-07-16-biiep-v1-lc-per-subject-marking-grading-v1
  (parallel sibling change — the per-subject marking scheme +
  grading pipeline)
- 2026-07-16-biiep-v1-lc-per-subject-agent-workflows-v1
  (parallel sibling — the per-subject agent workflows)
- 2026-07-16-biiep-v1-lc-per-subject-marimo-study-tools-v1
  (parallel sibling — the per-subject marimo study tools)
- 2026-07-16-biiep-v1-lc-per-subject-web-surface-v1
  (parallel sibling — the per-subject web surface)

All 5 BIEP v1 per-subject changes share the same
`b.ExtractLC6Syllabus` + 6 per-subject DLT sources + 6
per-subject defs YAMLs as their foundation. This change ships
the foundation; the 4 sibling changes build the agent +
dashboard + study-tool + web layers on top.

No openspec change is blocked by this one (this change ships
the foundation; downstream siblings depend on it but are
developed in parallel).

## Verification

- All 6 per-subject DLT sources AST-parse cleanly:
  - `ncca_mathematics.py` ✓
  - `ncca_chemistry.py` ✓
  - `ncca_geography.py` ✓
  - `ncca_gaeilge.py` ✓
  - `ncca_english.py` ✓
  - `ncca_computer_science.py` ✓
- All 6 per-subject qpack BAMLs exist + verified:
  - `qpack_mathematics.baml` ✓
  - `qpack_chemistry.baml` ✓
  - `qpack_geography.baml` ✓
  - `qpack_gaeilge.baml` ✓
  - `qpack_english.baml` ✓
  - `qpack_computer_science.baml` ✓
- 1 unified BAML extractor at
  `baml/education/unified_extraction.baml` compiles
  cleanly (verified by isolated `baml-cli generate` run — the
  `baml:generate` mise task is blocked by parallel agents'
  out-of-scope BAML files in `baml/education/grading/`,
  `baml/education/marking/`, and `baml/processing/_shared/video_kg.baml`
  which I am forbidden to touch).
- All 6 per-subject defs YAMLs validate as valid YAML:
  - `lc6/mathematics.yaml` ✓
  - `lc6/chemistry.yaml` ✓
  - `lc6/geography.yaml` ✓
  - `lc6/gaeilge.yaml` ✓
  - `lc6/english.yaml` ✓
  - `lc6/computer_science.yaml` ✓
- 1 MODIFIED spec delta on `british-isles-education-pipeline`
  (1 ADDED Requirement) is well-formed.
- `openspec validate 2026-07-16-biiep-v1-lc-per-subject-syllabus-ingestion-v1 --strict` passes.
- Pushed to `origin/pick-4-biep-v1` (NOT `main`).

Reference: `openspec/changes/2026-07-06-british-isles-education-pipeline-v1/`
(the canonical v1 capspec).