"""cultural_heritage — DLT sources (Wave 1 restructure).

Per the **2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec
change. The legacy `dlt_sources.language/`, `dlt_sources.media/`,
`dlt_sources.api_sources/`, `dlt_sources.crypteolas/`,
`dlt_sources.apple_photos/`, `dlt_sources.filesystem/`, and
`dlt_sources.portfolio/` packages have been split into these themed
sub-packages.

Legacy import paths still work via re-export shims at the old locations.
"""
from __future__ import annotations

from . import celtic_mythology  # noqa: F401
from . import duchas  # noqa: F401
from . import duchas_images  # noqa: F401
from . import gaois  # noqa: F401
from . import gaois_combined  # noqa: F401
from . import heritage  # noqa: F401
from . import hidden_heritages  # noqa: F401

__all__ = ['celtic_mythology', 'duchas', 'duchas_images', 'gaois', 'gaois_combined', 'heritage', 'hidden_heritages']
