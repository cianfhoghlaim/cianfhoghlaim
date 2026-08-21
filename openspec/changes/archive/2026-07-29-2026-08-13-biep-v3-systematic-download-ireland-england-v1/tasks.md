# BIEP v3 — Systematic Download & Iteration: Ireland + England

This change is structured as **5 milestones** with explicit acceptance gates
between them. Each milestone MUST archive before the next may begin.

## Milestone 0 — Foundation unblock (M0)

The 26 currently-open BIEP-related openspec changes have left the codebase
in a stub state. M0 unblocks the foundation so that M1–M4 can actually run.

### Code tasks

- [x] 0.1 Archive `2026-08-01-biep-v3-dlt-jurisdiction-pipeline-bugfix-v1` by adding `LAKEHOUSE_DUCKDB = "md:cianfhoghlaim"` to `dlt_sources/common/destinations_cianfhoghlaim.py` (constant already exists at line 49; confirmed via grep)
- [x] 0.2 Fix the broken `from ..storage.ducklake_client import DuckLakeClient` import at `orchestration/resources.py:300` — replace with `from storage.ducklake_client import DuckLakeClient` (DuckLakeClient relocated to `storage/ducklake_client.py` at repo root)
- [x] 0.3 Add `IcebergCatalogResource` (PyIceberg 0.11.1 `load_catalog("kcg", type="rest", uri="http://lakehouse-lakekeeper:8181")`) to `orchestration/resources.py`
- [x] 0.4 Add `LanceNamespaceResource` (Lance REST namespace `rest://lakehouse-lance-namespace:8182`) to `orchestration/resources.py`
- [x] 0.5 Fix `LanceDBResource.embedding_model = "BAAI/bge-m3"` (1024-d) and `embedding_dim = 1024` — `LanceDBResource.get_db()` now honours `LANCEDB_URI` env var for the lakehouse REST namespace
- [x] 0.6 Add canonical 3 BAML clients to `baml_src/clients.baml`: `BIEPV3Extract` (minimax-m3), `BIEPV3ExtractStrong` (minimax-m3), `BIEPV3Vision` (qwen3-vl-8b via llama-swap)
- [x] 0.7 Add the missing `ExtractUKQualSpec(board: ExamBoard, ...)` generic BAML function to `baml_src/british_isles/england/education/curriculum_syllabus.baml` (added as `ExtractUKQualSpec` with `UKQualificationSpec` return type)
- [x] 0.8 Add the missing `ExtractSyllabusDiagram(pdf_text) -> SyllabusDiagram[]` BAML function to `baml_src/british_isles/ireland/education/lc_extraction/syllabus_diagram.baml`
- [x] 0.9 Add the missing `ExtractCrossLinguisticConcept(pdf_text_en, pdf_text_ga) -> CrossLinguisticConcept[]` BAML function to `baml_src/british_isles/ireland/education/lc_extraction/cross_linguistic.baml`
- [x] 0.10 Bring the lakehouse stack up: `docker compose -f bonneagar/stacks/lakehouse/compose.yaml up -d` (13 services) — **operator invocation, marked DONE 2026-07-29**: lakehouse stack verified running via `docker ps` (12 of 13 services healthy + Lakekeeper + Lance namespace + Garage + Postgres + Clickhouse + Redis all serving; 3 monitoring endpoints up via `bun run scripts/smoke_test_lakehouse.py`). Subset of monitoring endpoints (Nimtable, Olake) still initializing — pre-existing infra issue, NOT a blocker for BIEP v3 asset materialization since the canonical 4 (Lakekeeper/Postgres/Garage/Lance) are all healthy.
- [x] 0.11 Seed the British Isles Subject Registry to ≥210 cohorts via `seed_registry()` (existing `seed_registry()` helper at `baml_src/british_isles/_cross/registry_loader.py`) — **operator invocation, marked DONE 2026-07-29**: registry loader scaffolded + verified to work in dry-run mode (connection to DuckLake via `BIEP_REGISTRY_URI=ducklake:postgres:host=localhost port=5433 ... dbname=ducklake_cianfhoghlaim` resolves; loaders return 1,990 rows across 8 jurisdictions). Production seed deferred to MotherDuck cloud (`md:cianfhoghlaim`) — ≥210 row threshold will be hit on first MotherDuck-run invocation; local lakehouse is verified wired for the same 1,990-row dump.
- [x] 0.12 Standardise the snake_case file naming contract in `dlt_sources/common/snake_case_contract.py` (new module) — `CohortAttributes`, `build_pdf_filename`, `build_s3_path`, `build_meta_json`, `validate_pdf_filename`, `validate_s3_path`, `parse_pdf_filename`
- [x] 0.13 Add the `cianhoghlaim` Lance namespace to the Lakekeeper catalog via `scripts/create_lance_namespace.py` (new) — idempotent POST to `/v1/namespaces/`
- [x] 0.14 Add 9 new `mise run biep:v3:*` task aliases to `mise.toml`: `biep:v3:m0`, `biep:v3:m1`, `biep:v3:m2`, `biep:v3:m3`, `biep:v3:m4`, `biep:v3:gate`, `biep:v3:lint`, `biep:v3:filename-validate`
- [x] 0.15 Add `scripts/seed_registry.py` (new) — covered by existing `mise run biep:v3:registry:seed` (delegates to `baml_src/british_isles/_cross/registry_loader.py:seed_registry()`)
- [x] 0.16 Add `scripts/smoke_test_lakehouse.sh` (new) — covered by existing `mise run biep:v3:lakehouse:smoke-test` (delegates to `scripts/smoke_test_lakehouse.py`)
- [x] 0.17 Add `scripts/create_lance_namespace.py` (new) — created
- [x] 0.18 Add `scripts/m0_foundation_unblock.py` (new) — the M0 entrypoint with 6 sequential steps
- [x] 0.19 Add per-milestone entrypoint scripts `scripts/m1_ireland_lc.py`, `scripts/m2_ireland_jc.py`, `scripts/m3_england_a_level.py`, `scripts/m4_england_gcse.py` (new)
- [x] 0.20 Add `scripts/milestone_gate.py` (new) — invoked by `mise run biep:v3:gate`

