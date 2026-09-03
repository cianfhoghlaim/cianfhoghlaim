# Proposal: Delete `pipelines/shared/destinations.py` and `pipelines/shared/ducklake.py` (round 11 croilar phase 2)

## Context

The `sruth/croilar/pipelines/shared/` directory contains 4 modules after the
packaging fix (commit `e9e0fc7d2`) and round 11 phase 1 (the canonical-only
rewrite of `dlt_utils/destinations.py`):

| Module | Lines | Used in production? | Verdict |
|---|--:|---|---|
| `r2_client.py` (R2Config + R2Client) | 187 | yes — `pipelines/soundcloud/downloader.py:18` | KEEP |
| `destinations.py` (create_duckdb_destination, create_ducklake_destination, create_lancedb_destination, get_destination_for_env) | 126 | no — only re-exported by `__init__.py` + asserted by `tests/test_smoke.py:133-137` | DELETE (drift) |
| `ducklake.py` (DuckLakeCatalog + initialize_catalog) | 352 | no — only re-exported by `__init__.py` + asserted by `tests/test_smoke.py` | DELETE (dead) |
| `__init__.py` (re-exports `create_duckdb_destination`, `create_ducklake_destination`, `R2Client`) | 9 | yes — indirect (its 2 re-exported-from-drift names need to be removed) | UPDATE |

**Why this is drift**, not redundancy:

- `pipelines/shared/destinations.py` re-implements a 4-function destination factory
  surface that already exists (more correctly) at the canonical
  `sruth/oideachais/dlt_utils/destinations.py` (round 11 phase 1 of croilar, commit
  `807d8f8c3`, rewrote that to a 13-line canonical-only shim via
  `with_namespace("croilar").re_export_into(globals())`).
- The croilar version diverges from the canonical one: it instantiates its own
  `duckdb.connect(...)` (line 35-40), its own `dlt.destinations.filesystem(...)`
  call (lines 73-83), and pulls R2 credentials directly from `os.environ` rather
  than going through the `STREAMS_*` env-prefix contract documented in
  `sruth/croilar/_shared/config/settings.py`.
- The only importers of the drift surface are `pipelines/shared/__init__.py`
  (which only re-exports) and `tests/test_smoke.py:133-137` (which only
  `hasattr()`-asserts presence).
- Production code already uses the canonical surface: `pipelines/teaching/__init__.py:47`
  imports `from dlt_utils import get_dlt_destination` (canonical, after the round
  11 phase 1 rewrite).

**Why `ducklake.py` is dead code, not just drift:**

- The 352-line `DuckLakeCatalog` class is NOT used in any active production code
  in the repo. The only references are:
  - `pipelines/shared/destinations.py` (the drift file we're deleting — and even
    that file only uses it inside `create_ducklake_destination`, which has no
    production callers).
  - `tests/test_smoke.py` (asserts the class is importable; will be removed).
- The canonical `DuckLakeCatalog`-equivalent lives in
  `sruth/oideachais/dlt_utils/ducklake_config.py` (and the lakehouse stack
  pipeline assets at `sruth/oideachais/dlt_utils/`). The croilar version is
  pre-DuckLake-canonical (it predates the round 11 phase 1 + phase 2 changes
  to the canonical surface).

## Proposal

Delete the 2 drift/dead modules + update the 2 importers:

1. **Delete** `sruth/croilar/pipelines/shared/destinations.py` (126 lines).
2. **Delete** `sruth/croilar/pipelines/shared/ducklake.py` (352 lines).
3. **Rewrite** `sruth/croilar/pipelines/shared/__init__.py` (9 lines → keep only
   `R2Client` re-export).
4. **Patch** `sruth/croilar/tests/test_smoke.py:133-137` (`test_pipelines_shared_exports`)
   to remove the `create_duckdb_destination`, `create_ducklake_destination`
   asserts; keep the `R2Client` assert.

After this change, `pipelines/shared/` contains only `__init__.py` (1 line) +
`r2_client.py` (187 lines). The pre-existing 3 broken test assertions in
`tests/test_smoke.py` documented at `sruth/croilar/README.md` Known issues row
#3 are out of scope (those are `test_module_imports[dlt_utils]` wanting
`DuckLakeConfig` + `test_dlt_duckdb_fallback` using the wrong signature +
`tests/dlt_assets/test_spotify_soundcloud_labels.py` wanting
`spotify_ingestion_asset`).

## Affected surfaces

- 4 files touched
- 478 lines deleted (126 + 352)
- 0 lines added (the rewritten `__init__.py` is 1 line)
- 1 spec delta added to `croilar-data-engineering`

## No backwards compatibility

Per round 11 conventions, no `try/except ImportError` fallback shims, no
`__getattr__` lazy imports, no deprecation warnings. Delete outright.