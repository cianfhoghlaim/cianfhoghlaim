# Proposal: Round 11 Phase 9 (tuatha Phase 1) — Delete broken `sruth/tuatha/storage/serial_executor.py` shim

## Why

The tuatha quadrant's `sruth/tuatha/storage/__init__.py:8` re-exports
`SerialDatabaseExecutor` + `get_executor` + `run_serial` from the broken
shim `sruth/tuatha/storage/serial_executor.py:19`, which in turn imports
those 3 names from the **deleted** `sruth.shared.storage` module.

`sruth/shared/` was deleted in commit `8484a6353` (per the tuatha-shared-http-shim
skill) as part of the broader canonical-home migration that landed
canonicals like `sruth.codeolas.core.embeddings` and the
`sruth.oideachais.core.storage` namespace.

The result: `sruth.tuatha.storage` is **unimportable**. Any code that
does `from sruth.tuatha.storage import SerialDatabaseExecutor` raises
`ModuleNotFoundError: No module named 'sruth.shared'`. The tuatha
README "Known issues" table #3 (packaging issue with missing
`__init__.py`) is unrelated — this broken-import failure pre-exists
that.

## Verification (pre-flight, all done)

```
$ PYTHONPATH=./sruth ./.venv/bin/python -c \
    "from sruth.tuatha.storage import SerialDatabaseExecutor"
ModuleNotFoundError: No module named 'sruth.shared'
```

The canonical home `sruth.oideachais.core.storage.serial_executor`
already exists (5,579 bytes) and exports the same 3 names.
Verified working:

```
$ PYTHONPATH=./sruth ./.venv/bin/python -c "
from sruth.oideachais.core.storage.serial_executor import (
    SerialDatabaseExecutor, get_executor, run_serial
)
"
Canonical OK: SerialDatabaseExecutor get_executor run_serial
```

## What changes

### 1. DELETE `sruth/tuatha/storage/serial_executor.py`

- 32 lines total (32 bytes of code + docstring).
- Imports from deleted `sruth.shared.storage` — broken since
  commit `8484a6353`.
- Emits a `DeprecationWarning` at module-load time pointing
  to the same non-existent `sruth.shared.storage`.
- 0 active importers of the broken path itself
  (verified via repo-wide `grep -rn "from sruth\.tuatha\.storage\.\|\.serial_executor"`).

### 2. REWRITE `sruth/tuatha/storage/__init__.py`

Rewire the re-export to point to the canonical home:

```python
"""Tuath Storage Layer — re-export shim to canonical oideachais storage."""

from sruth.oideachais.core.storage.serial_executor import (
    SerialDatabaseExecutor,
    get_executor,
    run_serial,
)

__all__ = [
    "SerialDatabaseExecutor",
    "get_executor",
    "run_serial",
]
```

The rewrite turns `sruth.tuatha.storage` from an unimportable broken
shim into a working thin re-export to the canonical oideachais home.
This is the same pattern used in
`sruth/meaisinfhoghlaim/agents/tools/__init__.py` (Round 11
meaisínfhoghlaim Phase 4) and `sruth/tuatha/agents/tools/__init__.py`
(this spec, V1 requirement).

## What does NOT change

- `sruth/oideachais/core/storage/serial_executor.py` — already
  canonical, exports the same 3 names. No modification.
- `sruth/tuatha/storage/__pycache__/` — gitignored.
- The 4 spec-mandated thin re-export shims at
  `sruth/tuatha/agents/adk/{celtic_tutor,mythology_narrator,quest_guide,research_assistant}.py`
  — these are `oideachais-pipeline/spec.md:580-660` V1 scenarios.
  Different scope.

## Out of scope (deferred to other changes)

- The pre-existing packaging issue (no `sruth/tuatha/__init__.py` +
  `pyproject.toml` doesn't declare `tuath` as a package — README #3).
  Same blast radius as the croilar fix (issue #17). Separate change.
- The pre-existing
  `sruth/oideachais/agents/adk/research_agent.py:114` Pydantic
  `ValidationError: ThinkingConfig.thinking_budget_tokens` that
  breaks the entire canonical-agent import chain. Unrelated to
  the storage shim.
- The `sruth.shared.http` replacement shim at
  `sruth/tuatha/dlt_sources/geospatial/_sruth_shim.py` — works as
  documented per `tuatha-shared-http-shim` skill. KEEP.
- The defensive `sruth/tuatha/dlt_utils/destinations.py` shim —
  works in production per README #2. KEEP.

## Impact

- **Net deletion**: 1 file (the broken shim, 32 lines).
- **Files touched**: 1 deletion + 1 rewrite (`__init__.py`) + 1
  README.md update + 1 spec delta.
- **No spec deletion**: spec is silent on `tuatha.storage`; the
  change adds 1 NEW requirement (no-broken-cross-quadrant-imports-in-tuatha)
  and 0 deletions.
- **Build risk**: very low. Zero importers of the broken module.
  Canonical already works.
- **Behavior change**: `sruth.tuatha.storage` becomes importable
  for the first time since commit `8484a6353`.
