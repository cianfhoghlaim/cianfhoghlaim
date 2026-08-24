"""dlt_sources/medicine/england/british_isles — DLT sources.

Per the **2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec
change, this package was migrated from its legacy jurisdiction-first
location. The `__init__.py` re-exports the local source modules.

Legacy import paths still work via re-export shims at the old locations.
"""
from __future__ import annotations

from . import gmc  # noqa: F401
from . import nhs_england  # noqa: F401
from . import nice  # noqa: F401

__all__ = ['gmc', 'nhs_england', 'nice']
