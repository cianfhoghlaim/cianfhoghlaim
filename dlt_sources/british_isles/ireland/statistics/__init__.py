"""dlt_sources/british_isles/ireland/statistics — DLT sources.

Per the **2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec
change, this package was migrated from its legacy jurisdiction-first
location. The `__init__.py` re-exports the local source modules.

Legacy import paths still work via re-export shims at the old locations.
"""
from __future__ import annotations

from . import _cso_small_areas_helpers  # noqa: F401
from . import _geohive_helpers  # noqa: F401
from . import _met_office_helpers  # noqa: F401
from . import cso_deprivation  # noqa: F401
from . import cso_education  # noqa: F401
from . import cso_small_areas  # noqa: F401
from . import geohive  # noqa: F401
from . import geohive_deprivation  # noqa: F401
from . import met_office  # noqa: F401
from . import met_office_forecast  # noqa: F401

__all__ = ['_cso_small_areas_helpers', '_geohive_helpers', '_met_office_helpers', 'cso_deprivation', 'cso_education', 'cso_small_areas', 'geohive', 'geohive_deprivation', 'met_office', 'met_office_forecast']
