"""
DLT Source for Dúchas.ie National Folklore Collection API.

Collections:
- cbe: Main Manuscript Collection
- cbes: Schools' Collection (1937-1939) - has XML API
- cbeg: Photographic Collection
- cbef: Audio Collection

Based on API documentation in duchas.json.

Uses HttpClientFactory for resilient HTTP client with:
- Circuit breaker pattern
- Rate limiting
- Automatic retries

Usage:
    from oideachais.dlt_sources.celtic.duchas import duchas_source

    pipeline = dlt.pipeline(
        pipeline_name="duchas",
        destination="duckdb",
    )
    pipeline.run(duchas_source())
"""
from __future__ import annotations

import re
from collections.abc import Iterator
from xml.etree import ElementTree as ET

import dlt
from bs4 import BeautifulSoup
from dlt.sources import DltResource
from oideachais.observability.logging import get_logger
from shared.http import duchas_client

logger = get_logger(__name__)


def _get_duchas_factory():
    """Get HTTP client factory for Dúchas.ie."""
    return duchas_client()


@dlt.source(name="duchas_folklore")
def duchas_source(
    collection: str = "cbes",
    max_pages: int = 100,
    per_page: int = 50,
    county: str | None = None,
    transcribed_only: bool = False,
) -> Iterator[DltResource]:
    """
    Source for Dúchas.ie National Folklore Collection.

    Args:
        collection: Collection identifier (cbe, cbes, cbeg, cbef)
        max_pages: Maximum pages to fetch
        per_page: Items per page
        county: Filter by county name
        transcribed_only: Only fetch transcribed items

    Yields:
        DLT resources for volumes and items
    """

    @dlt.resource(
        name="volumes",
        write_disposition="merge",
        primary_key="entry_id",
    )
    def volumes_resource() -> Iterator[dict]:
        """Paginate through collection volumes."""
        if collection == "cbes":
            path = "/en/cbes/volumes"
        elif collection == "cbe":
            path = "/en/cbe/volumes"
        elif collection == "cbeg":
            path = "/en/cbeg"
        elif collection == "cbef":
            path = "/en/cbef/recordings"
        else:
            raise ValueError(f"Unknown collection: {collection}")

        factory = _get_duchas_factory()
        with factory.create_client() as client:
            for page in range(1, max_pages + 1):
                params = {
                    "Page": page,
                    "PerPage": per_page,
                }
                if transcribed_only:
                    params["Transcribed"] = "true"
                if county:
                    params["County"] = county

                try:
                    response = client.get(path, params=params)
                    response.raise_for_status()

                except Exception as e:
                    logger.warning(
                        "duchas_fetch_error",
                        page=page,
                        error=str(e),
                    )
                    break

                soup = BeautifulSoup(response.text, "html.parser")

                # Extract items based on collection type
                items_found = False
                for item in _extract_volume_items(soup, collection):
                    items_found = True
                    item["collection"] = collection
                    item["source_url"] = f"https://www.duchas.ie{path}?Page={page}"
                    yield item

                if not items_found:
                    break  # No more results

    @dlt.resource(
        name="schools_xml",
        write_disposition="merge",
        primary_key="school_id",
    )
    def schools_xml_resource() -> Iterator[dict]:
        """
        Fetch Schools' Collection XML data.
        Only available for cbes collection.
        """
        if collection != "cbes":
            return

        # First get list of school IDs from volumes
        school_ids = []
        factory = _get_duchas_factory()

        with factory.create_client() as client:
            for page in range(1, min(max_pages, 10) + 1):
                params = {"Page": page, "PerPage": per_page}
                if county:
                    params["County"] = county

                try:
                    response = client.get("/en/cbes/volumes", params=params)
                    response.raise_for_status()

                    soup = BeautifulSoup(response.text, "html.parser")

                    # Extract school IDs from links
                    for link in soup.find_all("a", href=re.compile(r"/cbes/\d+")):
                        match = re.search(r"/cbes/(\d+)", link["href"])
                        if match:
                            school_ids.append(match.group(1))

                    if not soup.find_all("a", href=re.compile(r"/cbes/\d+")):
                        break

                except Exception as e:
                    logger.warning("schools_xml_error", page=page, error=str(e))
                    break

            # Fetch XML for each school
            for school_id in set(school_ids):
                xml_data = _fetch_school_xml(client, school_id)
                if xml_data:
                    yield xml_data

    yield volumes_resource
    if collection == "cbes":
        yield schools_xml_resource


def _extract_volume_items(soup: BeautifulSoup, collection: str) -> Iterator[dict]:
    """Extract volume items from HTML based on collection type."""

    if collection in ("cbe", "cbes"):
        # Look for volume list items
        for row in soup.select("table tbody tr, .volume-item, .list-item"):
            item = _parse_volume_row(row, collection)
            if item:
                yield item

    elif collection == "cbeg":
        # Photographic collection
        for item in soup.select(".photo-item, .gallery-item, .result-item"):
            photo = _parse_photo_item(item)
            if photo:
                yield photo

    elif collection == "cbef":
        # Audio collection
        for item in soup.select(".recording-item, .audio-item, .result-item"):
            audio = _parse_audio_item(item)
            if audio:
                yield audio


