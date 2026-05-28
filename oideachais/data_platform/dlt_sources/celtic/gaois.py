"""
DLT Sources for GAOIS Research Group APIs.

GAOIS (https://www.gaois.ie) provides linguistic research APIs:
- Logainm.ie: Placenames Database of Ireland
- Téarma.ie: National Terminology Database
- Ainm.ie: Biographical Database

Doras API base: https://www.logainm.ie/api/v1.1/

Uses HttpClientFactory for resilient HTTP client with:
- Circuit breaker pattern
- Rate limiting
- Automatic retries

Usage:
    from data_platform.dlt_sources.celtic.gaois import logainm_source

    pipeline = dlt.pipeline(
        pipeline_name="logainm",
        destination="duckdb",
    )
    pipeline.run(logainm_source(county="galway"))
"""
from __future__ import annotations

import re
from collections.abc import Iterator

import dlt
from bs4 import BeautifulSoup
from dlt.sources import DltResource
from observability.logging import get_logger
from shared.http import ainm_client, logainm_client, tearma_client

logger = get_logger(__name__)


def _get_logainm_factory():
    """Get HTTP client factory for Logainm.ie API."""
    return logainm_client()


def _get_tearma_factory():
    """Get HTTP client factory for Téarma.ie."""
    return tearma_client()


def _get_ainm_factory():
    """Get HTTP client factory for Ainm.ie."""
    return ainm_client()


# County ID mapping for Logainm
LOGAINM_COUNTIES = {
    "an-cabhán": 100001,
    "cavan": 100001,
    "dún-na-ngall": 100002,
    "donegal": 100002,
    "muineachán": 100003,
    "monaghan": 100003,
    "connacht": 100004,
    "gaillimh": 100005,
    "galway": 100005,
    "liatroim": 100006,
    "leitrim": 100006,
    "maigh-eo": 100007,
    "mayo": 100007,
    "ros-comáin": 100008,
    "roscommon": 100008,
    "sligeach": 100009,
    "sligo": 100009,
    "laighin": 100010,
    "leinster": 100010,
    "ceatharlach": 100011,
    "carlow": 100011,
    "baile-átha-cliath": 100012,
    "dublin": 100012,
    "cill-dara": 100013,
    "kildare": 100013,
    "cill-chainnigh": 100014,
    "kilkenny": 100014,
    "laois": 100015,
    "an-longfort": 100016,
    "longford": 100016,
    "an-lú": 100017,
    "louth": 100017,
    "an-mhí": 100018,
    "meath": 100018,
    "uíbh-fhailí": 100019,
    "offaly": 100019,
    "iarmhí": 100020,
    "westmeath": 100020,
    "loch-garman": 100021,
    "wexford": 100021,
    "cill-mhantáin": 100022,
    "wicklow": 100022,
    "mumha": 100023,
    "munster": 100023,
    "an-clár": 100024,
    "clare": 100024,
    "corcaigh": 100025,
    "cork": 100025,
    "ciarraí": 100026,
    "kerry": 100026,
    "luimneach": 100027,
    "limerick": 100027,
    "tiobraid-árann": 100028,
    "tipperary": 100028,
    "port-láirge": 100029,
    "waterford": 100029,
    "ulster-roi": 100030,
    "aontroim": 100031,
    "antrim": 100031,
    "ard-mhacha": 100032,
    "armagh": 100032,
    "an-dún": 100033,
    "down": 100033,
    "fear-manach": 100034,
    "fermanagh": 100034,
    "doire": 100035,
    "derry": 100035,
    "tír-eoghain": 100036,
    "tyrone": 100036,
}


@dlt.source(name="logainm_placenames")
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


@dlt.source(name="tearma_terminology")
def tearma_source(
    domain: str | None = None,
    max_terms: int = 500,
) -> Iterator[DltResource]:
    """
    Source for Téarma.ie National Terminology Database.

    Note: Téarma.ie does not have a public API, so this scrapes
    the search results and term pages.

    Args:
        domain: Filter by domain/subject area
        max_terms: Maximum terms to fetch

    Yields:
        DLT resources for terms and domains
    """

    @dlt.resource(
        name="terms",
        write_disposition="merge",
        primary_key="term_id",
    )
    def terms_resource() -> Iterator[dict]:
        """Scrape terminology from Téarma.ie search."""
        # Use alphabetical browse or common terms
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        terms_fetched = 0

        factory = _get_tearma_factory()
        with factory.create_client() as client:
            for letter in alphabet:
                if terms_fetched >= max_terms:
                    break

                params = {"t": letter, "foinse": "nta"}

                try:
                    response = client.get("/ga/cuardach", params=params)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, "html.parser")

                except Exception as e:
                    logger.warning("tearma_search_error", letter=letter, error=str(e))
                    continue

                # Extract term entries
                for entry in soup.select(".term-entry, .result-item, .iontráil"):
                    if terms_fetched >= max_terms:
                        break

                    term_link = entry.find("a", href=re.compile(r"/ga/téarma/\d+"))
                    if not term_link:
                        continue

                    match = re.search(r"/ga/téarma/(\d+)", term_link.get("href", ""))
                    if not match:
                        continue

                    term_id = match.group(1)

                    # Get Irish and English terms
                    term_ga = term_link.get_text(strip=True)
                    term_en = None

                    en_elem = entry.find(class_="term-en")
                    if en_elem:
                        term_en = en_elem.get_text(strip=True)

                    # Get domain
                    domain_text = None
                    domain_elem = entry.find(class_="domain")
                    if domain_elem:
                        domain_text = domain_elem.get_text(strip=True)

                    terms_fetched += 1

                    yield {
                        "term_id": term_id,
                        "term_ga": term_ga,
                        "term_en": term_en,
                        "domain": domain_text,
                        "source": "NTA",
                        "tearma_url": f"https://www.tearma.ie/ga/téarma/{term_id}",
                    }

    @dlt.resource(
        name="domains",
        write_disposition="replace",
        primary_key="domain_id",
    )
    def domains_resource() -> Iterator[dict]:
        """Extract terminology domains from Téarma.ie."""
        factory = _get_tearma_factory()
        with factory.create_client() as client:
            try:
                response = client.get("/ga/cuardach")
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")

            except Exception as e:
                logger.warning("tearma_domains_error", error=str(e))
                return

            # Find domain filter dropdown
            domain_select = soup.find("select", {"id": "domain", "name": "domain"})
            if not domain_select:
                domain_select = soup.find("select", class_="domain-filter")

            if domain_select:
                for idx, option in enumerate(domain_select.find_all("option")):
                    value = option.get("value")
                    if value and value != "":
                        yield {
                            "domain_id": f"domain_{idx}",
                            "domain_code": value,
                            "domain_name": option.get_text(strip=True),
                        }

    yield terms_resource
    yield domains_resource


