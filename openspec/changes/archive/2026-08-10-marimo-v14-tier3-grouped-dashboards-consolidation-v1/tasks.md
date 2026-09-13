# Tasks: Tier 3 grouped dashboards consolidation (marimo v14)

> **Phase plan**: 3 phases, ~10 days work.
> **Branch**: `token-plan-lc-pipeline-2026-08` (current working branch).
> **OpenSpec change**: `2026-08-10-marimo-v14-tier3-grouped-dashboards-consolidation-v1`.

## Phase 1 — Build the 6 area_shim modules + 6 grouped dashboard skeletons (3 days)

### T1.1 — Build `notebooks/_shared/area_shims/meaisin.py` (~80 LOC)

- [ ] T1.1.a — Write the `meaisin_fleet_overview()` helper that
  returns the 12-agent fleet summary + the 4 surfaces
  (openclaw + openchamber + hermes + ocr-router)
- [ ] T1.1.b — Write the `ireland_cohort_overview()` helper
- [ ] T1.1.c — Write the `england_cohort_overview()` helper
- [ ] T1.1.d — Write the `extraction_progress_overview()` helper
- [ ] T1.1.e — Write the `eval_regression_overview()` helper
- [ ] T1.1.f — Write the `bilingual_coverage_overview()` helper

### T1.2 — Build `notebooks/_shared/area_shims/celtic_languages.py` (~80 LOC)

- [ ] T1.2.a — Write the 7 per-tab overview helpers (Gaois /
  Dúchas / Heritage Sites / Canúint / UD Treebank / Local Documents /
  Celtic Curriculum)

### T1.3 — Build `notebooks/_shared/area_shims/corpus_overview.py` (~80 LOC)

- [ ] T1.3.a — Write the 4 per-tab overview helpers (BIEP Corpus /
  Leabharlann Corpus / Cognee Knowledge Graph / Embedding Coverage)

### T1.4 — Build `notebooks/_shared/area_shims/speedrun_mmo.py` (~80 LOC)

- [ ] T1.4.a — Write the 5 per-tab overview helpers (Celtic NFT /
  Mission Control / Language Staking / Token Shop / Exam Predictions)

### T1.5 — Build `notebooks/_shared/area_shims/academic_history.py` (~80 LOC)

- [ ] T1.5.a — Write the 6 per-tab overview helpers (UoG Maths /
  Module Map / Statistics / Numerical Analysis / Formulas / Worked
  Solutions)

### T1.6 — Build `notebooks/_shared/area_shims/irish_law.py` (~80 LOC)

- [ ] T1.6.a — Write the 6 per-tab overview helpers (Personal
  Injury / Courts Index / WRC Decisions / Citizens Info / Gov.ie
  Law / Unified Search)

### T1.7-T1.12 — Build the 6 grouped dashboard skeletons (~400 LOC total)

- [ ] T1.7 — `notebooks/meaisin_ops_console.py` (PEP 723 + imports
  + 3-column grid + `mo.ui.tabs` skeleton)
- [ ] T1.8 — `notebooks/celtic_languages.py`
- [ ] T1.9 — `notebooks/corpus_overview.py`
- [ ] T1.10 — `notebooks/speedrun_mmo.py`
- [ ] T1.11 — `notebooks/academic_history.py`
- [ ] T1.12 — `notebooks/irish_law.py`

## Phase 2 — Migrate the 40+ sub-notebooks' content into the 6 grouped dashboards (5 days)

### T2.1 — Migrate `60_meaisin_ireland_ops.py` → `meaisin_ops_console.py` Ireland tab (0.5 day)

- [ ] T2.1.a — Move the `header` cell
- [ ] T2.1.b — Move the `data` cell (calls `CohortRegistry().all("ireland")`)
- [ ] T2.1.c — Move the `overview` cell (renders total cohorts)
- [ ] T2.1.d — Move the `by_stage_table` cell (renders by stage)
- [ ] T2.1.e — Move the `bilingual_coverage` cell (renders EN + GA)
- [ ] T2.1.f — Move the `lifecycle_states` cell (renders lifecycle states)
- [ ] T2.1.g — Add the 5 educative outline patterns (E1-E5)
- [ ] T2.1.h — Add the LLM "Ask the cohort registry" tab (P3)

### T2.2 — Migrate `61_meaisin_england_ops.py` → `meaisin_ops_console.py` England tab (0.5 day)

- [ ] T2.2.a-h — Same as T2.1 but for England (`registry.all("england")`)

### T2.3 — Migrate `62_meaisin_extraction_progress.py` → `meaisin_ops_console.py` Extraction tab (0.5 day)

- [ ] T2.3.a — Move the `header` + `imports` cells
- [ ] T2.3.b — Move the `filters` cell (jurisdiction + stage +
  subject multiselect)
- [ ] T2.3.c — Move the `filtered_cohorts` cell
- [ ] T2.3.d — Move the `progress_table` cell
- [ ] T2.3.e — Add the 5 educative outline patterns (E1-E5)
- [ ] T2.3.f — Add the LLM tab (P3)

