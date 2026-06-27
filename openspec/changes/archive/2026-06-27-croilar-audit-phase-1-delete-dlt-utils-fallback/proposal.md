# Proposal: Round 11 Phase 12 (croilar Phase 1) — Delete local fallback in `sruth/croilar/dlt_utils/destinations.py`

## Why

`sruth/croilar/dlt_utils/destinations.py` (126 lines) is a
defensive shim with an 88-line local fallback that duplicates
pre-Phase-2.3 logic. The croilar README "Known issues"
table row #2 explicitly states:

> `sruth/croilar/dlt_utils/destinations.py` is a defensive
> shim identical in pattern to `sruth/tuatha/dlt_utils/destinations.py`
> (re-exports oideachais' namespaced destinations, falls back
> to local if `oideachais` not on sys.path). The local-fallback
> code duplicates pre-Phase-2.3 logic and should be deleted once
> the oideachais workspace dep is wired.

The precondition for deleting the local fallback was met in
Round 11 Phase 1 / croilar audit Phase 1.6 (commit
`e9e0fc7d2`): the croilar packaging fix added
`croilar/__init__.py` + changed pyproject `packages = ["."]`
+ post-install `croilar/scripts/fix-pth.sh`. After that
fix, `import sruth.oideachais.dlt_utils.destinations` works
reliably from inside croilar.

