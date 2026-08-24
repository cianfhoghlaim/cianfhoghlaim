"""dlt_sources/education/northern_ireland/british_isles — DLT sources.

Per the **2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec
change, this package was migrated from its legacy jurisdiction-first
location. The `__init__.py` re-exports the local source modules.

Legacy import paths still work via re-export shims at the old locations.
"""
from __future__ import annotations

from . import _ccea_curriculum_helpers  # noqa: F401
from . import ccea_qualifications  # noqa: F401
from . import education_ni  # noqa: F401
from . import etini  # noqa: F401
from . import irish_medium_ni  # noqa: F401
from . import ni_curriculum  # noqa: F401
from . import northern_ireland_jurisdiction_pipeline  # noqa: F401

__all__ = ['_ccea_curriculum_helpers', 'ccea_qualifications', 'education_ni', 'etini', 'irish_medium_ni', 'ni_curriculum', 'northern_ireland_jurisdiction_pipeline']
