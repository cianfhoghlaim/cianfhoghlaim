"""
Culture IE source: logainm_source

Split from celtic/gaois.py in Phase 3D.
"""

from __future__ import annotations

from collections.abc import Iterator

import dlt
from dlt.sources import DltResource

try:
    from cianfhoghlaim.dlt.common.http_client import ainm_client, logainm_client, tearma_client  # noqa: F401
except ImportError:
    pass  # shared.http is unavailable; functions must lazy-import at call-time


from ._gaois_helpers import (
    LOGAINM_COUNTIES,
    _get_logainm_factory,
)


def logainm_source(
    query: str | None = None,
    county: str | None = None,
    category: str | None = None,
    max_results: int = 1000,
    include_geography: bool = True,
) -> Iterator[DltResource]:
    """
    Source for Logainm.ie Placenames Database API.

    Args:
        query: Search query for placename
        county: Filter by county name (Irish or English)
        category: Filter by placename category
        max_results: Maximum results to fetch
        include_geography: Include geographic coordinates

    Yields:
        DLT resources for placenames and categories
    """

    @dlt.resource(
        name="placenames",
        write_disposition="merge",
        primary_key="logainm_id",
    )
    def placenames_resource() -> Iterator[dict]:
        """Fetch placenames from Logainm API."""
        # Build query parameters
        params = {"per_page": min(100, max_results)}

        if query:
            path = "search/"
            params["q"] = query
        elif county:
            county_key = county.lower().replace(" ", "-")
            county_id = LOGAINM_COUNTIES.get(county_key)
            if county_id:
                path = f"administrative-units/{county_id}/places"
            else:
                logger.warning("logainm_unknown_county", county=county)
                return
        else:
            path = "places"

        if category:
            params["cat"] = category

        total_fetched = 0
        page = 1

        factory = _get_logainm_factory()
        with factory.create_client() as client:
            while total_fetched < max_results:
                params["page"] = page

                try:
                    response = client.get(path, params=params)
                    response.raise_for_status()
                    data = response.json()

                except Exception as e:
                    logger.warning("logainm_request_error", page=page, error=str(e))
                    break

                places = data if isinstance(data, list) else data.get("places", [])
                if not places:
                    break

                for place in places:
                    if total_fetched >= max_results:
                        break

                    place_data = {
                        "logainm_id": place.get("id"),
                        "name_ga": place.get("nameGA"),
                        "name_en": place.get("nameEN"),
                        "category_id": place.get("category", {}).get("id"),
                        "category_name": place.get("category", {}).get("nameGA"),
                        "county_id": place.get("county", {}).get("id"),
                        "county_name_ga": place.get("county", {}).get("nameGA"),
                        "county_name_en": place.get("county", {}).get("nameEN"),
                        "province": place.get("province", {}).get("nameGA"),
                        "logainm_url": f"https://www.logainm.ie/ga/{place.get('id')}",
                    }

                    if include_geography:
                        geo = place.get("geography", {})
                        place_data["latitude"] = geo.get("lat")
                        place_data["longitude"] = geo.get("long")
                        place_data["osm_id"] = geo.get("osmID")

                    total_fetched += 1
                    yield place_data

                page += 1

                # Check if more pages
                pagination = data.get("pagination", {}) if isinstance(data, dict) else {}
                if page > pagination.get("totalPages", 1):
                    break

    @dlt.resource(
        name="categories",
        write_disposition="replace",
        primary_key="category_id",
    )
    def categories_resource() -> Iterator[dict]:
        """Fetch placename categories from Logainm API."""
        factory = _get_logainm_factory()
        with factory.create_client() as client:
            try:
                response = client.get("categories")
                response.raise_for_status()
                categories = response.json()

            except Exception as e:
                logger.warning("logainm_categories_error", error=str(e))
                return

            for cat in categories:
                yield {
                    "category_id": cat.get("id"),
                    "name_ga": cat.get("nameGA"),
                    "name_en": cat.get("nameEN"),
                    "parent_id": cat.get("parent", {}).get("id"),
                }

    yield placenames_resource
    yield categories_resource
