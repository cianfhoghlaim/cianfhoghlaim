"""dlt_sources/commonwealth/nigeria — DLT sources.

Per the **2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec
change, this package was migrated from its legacy jurisdiction-first
location. The `__init__.py` re-exports the local source modules.

Legacy import paths still work via re-export shims at the old locations.
"""
from __future__ import annotations

from . import federal_tier  # noqa: F401
from . import states  # noqa: F401

__all__ = ['federal_tier', 'states']