### T2.4 — Migrate `63_meaisin_eval_dashboard.py` → `meaisin_ops_console.py` Eval tab (0.5 day)

- [ ] T2.4.a — Move the `header` + `cohort_data` cells
- [ ] T2.4.b — Move the `compliance_table` cell (renders the ≥95%
  per-subject gate)
- [ ] T2.4.c — Move the `regression_alerts` cell (renders the
  RegressionDiffer output)
- [ ] T2.4.d — Add the 5 educative outline patterns (E1-E5)
- [ ] T2.4.e — Add the LLM tab (P3)

### T2.5 — Migrate `64_meaisin_bilingual_curriculum.py` → `meaisin_ops_console.py` Bilingual tab (0.5 day)

- [ ] T2.5.a — Move the `header` cell
- [ ] T2.5.b — Move the `cohort_selector` cell (4 dropdowns)
- [ ] T2.5.c — Move the `audit_runner` cell (calls
  `BilingualCoverageAuditor().audit(...)`)
- [ ] T2.5.d — Move the `coverage_dashboard` cell (renders the
  coverage table)
- [ ] T2.5.e — Move the `gap_topics_table` cell (renders the
  gap topics list)
- [ ] T2.5.f — Add the 5 educative outline patterns (E1-E5)
- [ ] T2.5.g — Add the LLM tab (P3)

### T2.6-T2.12 — Migrate the Celtic languages sub-notebooks (1 day, 7 files)

- [ ] T2.6 — Migrate `06_celtic_languages_01_gaois_terminology_explorer.py`
  → `celtic_languages.py` Gaois tab
- [ ] T2.7 — Migrate `06_celtic_languages_02_duchas_folklore_with_bboxes.py`
  → `celtic_languages.py` Dúchas tab
- [ ] T2.8 — Migrate `06_celtic_languages_03_heritage_sites_map.py`
  → `celtic_languages.py` Heritage Sites tab
- [ ] T2.9 — Migrate `06_celtic_languages_04_canuint_dialect_player.py`
  → `celtic_languages.py` Canúint tab
- [ ] T2.10 — Migrate `06_celtic_languages_05_ud_celtic_treebank_viewer.py`
  → `celtic_languages.py` UD Treebank tab
- [ ] T2.11 — Migrate `06_celtic_languages_06_local_documents_subject_viewer.py`
  → `celtic_languages.py` Local Documents tab
- [ ] T2.12 — Migrate `06_celtic_languages_07_celtic_curriculum_browser.py`
  → `celtic_languages.py` Celtic Curriculum tab

### T2.13-T2.16 — Migrate the corpus overview sub-notebooks (1 day, 8 files)

- [ ] T2.13 — Migrate `12_corpus_overview_01_biep_corpus_overview.py`
  → `corpus_overview.py` BIEP Corpus tab
- [ ] T2.14 — Migrate `12_corpus_overview_01_leabharlann_corpus_overview.py`
  → `corpus_overview.py` Leabharlann Corpus tab
- [ ] T2.15 — Migrate `12_corpus_overview_02_cognee_knowledge_graph.py`
  → `corpus_overview.py` Cognee tab
- [ ] T2.16 — Migrate `12_corpus_overview_02_leabharlann_subdir_matrix.py`
  → `corpus_overview.py` Leabharlann Subdir Matrix tab (merged into
  Leabharlann Corpus tab)
- [ ] T2.17 — Migrate `12_corpus_overview_03_bge_m3_embedding_coverage.py`
  → `corpus_overview.py` BGE-M3 Embedding Coverage tab
- [ ] T2.18 — Migrate `12_corpus_overview_03_cross_archive_navigation.py`
  → `corpus_overview.py` Cross-Archive Navigation tab
- [ ] T2.19 — Migrate `12_corpus_overview_04_lakehouse_table_browser.py`
  → `corpus_overview.py` Lakehouse Table Browser tab
- [ ] T2.20 — Migrate `12_corpus_overview_04_university_institution_matrix.py`
  → `corpus_overview.py` University Institution Matrix tab

### T2.21-T2.28 — Migrate the speedrun MMO sub-notebooks (1 day, 8 files)

- [ ] T2.21 — `16_speedrun_mmo_00_celtic_nft.py` → Celtic NFT tab
- [ ] T2.22 — `16_speedrun_mmo_01_language_staking.py` → Language
  Staking tab
- [ ] T2.23 — `16_speedrun_mmo_01_mission_control.py` → Mission
  Control tab
- [ ] T2.24 — `16_speedrun_mmo_02_cianfhoghlaim_mmo_progress.py` →
  Cianfhoghlaim Progress tab
- [ ] T2.25 — `16_speedrun_mmo_02_token_shop.py` → Token Shop tab
- [ ] T2.26 — `16_speedrun_mmo_03_quest_randomness.py` → Quest
  Randomness tab
