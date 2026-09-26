# Tasks: 2026-10-05-lakehouse-ml-assetgen-wiring-v1

## 1. Group A — Lakehouse bridge (the soft side)

- [x] **A1** `orchestration/assets/ducklake_maintenance.py` — `create_ducklake_assets_database()` + `register_asset_table()` + `sync_lancedb_to_iceberg()`
- [x] **A2** `orchestration/assets/otel_image_gen_traces.py` — OTel spans for the DLT → BAML → CocoIndex → image-gen → LanceDB chain
- [x] **A3** `notebooks/dashboards/asset_lakehouse_browser.py` — marimo dashboard (queries the asset table via DuckLake SQL)

## 2. Group B — Spec materialisation

- [x] **B1** `openspec/specs/lakehouse-assetgen-wiring/spec.md` — 4 Requirements
- [x] **B2** `bunx openspec validate 2026-10-05-lakehouse-ml-assetgen-wiring-v1 --strict` passes

## 3. Group C — Verification + commit + push

- [x] **C1** `uv run python -c "from orchestration.assets.ducklake_maintenance import register_asset_table"` works
- [x] **C2** `uv run python -c "from orchestration.assets.otel_image_gen_traces import trace_image_gen_chain"` works
- [x] **C3** `git add -A && git commit && git push`
- [x] **C4** Create PR via `gh pr create`
