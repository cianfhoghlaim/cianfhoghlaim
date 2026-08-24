"""dlt_sources/european_union/publications_office — DLT sources.

Per the **2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec
change, this package was migrated from its legacy jurisdiction-first
location. The `__init__.py` re-exports the local source modules.

Legacy import paths still work via re-export shims at the old locations.
"""
from __future__ import annotations

from . import cellar_documents  # noqa: F401
from . import eu_publications  # noqa: F401

__all__ = ['cellar_documents', 'eu_publications']
