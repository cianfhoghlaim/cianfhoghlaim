"""DEPRECATED — moved to ciandlíthe in 2026-08-25-ciandlithe-context-carveout-v1.

Canonical: ciandlíthe/dlt_sources/law/_context/commonwealth/nigeria/jigawa/law/legislation.py
Per openspec/changes/2026-08-24-dlt-sources-to-multi-repo-scaffold-v1 Phase 3.3.
"""

from __future__ import annotations

import warnings

warnings.warn(
    "dlt_sources.commonwealth.nigeria.states.jigawa.law.legislation moved to ciandlíthe; "
    "update to ciandlithe.dlt_sources.law._context.commonwealth.nigeria.jigawa.law.legislation",
    DeprecationWarning,
    stacklevel=2,
)

try:
    from ciandlithe.dlt_sources.law._context.commonwealth.nigeria.jigawa.law import legislation as _impl  # type: ignore[import-not-found]
except ImportError:
    _impl = None

if _impl is not None:
    legislation_source = _impl.legislation_source
    __all__ = ["legislation_source"]
else:
    __all__: list[str] = []
