# Tasks: Delete `pipelines/shared/destinations.py` and `pipelines/shared/ducklake.py`

## 1. Validate change

- [x] 1.1 Run `openspec validate croilar-audit-phase-2-delete-pipelines-shared-drift --strict`

## 2. Delete drift + dead modules

- [x] 2.1 Delete `sruth/croilar/pipelines/shared/destinations.py` (126 lines, drift vs canonical `dlt_utils/destinations.py`)
- [x] 2.2 Delete `sruth/croilar/pipelines/shared/ducklake.py` (352 lines, dead `DuckLakeCatalog`)

## 3. Update importers

- [x] 3.1 Rewrite `sruth/croilar/pipelines/shared/__init__.py` (9 → 1 line, keep only `R2Client` re-export from `r2_client.py`)
- [x] 3.2 Patch `sruth/croilar/tests/test_smoke.py:133-137` to remove `create_duckdb_destination` + `create_ducklake_destination` asserts; keep `R2Client` assert

## 4. Verify

- [x] 4.1 `python -c "import pipelines.shared; assert hasattr(pipelines.shared, 'R2Client'); assert not hasattr(pipelines.shared, 'create_duckdb_destination'); print('PASS')"` (canonical, no fallback)
- [x] 4.2 `python -c "import pipelines.soundcloud.downloader; print('PASS')"` (production caller of `R2Client` still works)
- [x] 4.3 `python -c "import pipelines.teaching; print('PASS')"` (production caller of canonical `dlt_utils.get_dlt_destination` still works)
- [x] 4.4 Run `mise run lint:skills` (must remain 123/123)

## 5. Spec delta + audit trail

- [x] 5.1 Add 1 ADDED Requirement to `openspec/specs/croilar-data-engineering/spec.md`: no-drift-pipelines-shared-destinations
- [x] 5.2 Add Known issues row to `sruth/croilar/README.md`: row #2 RESOLVED → drifted to row #3 (test_smoke drift asserts)

## 6. Commit + push + archive

- [x] 6.1 `git add` only the 4 files + the spec delta + the README Known issues row
- [x] 6.2 Commit (refactor)
- [x] 6.3 Push
- [x] 6.4 `openspec archive croilar-audit-phase-2-delete-pipelines-shared-drift --yes`
- [x] 6.5 Commit (spec delta + archive)
- [x] 6.6 Push