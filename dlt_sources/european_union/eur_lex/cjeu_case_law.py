"""DEPRECATED — this legal data moved to ciandlíthe in 2026-08-25-ciandlithe-context-carveout-v1.

The canonical implementation now lives at::

    ciandlíthe/dlt_sources/law/_context/eu/eur_lex/cjeu_case_law.py

Per ``openspec/changes/2026-08-24-dlt-sources-to-multi-repo-scaffold-v1``
Phase 3.3. See ``dlt_sources/european_union/eur_lex/__init__.py`` for the
shim rationale + the workspace-dependency wire plan.
"""

from __future__ import annotations

import warnings

warnings.warn(
    "dlt_sources.european_union.eur_lex.cjeu_case_law moved to ciandlíthe; "
    "update to ciandlithe.dlt_sources.law._context.eu.eur_lex.cjeu_case_law",
    DeprecationWarning,
    stacklevel=2,
)

try:
    from ciandlithe.dlt_sources.law._context.eu.eur_lex import cjeu_case_law as _impl  # type: ignore[import-not-found]
except ImportError:
    _impl = None  # type: ignore[assignment]

if _impl is not None:
    cjeu_case_law_source = _impl.cjeu_case_law_source
    __all__ = ["cjeu_case_law_source"]
else:
    __all__: list[str] = []
