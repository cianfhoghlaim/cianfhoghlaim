"""
DLT source for NISRA education statistics.

Northern Ireland Statistics and Research Agency provides
education data through data.nisra.gov.uk.

Uses HttpClientFactory for resilient HTTP client with:
- Circuit breaker pattern
- Rate limiting
- Automatic retries
"""

from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any

import dlt
from sruth.shared.http import nisra_client


def _get_nisra_factory():
    """Get HTTP client factory for NISRA API."""
    return nisra_client()


def _list_education_datasets() -> Iterator[dict[str, Any]]:
    """
    List available education datasets from NISRA.

    Yields:
        Dataset metadata
    """
    factory = _get_nisra_factory()
    with factory.create_client() as client:
        try:
            response = client.get("/datasets", params={"topic": "education"})
            response.raise_for_status()
            data = response.json()

            for dataset in data.get("datasets", []):
                yield {
                    "id": dataset.get("id"),
                    "title": dataset.get("title"),
                    "description": dataset.get("description"),
                    "last_updated": dataset.get("lastUpdated"),
                    "geographic_coverage": dataset.get("geographicCoverage"),
                    "temporal_coverage": dataset.get("temporalCoverage"),
                    "nation": "northern_ireland",
                    "source": "nisra",
                    "status": "success",
                    "fetched_at": datetime.now(UTC).isoformat(),
                }

        except Exception as e:
            yield {
                "error": str(e),
                "status": "error",
                "fetched_at": datetime.now(UTC).isoformat(),
            }


def _query_dataset(dataset_id: str, filters: dict | None = None) -> Iterator[dict[str, Any]]:
    """
    Query a NISRA dataset.

    Args:
        dataset_id: Dataset identifier
        filters: Optional query filters

    Yields:
        Data records
    """
    factory = _get_nisra_factory()
    with factory.create_client() as client:
        try:
            params = filters or {}
            response = client.get(f"/datasets/{dataset_id}/data", params=params)
            response.raise_for_status()
            data = response.json()

            for row in data.get("observations", data.get("data", [])):
                record = {
                    "dataset_id": dataset_id,
                    "nation": "northern_ireland",
                    "source": "nisra",
                    "status": "success",
                    "fetched_at": datetime.now(UTC).isoformat(),
                }
                record.update(row)
                yield record

        except Exception as e:
            yield {
                "dataset_id": dataset_id,
                "error": str(e),
                "status": "error",
                "fetched_at": datetime.now(UTC).isoformat(),
            }


@dlt.source(name="nisra")
def nisra_source(dataset_ids: list[str] | None = None):
    """
    DLT source for NISRA education statistics.

    Args:
        dataset_ids: Specific datasets to fetch (default: discover all)

    Returns:
        DLT source with datasets and data resources
    """

    @dlt.resource(
        name="datasets",
        write_disposition="replace",
        primary_key=["id"],
    )
    def datasets():
        """Available NISRA education datasets."""
        yield from _list_education_datasets()

    @dlt.resource(
        name="data",
        write_disposition="merge",
        primary_key=["dataset_id", "observation_id"],
    )
    def data():
        """Education statistics data."""
        if dataset_ids:
            for ds_id in dataset_ids:
                for record in _query_dataset(ds_id):
                    record["observation_id"] = record.get("id", record.get("fetched_at"))
                    yield record
        else:
            # Fetch all discovered datasets
            for ds in _list_education_datasets():
                if ds.get("id"):
                    for record in _query_dataset(ds["id"]):
                        record["observation_id"] = record.get("id", record.get("fetched_at"))
                        yield record

    return datasets, data