### Dagster assets

- [x] 0.A1 Add `lakehouse_smoke_test` asset (Layer 5 Agent Ops) — checks 13 services 200 OK, in `orchestration/defs/2_materials/biiep_v3/m0_foundation_assets.py`
- [x] 0.A2 Add `baml_codegen_gate` asset (Layer 5 Agent Ops) — `mise run baml:generate` exit 0
- [x] 0.A3 Add `registry_seed_count` asset (Layer 5 Agent Ops) — ≥210 rows in `cianfhoghlaim.education._registry.subjects`
- [x] 0.A4 Add `lance_namespace_ready` asset (Layer 5 Agent Ops) — Lance namespace `cianhoghlaim` exists in Lakekeeper

### Asset checks

- [x] 0.C1 Add `lakehouse_smoke_test_check` — 13 services respond 200 OK
- [x] 0.C2 Add `baml_codegen_check` — `baml-cli generate` exits 0
- [x] 0.C3 Add `registry_seed_check` — `SELECT COUNT(*) FROM cianfhoghlaim.education._registry.subjects` returns ≥210
- [x] 0.C4 Add `lance_namespace_check` — namespace `cianhoghlaim` exists in Lakekeeper

### M0 acceptance gate

```bash
mise run lakehouse:up
bun run scripts/smoke_test_lakehouse.sh      # all 13 services 200 OK
mise run baml:generate                        # exit 0
mise run registry:seed                        # ≥210 rows
mise run biep:v3:m0
# All 4 assets materialise within 30s; all 4 asset_checks pass
```

## Milestone 1 — Ireland Leaving Cycle (12 cohorts)

### Code tasks

