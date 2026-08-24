"""dlt_sources/european_union/government — DLT sources.

Per the **2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec
change, this package was migrated from its legacy jurisdiction-first
location. The `__init__.py` re-exports the local source modules.

Legacy import paths still work via re-export shims at the old locations.
"""
from __future__ import annotations

from . import commission_press  # noqa: F401
from . import council_documents  # noqa: F401
from . import europa_portal  # noqa: F401
from . import parliament_documents  # noqa: F401

__all__ = ['commission_press', 'council_documents', 'europa_portal', 'parliament_documents']
