# Tasks: Knowledge Graph Population + Bilingual Cross-Linguistic

## Phase 1 — 5-stage cognify wiring (5 tasks, ~1 hour)

- [ ] **T1.1** Read `cross_stage_cognify/defs.yaml` template + replicate for 4 missing stages
- [ ] **T1.2** Create `orchestration/defs/3_model_lifecycle/cognify/aistear_cognify/defs.yaml`
- [ ] **T1.3** Create `orchestration/defs/3_model_lifecycle/cognify/primary_cognify/defs.yaml`
- [ ] **T1.4** Create `orchestration/defs/3_model_lifecycle/cognify/junior_cycle_cognify/defs.yaml`
- [ ] **T1.5** Create `orchestration/defs/3_model_lifecycle/cognify/senior_cycle_cognify/defs.yaml`
- [ ] **T1.6** Create `orchestration/defs/3_model_lifecycle/cognify/university_cognify/defs.yaml`

## Phase 2 — Cross-stage cognify activation (2 tasks, ~1 hour)

- [ ] **T2.1** Extend `scripts/graph_storage/cognify/cognee_integration/cross_stage_cognify.py:23-79` to iterate 8 `EDGE_DEFINITIONS` + call BAML `ExtractCrossStageLink`
- [ ] **T2.2** Add `cross_stage_edges_check` asset check requiring `edges_count >= 8`

## Phase 3 — Cross-qualification Cognee migration (2 tasks, ~1 hour)

- [ ] **T3.1** Create `scripts/migrate_cross_qual_to_cognee.py` (loads 30 + 8 equivalences → Cognee dataset `british_isles_equivalences`)
- [ ] **T3.2** Extend `meaisinfhoghlaim/alignment/cross_qualification_subject_map.py:81-120` with 8 new equivalences (Scotland Nat 5/Higher/Adv Higher, Wales WJEC, NI CCEA, Jersey/Guernsey/IoM)

## Phase 4 — Cognify sensors (7 tasks, ~2 hours)

- [ ] **T4.1-T4.7** Create 7 sensor files under `orchestration/defs/3_model_lifecycle/cognify/sensors/`:
  - `baml_schemas_sensor.py` (watches `baml_src/*.baml`)
  - `dlt_sources_sensor.py` (watches `dlt_sources/**/*.py`)
  - `skills_sensor.py` (watches `.agents/skills/**/*.md`)
  - `agent_definitions_sensor.py` (watches `agents/**/*.py`)
  - `openspec_sensor.py` (watches `openspec/changes/`)
  - `stacks_catalog_sensor.py` (watches `bonneagar/stacks/`)
  - `notebooks_sensor.py` (watches `notebooks/**/*.py`)

## Phase 5 — Bilingual GA BAML (2 tasks, ~30 minutes)

- [ ] **T5.1** Add `ExtractBilingualLearningOutcome(en_text, ga_text) -> BilingualLearningOutcome` to `baml_src/british_isles/ireland/education/_cross/cross_linguistic.baml` with real prompt
- [ ] **T5.2** Add `ExtractCrossLinguisticGA(ga_text) -> CrossLinguisticConcept` to the same file

## Phase 6 — Validate (3 tasks, ~15 minutes)

- [ ] **T6.1** Run `.venv/bin/baml-cli generate --from baml_src` to regenerate 14 BAML client files
- [ ] **T6.2** `openspec validate 2026-08-10-knowledge-graph-population-v1 --strict`
- [ ] **T6.3** `mise run lint:registry && mise run lint:skills`

## Total

- **23 tasks** across **6 phases**
- **~5 hours of focused work**
- **14 new files** + **4 modified files**
- **~900 LOC + ~300 LOC of BAML**