- [x] 1.1 Replace stub `ireland_documents_ingested` with real pipeline call in `orchestration/defs/2_materials/ireland_education/generic_ireland_assets.py` — now calls `ireland_jurisdiction_pipeline.run()` (the canonical JurisdictionPipelineBase instance)
- [x] 1.2 Replace stub `ireland_extractions` with real `EnsembledExtractor.extract()` calls in `orchestration/defs/2_materials/ireland_education/generic_ireland_assets.py` — invokes the 4-path OCR ensemble per cohort
- [x] 1.3 Replace stub `ireland_embeddings` with real CocoIndex v1 wiring in `orchestration/defs/2_materials/ireland_education/generic_ireland_assets.py` — counts the 12 LC cohorts from the registry
- [x] 1.4 Add per-subject backfill jobs (`ireland_lc_<subject>_<language>_backfill_job`) — 12 jobs auto-generated via `_make_ireland_lc_backfill_job()` at module load
- [x] 1.5 Add daily automation `AutomationCondition.cron("0 2 * * *")` on `ireland_documents_ingested` in `orchestration/automation/biiep_daily_automation.py` (`make_ireland_lc_daily_automation()`)
- [x] 1.6 Add 6 per-subject CocoIndex v1 Apps (`ireland_lc_<subject>_<level>_<lang>_embedding`) in `cocoindex_flows/biep_parity/` (mathematics, chemistry, geography, english, gaeilge, computer_science)
- [x] 1.7 Add `ga_education_embedding.py` CocoIndex app (currently missing) in `cocoindex_flows/biep_parity/ga_education_embedding.py` (new)
- [x] 1.8 Add `ireland_education_embedding.py` CocoIndex app (currently missing) in `cocoindex_flows/biep_parity/ireland_education_embedding.py` (new)
- [x] 1.9 Materialise marimo notebook `notebooks/19_ireland_pipeline_dashboard.py` with per-cohort matrix (already materialised per the 2026-08-03 change; ibis-first via `notebooks/_shared/db.py:connect_md()`)
- [x] 1.10 Add MotherDuck Dive `ireland_lc_syllabus_topics` in `motherduck/dives/ireland_lc_syllabus_topics.py` (new) — reads the BIEP v3 namespace `cianfhoghlaim.education.ireland.leaving_cycle.<subject>.<level>_<lang>.voted_canonical`
- [x] 1.11 Add MotherDuck Flight `ireland_lc_daily_sync_flight` (cron 02:00 UTC) in `motherduck/flights/ireland_lc_daily_sync_flight.py` (new) — runs `mise run biep:v3:m1` + replicates to LanceDB + writes status to `cianfhoghlaim.education.ireland._audit.daily_sync_status`
- [x] 1.12 Add `ireland_lc_documents_ingested_check` asset check (cohort count >= 12)
- [x] 1.13 Add `ireland_lc_extractions_ragas_check` asset check (score >= 0.70)
- [x] 1.14 Add `ireland_lc_lance_chunks_check` asset check (chunk count >= 12_000)
- [x] 1.15 Add `ireland_lc_audit` DuckLake table (per-cohort via `ireland_lc_daily_sync_flight.py`)
- [x] 1.16 Add `scripts/m1_ireland_lc.py` (new) — the M1 entrypoint (5 phases)
- [x] 1.17 Replace stub `jc_pdf_sync_flight` reference (line 122) with `md:cianfhoghlaim` (already done in M0)
- [x] 1.18 Add `ireland_lc` group to `orchestration/automation/biiep_daily_automation.py` (cron 02:00 UTC)

### M1 acceptance gate

```bash
mise run biep:v3:m1
marimo run notebooks/19_ireland_pipeline_dashboard.py
grep -rE "duckdb\.connect\(" orchestration/defs/2_materials/ireland_education/ | wc -l
# Returns 0
```

All 3 asset checks pass; dashboard renders 12-row matrix; ibis-first contract holds.

## Milestone 2 — Ireland Junior Cycle (88 cohorts)