The croilar workspace member already declares `oideachais` as
a `[tool.uv.sources]` dep (per the Phase 2.3 lateralise
change's original packaging intent), so the canonical
import always succeeds. The local fallback is dead code.

## Verification (pre-flight, all done)

```
$ uv run --directory sruth/croilar python -c \
    "from sruth.oideachais.dlt_utils.destinations import with_namespace; \
     ns = with_namespace('croilar'); \
     print(type(ns).__name__)"
_NamespacedDestinations  # canonical works

$ PYTHONPATH=./sruth python -c \
    "from sruth.croilar.dlt_utils.destinations import NAMESPACE, DuckLakeConfig"
# Currently succeeds via the local fallback. After Phase 12:
# - DuckLakeConfig will NOT be exported (canonical doesn't have it)
# - NAMESPACE will be exported via canonical with_namespace('croilar')
```

## What changes

### 1. MODIFY `sruth/croilar/dlt_utils/destinations.py` (126 → 13 lines)

Replace the entire file with a thin canonical-only shim:

```python
"""croilar/dlt_utils/destinations.py — thin re-export shim from oideachais.

Phase 2.3 of the lateralise change: croilar no longer carries its
own DuckLake destination implementation. It re-exports the
oideachais canonical helpers with `namespace="croilar"` pre-bound.

The croilar packaging fix (commit `e9e0fc7d2`, "fix(croilar):
close issue #17 — packaging fix for the dagster code-location")
ensures `oideachais` is on the croilar venv's sys.path via
`sruth/croilar/scripts/fix-pth.sh` rewriting the broken
uv-generated .pth to contain `sruth/` (the parent of both
`croilar/` and `oideachais/`). The canonical import therefore
always succeeds.
"""
from sruth.oideachais.dlt_utils.destinations import with_namespace

with_namespace("croilar").re_export_into(globals())
```

The canonical `with_namespace("croilar").re_export_into(globals())`
exports 4 names: `NAMESPACE`, `create_pipeline`,
`get_dlt_destination`, `get_duckdb_fallback_destination`.

The old local fallback had 4 additional names (`DuckLakeConfig`,
`_get_local_config`, `get_duckdb_fallback`, `dlt`) — of these,
only `dlt` is used externally (and that import is now handled by
the canonical shim's internal dependency). The other 3 are
fallback-only and have **zero active callers** in the repo
(verified via grep for `DuckLakeConfig` outside the destinations
file itself).

### 2. MODIFY `sruth/croilar/dlt_utils/__init__.py` (21 → 18 lines)

The current `__init__.py` re-exports 4 names from `destinations`:

| Name | In canonical? | Action |
|:--|:--|:--|
| `DuckLakeConfig` | ❌ NOT exported | REMOVE |
| `create_pipeline` | ✓ | KEEP |
| `get_dlt_destination` | ✓ | KEEP |
| `get_duckdb_fallback` | ❌ Only `get_duckdb_fallback_destination` exists | RENAME to `get_duckdb_fallback_destination` |

After Phase 12, `__init__.py` becomes:

```python
"""
DLT utilities for croilar pipeline.

Provides environment-aware DuckLake destination factory for concurrent writes.
"""

from . import destinations
from .destinations import (
    NAMESPACE,
    create_pipeline,
    get_dlt_destination,
    get_duckdb_fallback_destination,
)

__all__ = [
    "destinations",
    "NAMESPACE",
    "get_dlt_destination",
    "get_duckdb_fallback_destination",
    "create_pipeline",
]
```

### 3. UPDATE `sruth/croilar/README.md` "Known issues" row #2 → mark RESOLVED

```
| 2 | **RESOLVED 2026-06-26 (Round 11 Phase 12 / croilar audit Phase 1).** ... |
```

## What does NOT change

- The `lateralise-british-isles-domains` Phase 2.3 cross-quadrant
  architecture — `croilar` continues to re-export `oideachais`
  canonical helpers with `namespace="croilar"` pre-bound.
- The pre-existing test failures documented in Known issues #3:
  - `tests/test_smoke.py::test_module_imports[dlt_utils]`
    (imports `DuckLakeConfig` which is no longer exported —
    the test was already failing before Phase 12 because
    `DuckLakeConfig` was never exported by the canonical shim;
    Phase 12 just makes the failure mode consistent with the
    canonical intent).
  - `tests/test_smoke.py::test_dlt_duckdb_fallback`
    (uses old API `get_duckdb_fallback(base_path=...)` — the
    canonical name is `get_duckdb_fallback_destination(database_path=...)`).
  - `tests/dlt_assets/test_spotify_soundcloud_labels.py::test_croilar_dlt_assets_module_imports`
    (asserts a `spotify_ingestion_asset` symbol that doesn't
    exist; pre-existing from the same Phase 2.3 change).
  These 3 failures are pre-existing and out of scope for
  Phase 12. They are deferred to a future "fix pre-existing
  croilar test failures" change.
- The 12 DLT pipelines under `sruth/croilar/pipelines/` — none
  use `DuckLakeConfig` or `get_duckdb_fallback` (the local
  fallback's exports were only used by the pre-Phase-2.3 code
  that's been migrated to canonical exports).

## Out of scope (deferred to other changes)

- The 3 pre-existing test failures from Known issues #3.
  They predate Phase 12; fixing them requires updating
  `tests/test_smoke.py` (lines 39-44 for module imports +
  line 220 for `get_duckdb_fallback` import + line 222 for
  signature) + `tests/dlt_assets/test_spotify_soundcloud_labels.py`.
- Renaming `get_duckdb_fallback_destination` → `get_duckdb_fallback`
  in the canonical `sruth.oideachais.dlt_utils.destinations`
  module to match the old API name. This is a wider API
  rename that affects oideachais consumers too — out of
  Phase 12 scope.

## Impact

- **Net change**: 126 lines → 13 lines in `destinations.py`
  (113 lines deleted); 21 lines → 18 lines in `__init__.py`
  (3 lines net change).
- **Files touched**: 2 modifications + 1 README update + 1 spec delta.
- **No spec deletion**: spec is silent on this shim; the change
  adds 1 NEW requirement
  (no-local-fallback-in-croilar-dlt-utils-destinations).
- **Behaviour change**: The 4 names exposed by
  `sruth.croilar.dlt_utils.destinations` change:
  - OLD: `DuckLakeConfig`, `get_duckdb_fallback`,
    `create_pipeline`, `get_dlt_destination`
  - NEW: `NAMESPACE`, `get_duckdb_fallback_destination`,
    `create_pipeline`, `get_dlt_destination`
  This change is intentional and aligns the croilar surface
  with the canonical oideachais surface (via `with_namespace("croilar")`).
- **Build risk**: very low. The canonical shim has been
  working in production since commit `e9e0fc7d2`. The local
  fallback was never the active code path.