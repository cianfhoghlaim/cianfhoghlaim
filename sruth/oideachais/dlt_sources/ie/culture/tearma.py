"""
Culture IE source: tearma_source

Split from celtic/gaois.py in Phase 3D.
"""

from __future__ import annotations
import re
from collections.abc import Iterator
import dlt
from bs4 import BeautifulSoup
from dlt.sources import DltResource
from observability.logging import get_logger
try:
    from shared.http import ainm_client, logainm_client, tearma_client  # noqa: F401
except ImportError:
    pass  # shared.http is unavailable; functions must lazy-import at call-time


from ._gaois_helpers import (
    _get_tearma_factory,
)

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
