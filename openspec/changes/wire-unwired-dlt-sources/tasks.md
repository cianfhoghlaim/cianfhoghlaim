# Tasks: wire-unwired-dlt-sources

## Phase 1: Pre-implementation audit

- [x] Confirm the 12 unwired dlt sources have no Dagster asset wrappers (verified by grep)
- [x] Confirm the 12 dlt source functions are importable

## Phase 2: Create the new asset module

- [ ] Create `sruth/oideachais/dagster_defs/assets/wire_unwired_dlt_sources.py`:
  - 12 `@asset` wrappers: `england_gias`, `scotland_insight`, `scotland_simd`, `wales_estyn`, `jersey_education`, `guernsey_education`, `ireland_primary_dlt`, `ireland_junior_cycle_dlt`, `ireland_tertiary_dlt`, `ireland_local_documents_dlt`, `ireland_parallel_corpus_dlt`
  - 12 `@asset_check` row_count checks
  - Module-level `WIRE_UNWIRED_DLT_ASSETS` and `WIRE_UNWIRED_DLT_CHECKS` lists
- [ ] Verify: `python -c "from oideachais.dagster_defs.assets.wire_unwired_dlt_sources import WIRE_UNWIRED_DLT_ASSETS, WIRE_UNWIRED_DLT_CHECKS; print(len(WIRE_UNWIRED_DLT_ASSETS), len(WIRE_UNWIRED_DLT_CHECKS))"` shows 12 12

## Phase 3: Register the new assets in definitions.py

- [ ] In `sruth/oideachais/dagster_defs/definitions.py`:
  - Add `from .assets.wire_unwired_dlt_sources import WIRE_UNWIRED_DLT_ASSETS`
  - Append `*WIRE_UNWIRED_DLT_ASSETS` to `combined_assets`
- [ ] In `sruth/oideachais/dagster_defs/asset_checks.py`:
  - Add the import of `WIRE_UNWIRED_DLT_CHECKS`
  - Append `*WIRE_UNWIRED_DLT_CHECKS` to `all_asset_checks`
- [ ] Verify: `python -c "import dagster_defs.definitions"` still loads
- [ ] Verify: `python -c "from dagster_defs.definitions import defs; print(len(list(defs.resolve_asset_graph().all_asset_keys)))"` shows 12 more asset keys

## Phase 4: Validation

- [ ] `openspec validate wire-unwired-dlt-sources --strict` passes
- [ ] All 12 dlt source functions are importable
- [ ] dagster_defs.definitions still loads

## Phase 5: Land the plane

- [ ] Stage the changes
- [ ] Commit: `git commit -m "wire-unwired-dlt-sources: add 12 Dagster asset wrappers"`
- [ ] `git pull --rebase`
- [ ] `git push origin q3-2026-oideachais-consolidation`
