"""DEPRECATED — moved to ciandlíthe in 2026-08-25-ciandlithe-context-carveout-v1.

Canonical: ciandlíthe/dlt_sources/law/_context/commonwealth/australia/law/
Per openspec/changes/2026-08-24-dlt-sources-to-multi-repo-scaffold-v1 Phase 3.3.

This shim emits a DeprecationWarning at import time. The actual DLT source
classes are NOT re-exported here because the implementation lives in the
sister repo. Until the workspace dependency is wired, callers get the
warning + an ImportError when they try to use the symbols — the canonical
signal to update imports.
"""

from __future__ import annotations

import warnings

warnings.warn(
    "dlt_sources.commonwealth.australia.law moved to ciandlíthe; "
    "update to ciandlithe.dlt_sources.law._context.commonwealth.australia.law",
    DeprecationWarning,
    stacklevel=2,
)

__all__: list[str] = []
