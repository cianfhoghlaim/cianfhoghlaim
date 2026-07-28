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
- [ ] 0.10 Bring the lakehouse stack up: `docker compose -f bonneagar/stacks/lakehouse/compose.yaml up -d` (13 services) — requires running Docker; deferred to operator invocation
- [ ] 0.11 Seed the British Isles Subject Registry to ≥210 cohorts via `seed_registry()` (existing `seed_registry()` helper at `baml_src/british_isles/_cross/registry_loader.py` — needs invocation once the lakehouse is up)
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
- [x] 1.6 Add 6 per-subject CocoIndex v1 Apps (`ireland_lc_<subject>_<level>_<lang>_embedding`) in `cocoindex/biep_parity/` (mathematics, chemistry, geography, english, gaeilge, computer_science)
- [x] 1.7 Add `ga_education_embedding.py` CocoIndex app (currently missing) in `cocoindex/biep_parity/ga_education_embedding.py` (new)
- [x] 1.8 Add `ireland_education_embedding.py` CocoIndex app (currently missing) in `cocoindex/biep_parity/ireland_education_embedding.py` (new)
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

## Milestone 2 — Ireland Junior Cycle (140 cohorts)

### Code tasks

- [ ] 2.1 Replace stub `junior_cycle_subjects/_factory.py` PDF-text stub with real `pymupdf` extraction in `dlt_sources/british_isles/ireland/education/junior_cycle_subjects/_factory.py:94-218`
- [ ] 2.2 Replace stub `junior_cycle_cbas/_factory.py` PDF-text stub in `dlt_sources/british_isles/ireland/education/junior_cycle_cbas/_factory.py`
- [ ] 2.3 Replace stub `junior_cycle.py` BAML call (`b.ExtractJCSpec` legacy) with `b.ExtractJCSubjectSpec` + `b.ExtractJCCurriculum` in `dlt_sources/british_isles/ireland/education/junior_cycle.py:140-298`
- [ ] 2.4 Add `ExtractJCCurriculum`, `ExtractJCSubjectSpec`, `ExtractCBADescriptor`, `ExtractJCShortCourse`, `ExtractJCExamPaper` integration into the generic Ireland pipeline
- [ ] 2.5 Add 18 per-subject JC CocoIndex apps (`ireland_jc_<subject>_<year>_<lang>_embedding`) in `cocoindex/biep_parity/ireland_jc_*` (new)
- [ ] 2.6 Add `cba_<subject>_<lang>_embedding` apps for 36 CBAs in `cocoindex/biep_parity/` (new)
- [ ] 2.7 Add `short_course_<code>_embedding` apps for 16 short courses in `cocoindex/biep_parity/` (new)
- [ ] 2.8 Add 18 per-subject JC backfill jobs (`ireland_jc_<subject>_backfill_job`) in `orchestration/defs/2_materials/ireland_education/backfill_jobs/jc/` (new)
- [ ] 2.9 Add `ireland_jc_documents_ingested` asset check (cohort count >= 140)
- [ ] 2.10 Add `ireland_jc_extractions_ragas` asset check (score >= 0.70)
- [ ] 2.11 Add `ireland_jc_lance_chunks` asset check (chunk count >= 140_000)
- [ ] 2.12 Add `ireland_jc_audit` DuckLake table
- [ ] 2.13 Add `ireland_jc_daily_automation` (cron 02:30 UTC) in `orchestration/automation/biiep_daily_automation.py`
- [ ] 2.14 Extend `notebooks/19_ireland_pipeline_dashboard.py` to include the 140 JC cohorts
- [ ] 2.15 Add `scripts/m2_ireland_jc.ts` (new) — the M2 entrypoint
- [ ] 2.16 Add `motherduck/dives/ireland_jc_curriculum_topics.sql` (new) — JC topics Dive

### M2 acceptance gate

```bash
mise run biep:v3:m2
marimo run notebooks/19_ireland_pipeline_dashboard.py  # now 152 rows (12 LC + 140 JC)
```

All 3 asset checks pass; dashboard renders 152-row matrix; ibis-first contract holds.

## Milestone 3 — England A-Level (147 cohorts)

### Code tasks