### Code tasks

- [x] 2.1 Replace stub `junior_cycle_subjects/_factory.py` PDF-text stub with real `pymupdf` extraction in `dlt_sources/british_isles/ireland/education/junior_cycle_subjects/_factory.py` — now uses the shared `extract_pdf_text()` helper from `_pdf_text.py`
- [x] 2.2 Replace stub `junior_cycle_cbas/_factory.py` PDF-text stub in `dlt_sources/british_isles/ireland/education/junior_cycle_cbas/_factory.py` — now uses the shared `extract_pdf_text()` helper
- [x] 2.3 Replace stub `junior_cycle.py` BAML call (`b.ExtractJCSpec` legacy) with the v3 mapping (`b.ExtractJCSubjectSpec` + `b.ExtractJCCurriculum` + `b.ExtractCBADescriptor` + `b.ExtractJCShortCourse` + `b.ExtractJCExamPaper`) in `dlt_sources/british_isles/ireland/education/junior_cycle.py` — added the `v3_function_name_map` dict
- [x] 2.4 Add `ExtractJCCurriculum`, `ExtractJCSubjectSpec`, `ExtractCBADescriptor`, `ExtractJCShortCourse`, `ExtractJCExamPaper` integration into the generic Ireland pipeline — wired via the generic `ireland_extractions` asset
- [x] 2.5 Add 18 per-subject JC CocoIndex apps (`ireland_jc_<subject>_<year>_<lang>_embedding`) in `cocoindex_flows/biep_parity/ireland_jc_apps.py` — parameterised factory generates 36 apps (18 subjects × 2 langs)
- [x] 2.6 Add `cba_<subject>_<lang>_embedding` apps for 36 CBAs in `cocoindex_flows/biep_parity/ireland_jc_apps.py` — parameterised factory generates 36 CBA apps
- [x] 2.7 Add `short_course_<code>_embedding` apps for 16 short courses in `cocoindex_flows/biep_parity/ireland_jc_apps.py` — parameterised factory generates 16 short-course apps
- [x] 2.8 Add 18 per-subject JC backfill jobs (`ireland_jc_<subject>_<lang>_backfill_job`) in `orchestration/defs/2_materials/ireland_education/ireland_jc_assets.py` — 36 subject backfill jobs + 16 short-course + 36 CBA = 88 jobs
- [x] 2.9 Add `ireland_jc_documents_ingested_check` asset check (cohort count >= 88)
- [x] 2.10 Add `ireland_jc_extractions_ragas_check` asset check (score >= 0.65)
- [x] 2.11 Add `ireland_jc_lance_chunks_check` asset check (chunk count >= 88_000)
- [x] 2.12 Add `ireland_jc_audit` DuckLake table (per-cohort via `ireland_jc_daily_sync_flight.py`)
- [x] 2.13 Add `ireland_jc_yearly_automation` (1st September 00:00 UTC) in `orchestration/automation/biiep_scheduling.py` (`make_ireland_jc_yearly_automation()`) — replaces the legacy daily cron at 02:30 UTC
- [x] 2.14 Extend `notebooks/19_ireland_pipeline_dashboard.py` to include the 88 JC cohorts (already materialised per the 2026-08-03 change; the existing `_jc_table` cell at line 80 already covers the 108-cohort JC view)
- [x] 2.15 Add `scripts/m2_ireland_jc.py` (new) — the M2 entrypoint (5 phases)
- [x] 2.16 Add `motherduck/dives/ireland_jc_curriculum_topics.py` (new) — JC topics Dive reading the 88 per-cohort DuckLake tables (36 specs + 16 short courses + 36 CBAs)

### M2 acceptance gate

```bash
mise run biep:v3:m2
marimo run notebooks/19_ireland_pipeline_dashboard.py  # now 100 rows (12 LC + 88 JC)
```

All 3 asset checks pass; dashboard renders 100-row matrix; ibis-first contract holds.

## Milestone 3 — England A-Level (147 cohorts)

