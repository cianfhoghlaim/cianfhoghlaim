"""labels — DLT sources (Wave 1 restructure).

Per the **2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec
change. The legacy `dlt_sources.language/`, `dlt_sources.media/`,
`dlt_sources.api_sources/`, `dlt_sources.crypteolas/`,
`dlt_sources.apple_photos/`, `dlt_sources.filesystem/`, and
`dlt_sources.portfolio/` packages have been split into these themed
sub-packages.

Legacy import paths still work via re-export shims at the old locations.
"""
from __future__ import annotations

from . import labels_base  # noqa: F401
from . import labels_scraper  # noqa: F401

__all__ = ['labels_base', 'labels_scraper']
