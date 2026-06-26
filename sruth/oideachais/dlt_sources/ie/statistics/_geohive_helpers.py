"""
Shared helpers split from geospatial/geohive.py

Phase 3D of openspec change.
"""

from __future__ import annotations
import json
from collections.abc import Iterator
from typing import Any
import dlt
from dlt.sources import TDataItem
try:
    from shared.http import arcgis_geohive_client, cso_pxstat_client, data_gov_ie_client  # noqa: F401
except ImportError:
    pass  # shared.http is unavailable; functions must lazy-import at call-time


ENDPOINTS = {
    "small_areas": "/Small_Areas_Ungeneralised_-_OSi_National_Statistical_Boundaries_-_2015/FeatureServer/0",
    "counties": "/Admin_Counties_-_OSi_National_Statutory_Boundaries_-_Generalised_20m/FeatureServer/0",
    "electoral_divisions": "/Electoral_Divisions_-_OSi_National_Electoral_Boundaries_-_2015/FeatureServer/0",
}

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

def _get_cso_factory():
    """Get HTTP client factory for CSO PxStat API."""
    return cso_pxstat_client()

def _get_data_gov_factory():
    """Get HTTP client factory for data.gov.ie."""
    return data_gov_ie_client()

def _get_geohive_factory():
    """Get HTTP client factory for GeoHive ArcGIS FeatureServer."""
    return arcgis_geohive_client()
