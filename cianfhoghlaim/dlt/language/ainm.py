"""
Culture IE source: ainm_source

Split from celtic/gaois.py in Phase 3D.
"""

from __future__ import annotations

import re
from collections.abc import Iterator

import dlt
from bs4 import BeautifulSoup
from dlt.sources import DltResource

try:
    from cianfhoghlaim.dlt.common.http_client import ainm_client, logainm_client, tearma_client  # noqa: F401
except ImportError:
    pass  # shared.http is unavailable; functions must lazy-import at call-time


from ._gaois_helpers import (
    _get_ainm_factory,
)


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
