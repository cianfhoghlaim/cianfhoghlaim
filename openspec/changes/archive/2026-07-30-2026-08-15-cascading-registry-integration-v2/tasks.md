# Tasks — 2026-08-15-cascading-registry-integration-v2

## Phase 1 — Marimo dashboard migrations (25 files)

- [ ] Migrate notebooks/02_education_overview.py (BIEP v2 portal)
- [ ] Migrate notebooks/05_england_aqa_ocr_edexcel.py
- [ ] Migrate notebooks/06_celtic_languages__shared.py
- [ ] Migrate notebooks/06_celtic_languages_01_gaois_terminology_explorer.py
- [ ] Migrate notebooks/06_celtic_languages_02_duchas_folklore_with_bboxes.py
- [ ] Migrate notebooks/06_celtic_languages_03_heritage_sites_map.py
- [ ] Migrate notebooks/06_celtic_languages_04_canuint_dialect_player.py
- [ ] Migrate notebooks/06_celtic_languages_05_ud_celtic_treebank_viewer.py
- [ ] Migrate notebooks/06_celtic_languages_06_local_documents_subject_viewer.py
- [ ] Migrate notebooks/06_celtic_languages_07_celtic_curriculum_browser.py
- [ ] Migrate notebooks/07_junior_cycle_ireland.py
- [ ] Migrate notebooks/08_ocr_ensemble_audit.py
- [ ] Migrate notebooks/11_irish_law_01_personal_injury_journey.py
- [ ] Migrate notebooks/11_irish_law_02_courts_index.py
- [ ] Migrate notebooks/11_irish_law_03_wrc_decision_search.py
- [ ] Migrate notebooks/11_irish_law_04_citizensinfo_rights.py
- [ ] Migrate notebooks/11_irish_law_05_gov_ie_law_corpus.py
- [ ] Migrate notebooks/11_irish_law_06_unified_cross_source_query.py
- [ ] Migrate notebooks/12_corpus_overview__shared.py
- [ ] Migrate notebooks/12_corpus_overview_01_biep_corpus_overview.py
- [ ] Migrate notebooks/12_corpus_overview_01_leabharlann_corpus_overview.py
- [ ] Migrate notebooks/12_corpus_overview_02_cognee_knowledge_graph.py
- [ ] Migrate notebooks/12_corpus_overview_02_leabharlann_subdir_matrix.py
- [ ] Migrate notebooks/12_corpus_overview_03_bge_m3_embedding_coverage.py
- [ ] Migrate notebooks/12_corpus_overview_03_cross_archive_navigation.py

## Phase 2 — Dagster sensor wiring

- [ ] Add `_get_registry_drift_files()` helper to orchestration/defs/sync_assets.py
- [ ] Add `registry_drift_alert` asset (key: ["registry", "drift_alert"])
- [ ] Add `materialize_registry_drift_alert_op` (re-runs audit + raises Failure on drift)
- [ ] Add `materialize_registry_drift_alert_job`
- [ ] Add `registry_drift_alert_sensor` (1-hour polling + cursor-based dedup)
- [ ] Wire the 3 symbols into orchestration/definitions.py via dg.Definitions.merge

## Phase 3 — Documentation cascade

- [ ] Add `## Centralized Registries` section to agents/meaisinfhoghlaim/AGENTS.md
- [ ] Add `centralized-registry` row to the skill pointers table in agents/meaisinfhoghlaim/AGENTS.md
- [ ] Add `## Centralized Registries` section to spaces/_common/AGENTS.md
- [ ] Add `## Centralized Registries (the single source of truth)` section to root README.md
      (with 2 code snippets for `model_for()` + `schema_introspect()`)

## Phase 4 — Test suite

- [ ] Create tests/test_model_registry.py (8 tests)
- [ ] Create tests/test_registry_audit.py (5 tests)
- [ ] Create tests/test_schema_introspect.py (5 tests)
- [ ] Verify all 18 tests pass via pytest

## Phase 5 — Drift watcher notebook

- [ ] Create notebooks/14_dev_env_tools_08_registry_drift_watch.py

## Phase 6 — Spec deltas + validation

- [ ] Add spec delta to openspec/changes/2026-08-15-cascading-registry-integration-v2/specs/centralized-model-registry/spec.md
- [ ] Add spec delta to openspec/changes/2026-08-15-cascading-registry-integration-v2/specs/dagster-5-layer-component-architecture/spec.md
- [ ] Run `openspec validate 2026-08-15-cascading-registry-integration-v2 --strict`

## Phase 7 — Archive + commit

- [ ] Archive: `openspec archive 2026-08-15-cascading-registry-integration-v2 --yes`
- [ ] Commit the staged changes
- [ ] Push to origin/main
- [ ] Verify with the 11 quality gates