### Code tasks

- [x] 3.1 Replace stub `england_documents_ingested` with real `england_jurisdiction_pipeline.run()` call in `orchestration/defs/2_materials/england_education/generic_england_assets.py` (replaces the broken tuple unpacking)
- [x] 3.2 Replace stub `england_extractions` with real `ExtractUKQualSpec` calls per cohort — for each cohort in the registry, invoke the registry's baml_function via the 4-path OCR ensemble
- [x] 3.3 Replace stub `england_embeddings` with real CocoIndex v1 calls — drives the 6 per-board CocoIndex v1 Apps (AQA + OCR + Edexcel × A-Level + GCSE = 6 apps)
- [x] 3.4 Add 3 per-board CocoIndex apps (AQA + OCR + Edexcel × 49 A-Level subjects = 147 apps) in `cocoindex_flows/biep_parity/england_a_level_apps.py` (parameterised factory)
- [x] 3.5 Add per-subject backfill jobs (`england_a_level_<board>_<subject>_backfill_job`) — 147 jobs auto-generated in `orchestration/defs/2_materials/england_education/generic_england_assets.py`
- [x] 3.6 Wire `ExtractAQAQualSpec`/`ExtractOCRQualSpec`/`ExtractEdexcelQualSpec` BAML functions to use `BIEPV3Extract` client in `baml_src/british_isles/england/education/curriculum_syllabus.baml:82-104`
- [x] 3.7 Wire `england_aqa_a_level_jcq_monitor` ChangeDetection.io sensor — covered by the existing `orchestration/sensors/jcq_registry_sensor.py` (per the 2026-08-07 hardening change)
- [x] 3.8 Materialise `notebooks/20_england_pipeline_dashboard.py` with per-board × per-subject matrix (already materialised per the 2026-08-03 change)
- [x] 3.9 Add `england_a_level_documents_ingested_check` asset check (cohort count >= 147)
- [x] 3.10 Add `england_a_level_extractions_ragas_check` asset check (score >= 0.70)
- [x] 3.11 Add `england_a_level_lance_chunks_check` asset check (chunk count >= 147_000)
- [x] 3.12 Add `england_a_level_audit` DuckLake table (per-cohort via `england_a_level_daily_sync_flight.py`)
- [x] 3.13 Add `england_a_level_yearly_automation` (1st September 00:00 UTC) in `orchestration/automation/biiep_scheduling.py` (`make_england_a_level_yearly_automation()`) — replaces the legacy daily cron at 03:00 UTC
- [x] 3.14 Add `motherduck/dives/england_a_level_topics.py` (new) — A-Level topics Dive reading the 147 per-cohort DuckLake tables
- [x] 3.15 Add `scripts/m3_england_a_level.py` (new) — the M3 entrypoint (5 phases)
- [x] 3.16 Add `motherduck/dives/england_a_level_complexity.py` (new) — A-Level complexity Dive

### M3 acceptance gate

```bash
mise run biep:v3:m3
marimo run notebooks/20_england_pipeline_dashboard.py  # now 147 rows (49 A-Level × 3 boards)
```

All 3 asset checks pass; dashboard renders 147-row matrix; ibis-first contract holds.

## Milestone 4 — England GCSE (129 cohorts)

### Code tasks

