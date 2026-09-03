# Tasks: England BIEP Pipeline (3 Boards × 92 Subjects)

## Phase 1 — DLT sources (7 tasks, ~3 hours)

- [ ] **T1.1** Read existing `dlt_sources/british_isles/ireland/education/ireland_jurisdiction_pipeline.py` to understand the jurisdiction pipeline pattern
- [ ] **T1.2** Create `dlt_sources/british_isles/england/education/gcse/aqa_gcse_source.py` (consumes `stedding/site_scrape_samples/england/gcse/aqa/`)
- [ ] **T1.3** Create `dlt_sources/british_isles/england/education/gcse/ocr_gcse_source.py`
- [ ] **T1.4** Create `dlt_sources/british_isles/england/education/gcse/edexcel_gcse_source.py`
- [ ] **T1.5** Create `dlt_sources/british_isles/england/education/a_level/aqa_a_level_source.py`
- [ ] **T1.6** Create `dlt_sources/british_isles/england/education/a_level/ocr_a_level_source.py`
- [ ] **T1.7** Create `dlt_sources/british_isles/england/education/a_level/edexcel_a_level_source.py`

## Phase 2 — Dagster asset groups (3 tasks, ~2 hours)

- [ ] **T2.1** Create `orchestration/defs/2_materials/england_education/gcse_assets.py` (wraps 3 DLT sources + BAML extraction + CocoIndex embedding + MotherDuck load)
- [ ] **T2.2** Create `orchestration/defs/2_materials/england_education/a_level_assets.py` (wraps 3 DLT sources + same pipeline)
- [ ] **T2.3** Register the 6 asset groups in `orchestration/definitions.py`

## Phase 3 — BAML extraction (2 tasks, ~30 minutes)

- [ ] **T3.1** Read `baml_src/british_isles/england/education/curriculum_syllabus.baml` to identify the stub `ExtractAQAQualSpec`
- [ ] **T3.2** Add real prompt for `ExtractAQAQualSpec` (3 of 4 functions already have real prompts)

## Phase 4 — Asset checks + misconfig (2 tasks, ~30 minutes)

- [ ] **T4.1** Create `orchestration/defs/2_materials/england_education/misconfig_check.py` (asserts every AQA subject has a corresponding OCR + Edexcel subject)
- [ ] **T4.2** Add `england_gcse_aqa_loaded_check` + `england_a_level_aqa_loaded_check` (>= 1 row per board × qualification)

## Phase 5 — Validate (3 tasks, ~15 minutes)

- [ ] **T5.1** `openspec validate 2026-08-10-england-biiep-pipeline-v1 --strict`
- [ ] **T5.2** `dagster asset list -m orchestration.definitions | grep england | wc -l` (should show 276 CocoIndex Apps)
- [ ] **T5.3** `mise run lint:registry && mise run lint:skills`

## Total

- **17 tasks** across **5 phases**
- **~6 hours of focused work**
- **6 new DLT sources** + **2 new asset groups** + **2 new asset checks**
- **276 CocoIndex Apps activated**
