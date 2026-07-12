"""oideachais.cianfhoghlaim.dlt.british_isles.ireland.statistics — Ireland statistics sub-package.

Per Phase 3D, each DLT source lives in its own file. Per-source functions
are re-exported at this package level for backward compatibility.
"""
from __future__ import annotations

from cianfhoghlaim.dlt.british_isles.ireland.statistics.cso_deprivation import cso_deprivation_source
from cianfhoghlaim.dlt.british_isles.ireland.statistics.cso_education import cso_education_source
from cianfhoghlaim.dlt.british_isles.ireland.statistics.cso_small_areas import cso_small_areas_source
from cianfhoghlaim.dlt.british_isles.ireland.statistics.geohive import geohive_source
from cianfhoghlaim.dlt.british_isles.ireland.statistics.geohive_deprivation import (
    geohive_deprivation_source,
)

# Phase 3D per-source re-exports.
from cianfhoghlaim.dlt.british_isles.ireland.statistics.met_office import met_office_source
from cianfhoghlaim.dlt.british_isles.ireland.statistics.met_office_forecast import (
    met_office_forecast_source,
)

__all__ = [
    "cso_deprivation_source",
    "cso_education_source",
    "cso_small_areas_source",
    "geohive_deprivation_source",
    "geohive_source",
    "met_office_forecast_source",
    "met_office_source",
]
