"""
DLT source for GIAS (Get Information About Schools).

Provides school metadata including:
- Establishment details
- Location and contact information
- Phase, type, and governance
- Ofsted ratings
- Capacity and pupil numbers

Uses HttpClientFactory for resilient HTTP client with:
- Circuit breaker pattern
- Rate limiting
- Automatic retries
"""

from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any

import dlt
from cianfhoghlaim.dlt.common.http_client import get_info_schools_client


def _get_gias_factory():
    """Get HTTP client factory for GIAS."""
    return get_info_schools_client()


def _download_establishments(
    region: str | None = None,
    local_authority: str | None = None,
    establishment_type: str | None = None,
) -> Iterator[dict[str, Any]]:
    """
    Download establishment data from GIAS.

    The GIAS service provides CSV downloads that can be parsed.
    This implementation uses the search API where available.
    """
    factory = _get_gias_factory()
    with factory.create_client():
        try:
            # GIAS uses a search endpoint that returns paginated results
            params = {
                "SelectedTab": "Establishments",
                "PageSize": 500,
                "PageNumber": 1,
            }

            if region:
                params["Searchtype"] = "ByLocalAuthority"
                params["Region"] = region

            if local_authority:
                params["LocalAuthorityId"] = local_authority

            if establishment_type:
                params["EstablishmentTypeId"] = establishment_type

            # Note: GIAS doesn't have a public REST API
            # This is a placeholder for the actual implementation
            # Real implementation would use CSV downloads or scraping

            # For now, yield a status indicator
            yield {
                "status": "api_not_available",
                "message": "GIAS requires CSV download or web scraping",
                "params": params,
                "fetched_at": datetime.now(UTC).isoformat(),
            }

        except Exception as e:
            yield {
                "error": str(e),
                "status": "error",
                "fetched_at": datetime.now(UTC).isoformat(),
            }


def _parse_gias_csv(csv_path: str) -> Iterator[dict[str, Any]]:
    """
    Parse GIAS establishment data from CSV.

    The GIAS extract can be downloaded from:
    https://get-information-schools.service.gov.uk/Downloads

    Args:
        csv_path: Path to downloaded GIAS CSV file

    Yields:
        Parsed establishment records
    """
    import csv
    from pathlib import Path

    path = Path(csv_path)
    if not path.exists():
        yield {
            "status": "file_not_found",
            "path": csv_path,
            "fetched_at": datetime.now(UTC).isoformat(),
        }
        return

    try:
        with open(path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)

            for row in reader:
                # Map GIAS columns to standardized schema
                yield {
                    "urn": row.get("URN"),
                    "establishment_name": row.get("EstablishmentName"),
                    "establishment_type": row.get("EstablishmentType (name)"),
                    "phase": row.get("PhaseOfEducation (name)"),
                    "status": row.get("EstablishmentStatus (name)"),
                    "local_authority": row.get("LA (name)"),
                    "local_authority_code": row.get("LA (code)"),
                    "region": row.get("GOR (name)"),
                    "address_line1": row.get("Street"),
                    "address_line2": row.get("Locality"),
                    "town": row.get("Town"),
                    "postcode": row.get("Postcode"),
                    "latitude": row.get("Latitude"),
                    "longitude": row.get("Longitude"),
                    "easting": row.get("Easting"),
                    "northing": row.get("Northing"),
                    "telephone": row.get("TelephoneNum"),
                    "website": row.get("SchoolWebsite"),
                    "ofsted_rating": row.get("OfstedRating (name)"),
                    "last_inspection_date": row.get("OfstedLastInsp"),
                    "number_of_pupils": row.get("NumberOfPupils"),
                    "school_capacity": row.get("SchoolCapacity"),
                    "gender": row.get("Gender (name)"),
                    "religious_character": row.get("ReligiousCharacter (name)"),
                    "admissions_policy": row.get("AdmissionsPolicy (name)"),
                    "sixth_form": row.get("OfficialSixthForm (name)"),
                    "nursery_provision": row.get("NurseryProvision (name)"),
                    "open_date": row.get("OpenDate"),
                    "close_date": row.get("CloseDate"),
                    "nation": "england",
                    "source": "gias",
                    "record_status": "success",
                    "fetched_at": datetime.now(UTC).isoformat(),
                }

    except Exception as e:
        yield {
            "error": str(e),
            "status": "error",
            "path": csv_path,
            "fetched_at": datetime.now(UTC).isoformat(),
        }


@dlt.source(name="gias")
def gias_source(
    csv_path: str | None = None,
    region: str | None = None,
    local_authority: str | None = None,
):
    """
    DLT source for GIAS school information.

    Args:
        csv_path: Path to downloaded GIAS CSV (preferred method)
        region: Filter by region (if using API)
        local_authority: Filter by LA (if using API)

    Returns:
        DLT source with establishments resource
    """

    @dlt.resource(
        name="establishments",
        write_disposition="merge",
        primary_key=["urn"],
    )
    def establishments():
        """School establishment data."""
        if csv_path:
            yield from _parse_gias_csv(csv_path)
        else:
            yield from _download_establishments(region, local_authority)

    return establishments
