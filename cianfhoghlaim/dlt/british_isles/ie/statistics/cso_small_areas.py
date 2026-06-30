"""
Statistics IE source: cso_small_areas_source

Split from geospatial/cso_small_areas.py in Phase 3D.
"""

from __future__ import annotations

from collections.abc import Iterator

import dlt
from dlt.sources import TDataItem

try:
    from shared.http import cso_pxstat_client, data_gov_ie_client  # noqa: F401
except ImportError:
    pass  # shared.http is unavailable; functions must lazy-import at call-time


from ._cso_small_areas_helpers import (
    CENSUS_TABLES,
    _fetch_pxstat_table,
)


def cso_small_areas_source(
    include_all_tables: bool = False,
) -> list:
    """
    Irish Small Area statistics from CSO.

    Args:
        include_all_tables: Whether to fetch all census tables or just population

    Returns:
        List of DLT resources
    """

    @dlt.resource(
        name="population",
        primary_key="id",
        write_disposition="replace",
    )
    def population() -> Iterator[TDataItem]:
        """Population by Small Area from Census 2022."""
        for i, record in enumerate(_fetch_pxstat_table(CENSUS_TABLES["population"])):
            yield {
                "id": f"pop_{i}",
                **record,
            }

    @dlt.resource(
        name="education_attainment",
        primary_key="id",
        write_disposition="replace",
    )
    def education_attainment() -> Iterator[TDataItem]:
        """Educational attainment by Small Area."""
        if not include_all_tables:
            return

        for i, record in enumerate(_fetch_pxstat_table(CENSUS_TABLES["education"])):
            yield {
                "id": f"edu_{i}",
                **record,
            }

    @dlt.resource(
        name="irish_language",
        primary_key="id",
        write_disposition="replace",
    )
    def irish_language() -> Iterator[TDataItem]:
        """Irish language speakers by Small Area."""
        for i, record in enumerate(_fetch_pxstat_table(CENSUS_TABLES["language"])):
            yield {
                "id": f"lang_{i}",
                **record,
            }

    @dlt.resource(
        name="employment",
        primary_key="id",
        write_disposition="replace",
    )
    def employment() -> Iterator[TDataItem]:
        """Employment status by Small Area."""
        if not include_all_tables:
            return

        for i, record in enumerate(_fetch_pxstat_table(CENSUS_TABLES["employment"])):
            yield {
                "id": f"emp_{i}",
                **record,
            }

    resources = [population, irish_language]
    if include_all_tables:
        resources.extend([education_attainment, employment])

    return resources
