# 2026-07-20-biep-v2-junior-cycle-extraction-v1 — Tasks

## Pre-implementation

- [ ] Verify openspec CLI ≥1.4: `openspec --version` → 1.4.1
- [ ] Verify the 6-subject BIEP v1 baseline passes: `mise run dagster:oideachais`
- [ ] Verify the ccc code index is fresh: `bun run ccc:index`

## Stage 1 — BAML extraction schemas

- [ ] Create `baml_src/british_isles/ireland/education/junior_cycle/__init__.py`
- [ ] Create `baml_src/british_isles/ireland/education/junior_cycle/jc_curriculum_syllabus.baml` with the `ExtractJCCurriculum` function + `JCCurriculumSpec` Pydantic class + `JuniorCycleSubject` + `Year` enums
- [ ] Create `baml_src/british_isles/ireland/education/junior_cycle/jc_cba_descriptor.baml` with `ExtractCBADescriptor` + `CBATask`
- [ ] Create `baml_src/british_isles/ireland/education/junior_cycle/jc_short_course.baml` with `ExtractJCShortCourse` + `JCShortCourse`
- [ ] Create `baml_src/british_isles/ireland/education/junior_cycle/jc_exam_paper_layout.baml` with `ExtractJCExamPaper` + `JCExamPaper`
- [ ] Re-export from the parent `baml_src/british_isles/ireland/education/__init__.baml` (or via a sibling re-export file per the v6 convention)
- [ ] Run `baml-cli generate` to regenerate the Python + TS clients
- [ ] Run `baml-cli test jc_curriculum_syllabus` with the 18 fixture PDFs from `/stedding/ingest_queue/junior_cycle/`

## Stage 2 — Per-subject DLT sources

- [ ] Create `dlt/british_isles/ireland/education/junior_cycle_subjects/__init__.py`
- [ ] Create the 18 × 2 = 36 per-subject DLT sources, following the `ncca_<subject>.py` pattern. Each file MUST:
  - Use `from cianfhoghlaim.dlt.common.destinations_oideachais import with_namespace` and call `with_namespace("cianfhoghlaim")` (per the v6 destination contract)
  - Honour `USE_LOCAL_SCRAPES=true` (default)
  - Read from `/stedding/ingest_queue/junior_cycle/<subject>/<lang>/`
  - Yield `dlt.resource` records keyed by `source_id` of the form `british_isles.ireland.education.jc_<subject>_<lang>` (per `cross-region-pipeline/spec.md` Requirement "Canonical source_id shape")
  - Write to `ducklake_cianfhoghlaim.education.british_isles.ireland.junior_cycle.<subject>.<lang>`
  - Be tagged with `country_code="ireland"` and `jurisdiction="ireland"`
- [ ] Create `dlt/british_isles/ireland/education/junior_cycle_short_courses/__init__.py`
- [ ] Create the 16 short-course DLT sources following the same pattern
- [ ] Test a sample DLT load: `python -m dlt.pipeline ci_run_jc_english_en`

## Stage 3 — CocoIndex v1 App

- [ ] Create `cocoindex_flows/subjects/junior_cycle_embedding.py` mirroring the existing `mathematics_embedding.py` pattern
- [ ] Verify R1–R4 conformance:
  - **R1** — `from cocoindex_flows._shared._lifespan import shared_lifespan`
  - **R2** — Imports `LANCE_DB` + `EMBEDDER` from `_lifespan`
  - **R3** — `app = coco.App(coco.AppConfig(name="junior_cycle_embedding"))` at module scope
  - **R4** — `@coco.fn` decorator + `lancedb.mount_table_target(LANCE_DB, ...)`
- [ ] Verify the LanceDB table names: `cianfhoghlaim.jc.<subject>.<year>_<lang>` for each of 18 subjects × 3 years × 2 languages = 108 tables
- [ ] Run `mise run cocoindex:v1-conformance` to validate the App against the conformance contract
- [ ] Run the canonical `cianfhoghlaim-cocoindex-v1-migration` test fixture for the new App

## Stage 4 — Dagster L2 assets

- [ ] Create `orchestration/defs/2_materials/junior_cycle/__init__.py`
- [ ] Create 18 `jc_<subject>_ingested` asset defs (Layer 1)
- [ ] Create 18 `jc_<subject>_curriculum_extracted` asset defs (Layer 2 — calls `b.ExtractJCCurriculum`)
- [ ] Create 18 `jc_<subject>_embedding_flow` asset defs (Layer 3 — points at the CocoIndex App)
- [ ] Create 18 `jc_<subject>_cognified` asset defs (Layer 4 — invokes Cognee)
- [ ] Create 1 `jc_cross_subject_graphiti_stream` (cross-subject Graphiti)
- [ ] Create 1 `jc_*_composite` orchestrator asset
- [ ] Create the 16 short-course assets in `orchestration/defs/2_materials/junior_cycle/short_courses/`
- [ ] Create the 36 CBA assets in `orchestration/defs/2_materials/junior_cycle/cbas/`
- [ ] All asset `group_name`s MUST follow the 5-layer convention `<N>_<layer>/<domain>/<slug>`
- [ ] Run `dg check yaml` to validate the 72 defs
- [ ] Run `mise run dagster:oideachais` to verify the existing 6-subject LC test still passes (regression check)

## Stage 5 — MotherDuck Dive + daily Flight

- [ ] Create `motherduck/dives/jc_curriculum_dive.sql` (the canonical Dive definition)
- [ ] Create `motherduck/flights/jc_pdf_sync_flight.sql` (the daily scheduled Flight)
- [ ] Register both in the MotherDuck project via Komodo resource-sync
- [ ] Verify the Dive dashboard renders with the 18-subject cohort at
  `dives.cianfhoghlaim.ie/jc_curriculum_dive`

## Stage 6 — Spec delta commits + validation

- [ ] Run `openspec validate 2026-07-20-biep-v2-junior-cycle-extraction-v1 --strict`
- [ ] Commit the change on a dedicated branch `openspec/2026-07-20-biep-v2-junior-cycle-extraction-v1`
- [ ] Open a PR on `origin/main` referencing this change
- [ ] Run `mise run lint:skills` — must remain 53/53
- [ ] After the PR merges and the change is deployed, run
  `openspec archive 2026-07-20-biep-v2-junior-cycle-extraction-v1 --yes`

## Post-implementation hand-off

- [ ] File any remaining bugs as GitHub issues
- [ ] Update `docs/research/junior_cycle_status.md` with the now-green status
- [ ] Run `./scripts/sync_agent_docs.sh` per the global agent protocol
