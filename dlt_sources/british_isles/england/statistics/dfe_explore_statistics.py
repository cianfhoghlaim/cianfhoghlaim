import dlt

"""
DLT source for England DfE Explore Education Statistics API.

API Reference: https://explore-education-statistics.service.gov.uk/data-api

Provides access to:
- Key Stage attainment data
- School absence statistics
- Exclusions data
- Teacher workforce census
- School capacity and projections

Uses HttpClientFactory for resilient HTTP client with:
- Circuit breaker pattern
- Rate limiting
- Automatic retries
"""

from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any

import dlt_sources
import structlog
from dlt_sources.common.http_client import dfe_explore_client

logger = structlog.get_logger(__name__)


def _get_dfe_factory():
    """Get HTTP client factory for DfE Explore Statistics API."""
    return dfe_explore_client()

# Key datasets to fetch
DFE_DATASETS = {
    "key-stage-4-attainment": {
        "description": "Key Stage 4 attainment (GCSEs)",
        "partitions": ["year", "local_authority"],
    },
    "key-stage-2-attainment": {
        "description": "Key Stage 2 attainment (primary)",
        "partitions": ["year", "local_authority"],
    },
    "pupil-absence": {
        "description": "Pupil absence in schools",
        "partitions": ["year", "school_type"],
    },
    "permanent-exclusions": {
        "description": "Permanent and fixed-period exclusions",
        "partitions": ["year", "local_authority"],
    },
    "school-workforce": {
        "description": "School workforce census",
        "partitions": ["year"],
    },
    "school-capacity": {
        "description": "School capacity and pupil forecasts",
        "partitions": ["year", "region"],
    },
}


def _list_publications() -> Iterator[dict[str, Any]]:
    """List all available publications."""
    factory = _get_dfe_factory()
    with factory.create_client() as client:
        try:
            response = client.get("/publications")
            response.raise_for_status()
            data = response.json()
            yield from data.get("results", [])
        except (httpx.HTTPError, httpx.TimeoutException, ValueError) as e:
            logger.error("dfe_publications_fetch_failed", error=str(e))
            yield {
                "error": str(e),
                "status": "error",
                "fetched_at": datetime.now(UTC).isoformat(),
            }


def _list_data_sets(publication_id: str | None = None) -> Iterator[dict[str, Any]]:
    """List available data sets, optionally filtered by publication."""
    factory = _get_dfe_factory()
    with factory.create_client() as client:
        try:
            params = {}
            if publication_id:
                params["publicationId"] = publication_id

            response = client.get("/data-sets", params=params)
            response.raise_for_status()
            data = response.json()

            for dataset in data.get("results", []):
                yield {
                    "id": dataset.get("id"),
                    "title": dataset.get("title"),
                    "summary": dataset.get("summary"),
                    "publication_id": dataset.get("publication", {}).get("id"),
                    "publication_title": dataset.get("publication", {}).get("title"),
                    "geographic_levels": dataset.get("geographicLevels", []),
                    "time_periods": dataset.get("timePeriods", []),
                    "latest_version": dataset.get("latestVersion"),
                    "status": "success",
                    "fetched_at": datetime.now(UTC).isoformat(),
                }
        except (httpx.HTTPError, httpx.TimeoutException, ValueError) as e:
            logger.error("dfe_datasets_fetch_failed", error=str(e))
            yield {
                "error": str(e),
                "status": "error",
                "fetched_at": datetime.now(UTC).isoformat(),
            }


def _query_data_set(
    data_set_id: str,
    indicators: list[str] | None = None,
    filters: dict[str, list[str]] | None = None,
    geographic_level: str = "localAuthority",
    time_period: str | None = None,
    page_size: int = 1000,
) -> Iterator[dict[str, Any]]:
    """
    Query a data set using the DfE API.

    Args:
        data_set_id: ID of the data set
        indicators: List of indicator IDs to include
        filters: Filter criteria
        geographic_level: Geographic level (national, region, localAuthority, school)
        time_period: Academic year (e.g., "2022/23")
        page_size: Results per page
    """
    factory = _get_dfe_factory()
    with factory.create_client() as client:
        try:
            # Build query payload
            query = {
                "criteria": {
                    "geographicLevel": {"in": [geographic_level]},
                },
                "page": 1,
                "pageSize": page_size,
            }

            if indicators:
                query["indicators"] = indicators
            if filters:
                query["criteria"]["filters"] = filters
            if time_period:
                query["criteria"]["timePeriod"] = {"eq": time_period}

            # Paginate through results
            while True:
                response = client.post(
                    f"/data-sets/{data_set_id}/query",
                    json=query,
                )
                response.raise_for_status()
                data = response.json()

                results = data.get("results", [])
                if not results:
                    break

                for row in results:
                    yield {
                        "data_set_id": data_set_id,
                        "time_period": row.get("timePeriod"),
                        "geographic_level": row.get("geographicLevel"),
                        "location_id": row.get("locationId"),
                        "location_name": row.get("locationName"),
                        "values": row.get("values", {}),
                        "filters": row.get("filters", {}),
                        "nation": "england",
                        "status": "success",
                        "fetched_at": datetime.now(UTC).isoformat(),
                    }

                # Check for more pages
                paging = data.get("paging", {})
                if query["page"] >= paging.get("totalPages", 1):
                    break
                query["page"] += 1

        except (httpx.HTTPError, httpx.TimeoutException, ValueError) as e:
            logger.error("dfe_query_failed", data_set_id=data_set_id, error=str(e))
            yield {
                "data_set_id": data_set_id,
                "error": str(e),
                "status": "error",
                "fetched_at": datetime.now(UTC).isoformat(),
            }


@dlt.source(name="dfe_statistics")
def dfe_statistics_source(
    datasets: list[str] | None = None,
    time_periods: list[str] | None = None,
    geographic_level: str = "localAuthority",
):
    """
    DLT source for DfE Explore Education Statistics.

    Args:
        datasets: List of dataset slugs to fetch (default: all key datasets)
        time_periods: Academic years to fetch (e.g., ["2022/23", "2023/24"])
        geographic_level: Geographic level for data

    Returns:
        DLT source with publications, data_sets, and statistics resources
    """
    datasets = datasets or list(DFE_DATASETS.keys())
    time_periods = time_periods or ["2022/23", "2023/24"]

    @dlt.resource(
        name="publications",
        write_disposition="replace",
        primary_key=["id"],
    )
    def publications():
        """Available DfE publications."""
        yield from _list_publications()

    @dlt.resource(
        name="data_sets",
        write_disposition="merge",
        primary_key=["id"],
    )
    def data_sets():
        """Available data sets metadata."""
        yield from _list_data_sets()

    @dlt.resource(
        name="statistics",
        write_disposition="merge",
        primary_key=["data_set_id", "time_period", "location_id"],
    )
    def statistics():
        """Education statistics data."""
        # First get available datasets
        available = list(_list_data_sets())
        dataset_ids = {ds.get("title", "").lower(): ds.get("id") for ds in available if "id" in ds}

        for dataset_slug in datasets:
            # Try to find matching dataset ID
            dataset_id = None
            for title, ds_id in dataset_ids.items():
                if dataset_slug.replace("-", " ") in title.lower():
                    dataset_id = ds_id
                    break

            if not dataset_id:
                continue

            for time_period in time_periods:
                yield from _query_data_set(
                    data_set_id=dataset_id,
                    geographic_level=geographic_level,
                    time_period=time_period,
                )

    return publications, data_sets, statistics