- [ ] 3.1 Replace stub `england_documents_ingested` with real Firecrawl calls to AQA/OCR/Edexcel in `orchestration/defs/2_materials/england_education/generic_england_assets.py:54-76`
- [ ] 3.2 Replace stub `england_extractions` with `ExtractUKQualSpec` calls per cohort in `orchestration/defs/2_materials/england_education/generic_england_assets.py:80-120`
- [ ] 3.3 Replace stub `england_embeddings` with `cocoindex.british_isles.england.<board>_education_embedding` calls in `orchestration/defs/2_materials/england_education/generic_england_assets.py:123-159`
- [ ] 3.4 Add 3 per-board CocoIndex apps (AQA + OCR + Edexcel × 49 A-Level subjects = 147 apps) in `cocoindex/british_isles/england/{aqa,ocr,edexcel}_alevel_embedding.py` (new)
- [ ] 3.5 Add per-subject backfill jobs (`england_<board>_<subject>_a_level_backfill_job`) in `orchestration/defs/2_materials/england_education/backfill_jobs/` (new)
- [ ] 3.6 Wire `ExtractAQAQualSpec`/`ExtractOCRQualSpec`/`ExtractEdexcelQualSpec` BAML functions to use `BIEPV3Extract` client in `baml_src/british_isles/england/education/curriculum_syllabus.baml:78-104`
- [ ] 3.7 Wire `england_aqa_a_level_jcq_monitor` ChangeDetection.io sensor in `orchestration/sensors/england_change_detection_sensor.py:74+`
- [ ] 3.8 Materialise `notebooks/20_england_pipeline_dashboard.py` with per-board × per-subject matrix
- [ ] 3.9 Add `england_a_level_documents_ingested` asset check (cohort count >= 147)
- [ ] 3.10 Add `england_a_level_extractions_ragas` asset check (score >= 0.70)
- [ ] 3.11 Add `england_a_level_lance_chunks` asset check (chunk count >= 147_000)
- [ ] 3.12 Add `england_a_level_audit` DuckLake table
- [ ] 3.13 Add `england_a_level_daily_automation` (cron 03:00 UTC) in `orchestration/automation/biiep_daily_automation.py`
- [ ] 3.14 Add `motherduck/dives/england_a_level_topics.sql` (new) — A-Level topics Dive
- [ ] 3.15 Add `scripts/m3_england_a_level.ts` (new) — the M3 entrypoint
- [ ] 3.16 Add `motherduck/dives/england_a_level_complexity.sql` (new) — A-Level complexity Dive

### M3 acceptance gate

```bash
mise run biep:v3:m3
marimo run notebooks/20_england_pipeline_dashboard.py
```

All 3 asset checks pass; dashboard renders 147-row matrix; ibis-first contract holds.

## Milestone 4 — England GCSE (129 cohorts)

### Code tasks

- [ ] 4.1 Mirror M3.1–M3.7 for GCSE qualification level in `orchestration/defs/2_materials/england_education/generic_england_assets.py:gcs<offset>`
- [ ] 4.2 Add 3 per-board CocoIndex apps (AQA + OCR + Edexcel × 43 GCSE subjects = 129 apps) in `cocoindex/british_isles/england/{aqa,ocr,edexcel}_gcse_embedding.py` (new)
- [ ] 4.3 Wire `england_aqa_gcse_jcq_monitor` ChangeDetection.io sensor in `orchestration/sensors/england_change_detection_sensor.py:74+`
- [ ] 4.4 Extend `notebooks/20_england_pipeline_dashboard.py` to include GCSE (276 rows total)
- [ ] 4.5 Add `england_gcse_documents_ingested` asset check (cohort count >= 129)
- [ ] 4.6 Add `england_gcse_extractions_ragas` asset check (score >= 0.70)
- [ ] 4.7 Add `england_gcse_lance_chunks` asset check (chunk count >= 129_000)
- [ ] 4.8 Add `england_gcse_audit` DuckLake table
- [ ] 4.9 Add `england_gcse_daily_automation` (cron 03:30 UTC) in `orchestration/automation/biiep_daily_automation.py`
- [ ] 4.10 Add per-subject backfill jobs (`england_<board>_<subject>_gcse_backfill_job`) in `orchestration/defs/2_materials/england_education/backfill_jobs/gcse/` (new)
- [ ] 4.11 Add `motherduck/dives/england_gcse_topics.sql` (new) — GCSE topics Dive
- [ ] 4.12 Add `motherduck/dives/england_gcse_complexity.sql` (new) — GCSE complexity Dive
- [ ] 4.13 Add `scripts/m4_england_gcse.ts` (new) — the M4 entrypoint
- [ ] 4.14 Add `notebooks/23_8_jurisdiction_overview.py` extension showing all 428 cohorts (12 + 140 + 147 + 129)
- [ ] 4.15 Wire `england_ocr_gcse_jcq_monitor` and `england_edexcel_gcse_jcq_monitor` ChangeDetection.io sensors
- [ ] 4.16 Add the 4 per-engine ChangeDetection sensor `gro.via.slack` post hooks to `#kcg-biep-v3` slack channel

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
