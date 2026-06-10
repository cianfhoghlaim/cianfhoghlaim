"""
DLT source for StatsWales OData API.

StatsWales provides education statistics via an OData API:
https://statswales.gov.wales/Catalogue/Education-and-Skills

Includes:
- School statistics
- Pupil attainment
- Welsh medium education
- Post-16 learning

Uses HttpClientFactory for resilient HTTP client with:
- Circuit breaker pattern
- Rate limiting
- Automatic retries
"""

from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any

import dlt
from shared.http import stats_wales_odata_client


def _get_odata_factory():
    """Get HTTP client factory for StatsWales OData API."""
    return stats_wales_odata_client()


# Key education datasets
EDUCATION_DATASETS = {
    # Schools
    "SCHS0100": "Number of schools by sector and type",
    "SCHS0101": "Number of schools by local authority",
    "SCHS0300": "Number of pupils by local authority and school sector",
    "SCHS0400": "Pupil:teacher ratios by local authority",
    # Attainment
    "EXAM0100": "Key Stage 4 capped points score",
    "EXAM0200": "A level results by local authority",
    "EXAM0300": "GCSE results by subject",
    # Welsh medium
    "SCHS0500": "Welsh medium schools",
    "SCHS0501": "Pupils taught through Welsh medium",
    # Workforce
    "SCHS0600": "Teachers by local authority",
    "SCHS0601": "Teacher qualifications",
}


def _list_education_datasets() -> Iterator[dict[str, Any]]:
    """
    List available education datasets from StatsWales.

    Yields:
        Dataset metadata
    """
    factory = _get_odata_factory()
    with factory.create_client() as client:
        try:
            # Query catalogue for education datasets
            response = client.get(
                "/",
                params={"$filter": "startswith(Name, 'SCHS') or startswith(Name, 'EXAM')"},
            )
            response.raise_for_status()
            data = response.json()

            for dataset in data.get("value", []):
                yield {
                    "id": dataset.get("Name"),
                    "title": dataset.get("Title"),
                    "description": dataset.get("Description"),
                    "last_updated": dataset.get("LastUpdated"),
                    "nation": "wales",
                    "source": "statswales",
                    "status": "success",
                    "fetched_at": datetime.now(UTC).isoformat(),
                }

        except Exception as e:
            yield {
                "error": str(e),
                "status": "error",
                "fetched_at": datetime.now(UTC).isoformat(),
            }


def _query_dataset(
    dataset_id: str,
    language: str = "en-GB",
    top: int | None = None,
    skip: int | None = None,
) -> Iterator[dict[str, Any]]:
    """
    Query a StatsWales dataset via OData.

    Args:
        dataset_id: Dataset identifier (e.g., SCHS0100)
        language: Language code (en-GB or cy-GB for Welsh)
        top: Maximum records to return
        skip: Records to skip (for pagination)

    Yields:
        Data records
    """
    factory = _get_odata_factory()
    with factory.create_client() as client:
        try:
            params = {}
            if top:
                params["$top"] = top
            if skip:
                params["$skip"] = skip

            # Add language header for bilingual support
            headers = {"Accept-Language": language}

            response = client.get(f"/{dataset_id}", params=params, headers=headers)
            response.raise_for_status()
            data = response.json()

            for row in data.get("value", []):
                # Standardize field names
                record = {
                    "dataset_id": dataset_id,
                    "language": language,
                    "nation": "wales",
                    "source": "statswales",
                    "status": "success",
                    "fetched_at": datetime.now(UTC).isoformat(),
                }

                # Add all fields from the row
                for key, value in row.items():
                    # Convert OData field names to snake_case
                    snake_key = key.replace("@", "").replace(".", "_").lower()
                    record[snake_key] = value

                yield record

        except Exception as e:
            yield {
                "dataset_id": dataset_id,
                "error": str(e),
                "status": "error",
                "fetched_at": datetime.now(UTC).isoformat(),
            }


def _query_all_datasets(
    datasets: list[str],
    language: str = "en-GB",
    max_records_per_dataset: int = 10000,
) -> Iterator[dict[str, Any]]:
    """
    Query multiple datasets.

    Args:
        datasets: List of dataset IDs
        language: Language code
        max_records_per_dataset: Maximum records per dataset

    Yields:
        Data records from all datasets
    """
    for dataset_id in datasets:
        skip = 0
        batch_size = 1000
        total = 0

        while total < max_records_per_dataset:
            batch = list(
                _query_dataset(
                    dataset_id,
                    language=language,
                    top=batch_size,
                    skip=skip,
                )
            )

            if not batch or (len(batch) == 1 and batch[0].get("status") == "error"):
                break

            yield from batch
            total += len(batch)
            skip += batch_size

            if len(batch) < batch_size:
                break


@dlt.source(name="statswales")
def statswales_source(
    datasets: list[str] | None = None,
    language: str = "en-GB",
    max_records: int = 10000,
):
    """
    DLT source for StatsWales education statistics.

    Args:
        datasets: List of dataset IDs to fetch (default: all education datasets)
        language: Language code (en-GB or cy-GB for Welsh)
        max_records: Maximum records per dataset

    Returns:
        DLT source with catalogue and data resources
    """
    datasets = datasets or list(EDUCATION_DATASETS.keys())

    @dlt.resource(
        name="catalogue",
        write_disposition="replace",
        primary_key=["id"],
    )
    def catalogue():
        """Available education datasets."""
        yield from _list_education_datasets()

    @dlt.resource(
        name="data",
        write_disposition="merge",
        primary_key=["dataset_id", "row_key"],
    )
    def data():
        """Education statistics data."""
        for record in _query_all_datasets(datasets, language, max_records):
            # Create a unique row key from available identifiers
            row_parts = []
            for key in ["year", "local_authority", "school_type", "area_code"]:
                if key in record:
                    row_parts.append(str(record[key]))

            record["row_key"] = "_".join(row_parts) if row_parts else record.get("fetched_at")
            yield record

    return catalogue, data
