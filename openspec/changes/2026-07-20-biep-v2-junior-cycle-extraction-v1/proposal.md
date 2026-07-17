# 2026-07-20-biep-v2-junior-cycle-extraction-v1

## Why

The British Isles Education Pipeline v1 covers the **6 Leaving Certificate priority
subjects** (Mathematics, Chemistry, Geography, Gaeilge, English, Computer Science)
end-to-end. The `british-isles-education-pipeline` spec explicitly defers Junior Cycle
depth — today only a single `junior_cycle.py` DLT source exists at
`dlt/british_isles/ireland/education/junior_cycle.py`, with stage-level BAML schemas at
`baml_src/british_isles/ireland/education/junior_cycle/` and
`baml_src/british_isles/ireland/education/stages/junior_cycle.baml`. There is no per-subject
DLT source, no CocoIndex v1 embedder, no Dagster L2 extraction assets, and no
MotherDuck Dive for Junior Cycle.

This change ships the **full BIEP-grade Junior Cycle pipeline** for the
Republic of Ireland:

- **18 NCCA JC subjects** × 2 languages (EN + GA) = **36 per-subject DLT sources**
- **16 NCCA JC short courses** (Coding, Chinese, Philosophy, …) = **16 short-course DLT sources**
- **36 NCCA JC CBAs** (2 per subject) — BAML-extracted from `examinations.ie`
- **4 new BAML extraction functions** (`ExtractJCCurriculum`, `ExtractCBADescriptor`,
  `ExtractJCShortCourse`, `ExtractJCExamPaper`)
- **1 CocoIndex v1 App** with **36 LanceDB tables** at
  `cianfhoghlaim.jc.<subject>.<year>_<lang>` (one per subject × year × language)
- **72 Dagster L2 assets** in `orchestration/defs/2_materials/junior_cycle/`
  (18 subjects × 4 layers: ingest → BAML extract → embed → cognify)
- **1 MotherDuck Dive** `jc_curriculum_dive` + **1 daily Flight** `jc_pdf_sync_flight`

The Junior Cycle is the **middle tier of the Irish secondary education system**
(Junior Cycle Years 1-3 + optional Transition Year), and NCCA has 18 core subjects
plus 16 short courses plus 36 Classroom-Based Assessments (the JC alternative to
exam-only assessment). This change brings all of those onto the same platform as
the existing BIEP LC pipeline, ready for the BIEP v2 umbrella that Change 2 (England)
and Changes 3-5 will extend.

## What changes

### 1. New BAML extraction schemas

4 new BAML files at
`baml_src/british_isles/ireland/education/junior_cycle/`:

- `jc_curriculum_syllabus.baml` — declares
  `ExtractJCCurriculum(subject, language, year, text) -> JCCurriculumSpec`
  Pydantic class with the 18-subject `JuniorCycleSubject` enum, the 3-year
  `Year` enum (YEAR_1, YEAR_2, YEAR_3), `Strand` enum (per-subject), and the
  full `LearningOutcome[]` per strand.
- `jc_cba_descriptor.baml` — declares
  `ExtractCBADescriptor(text) -> CBATask { subject, cba_id, title, descriptor,
  weighting, year }`
- `jc_short_course.baml` — declares
  `ExtractJCShortCourse(text) -> JCShortCourse { course_slug, title_en, title_ga,
  hours, learning_outcomes[] }`
- `jc_exam_paper_layout.baml` — declares
  `ExtractJCExamPaper(text) -> JCExamPaper { subject, year, level, sections[],
  cba_marks[] }` (with `Level ∈ {FOUNDATION, ORDINARY, HIGHER}` for the
  common-level subjects + CBA-marked sections)

Reuses the `clients.baml` `ExtractEn` (Gemma 3 4B) + `ExtractGa` (UCCIX-Mistral-24B)
clients — no new BAML clients needed for v1.

### 2. New per-subject DLT sources

36 per-subject DLT sources at
`dlt/british_isles/ireland/education/junior_cycle_subjects/{subject}_{lang}.py` —
mirror of the existing `ncca_<subject>.py` pattern, reading PDFs from
`/stedding/ingest_queue/junior_cycle/<subject>/<lang>/` (local cache per
`USE_LOCAL_SCRAPES=true`).

16 short-course DLT sources at
`dlt/british_isles/ireland/education/junior_cycle_short_courses/{course}.py`.

The 18 JC subjects (per `JC_SUBJECTS` in the existing
`dlt/british_isles/ireland/education/junior_cycle.py:51-70`): english, gaeilge,
mathematics, irish_history, geography, science, business_studies, french,
german, spanish, italian, home_economics, music, art, technology,
engineering, graphics, wood_technology.

The 16 JC short courses (per `JC_SHORT_COURSES` at line 73-90): coding,
chinese, japanese, russian, polish, lithuanian, portuguese, arabic,
hebrew, philosophy, film_studies, financial_literacy, media_literacy,
personal_professional_development, digital_media, athletic_studies.

All 52 sources honour `USE_LOCAL_SCRAPES=true` and write to the canonical
DuckLake namespace `cianfhoghlaim.education.british_isles.ireland.junior_cycle.<subject>.<lang>`
(per the `cross-region-pipeline/spec.md` Requirement "Canonical DuckLake namespace shape").

### 3. New CocoIndex v1 App

`cocoindex/subjects/junior_cycle_embedding.py` — 36 LanceDB tables at
`cianfhoghlaim.jc.<subject>.<year>_<lang>`. Conforms to the R1–R4 v1 contract:

