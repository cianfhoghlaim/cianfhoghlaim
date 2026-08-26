"""DEPRECATED — moved to ciandlíthe in 2026-08-25-ciandlithe-context-carveout-v1.

Canonical: ciandlíthe/dlt_sources/law/_context/eu/eur_lex/decisions.py
Per openspec/changes/2026-08-24-dlt-sources-to-multi-repo-scaffold-v1 Phase 3.3.
"""

from __future__ import annotations

import warnings

warnings.warn(
    "dlt_sources.european_union.eur_lex.decisions moved to ciandlíthe; "
    "update to ciandlithe.dlt_sources.law._context.eu.eur_lex.decisions",
    DeprecationWarning,
    stacklevel=2,
)

try:
    from ciandlithe.dlt_sources.law._context.eu.eur_lex import decisions as _impl  # type: ignore[import-not-found]
except ImportError:
    _impl = None

if _impl is not None:
    decisions_source = _impl.decisions_source
    __all__ = ["decisions_source"]
else:
    __all__: list[str] = []
