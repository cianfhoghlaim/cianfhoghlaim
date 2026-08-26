"""DEPRECATED — this legal data moved to ciandlíthe in 2026-08-25-ciandlithe-context-carveout-v1.

The canonical implementation now lives at::

    ciandlíthe/dlt_sources/law/_context/eu/eur_lex/

To consume it directly, install ciandlíthe as a workspace dependency::

    uv pip install -e ../ciandlithe

and import from::

    from ciandlithe.dlt_sources.law._context.eu.eur_lex import (
        cjeu_case_law_source,
        decisions_source,
        directives_source,
        regulations_source,
        treaties_source,
    )

This shim emits a ``DeprecationWarning`` at import time. The actual DLT
source classes are NOT re-exported here because the implementation lives
in the sister repo. If you have not yet wired the workspace dependency,
``from dlt_sources.european_union.eur_lex import cjeu_case_law_source``
will raise ``ImportError`` once the shim's fallback path is taken — this
is the canonical signal to update your imports.

Per ``openspec/changes/2026-08-24-dlt-sources-to-multi-repo-scaffold-v1``
Phase 3.3 (the EU + Commonwealth + European-context legal carve-out to
ciandlíthe).
"""

from __future__ import annotations

import warnings

warnings.warn(
    "dlt_sources.european_union.eur_lex moved to ciandlíthe in "
    "2026-08-25-ciandlithe-context-carveout-v1; update your imports to "
    "ciandlithe.dlt_sources.law._context.eu.eur_lex",
    DeprecationWarning,
    stacklevel=2,
)

try:
    from ciandlithe.dlt_sources.law._context.eu.eur_lex import (  # type: ignore[import-not-found]
        cjeu_case_law_source,
        decisions_source,
        directives_source,
        regulations_source,
        treaties_source,
    )
except ImportError:
    # ciandlíthe is not installed as a workspace member yet — the carve-out
    # ships the data files into ciandlíthe but the workspace dependency wire
    # is deferred to a follow-up openspec change. Until then, callers get a
    # DeprecationWarning at import time + an ImportError when they try to
    # use the symbols. This is the canonical signal to update imports.
    _MISSING_DEPENDENCY = True
else:
    _MISSING_DEPENDENCY = False


__all__: list[str] = [
    "cjeu_case_law_source",
    "decisions_source",
    "directives_source",
    "regulations_source",
    "treaties_source",
]