- **R1** — `from cocoindex._shared._lifespan import shared_lifespan`
- **R2** — Imports the canonical `LANCE_DB` + `EMBEDDER` from `_lifespan`
- **R3** — `app = coco.App(coco.AppConfig(name="junior_cycle_embedding"))` at module scope
- **R4** — `@coco.fn` decorator + `lancedb.mount_table_target(LANCE_DB, ...)`

Embedder: `BAAI/bge-m3` (1024-d) per the BIEP v1 spec. Backed by the canonical
Lakehouse Lance namespace at `rest://lakehouse-lance-namespace:8182`.

### 4. New Dagster L2 assets

72 assets at `orchestration/defs/2_materials/junior_cycle/` with the 5-layer
group_name convention `2_materials.<subject>.<extraction_slug>`:

- 18 × `jc_<subject>_ingested` (Layer 1 — DLT source)
- 18 × `jc_<subject>_curriculum_extracted` (Layer 2 — BAML `ExtractJCCurriculum`)
- 18 × `jc_<subject>_embedding_flow` (Layer 3 — CocoIndex v1)
- 18 × `jc_<subject>_cognified` (Layer 4 — Cognee)

+ 16 short-course assets in `orchestration/defs/2_materials/junior_cycle/short_courses/`
+ 36 CBA assets in `orchestration/defs/2_materials/junior_cycle/cbas/`
+ 1 `jc_*_cross_subject_graphiti_stream` cross-subject Graphiti stream
+ 1 `jc_*_composite` dagster asset that orchestrates all 72

### 5. New MotherDuck Dive + daily Flight

- **MotherDuck Dive** `jc_curriculum_dive` — topic coverage per JC subject × year × language,
  with cross-references to the LC dive (so a teacher can compare Year 3 (JC) → Year 4
  (LC) topic progression).
- **Daily MotherDuck Flight** `jc_pdf_sync_flight` — re-runs BAML extraction on any new
  PDFs landed in `s3://garage/cianfhoghlaim/junior_cycle/<subject>/<lang>/<year>/<file>.pdf`.

### 6. Spec deltas

2 spec deltas:

- `openspec/specs/ireland-primary-jc-dlt-baml/spec.md` — add 1 new requirement:
  "Requirement: Junior Cycle BAML extraction (per-subject)" with the 4 BAML
  functions, the 36+ DLT sources, the CocoIndex App, and the 72 Dagster assets.
- `openspec/specs/british-isles-education-pipeline/spec.md` — add 1 new sibling
  requirement: "Requirement: Junior Cycle end-to-end" that mirrors the existing
  "Requirement: 6 Irish LC subjects end-to-end" but for JC.

## Dependencies

```yaml
Blocked by: none
Blocked by (soft): 2026-07-22-biep-v2-ocr-vlm-pipeline-convergence-v1
                   (JC is the first jurisdiction to use the OCR ensemble; the
                    convergence change formalises the VLM backends for it)
Affected repos: cianfhoghlaim (single-repo change)
```

## Acceptance gates

- `openspec validate 2026-07-20-biep-v2-junior-cycle-extraction-v1 --strict` passes
- `dg check yaml` passes on all new defs
- `baml-cli generate` succeeds on the 4 new BAML files
- 4 new BAML files exist + AST-parse
- 52 new DLT sources exist + AST-parse
- 1 CocoIndex v1 App exists + conforms to R1–R4 (verified by
  `mise run cocoindex:v1-conformance`)
- 72+ new Dagster L2 defs.yaml files YAML-parse
- 1 new MotherDuck Dive YAML + 1 Flight YAML exist
- The 6-subject BIEP v1 test (`mise run dagster:oideachais`) still passes —
  this change MUST NOT regress existing functionality
- `mise run lint:skills` still passes (53/53)
- Push target: `origin/main`

## Cross-references

- [`british-isles-education-pipeline`](../../specs/british-isles-education-pipeline/spec.md) —
  the BIEP v1 flagship that this change extends with JC parity
- [`ireland-primary-jc-dlt-baml`](../../specs/ireland-primary-jc-dlt-baml/spec.md) —
  the JC capability being extended to full extraction depth
- [`cross-region-pipeline`](../../specs/cross-region-pipeline/spec.md) —
  the umbrella contract (DuckLake namespace shape, DLT path contract, partition contract)
- [`cianfhoghlaim-baml-schemas`](../../specs/cianfhoghlaim-baml-schemas/spec.md) —
  the BAML extraction library this change writes 4 new files into
- [`cianfhoghlaim-cocoindex-v1-migration`](../../specs/cianfhoghlaim-cocoindex-v1-migration/spec.md) —
  the R1–R4 v1 conformance contract the new CocoIndex App must obey
- [`cianfhoghlaim-marimo-dashboards`](../../specs/cianfhoghlaim-marimo-dashboards/spec.md) —
  the 6 BIEP marimo notebooks (this change extends the LC pattern to JC)
- [`dagster-5-layer-component-architecture`](../../specs/dagster-5-layer-component-architecture/spec.md) —
  the 5-layer Dagster component architecture (Ingestion / Materials / Lifecycle / Asset Generation / Agent Ops)
- `docs/research/junior_cycle_ncca_endpoints.md` *(authoritative endpoint inventory)*
- `.agents/skills/dlt/SKILL.md` — DLT conventions
- `.agents/skills/baml/SKILL.md` — BAML schema patterns
- `.agents/skills/cocoindex/SKILL.md` — the R1–R4 conformance contract
- `.agents/skills/dagster/SKILL.md` — the 5-layer component architecture
