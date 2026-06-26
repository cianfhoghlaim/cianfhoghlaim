"""oideachais.dlt_sources.ie.statistics — Ireland statistics sub-package.

Per Phase 3D, each DLT source lives in its own file. Per-source functions
are re-exported at this package level for backward compatibility.
"""
from __future__ import annotations

# Phase 3D per-source re-exports.
from dlt_sources.ie.statistics.met_office import met_office_source  # noqa: F401
from dlt_sources.ie.statistics.met_office_forecast import (  # noqa: F401
    met_office_forecast_source,
)
from dlt_sources.ie.statistics.cso_small_areas import cso_small_areas_source  # noqa: F401
from dlt_sources.ie.statistics.cso_education import cso_education_source  # noqa: F401
from dlt_sources.ie.statistics.cso_deprivation import cso_deprivation_source  # noqa: F401
from dlt_sources.ie.statistics.geohive import geohive_source  # noqa: F401
from dlt_sources.ie.statistics.geohive_deprivation import (  # noqa: F401
    geohive_deprivation_source,
)


__all__ = [
    "met_office_source",
    "met_office_forecast_source",
    "cso_small_areas_source",
    "cso_education_source",
    "cso_deprivation_source",
    "geohive_source",
    "geohive_deprivation_source",
]