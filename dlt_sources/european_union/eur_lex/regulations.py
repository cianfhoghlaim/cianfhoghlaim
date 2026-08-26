"""DEPRECATED — moved to ciandlíthe in 2026-08-25-ciandlithe-context-carveout-v1.

Canonical: ciandlíthe/dlt_sources/law/_context/eu/eur_lex/regulations.py
Per openspec/changes/2026-08-24-dlt-sources-to-multi-repo-scaffold-v1 Phase 3.3.
"""

from __future__ import annotations

import warnings

warnings.warn(
    "dlt_sources.european_union.eur_lex.regulations moved to ciandlíthe; "
    "update to ciandlithe.dlt_sources.law._context.eu.eur_lex.regulations",
    DeprecationWarning,
    stacklevel=2,
)

try:
    from ciandlithe.dlt_sources.law._context.eu.eur_lex import regulations as _impl  # type: ignore[import-not-found]
except ImportError:
    _impl = None

if _impl is not None:
    regulations_source = _impl.regulations_source
    __all__ = ["regulations_source"]
else:
    __all__: list[str] = []
