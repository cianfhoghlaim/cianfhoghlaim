"""lexicographic — DLT sources (Wave 1 restructure).

Per the **2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec
change. The legacy `dlt_sources.language/`, `dlt_sources.media/`,
`dlt_sources.api_sources/`, `dlt_sources.crypteolas/`,
`dlt_sources.apple_photos/`, `dlt_sources.filesystem/`, and
`dlt_sources.portfolio/` packages have been split into these themed
sub-packages.

Legacy import paths still work via re-export shims at the old locations.
"""
from __future__ import annotations

from . import ainm  # noqa: F401
from . import canuint  # noqa: F401
from . import canuint_audio  # noqa: F401
from . import canuint_dialect_summary  # noqa: F401
from . import canuint_search  # noqa: F401
from . import canuint_word_alignment  # noqa: F401
from . import logainm  # noqa: F401
from . import tearma  # noqa: F401
from . import tearma_search  # noqa: F401
from . import universal_dependencies  # noqa: F401

__all__ = ['ainm', 'canuint', 'canuint_audio', 'canuint_dialect_summary', 'canuint_search', 'canuint_word_alignment', 'logainm', 'tearma', 'tearma_search', 'universal_dependencies']
