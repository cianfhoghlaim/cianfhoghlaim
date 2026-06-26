# Proposal: Round 11 Phase 10 (tuatha Phase 2) — Split `dlt_source` from `leaving_cert/__init__.py`

## Why

`sruth/tuatha/dlt_sources/leaving_cert/__init__.py` (97 lines)
violates the canonical tuatha DLT convention: it contains
**5 function definitions** (1 `@dlt.source` +
3 `@dlt.resource` + 1 helper) inside the `__init__.py` itself,
rather than splitting them into a sibling module file like
the other 4 tuatha DLT packages do:

- `dlt_sources/mythology/celtic_mythology.py` defines
  `celtic_mythology_source` (the `@dlt.source` function)
- `dlt_sources/geospatial/gaeltacht_boundaries.py` defines
  `gaeltacht_boundaries_source`
- `dlt_sources/geospatial/gaelic_communities.py` defines
  `gaelic_communities_source`
- `dlt_sources/geospatial/welsh_language_areas.py` defines
  `welsh_language_areas_source`

The convention for each package is:

- `dlt_sources/<entity>/__init__.py` — thin re-export shim:
  `from .<entity> import <entity>_source`
- `dlt_sources/<entity>/<entity>.py` — the actual
  `@dlt.source` + `@dlt.resource` function bodies

`leaving_cert/` violates this convention — its `__init__.py`
contains the source code itself. This is the same anti-pattern
the Round 11 oideachais audit fixed in Phase 3D (16 multi-source
files split into 50+ canonical source files + 16 `_helpers.py`
files; archived as
`2026-06-26-oideachais-audit-phase-3d-split-multi-source-files/`).

## Verification (pre-flight, all done)

```
$ wc -l sruth/tuatha/dlt_sources/leaving_cert/__init__.py
      97 sruth/tuatha/dlt_sources/leaving_cert/__init__.py
```

The 97 lines contain:

- `import os` + `from typing import Iterator, Dict, Any, List`
- `import dlt` + `from dlt.sources.helpers import requests`
- `leaving_cert_source(years, subjects)` — `@dlt.source` that
  yields 3 `@dlt.resource`s (`exam_papers` +
  `marking_schemes` + `syllabus_documents`)
- `download_and_upload_to_s3(url, s3_key)` — mock helper
  (returns `f"s3://{bucket}/{s3_key}"` without actually
  downloading or uploading)
- 3 `@dlt.resource` functions (`exam_papers` +
  `marking_schemes` + `syllabus_documents`)

The active importer is
`sruth/tuatha/dagster_assets/exam_analysis.py:22`:

```python
from dlt_sources.leaving_cert import leaving_cert_source
```

After the split, this import continues to work because
`dlt_sources/leaving_cert/__init__.py` becomes a re-export
shim: `from .leaving_cert import leaving_cert_source`.

## What changes

### 1. CREATE `sruth/tuatha/dlt_sources/leaving_cert/leaving_cert.py`

Move all 97 lines from `__init__.py` into the new sibling
file `leaving_cert.py`. No code modification — pure file
move. The 5 functions, the 4 import statements, and the
module docstring all move verbatim.

### 2. REWRITE `sruth/tuatha/dlt_sources/leaving_cert/__init__.py`

Replace the 97-line code-bearing `__init__.py` with a 7-line
thin re-export shim matching the convention used by
`dlt_sources/mythology/__init__.py:7-11`:

```python
"""DLT sources for Leaving Certificate syllabus + exam extraction."""

from .leaving_cert import leaving_cert_source

__all__ = ["leaving_cert_source"]
```

## What does NOT change

- The function name `leaving_cert_source` (matches the
  `{module}_source` convention used by
  `celtic_mythology_source` + `gaeltacht_boundaries_source`)
- `sruth/tuatha/dlt_sources/__init__.py` (does NOT import
  from `leaving_cert/` — that package isn't exposed in the
  top-level `__all__`)
- `sruth/tuatha/dlt_sources/__pycache__/` (gitignored)
- The active importer
  `sruth/tuatha/dagster_assets/exam_analysis.py:22` — the
  `from dlt_sources.leaving_cert import leaving_cert_source`
  line continues to work via the new re-export shim
- The 4 spec-mandated thin re-export shims at
  `sruth/tuatha/agents/adk/{celtic_tutor,mythology_narrator,quest_guide,research_assistant}.py`
  — different package, different scope.

## Out of scope (deferred to other changes)

- The pre-existing
  `sruth/oideachais/agents/adk/research_agent.py:114` Pydantic
  `ValidationError: ThinkingConfig.thinking_budget_tokens` that
  breaks the canonical-agent import chain. Unrelated to
  tuatha DLT sources.
- `sruth/tuatha/dlt_sources/leaving_cert/__init__.py` imports
  `from dlt.sources.helpers import requests` but `requests`
  is **never used** in the module (verified by grepping for
  `requests.` calls in the module). The import is dead.
  Removing it is a side-cleanup that can be folded into this
  Phase 2 change OR deferred. **Decision: include the
  cleanup in this Phase** because it's a 1-line change
  inside the file move.
- The mock `download_and_upload_to_s3()` helper does NOT
  actually call `requests.get()` or `s3_client.put_object()`
  (the implementation is commented out per lines 24-27 of
  the current file). It returns a fake S3 URI. This is
  intentional mock behaviour for development. KEEP.

## Impact

- **Net change**: 1 file split (97 lines → 87 + 7 lines).
- **Files touched**: 2 (`__init__.py` rewrite + new
  `leaving_cert.py`) + 1 README.md update + 1 spec delta.
- **No spec deletion**: spec is silent on tuatha DLT
  conventions; the change adds 1 NEW requirement
  (no-dlt-source-in-package-init).
- **Build risk**: very low. The active importer continues
  to work via the re-export shim. The dead `requests`
  import is removed (no callers).
- **Behaviour change**: zero. Same function, same module
  path, same import chain.