- [ ] T2.27 — `16_speedrun_mmo_04_item_exchange.py` → Item Exchange tab
- [ ] T2.28 — `16_speedrun_mmo_05..08_*.py` → remaining tabs

### T2.29-T2.36 — Migrate the academic history sub-notebooks (1 day, 8 files)

- [ ] T2.29 — `17_academic_history_01_uog_maths_corpus_overview.py` →
  UoG Maths Corpus tab
- [ ] T2.30 — `17_academic_history_02_module_syllabus_assessment_map.py` →
  Module Syllabus tab
- [ ] T2.31 — `17_academic_history_03_statistics_methods_lab.py` →
  Statistics Methods tab
- [ ] T2.32 — `17_academic_history_04_numerical_analysis_lab.py` →
  Numerical Analysis tab
- [ ] T2.33 — `17_academic_history_05_nonlinear_systems_lab.py` →
  Nonlinear Systems tab
- [ ] T2.34 — `17_academic_history_06_formulas_theorems_worked_solutions.py` →
  Formulas & Theorems tab
- [ ] T2.35 — `17_academic_history_07_assignments_exams_answers.py` →
  Assignments & Exams tab
- [ ] T2.36 — `17_academic_history_08_academic_history_chat.py` →
  Academic History Chat tab (P3 LLM chat)

### T2.37-T2.42 — Migrate the Irish law sub-notebooks (0.5 day, 6 files)

- [ ] T2.37 — `11_irish_law_01_personal_injury_journey.py` →
  Personal Injury tab
- [ ] T2.38 — `11_irish_law_02_courts_index.py` → Courts Index tab
- [ ] T2.39 — `11_irish_law_03_wrc_decision_search.py` → WRC
  Decisions tab
- [ ] T2.40 — `11_irish_law_04_citizensinfo_rights.py` → Citizens
  Info Rights tab
- [ ] T2.41 — `11_irish_law_05_gov_ie_law_corpus.py` → Gov.ie Law
  Corpus tab
- [ ] T2.42 — `11_irish_law_06_unified_cross_source_query.py` →
  Unified Cross-Source Query tab

## Phase 3 — Move the 40+ old sub-notebooks to `legacy/` + validate + archive (2 days)

### T3.1 — Move the 40+ old sub-notebooks to `notebooks/legacy/v7_consolidation/`

- [ ] T3.1.a — `mkdir -p notebooks/legacy/v7_consolidation/meaisin/`
- [ ] T3.1.b — `mkdir -p notebooks/legacy/v7_consolidation/celtic/`
- [ ] T3.1.c — `mkdir -p notebooks/legacy/v7_consolidation/corpus/`
- [ ] T3.1.d — `mkdir -p notebooks/legacy/v7_consolidation/speedrun/`
- [ ] T3.1.e — `mkdir -p notebooks/legacy/v7_consolidation/academic/`
- [ ] T3.1.f — `mkdir -p notebooks/legacy/v7_consolidation/irish_law/`
- [ ] T3.1.g — `git mv` all 40+ sub-notebooks to their respective
  subdirectories
- [ ] T3.1.h — Add a `DEPRECATED.md` redirect note in each
  subdirectory pointing to the new grouped dashboard

### T3.2 — `mise.toml` updates

- [ ] T3.2.a — Add `biep:v3:marimo:meaisin:dev` task
- [ ] T3.2.b — Add `biep:v3:marimo:celtic:dev` task
- [ ] T3.2.c — Add `biep:v3:marimo:corpus:dev` task
- [ ] T3.2.d — Add `biep:v3:marimo:speedrun:dev` task
- [ ] T3.2.e — Add `biep:v3:marimo:academic:dev` task
- [ ] T3.2.f — Add `biep:v3:marimo:irish_law:dev` task

### T3.3 — OpenSpec validation

- [ ] T3.3.a — Run `openspec validate
  2026-08-10-marimo-v14-tier3-grouped-dashboards-consolidation-v1
  --strict`
- [ ] T3.3.b — Run `marimo check` on all 6 grouped dashboards
- [ ] T3.3.c — Run `mise run biep:v3:marimo:lint`

### T3.4 — Archive

- [ ] T3.4.a — Run `openspec archive
  2026-08-10-marimo-v14-tier3-grouped-dashboards-consolidation-v1
  --yes`
- [ ] T3.4.b — Commit + push the change (per the AGENTS.md mandatory
  push policy)

## Acceptance gates

- [ ] All 6 grouped dashboards open via `marimo edit` without errors
- [ ] All 6 grouped dashboards surface the per-domain tabs
- [ ] All 40+ old sub-notebooks moved to `notebooks/legacy/v7_consolidation/`
- [ ] Each subdirectory has a `DEPRECATED.md` redirect note
- [ ] `openspec validate --strict` passes
- [ ] `marimo check` passes on all 6 grouped dashboards
- [ ] Total LOC saved: ~2,000+ (consolidation of the 40+ sub-notebooks)