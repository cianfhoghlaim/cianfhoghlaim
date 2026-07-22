# Tasks for 2026-08-11-biep-v3-lakehouse-population-v1

## Phase B: Lakehouse stack local deploy

- [ ] Run `bun run preflight:arm-oci` (safety check)
- [ ] `km deploy stack lakehouse-bunchloch --action=up`
- [ ] Wait for health: `mise run biep:v3:lakehouse:smoke-test`
- [ ] Verify Nimtable :3018 → HTTP 200 at `/`
- [ ] Verify Olake :3901 → HTTP 200 at `/health`
- [ ] Verify LanceDB Viewer :8081 → HTTP 200 at `/v1/databases`
- [ ] Verify Lakekeeper :8181 → HTTP 200 at `/health/deep`
- [ ] Verify Lakekeeper deep health: `{"postgres": "healthy", "s3": "healthy"}`

## Phase E: Registry seed + 4 pipeline runs

- [ ] `mise run biep:v3:registry:seed` → returns 3,780-row counts dict
- [ ] Verify: `SELECT COUNT(*) FROM cianfhoghlaim.education._registry.subjects` = 3,780
- [ ] Verify: 8 jurisdiction namespaces in Lakekeeper (`GET /v1/namespaces`)
- [ ] `dg launch --job ireland_jurisdiction_pipeline` → writes 544 cohort rows to DuckLake
- [ ] `dg launch --job england_jurisdiction_pipeline` → writes 276 cohort rows
- [ ] `dg launch --job sct_wls_ni_jurisdiction_pipeline --jurisdiction scotland` → 200 rows
- [ ] `dg launch --job sct_wls_ni_jurisdiction_pipeline --jurisdiction wales` → 320 rows
- [ ] `dg launch --job sct_wls_ni_jurisdiction_pipeline --jurisdiction northern_ireland` → 140 rows
- [ ] `dg launch --job crown_dependencies_jurisdiction_pipeline --jurisdiction jersey` → 240 rows
- [ ] `dg launch --job crown_dependencies_jurisdiction_pipeline --jurisdiction guernsey` → 240 rows
- [ ] `dg launch --job crown_dependencies_jurisdiction_pipeline --jurisdiction isle_of_man` → 240 rows

## Phase G: Wire CocoIndex v1 apps

- [ ] `dg launch --job ireland_education_embedding` (CocoIndex App)
- [ ] `dg launch --job en_education_embedding` (CocoIndex App)
- [ ] `dg launch --job sct_education_embedding` (CocoIndex App)
- [ ] `dg launch --job wls_education_embedding` (CocoIndex App)
- [ ] `dg launch --job ni_education_embedding` (CocoIndex App)
- [ ] `dg launch --job jersey_education_embedding` (CocoIndex App)
- [ ] `dg launch --job guernsey_education_embedding` (CocoIndex App)
- [ ] `dg launch --job isle_of_man_education_embedding` (CocoIndex App)
- [ ] Run `consume_voted_ducklake_to_lance()` for each LC6 subject (mathematics, chemistry, geography, gaeilge, english, computer_science)
- [ ] Verify LanceDB Viewer :8081 → `codebase_chunks` populated (≥ 1,000 rows)
- [ ] Verify LanceDB Viewer :8081 → `codebase_graph` populated (≥ 500 edges)

## Phase F: BIEP v3 MotherDuck Flights

- [ ] `dg list jobs | grep -E "(ireland|england|sct_wls_ni|crown_dependencies)_full_coverage"` → 4 entries
- [ ] `dg launch --job ireland_full_coverage_flight` → triggers Dagster RunRequest
- [ ] `dg launch --job england_full_coverage_flight` → triggers Dagster RunRequest
- [ ] `dg launch --job sct_wls_ni_flight` → triggers Dagster RunRequest
- [ ] `dg launch --job crown_dependencies_flight` → triggers Dagster RunRequest
- [ ] Validate in `notebooks/12_corpus_overview_05_baml_extraction_log_viewer.py` (RAGAS logs visible)

## Notebook namespace sweep

- [ ] Run `bun run scripts/refactor-biep-notebooks.py --write`
- [ ] Verify: `grep -rn "md:oideachais" notebooks/ | wc -l` returns 0
- [ ] Verify: `notebooks/_shared/db.py:26` still defines `LAKEHOUSE_URI_DEFAULT = "md:cianfhoghlaim"`
- [ ] Smoke-test: `notebooks/01_overview_setup.py` connects via `md:cianfhoghlaim`
- [ ] Smoke-test: `notebooks/23_8_jurisdiction_overview.py` queries the 8-jurisdiction registry

## Final gate

- [ ] `openspec validate 2026-08-11-biep-v3-lakehouse-population-v1 --strict` passes
- [ ] All 8 jurisdictions visible in `notebooks/23_8_jurisdiction_overview.py`
- [ ] All 4 BIEP v3 MotherDuck Flights emit at least 1 RunRequest each
- [ ] Both changes archived together:
  - `openspec archive 2026-08-10-biep-v3-preflight-bug-fixes-v1 --yes`
  - `openspec archive 2026-08-11-biep-v3-lakehouse-population-v1 --yes`
- [ ] Final commit + push to `origin/openspec/2026-07-25-refactor-batch-v1`