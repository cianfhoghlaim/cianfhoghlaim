"""dlt_sources/media_personal — DLT sources.

Per the **2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec
change, this package was migrated from its legacy jurisdiction-first
location. The `__init__.py` re-exports the local source modules.

Legacy import paths still work via re-export shims at the old locations.
"""
from __future__ import annotations

from . import document_scans  # noqa: F401
from . import library_export  # noqa: F401
from . import vehicles  # noqa: F401

__all__ = ['document_scans', 'library_export', 'vehicles']
