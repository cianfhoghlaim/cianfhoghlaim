"""
CSO Small Areas DLT Source - Irish Statistical Geography.

Fetches Small Area statistics from CSO (Central Statistics Office) APIs:
- Population by Small Area
- Education statistics
- Economic indicators
- Deprivation measures

Ireland has 18,641 Small Areas - the most granular geographic unit
for which census data is published.

API Documentation: https://data.cso.ie/

Uses HttpClientFactory for resilient HTTP client with:
- Circuit breaker pattern
- Rate limiting
- Automatic retries

Usage:
    import dlt
    from dlt_sources.geospatial.cso_small_areas import cso_small_areas_source

    pipeline = dlt.pipeline(
        pipeline_name="cso_small_areas",
        destination="duckdb",
        dataset_name="statistics",
    )
    pipeline.run(cso_small_areas_source())
"""
from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import dlt
from dlt.sources import TDataItem
from shared.http import cso_pxstat_client, data_gov_ie_client


def _get_pxstat_factory():
    """Get HTTP client factory for CSO PxStat API."""
    return cso_pxstat_client()


def _get_data_gov_factory():
    """Get HTTP client factory for data.gov.ie API."""
    return data_gov_ie_client()


# Census 2022 table codes
CENSUS_TABLES = {
    "population": "FY001B",  # Population by Small Area
    "age_groups": "FY002B",  # Age groups
    "education": "FY008B",   # Educational attainment
    "housing": "FY011B",     # Housing
    "employment": "FY013B",  # Employment status
    "language": "FY016B",    # Irish language speakers
}


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

        metadata = response.json().get("result", {})

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


@dlt.source(name="cso_small_areas")
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


@dlt.source(name="cso_education")
def cso_education_source() -> list:
    """
    Education-specific statistics from CSO.

    Includes school enrollment, DEIS designation, and
    educational outcomes data.
    """

    @dlt.resource(
        name="primary_schools",
        primary_key="roll_number",
        write_disposition="replace",
    )
    def primary_schools() -> Iterator[TDataItem]:
        """Primary school statistics."""
        # Department of Education school list
        factory = _get_data_gov_factory()
        with factory.create_client() as client:
            # This would need the actual resource ID from data.gov.ie
            # For now, yield placeholder structure
            response = client.get(
                "/package_show",
                params={"id": "primary-schools-list"},
            )

            if response.status_code == 200:
                data = response.json()
                resources = data.get("result", {}).get("resources", [])

                for resource in resources:
                    if resource.get("format", "").upper() == "JSON":
                        for record in _fetch_data_gov_resource(resource["id"]):
                            yield record

    @dlt.resource(
        name="secondary_schools",
        primary_key="roll_number",
        write_disposition="replace",
    )
    def secondary_schools() -> Iterator[TDataItem]:
        """Post-primary school statistics."""
        factory = _get_data_gov_factory()
        with factory.create_client() as client:
            response = client.get(
                "/package_show",
                params={"id": "post-primary-schools-list"},
            )

            if response.status_code == 200:
                data = response.json()
                resources = data.get("result", {}).get("resources", [])

                for resource in resources:
                    if resource.get("format", "").upper() == "JSON":
                        for record in _fetch_data_gov_resource(resource["id"]):
                            yield record

    @dlt.resource(
        name="gaeltacht_schools",
        primary_key="roll_number",
        write_disposition="replace",
    )
    def gaeltacht_schools() -> Iterator[TDataItem]:
        """Schools in Gaeltacht areas and Irish-medium schools."""
        # Filter for Irish-medium education
        factory = _get_data_gov_factory()
        with factory.create_client() as client:
            # Gaeltacht areas list
            response = client.get(
                "/package_show",
                params={"id": "gaeltacht-areas"},
            )

            if response.status_code == 200:
                data = response.json()
                resources = data.get("result", {}).get("resources", [])

                for resource in resources:
                    if resource.get("format", "").upper() in ("JSON", "GEOJSON"):
                        for record in _fetch_data_gov_resource(resource["id"]):
                            yield record

    return [primary_schools, secondary_schools, gaeltacht_schools]


@dlt.source(name="cso_deprivation")
def cso_deprivation_source() -> list:
    """
    Deprivation indices for Irish Small Areas.

    Includes Pobal HP Deprivation Index and related measures.
    """

    @dlt.resource(
        name="hp_deprivation_2022",
        primary_key="sa_2022",
        write_disposition="replace",
    )
    def hp_deprivation() -> Iterator[TDataItem]:
        """
        Pobal HP Deprivation Index 2022.

        The HP Index measures relative affluence and deprivation
        based on demographic, social, and economic indicators.
        """
        # Pobal HP Index data from data.gov.ie
        # Resource ID needs to be updated when 2022 data is published
        for record in _fetch_data_gov_resource("hp-deprivation-index-2022"):
            yield record

    @dlt.resource(
        name="deis_schools",
        primary_key="roll_number",
        write_disposition="replace",
    )
    def deis_schools() -> Iterator[TDataItem]:
        """
        DEIS (Delivering Equality of Opportunity in Schools) designated schools.

        DEIS provides additional resources to schools serving
        disadvantaged communities.
        """
        factory = _get_data_gov_factory()
        with factory.create_client() as client:
            response = client.get(
                "/package_show",
                params={"id": "deis-schools"},
            )

            if response.status_code == 200:
                data = response.json()
                resources = data.get("result", {}).get("resources", [])

                for resource in resources:
                    if resource.get("format", "").upper() == "JSON":
                        for record in _fetch_data_gov_resource(resource["id"]):
                            yield {
                                "roll_number": record.get("Roll_Number", record.get("roll_number")),
                                "school_name": record.get("School_Name", record.get("school_name")),
                                "deis_band": record.get("DEIS_Band", record.get("deis_band")),
                                "county": record.get("County", record.get("county")),
                                "school_type": record.get("School_Type", record.get("school_type")),
                            }

    return [hp_deprivation, deis_schools]


if __name__ == "__main__":
    # Test the source
    import dlt

    pipeline = dlt.pipeline(
        pipeline_name="cso_small_areas_test",
        destination="duckdb",
        dataset_name="statistics",
    )

    info = pipeline.run(cso_small_areas_source(include_all_tables=False))
    print(info)