@dlt.source(name="ainm_biographies")
def ainm_source(
    profession: str | None = None,
    max_entries: int = 200,
) -> Iterator[DltResource]:
    """
    Source for Ainm.ie National Biographical Database.

    Note: Ainm.ie does not have a public API, so this scrapes
    the directory and biography pages.

    Args:
        profession: Filter by profession/occupation
        max_entries: Maximum entries to fetch

    Yields:
        DLT resources for biographical entries
    """

    @dlt.resource(
        name="biographies",
        write_disposition="merge",
        primary_key="ainm_id",
    )
    def biographies_resource() -> Iterator[dict]:
        """Scrape biographical entries from Ainm.ie."""
        # Use alphabetical directory
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        entries_fetched = 0

        factory = _get_ainm_factory()
        with factory.create_client() as client:
            for letter in alphabet:
                if entries_fetched >= max_entries:
                    break

                try:
                    response = client.get("/ga/ainm", params={"letter": letter})
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, "html.parser")

                except Exception as e:
                    logger.warning("ainm_browse_error", letter=letter, error=str(e))
                    continue

                # Extract person entries
                for entry in soup.select(".person-entry, .result-item, a[href*='/ga/ainm/']"):
                    if entries_fetched >= max_entries:
                        break

                    # Get person ID from link
                    href = entry.get("href") if entry.name == "a" else None
                    if not href:
                        link = entry.find("a", href=re.compile(r"/ga/ainm/\d+"))
                        if link:
                            href = link.get("href")

                    if not href:
                        continue

                    match = re.search(r"/ga/ainm/(\d+)", href)
                    if not match:
                        continue

                    ainm_id = match.group(1)
                    name = entry.get_text(strip=True) if entry.name == "a" else None

                    if not name:
                        name_elem = entry.find(class_="person-name")
                        if name_elem:
                            name = name_elem.get_text(strip=True)

                    # Get additional metadata
                    dates = None
                    profession_text = None
                    location = None

                    dates_elem = entry.find(class_="dates")
                    if dates_elem:
                        dates = dates_elem.get_text(strip=True)

                    prof_elem = entry.find(class_="profession")
                    if prof_elem:
                        profession_text = prof_elem.get_text(strip=True)

                    loc_elem = entry.find(class_="location")
                    if loc_elem:
                        location = loc_elem.get_text(strip=True)

                    entries_fetched += 1

                    yield {
                        "ainm_id": ainm_id,
                        "name": name,
                        "dates": dates,
                        "profession": profession_text,
                        "location": location,
                        "ainm_url": f"https://www.ainm.ie/ga/ainm/{ainm_id}",
                    }

    @dlt.resource(
        name="professions",
        write_disposition="replace",
        primary_key="profession_id",
    )
    def professions_resource() -> Iterator[dict]:
        """Extract profession/occupation categories from Ainm.ie."""
        factory = _get_ainm_factory()
        with factory.create_client() as client:
            try:
                response = client.get("/ga/")
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")

            except Exception as e:
                logger.warning("ainm_professions_error", error=str(e))
                return

            # Find profession filter or navigation
            for idx, link in enumerate(
                soup.find_all("a", href=re.compile(r"profession=|gairm="))
            ):
                href = link.get("href", "")
                match = re.search(r"(?:profession|gairm)=([^&]+)", href)
                if match:
                    yield {
                        "profession_id": f"prof_{idx}",
                        "profession_code": match.group(1),
                        "profession_name": link.get_text(strip=True),
                    }

    yield biographies_resource
    yield professions_resource


@dlt.source(name="gaois_combined")
def gaois_combined_source(
    logainm_county: str | None = None,
    max_placenames: int = 500,
    max_terms: int = 200,
    max_biographies: int = 100,
) -> Iterator[DltResource]:
    """
    Combined source for all GAOIS databases.

    Args:
        logainm_county: Filter placenames by county
        max_placenames: Maximum placenames to fetch
        max_terms: Maximum terminology entries
        max_biographies: Maximum biographical entries

    Yields:
        Combined DLT resources from all GAOIS databases
    """
    # Yield placenames
    for resource in logainm_source(
        county=logainm_county, max_results=max_placenames
    ):
        yield resource

    # Yield terminology
    for resource in tearma_source(max_terms=max_terms):
        yield resource

    # Yield biographies
    for resource in ainm_source(max_entries=max_biographies):
        yield resource
