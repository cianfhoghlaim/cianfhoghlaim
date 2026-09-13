# Change: CocoIndex Skill + Test Audit v1

## Why

Plan 4 (CocoIndex deep audit) revealed version drift and import gaps
across the 42 cocoindex flow files:

1. **Version drift**:
   - `.agents/skills/cocoindex/SKILL.md` claims v1.0.14 (verified 2026-06-29)
   - Actual installed: `cocoindex==1.0.20` (per uv pip show, 2026-09-12)
   - Mismatch between skill and installed library

2. **Lost flow files** (from Phase 16-29 disaster):
   - `cocoindex_flows/british_isles/ireland/education/lc/physics.py` doesn't exist
   - The test file `tests/cocoindex/test_cocoindex.py` initially referenced it
   - Fixed by removing from the test list

3. **BAML fallback** (already implemented):
   - All Ireland LC flows use `python_baml_fallback_extract` when
     `baml_client` is unavailable (the Plan 2 BAML compilation blocker)
   - This is well-documented in the docstrings

This change updates the cocoindex skill version + adds smoke tests
that verify the flow inventory and v1 App pattern compliance.

## What Changes

### 1. Skill update
- `.agents/skills/cocoindex/SKILL.md`: v1.0.14 → v1.0.20
  - Adds "⚠️ CURRENT STATUS" section documenting 42 flows, 6 Ireland
    LC flows with BAML fallback, biep_parity_lc tests
  - Notes new v1.0.20 features not yet adopted (memo=True, Lance REST,
    concurrent_source)

### 2. CocoIndex health tests
- `tests/cocoindex/__init__.py`: new test package
- `tests/cocoindex/test_cocoindex.py`: 6 tests
  - `test_cocoindex_lib_installed` — library v1.x present
  - `test_cocoindex_flow_files_inventory` — ≥30 *_embedding.py files
  - `test_cocoindex_ireland_lc_flows_importable` — 6 LC flows + shared
  - `test_cocoindex_ireland_lc_baml_fallback_present` — Python fallback
  - `test_biep_parity_lc_tests_exist` — ≥5 parity tests
  - `test_cocoindex_v1_app_pattern_used` — no deprecated v0 patterns

## What Does NOT Change

- ❌ No new cocoindex flow files added (Phase 16-29 work to be re-applied)
- ❌ No flow logic changed (each flow uses its BAML fallback correctly)
- ❌ No new CocoIndex features adopted (memo=True, Lance REST deferred)
- ❌ No lance_db / postgres / FalkorDB destinations touched

## Dependencies

- `Blocked by: none`
- `Affected repos: cianfhoghlaim`
- Soft dependency: `2026-09-13-baml-health-test-and-skill-update-v1` (Plan 2)
  (the BAML fallback is in place because baml_client is unavailable)

## Cross-links

- Sister change: `2026-09-13-llm-serving-skill-and-test-audit-v1` (Plan 3)
- Sister change: `2026-09-13-baml-health-test-and-skill-update-v1` (Plan 2)
- Sister change: `2026-09-12-dlt-1.29-feature-adoption-v1` (Plan 1)
- Stacks: `bonneagar/stacks/lakehouse/` (DuckLake + Lance namespace)
