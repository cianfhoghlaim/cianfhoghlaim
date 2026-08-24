"""dlt_sources/european_union/education — DLT sources.

Per the **2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec
change, this package was migrated from its legacy jurisdiction-first
location. The `__init__.py` re-exports the local source modules.

Legacy import paths still work via re-export shims at the old locations.
"""
from __future__ import annotations

from . import cedefop  # noqa: F401
from . import eurydice  # noqa: F401
from . import school_education_gateway  # noqa: F401

__all__ = ['cedefop', 'eurydice', 'school_education_gateway']
