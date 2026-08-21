# 2026-07-21-biep-v2-england-aqa-ocr-baml-pipeline-v1 — Tasks

## Pre-implementation

- [ ] Verify openspec CLI ≥1.4: `openspec --version` → 1.4.1
- [ ] Verify Change 1 (JC) merged on `origin/main`
- [ ] Verify the 6-subject BIEP v1 + JC pipelines still pass: `mise run dagster:oideachais`
- [ ] Verify the ccc code index is fresh: `bun run ccc:index`

## Stage 1 — BAML extraction schemas

- [ ] Create `baml_src/british_isles/england/education/__init__.baml` (the parent re-export)
- [ ] Create `baml_src/british_isles/england/education/curriculum_syllabus.baml` with the 3 `Extract<Board>QualSpec` functions + `AQAQualSpec`, `OCRQualSpec`, `EdexcelQualSpec` Pydantic classes
- [ ] Create `baml_src/british_isles/england/education/exam_paper_layout.baml` with `ExtractAQAExamPaper` (multi-board dispatch) + `AQAExamPaper`
- [ ] Create `baml_src/british_isles/england/education/marking_scheme.baml` with `ExtractAQAMarkingScheme` + `AQAMarkingScheme` (UMS / 9-1)
- [ ] Create `baml_src/british_isles/england/education/subject_taxonomy.baml` with the 4 enums (EXAM_BOARD, QUALIFICATION_LEVEL, GCSE_AQA_SUBJECTS, A_LEVEL_AQA_SUBJECTS)
- [ ] Create `baml_src/british_isles/england/education/ensembled_extraction.baml` with `ExtractEnglandEnsembleConsensus` (the input contract for Change 3)
- [ ] Re-export from the parent `baml_src/british_isles/england/__init__.baml` (per the v6 convention)
- [ ] Run `baml-cli generate` to regenerate the Python + TS clients
- [ ] Run `baml-cli test england_curriculum_syllabus` with 9 fixture PDFs × 3 boards = 27 fixtures

## Stage 2 — Per-subject DLT sources

- [ ] Create `dlt/british_isles/england/education/subjects/__init__.py`
- [ ] Create 9 AQA per-subject sources at `dlt/.../subjects/aqa_{subject}.py` (mathematics, english_language, english_literature, chemistry, biology, physics, computer_science, history, geography)
- [ ] Create 9 OCR per-subject sources at `dlt/.../subjects/ocr_{subject}.py`
- [ ] Create 9 Edexcel per-subject sources at `dlt/.../subjects/edexcel_{subject}.py`
- [ ] Each file MUST:
  - Use `from cianfhoghlaim.dlt.common.destinations_oideachais import with_namespace` and call `with_namespace("cianfhoghlaim")`
  - Honour `USE_LOCAL_SCRAPES=true`
  - Read from `/stedding/ingest_queue/england/<board>/<subject>/`
  - Tag every row with `country_code="england"`, `jurisdiction="england"`, `exam_board="<board>"`, `qualification_level="gcse"` or `qualification_level="a_level"`
  - Yield records keyed by `source_id = "british_isles.england.education.{board}_{subject}"`
  - Write to `ducklake_cianfhoghlaim.education.british_isles.england.<board>.<subject>.<qualification_level>`
- [ ] Test a sample DLT load: `python -m dlt.pipeline ci_run_eng_aqa_mathematics`

## Stage 3 — CocoIndex v1 Apps

- [ ] Create `cocoindex_flows/british_isles/england/__init__.py`
- [ ] Create `cocoindex_flows/british_isles/england/aqa_education_embedding.py` — verify R1–R4 conformance
- [ ] Create `cocoindex_flows/british_isles/england/ocr_education_embedding.py`
- [ ] Create `cocoindex_flows/british_isles/england/edexcel_education_embedding.py`
- [ ] All 3 Apps MUST:
  - Import `from cocoindex_flows._shared._lifespan import shared_lifespan`
  - Import `LANCE_DB` + `EMBEDDER` from `_lifespan`
  - Declare `app = coco.App(coco.AppConfig(name="england_<board>_education_embedding"))` at module scope
  - Use `@coco.fn` decorator + `lancedb.mount_table_target(LANCE_DB, ...)`
- [ ] Verify the 27 LanceDB table names: `cianfhoghlaim.england.<board>.<subject>.<level>`
- [ ] Run `mise run cocoindex:v1-conformance` to validate all 3 Apps

## Stage 4 — Dagster L2 assets

- [ ] Create `orchestration/defs/2_materials/england_education/__init__.py`
- [ ] Create `orchestration/defs/2_materials/england_education/aqa/` with the 27 AQA assets (Layer 1: ingest, Layer 2: BAML extract, Layer 3: embed)
- [ ] Create `orchestration/defs/2_materials/england_education/ocr/` (mirrors aqa)
- [ ] Create `orchestration/defs/2_materials/england_education/edexcel/` (mirrors aqa)
- [ ] Create 1 cross-board diff asset `eng_aqa_vs_ocr_diff` that joins AQA + OCR + Edexcel for the same subject
- [ ] Create 1 orchestrator composite asset `eng_<board>_*_composite`
- [ ] All asset `group_name`s MUST follow the 5-layer convention
- [ ] Run `dg check yaml` to validate all defs
- [ ] Run `mise run dagster:oideachais` to verify the existing 6-subject LC + JC test still passes

## Stage 5 — MotherDuck Dives + daily Flight

- [ ] Create `motherduck/dives/eng_aqa_curriculum_dive.sql`
- [ ] Create `motherduck/dives/eng_gcse_difficulty_dive.sql`
- [ ] Create `motherduck/dives/eng_a_level_complexity_dive.sql`
- [ ] Create `motherduck/flights/eng_daily_sync_flight.sql`
- [ ] Register all 3 Dives + 1 Flight in the MotherDuck project via Komodo resource-sync
- [ ] Verify the dashboard renders at `dives.cianfhoghlaim.ie/eng_*`

## Stage 6 — Spec delta commits + validation

- [ ] Run `openspec validate 2026-07-21-biep-v2-england-aqa-ocr-baml-pipeline-v1 --strict`
- [ ] Commit the change on a dedicated branch `openspec/2026-07-21-biep-v2-england-aqa-ocr-baml-pipeline-v1`
- [ ] Open a PR on `origin/main` referencing this change
- [ ] Run `mise run lint:skills` — must remain 53/53
- [ ] After the PR merges and the change is deployed, run
  `openspec archive 2026-07-21-biep-v2-england-aqa-ocr-baml-pipeline-v1 --yes`

## Post-implementation hand-off

- [ ] File any remaining bugs as GitHub issues
- [ ] Update `docs/research/aqa_ocr_edexcel_status.md` with the now-green status
- [ ] Run `./scripts/sync_agent_docs.sh` per the global agent protocol
