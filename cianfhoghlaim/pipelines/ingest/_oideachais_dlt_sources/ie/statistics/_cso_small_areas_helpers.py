"""
Shared helpers split from geospatial/cso_small_areas.py

Phase 3D of openspec change.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

try:
    from shared.http import cso_pxstat_client, data_gov_ie_client
except ImportError:
    pass  # shared.http is unavailable; functions must lazy-import at call-time


CENSUS_TABLES = {
    "population": "FY001B",  # Population by Small Area
    "age_groups": "FY002B",  # Age groups
    "education": "FY008B",   # Educational attainment
    "housing": "FY011B",     # Housing
    "employment": "FY013B",  # Employment status
    "language": "FY016B",    # Irish language speakers
}

def _fetch_data_gov_resource(resource_id: str) -> Iterator[dict[str, Any]]:
    """Fetch data from data.gov.ie CKAN API."""
    factory = _get_data_gov_factory()
    with factory.create_client() as client:
        offset = 0
        limit = 1000

        while True:
            response = client.get(
                "/datastore_search",
                params={
                    "resource_id": resource_id,
                    "limit": limit,
                    "offset": offset,
                },
            )

            if response.status_code != 200:
                break

            data = response.json()
            records = data.get("result", {}).get("records", [])

            if not records:
                break

            for record in records:
                # Remove internal fields
                yield {k: v for k, v in record.items() if not k.startswith("_")}

            offset += limit

def _fetch_pxstat_table(table_code: str) -> Iterator[dict[str, Any]]:
    """Fetch data from CSO PxStat API."""
    factory = _get_pxstat_factory()
    with factory.create_client() as client:
        # First get table metadata
        response = client.post(
            "",  # base_url already has the endpoint
            json={
                "jsonrpc": "2.0",
                "method": "PxStat.Data.Cube_API.ReadMetadata",
                "params": {
                    "matrix": table_code,
                    "language": "en",
                },
            },
        )

        if response.status_code != 200:
            return

        response.json().get("result", {})

        # Then get data
        response = client.post(
            "",
            json={
                "jsonrpc": "2.0",
                "method": "PxStat.Data.Cube_API.ReadDataset",
                "params": {
                    "matrix": table_code,
                    "language": "en",
                    "format": {"type": "JSON-stat2"},
                },
            },
        )

        if response.status_code != 200:
            return

        data = response.json().get("result", {})

        # Parse JSON-stat format
        dimensions = data.get("dimension", {})
        values = data.get("value", [])

        # Get dimension categories
        dim_categories = {}
        dim_sizes = []
        dim_names = []

        for dim_id in data.get("id", []):
            dim = dimensions.get(dim_id, {})
            dim_names.append(dim_id)
            categories = dim.get("category", {}).get("label", {})
            dim_categories[dim_id] = list(categories.values())
            dim_sizes.append(len(categories))

        # Flatten multi-dimensional data
        if values and dim_names:
            from itertools import product

            # Generate all combinations of dimension indices
            ranges = [range(size) for size in dim_sizes]

            for i, indices in enumerate(product(*ranges)):
                if i >= len(values):
                    break

                value = values[i]
                if value is None:
                    continue

                record = {"value": value, "table_code": table_code}

                for j, dim_name in enumerate(dim_names):
                    idx = indices[j]
                    if idx < len(dim_categories.get(dim_name, [])):
                        record[dim_name.lower()] = dim_categories[dim_name][idx]

                yield record

def _get_data_gov_factory():
    """Get HTTP client factory for data.gov.ie API."""
    return data_gov_ie_client()

def _get_pxstat_factory():
    """Get HTTP client factory for CSO PxStat API."""
    return cso_pxstat_client()
