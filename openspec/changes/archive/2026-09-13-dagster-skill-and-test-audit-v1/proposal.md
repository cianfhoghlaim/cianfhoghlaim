# Change: Dagster Skill + Test Audit v1

## Why

Plan 5 (Dagster deep audit) revealed version drift and a lost factory
across the Dagster orchestration layer:

1. **Version drift**:
   - `.agents/skills/dagster/SKILL.md` claims `42 lc5/lc6 assets` and
     references the lost Phase 17.1 factory
   - Actual installed: `dagster==1.13.17`
   - Actual asset count: **150 `@asset` + 54 `@asset_check`** across 77 .py files

2. **Lost factory** (from Phase 16-29 disaster):
   - `orchestration/defs/2_materials/_base/jurisdiction_assets_factory.py`
     does NOT exist
   - The 10 per-jurisdiction `*_assets.py` shims still use the
     pre-Phase-17 `JurisdictionAssetsBase` subclass pattern
   - Factory restoration deferred until Phase 16-29 work is re-applied

3. **Test coverage gap**:
   - No tests verify Dagster health (lib version, asset count, asset
     check count, per-jurisdiction shim count, dg CLI availability)

This change updates the Dagster skill + adds smoke tests that catch
version drift and inventory changes.

## What Changes

### 1. Skill update
- `.agents/skills/dagster/SKILL.md`:
  - Description: 42 assets → 150 @asset + 54 @asset_check
  - Adds "⚠️ CURRENT STATUS" section documenting the lost factory +
    jurisdiction_assets_base ABC architecture + 1.13.17 features
    not yet adopted

### 2. Dagster health tests
- `tests/dagster/__init__.py`: new test package
- `tests/dagster/test_dagster.py`: 8 tests
  - `test_dagster_lib_installed` — v1.x present
  - `test_dagster_asset_count` — ≥100 @asset decorators
  - `test_dagster_asset_check_count` — ≥30 @asset_check decorators
  - `test_jurisdiction_assets_base_exists` — ABC exists
  - `test_per_jurisdiction_shims_count` — ≥8 shims
  - `test_dagster_dg_cli_available` — dg CLI optional
  - `test_dagster_orchestrator_imports` — ireland orchestrator imports
  - `test_build_jurisdiction_assets_factory_missing` — informational

## What Does NOT Change

- ❌ No new Dagster assets added (Phase 16-29 work to be re-applied)
- ❌ No `build_jurisdiction_assets` factory restored
- ❌ No component YAML loaders adopted (Dagster 1.10+ feature)
- ❌ No Declarative Automation (Dagster 1.13+ feature)
- ❌ Per-jurisdiction shim files not modified

## Dependencies

- `Blocked by: none`
- `Affected repos: cianfhoghlaim`
- Soft dependency: Plan 1 (DLT) — orchestrators consume DLT sources

## Cross-links

- Sister change: `2026-09-13-cocoindex-skill-and-test-audit-v1` (Plan 4)
- Sister change: `2026-09-13-llm-serving-skill-and-test-audit-v1` (Plan 3)
- Sister change: `2026-09-13-baml-health-test-and-skill-update-v1` (Plan 2)
- Sister change: `2026-09-12-dlt-1.29-feature-adoption-v1` (Plan 1)