def _parse_volume_row(row, collection: str) -> dict | None:
    """Parse a volume row from HTML."""
    # Try to extract entry ID from link
    link = row.find("a", href=re.compile(rf"/{collection}/\d+"))
    if not link:
        return None

    match = re.search(rf"/{collection}/(\d+)", link["href"])
    if not match:
        return None

    entry_id = match.group(1)

    # Extract other fields
    cells = row.find_all("td") if row.name == "tr" else [row]

    return {
        "entry_id": entry_id,
        "volume_number": _extract_text(row, ".volume-number, .vol-num"),
        "page_count": _extract_text(row, ".page-count"),
        "transcription_status": "transcribed" in row.get("class", [])
        or bool(row.find(class_=re.compile("transcribed"))),
        "county": _extract_text(row, ".county"),
        "location": _extract_text(row, ".location"),
        "collector": _extract_text(row, ".collector, .person"),
    }


def _parse_photo_item(item) -> dict | None:
    """Parse a photographic collection item."""
    link = item.find("a", href=re.compile(r"/cbeg/\d+"))
    if not link:
        return None

    match = re.search(r"/cbeg/(\d+)", link["href"])
    if not match:
        return None

    return {
        "entry_id": match.group(1),
        "archival_reference": _extract_text(item, ".reference"),
        "subject": _extract_text(item, ".subject, .title"),
        "date": _extract_text(item, ".date"),
        "location": _extract_text(item, ".location"),
        "handbook_topic_id": _extract_attr(item, "data-topic-id"),
        "logainm_id": _extract_attr(item, "data-logainm-id"),
    }


def _parse_audio_item(item) -> dict | None:
    """Parse an audio collection item."""
    link = item.find("a", href=re.compile(r"/cbef/\d+"))
    if not link:
        return None

    match = re.search(r"/cbef/(\d+)", link["href"])
    if not match:
        return None

    return {
        "entry_id": match.group(1),
        "carrier_id": _extract_text(item, ".carrier"),
        "format": _extract_text(item, ".format"),
        "recording_date": _extract_text(item, ".date"),
        "collector": _extract_text(item, ".collector"),
        "informant": _extract_text(item, ".informant"),
        "location": _extract_text(item, ".location"),
    }


def _fetch_school_xml(client, school_id: str) -> dict | None:
    """Fetch and parse Schools' Collection XML for a school."""
    xml_path = f"/xml/cbes/{school_id}"

    try:
        response = client.get(xml_path)

        if response.status_code != 200:
            logger.debug(
                "school_xml_not_found",
                school_id=school_id,
                status_code=response.status_code,
            )
            return None

        root = ET.fromstring(response.text)

        # Parse school location
        location_elem = root.find(".//schoolLocation")
        location = None
        if location_elem is not None:
            location = {
                "name_ga": location_elem.findtext("nameGA"),
                "name_en": location_elem.findtext("nameEN"),
                "latitude": _safe_float(location_elem.findtext("lat")),
                "longitude": _safe_float(location_elem.findtext("lon")),
                "county": location_elem.findtext("county"),
                "logainm_url": location_elem.get("href"),
            }

        # Parse pages
        pages = [
            {"page_id": p.get("id"), "page_number": p.text}
            for p in root.findall(".//page")
        ]

        logger.debug(
            "school_xml_parsed",
            school_id=school_id,
            page_count=len(pages),
        )

        return {
            "school_id": school_id,
            "entry_id": root.get("entryID"),
            "volume_number": root.get("volumeNumber"),
            "volume_status": _safe_int(root.get("volumeStatus")),
            "school_name": root.findtext(".//schoolName"),
            "school_roll_number": root.findtext(".//schoolRollNumber"),
            "teacher_name": root.findtext(".//teacherName"),
            "location": location,
            "pages": pages,
            "page_count": len(pages),
            "source_url": f"https://www.duchas.ie{xml_path}",
        }

    except ET.ParseError as e:
        logger.error(
            "school_xml_parse_error",
            school_id=school_id,
            error=str(e),
        )
        return None
    except Exception as e:
        logger.warning(
            "school_xml_error",
            school_id=school_id,
            error=str(e),
        )
        return None


def _extract_text(element, selector: str) -> str | None:
    """Extract text from element using CSS selector."""
    for sel in selector.split(","):
        found = element.select_one(sel.strip())
        if found:
            return found.get_text(strip=True)
    return None


def _extract_attr(element, attr: str) -> str | None:
    """Extract attribute value from element."""
    return element.get(attr)


def _safe_float(value: str | None) -> float | None:
    """Safely convert to float."""
    if value:
        try:
            return float(value)
        except ValueError:
            pass
    return None


def _safe_int(value: str | None) -> int | None:
    """Safely convert to int."""
    if value:
        try:
            return int(value)
        except ValueError:
            pass
    return None
