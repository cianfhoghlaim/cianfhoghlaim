"""
Statistics IE source: geohive_source

Split from geospatial/geohive.py in Phase 3D.
"""

from __future__ import annotations

from collections.abc import Iterator

import dlt
from dlt.sources import TDataItem

try:
    from shared.http import (  # noqa: F401
        arcgis_geohive_client,
        cso_pxstat_client,
        data_gov_ie_client,
    )
except ImportError:
    pass  # shared.http is unavailable; functions must lazy-import at call-time


from ._geohive_helpers import (
    ENDPOINTS,
    _fetch_census_table,
    _fetch_features,
)


def geohive_source(
    include_geometry: bool = True,
    small_area_county_filter: str | None = None,
) -> list:
    """
    Irish geospatial data from GeoHive.ie.

    Args:
        include_geometry: Whether to include GeoJSON geometry
        small_area_county_filter: Optional county name to filter small areas

    Returns:
        List of DLT resources
    """

    @dlt.resource(
        name="small_areas",
        primary_key="sa_2016",
        write_disposition="replace",
    )
    def small_areas() -> Iterator[TDataItem]:
        """
        CSO Small Areas (18,641 areas) with boundaries.

        Small Areas are the lowest level of geography for which
        Census data is available in Ireland.
        """
        where = "1=1"
        if small_area_county_filter:
            where = f"COUNTYNAME = '{small_area_county_filter}'"

        for feature in _fetch_features(
            ENDPOINTS["small_areas"],
            where=where,
            out_fields="SA_2016,COUNTYNAME,EDNAME,NUTS3NAME",
        ):
            yield {
                "sa_2016": feature.get("SA_2016"),
                "county": feature.get("COUNTYNAME"),
                "electoral_division": feature.get("EDNAME"),
                "nuts3_region": feature.get("NUTS3NAME"),
                "geometry": feature.get("geometry") if include_geometry else None,
            }

    @dlt.resource(
        name="counties",
        primary_key="county_id",
        write_disposition="replace",
    )
    def counties() -> Iterator[TDataItem]:
        """County boundaries (26 counties + 5 county boroughs)."""
        for feature in _fetch_features(
            ENDPOINTS["counties"],
            out_fields="COUNTYNAME,COUNTY,PROVINCE,AREA_GEO",
        ):
            yield {
                "county_id": feature.get("COUNTY"),
                "county_name": feature.get("COUNTYNAME"),
                "province": feature.get("PROVINCE"),
                "area_km2": feature.get("AREA_GEO"),
                "geometry": feature.get("geometry") if include_geometry else None,
            }

    @dlt.resource(
        name="electoral_divisions",
        primary_key="ed_id",
        write_disposition="replace",
    )
    def electoral_divisions() -> Iterator[TDataItem]:
        """Electoral Divisions (3,440 areas)."""
        for feature in _fetch_features(
            ENDPOINTS["electoral_divisions"],
            out_fields="EDNAME,ED_ID,COUNTYNAME,CSOED_ID",
        ):
            yield {
                "ed_id": feature.get("ED_ID"),
                "ed_name": feature.get("EDNAME"),
                "county": feature.get("COUNTYNAME"),
                "csoed_id": feature.get("CSOED_ID"),
                "geometry": feature.get("geometry") if include_geometry else None,
            }

    @dlt.resource(
        name="census_population",
        primary_key="id",
        write_disposition="replace",
    )
    def census_population() -> Iterator[TDataItem]:
        """
        Population by Small Area from Census 2022.

        Table: SAPS 2022 - Population
        """
        # CSO table for Small Area Population Statistics
        table_id = "SAPS2022"

        for record in _fetch_census_table(table_id, year=2022):
            yield {
                "id": f"{table_id}_{record['index']}",
                **record,
            }

    return [small_areas, counties, electoral_divisions, census_population]