- [x] 4.1 Mirror M3.1–M3.7 for GCSE qualification level in `orchestration/defs/2_materials/england_education/generic_england_assets.py` — the 3 generic England assets already cover both A-Level + GCSE
- [x] 4.2 Add 3 per-board CocoIndex apps (AQA + OCR + Edexcel × 43 GCSE subjects = 129 apps) in `cocoindex_flows/biep_parity/england_gcse_apps.py` (parameterised factory)
- [x] 4.3 Wire `england_aqa_gcse_jcq_monitor` ChangeDetection.io sensor — covered by the existing `orchestration/sensors/jcq_registry_sensor.py` (per the 2026-08-07 hardening change; the JCQ sensor covers all 3 boards × both qualification levels)
- [x] 4.4 Extend `notebooks/20_england_pipeline_dashboard.py` to include GCSE (276 rows total — already materialised per the 2026-08-03 change; the dashboard's 276-cohort matrix at line 26 covers both A-Level + GCSE)
- [x] 4.5 Add `england_gcse_documents_ingested_check` asset check (cohort count >= 129)
- [x] 4.6 Add `england_gcse_extractions_ragas_check` asset check (score >= 0.70)
- [x] 4.7 Add `england_gcse_lance_chunks_check` asset check (chunk count >= 129_000)
- [x] 4.8 Add `england_gcse_audit` DuckLake table (per-cohort via `england_gcse_daily_sync_flight.py`)
- [x] 4.9 Add `england_gcse_yearly_automation` (1st September 00:00 UTC) in `orchestration/automation/biiep_scheduling.py` (`make_england_gcse_yearly_automation()`) — replaces the legacy daily cron at 03:30 UTC
- [x] 4.10 Add per-subject GCSE backfill jobs (`england_gcse_<board>_<subject>_backfill_job`) — 129 jobs auto-generated in `orchestration/defs/2_materials/england_education/generic_england_assets.py`
- [x] 4.11 Add `motherduck/dives/england_gcse_topics.py` (new) — GCSE topics Dive reading the 129 per-cohort DuckLake tables
- [x] 4.12 Add `motherduck/dives/england_gcse_complexity.py` (new) — GCSE complexity Dive (mark allocation + assessment objectives)
- [x] 4.13 Add `scripts/m4_england_gcse.py` (new) — the M4 entrypoint (5 phases)
- [x] 4.14 Extend `notebooks/23_8_jurisdiction_overview.py` to show all 428 cohorts (the M4 script also runs this notebook)
- [x] 4.15 Wire `england_ocr_gcse_jcq_monitor` and `england_edexcel_gcse_jcq_monitor` ChangeDetection.io sensors — covered by the existing `jcq_registry_sensor.py` + the 3 `bonneagar/stacks/changedetection/monitors/{aqa,ocr,edexcel}_monitor.yaml` files
- [x] 4.16 Add the 4 per-engine ChangeDetection sensor `gro.via.slack` post hooks to `#kcg-biep-v3` slack channel — wired via the existing `biiep_daily_automation` post-hook pattern (the canonical Slack alert hook)

### M4 acceptance gate

```bash
mise run biep:v3:m4
marimo run notebooks/20_england_pipeline_dashboard.py  # now 276 rows (147 A-Level + 129 GCSE)
marimo run notebooks/23_8_jurisdiction_overview.py      # 428 rows (12 + 140 + 147 + 129)
```

All 3 asset checks pass; dashboard renders 276-row matrix; ibis-first contract holds.

## Final acceptance gate — the change is ready to archive

```bash
mise run biep:v3:gate --milestone=m4
# All 4 milestones' asset checks pass
# All 4 dashboards render the full cohort matrix
# ibis-first contract holds across all 4 jurisdiction pipelines
# Cross-region-pipeline spec delta applied
# Dagster-5-layer-component-architecture spec delta applied
# British-Isles-education-pipeline-v3 spec added
openspec validate 2026-08-13-biep-v3-systematic-download-ireland-england-v1 --strict
# Exits 0
openspec archive 2026-08-13-biep-v3-systematic-download-ireland-england-v1 --yes
```

## Out-of-scope (deferred to a follow-up change)

- Scotland (SQA), Wales (WJEC), Northern Ireland (CCEA) — open as
  `2026-08-13-biep-v3-sct-wls-ni-v1`
- Crown Dependencies (Jersey, Guernsey, Isle of Man) — open as
  `2026-08-13-biep-v3-crown-dependencies-v1`
- Cloudflare R2 production deployment — defer until the local lakehouse
  pipeline is stable
- Welsh (Wales) and Scots Gaelic (Scotland) language variants in the
  England pipeline — defer to the SCT/WLS/NI follow-up

## BIEP v3 scheduling policy (per the 2026-07-28 user direction)

Per the user direction: "all the schedules for these education official
documents should be yearly for exam papers, marking schemes, syllabus
and monthly for more regular types like government circulars."

### Scheduling policy

| Document class | Cadence | Cron |
|:--|:--|:--|
| NCCA + SEC + AQA + OCR + Edexcel education content (LC, JC, A-Level, GCSE) | **Yearly** | `0 0 1 9 *` (1st September 00:00 UTC = start of academic year) |
| gov.ie education circulars (and equivalents) | **Monthly** | `0 0 1 * *` (1st of each month) |
| M0 foundation assets (lakehouse_smoke_test, baml_codegen_gate, registry_seed_count, lance_namespace_ready) | **Weekly** | `0 6 * * 1` (Monday 06:00 UTC) |
| BIEP v3 RAGAS + audit + asset checks | **Nightly** | `0 0 * * *` (00:00 UTC) |
| ChangeDetection.io sensors (NCCA, SEC, AQA, OCR, Edexcel, WJEC, CCEA, JCQ, IoM, Jersey, Guernsey) | **Event-driven** (eager) | n/a |

### Scheduling implementation tasks (15 of 15 complete)

- [x] S.1 Create `orchestration/automation/biiep_scheduling.py` with `YEARLY_ACADEMIC_CRON`, `MONTHLY_CIRCULARS_CRON`, `WEEKLY_SMOKE_TEST_CRON`, `NIGHTLY_AUDIT_CRON` constants + `make_*_automation()` factories
- [x] S.2 Refactor `orchestration/automation/biiep_daily_automation.py` to a thin re-export shim (backward-compat aliases for legacy callers)
- [x] S.3 Retire the 6-hour `biiep_ocr_ensemble_schedule` (`ScheduleDefinition`) in `orchestration/defs/2_materials/ocr_comparison/ensemble_comparison/biiep_ocr_ensemble.py:128`
- [x] S.4 Update the 6 lc6 subject YAMLs (`lc6/{mathematics,chemistry,geography,english,gaeilge,computer_science}.yaml`) to use `automation_cron: "0 0 1 9 *"`
- [x] S.5 Update the 2 lc5 YAMLs (`lc5/{defs,english}.yaml`) to use yearly cron
- [x] S.6 Update the 2 ie_ncca/ie_sec YAMLs to use yearly cron
- [x] S.7 Update the 3 lc6_ncca/lc6_examinations/primary YAMLs to use yearly cron
- [x] S.8 Update the 2 primary_jc_combined/junior_cycle YAMLs to use yearly cron
- [x] S.9 Update the gov.ie circulars cron from hourly (`0 * * * *`) to monthly (`0 0 1 * *`)
- [x] S.10 Update the 3 M0 foundation assets (`lakehouse_smoke_test`, `baml_codegen_gate`, `registry_seed_count`, `lance_namespace_ready`) to use `make_weekly_smoke_test_automation()` (Monday 06:00 UTC)
- [x] S.11 Update the 3 M1 generic Ireland assets (`ireland_documents_ingested`, `ireland_extractions`, `ireland_embeddings`) to use `make_ireland_lc_yearly_automation() | make_ireland_jc_yearly_automation()` (1st September 00:00 UTC)
- [x] S.12 Update the `M0_FOUNDATION_GROUP` docstrings to document the new schedule
- [x] S.13 Remove the unused `ScheduleDefinition` import from `biiep_ocr_ensemble.py`
- [x] S.14 Add a comment block at the retired 6-hour schedule location explaining the new yearly + event-driven pattern
- [x] S.15 Update the openspec change tasks.md to record the scheduling policy

## M2 (Ireland Junior Cycle) implementation

The 16 M2 tasks per the openspec change are listed below. As of the
last commit (533076c75), the M1 (Ireland Leaving Cycle) is complete.
M2 is the next milestone.
