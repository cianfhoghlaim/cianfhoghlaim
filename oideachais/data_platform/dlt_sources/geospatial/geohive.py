"""
GeoHive.ie DLT Source - Irish Geospatial Data.

Fetches boundaries and census data from GeoHive.ie APIs:
- Small Area boundaries (18,641 areas)
- County boundaries
- Electoral Divisions
- Census SAPS (Small Area Population Statistics)

API Documentation: https://data.gov.ie/dataset/geohive

Uses HttpClientFactory for resilient HTTP client with:
- Circuit breaker pattern
- Rate limiting
- Automatic retries

Usage:
    import dlt
    from oideachais.data_platform.dlt_sources.geospatial.geohive import geohive_source

    pipeline = dlt.pipeline(
        pipeline_name="geohive",
        destination="duckdb",
        dataset_name="geospatial",
    )
    pipeline.run(geohive_source())
"""
from __future__ import annotations

import json
from collections.abc import Iterator
from typing import Any

import dlt
from dlt.sources import TDataItem
from sruth.shared.http import arcgis_geohive_client, cso_pxstat_client, data_gov_ie_client


def _get_geohive_factory():
    """Get HTTP client factory for GeoHive ArcGIS FeatureServer."""
    return arcgis_geohive_client()


def _get_cso_factory():
    """Get HTTP client factory for CSO PxStat API."""
    return cso_pxstat_client()


def _get_data_gov_factory():
    """Get HTTP client factory for data.gov.ie."""
    return data_gov_ie_client()


# Feature service endpoints (relative to ArcGIS base URL)
ENDPOINTS = {
    "small_areas": "/Small_Areas_Ungeneralised_-_OSi_National_Statistical_Boundaries_-_2015/FeatureServer/0",
    "counties": "/Admin_Counties_-_OSi_National_Statutory_Boundaries_-_Generalised_20m/FeatureServer/0",
    "electoral_divisions": "/Electoral_Divisions_-_OSi_National_Electoral_Boundaries_-_2015/FeatureServer/0",
}


def _fetch_features(
    endpoint: str,
    where: str = "1=1",
    out_fields: str = "*",
    max_records: int = 2000,
) -> Iterator[dict[str, Any]]:
    """Fetch features from ArcGIS FeatureServer with pagination."""
    factory = _get_geohive_factory()
    with factory.create_client() as client:
        offset = 0

        while True:
            params = {
                "where": where,
                "outFields": out_fields,
                "returnGeometry": "true",
                "f": "geojson",
                "resultOffset": offset,
                "resultRecordCount": max_records,
            }

            response = client.get(f"{endpoint}/query", params=params)
            response.raise_for_status()
            data = response.json()

            features = data.get("features", [])
            if not features:
                break

            for feature in features:
                props = feature.get("properties", {})
                geometry = feature.get("geometry")

                yield {
                    **props,
                    "geometry": json.dumps(geometry) if geometry else None,
                }

            if len(features) < max_records:
                break

            offset += max_records


def _fetch_census_table(table_id: str, year: int = 2022) -> Iterator[dict[str, Any]]:
    """Fetch census data from CSO API."""
    factory = _get_cso_factory()
    with factory.create_client() as client:
        # Get table dimensions first
        response = client.post(
            "",  # base_url already has the endpoint
            json={
                "jsonrpc": "2.0",
                "method": "PxStat.Data.Cube_API.ReadDataset",
                "params": {
                    "matrix": table_id,
                    "language": "en",
                },
            },
        )
        response.raise_for_status()
        data = response.json()

        if "result" in data:
            # Extract data points
            result = data["result"]
            dimensions = result.get("dimension", {})
            values = result.get("value", [])

            # Yield flattened records
            for i, value in enumerate(values):
                yield {
                    "table_id": table_id,
                    "year": year,
                    "value": value,
                    "index": i,
                }


@dlt.source(name="geohive")
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


@dlt.source(name="geohive_deprivation")
def geohive_deprivation_source() -> list:
    """
    Pobal HP Deprivation Index data for Small Areas.

    The HP Deprivation Index provides a relative measure of
    deprivation for each Small Area based on Census 2016 data.
    """

    @dlt.resource(
        name="hp_deprivation",
        primary_key="sa_2016",
        write_disposition="replace",
    )
    def hp_deprivation() -> Iterator[TDataItem]:
        """HP Deprivation Index scores by Small Area."""
        # Pobal HP Index endpoint (from data.gov.ie)
        factory = _get_data_gov_factory()
        with factory.create_client() as client:
            response = client.get(
                "/datastore_search",
                params={
                    "resource_id": "hp-deprivation-index-2016",
                    "limit": 32000,  # All Small Areas
                },
            )

            if response.status_code == 200:
                data = response.json()
                for record in data.get("result", {}).get("records", []):
                    yield {
                        "sa_2016": record.get("SA_GUID_2016"),
                        "hp_score": record.get("HP_Score"),
                        "hp_decile": record.get("HP_Decile"),
                        "affluence_deprivation": record.get("Afflu_Depv"),
                        "demographic_growth_decline": record.get("Demo_Grwth_Dec"),
                        "age_dependency": record.get("Age_Dep"),
                        "lone_parent": record.get("Lone_Parent"),
                        "primary_education_only": record.get("Prim_Ed_Only"),
                        "third_level_education": record.get("Third_Level"),
                        "unemployment_rate": record.get("Unemp_Rate"),
                    }

    return [hp_deprivation]


if __name__ == "__main__":
    # Test the source
    import dlt

    pipeline = dlt.pipeline(
        pipeline_name="geohive_test",
        destination="duckdb",
        dataset_name="geospatial",
    )

    # Run with a county filter for testing
    info = pipeline.run(
        geohive_source(
            include_geometry=True,
            small_area_county_filter="Dublin City",
        )
    )
    print(info)
