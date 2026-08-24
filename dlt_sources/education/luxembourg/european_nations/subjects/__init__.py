"""dlt_sources/education/luxembourg/european_nations/subjects — DLT sources.

Per the **2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec
change, this package was migrated from its legacy jurisdiction-first
location. The `__init__.py` re-exports the local source modules.

Legacy import paths still work via re-export shims at the old locations.
"""
from __future__ import annotations

from . import biology  # noqa: F401
from . import chemistry  # noqa: F401
from . import computing_science  # noqa: F401
from . import language  # noqa: F401
from . import mathematics  # noqa: F401
from . import physics  # noqa: F401

__all__ = ['biology', 'chemistry', 'computing_science', 'language', 'mathematics', 'physics']
