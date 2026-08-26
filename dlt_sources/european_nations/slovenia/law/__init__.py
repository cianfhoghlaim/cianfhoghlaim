"""DEPRECATED — moved to ciandlíthe in 2026-08-25-ciandlithe-context-carveout-v1.

Canonical: ciandlíthe/dlt_sources/law/_context/european_nations/slovenia/law/
Per openspec/changes/2026-08-24-dlt-sources-to-multi-repo-scaffold-v1 Phase 3.3.

This shim is the context-data carve-out per the v2 plan §A — non-BI
European-nation law data is **context** for ciandlíthe's BI jurisdiction
pipelines, lower priority than the BI jurisdiction law content. The
European BI nations (UK + Ireland) stay in cianfhoghlaim's british_isles
subtree per Phase 3.1.
"""

from __future__ import annotations

import warnings

warnings.warn(
    "dlt_sources.european_nations.slovenia.law moved to ciandlíthe; "
    "update to ciandlithe.dlt_sources.law._context.european_nations.slovenia.law",
    DeprecationWarning,
    stacklevel=2,
)

__all__: list[str] = []
