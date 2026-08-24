"""dlt_sources/education/jersey/british_isles — DLT sources.

Per the **2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec
change, this package was migrated from its legacy jurisdiction-first
location. The `__init__.py` re-exports the local source modules.

Legacy import paths still work via re-export shims at the old locations.
"""
from __future__ import annotations

from . import _channel_islands_helpers  # noqa: F401
from . import channel_islands  # noqa: F401
from . import jersey_jurisdiction_pipeline  # noqa: F401

__all__ = ['_channel_islands_helpers', 'channel_islands', 'jersey_jurisdiction_pipeline']
