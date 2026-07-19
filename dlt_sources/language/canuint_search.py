"""
Culture IE source: canuint_search_source

Split from celtic/canuint.py in Phase 3D.
"""

from __future__ import annotations
import dlt


import re
from collections.abc import Iterator

import dlt_sources
from bs4 import BeautifulSoup
from dlt.sources import DltResource

try:
    from dlt_sources.common.http_client import canuint_client  # noqa: F401
except ImportError:
    pass  # shared.http is unavailable; functions must lazy-import at call-time


from ._canuint_helpers import (
    CANUINT_BASE,
    _get_canuint_factory,
)


def canuint_search_source(
    query: str,
    language: str = "ga",
    max_results: int = 100,
) -> Iterator[DltResource]:
    """
    Search Canuint.ie for specific words or phrases.

    Args:
        query: Search term
        language: Interface language ('ga' or 'en')
        max_results: Maximum results to return

    Yields:
        DLT resource for search results
    """

    @dlt.resource(
        name="search_results",
        write_disposition="append",
        primary_key="result_id",
    )
    def search_results_resource() -> Iterator[dict]:
        """Search for pronunciation recordings."""
        factory = _get_canuint_factory()
        search_path = "cuardach" if language == "ga" else "search"

        with factory.create_client() as client:
            try:
                response = client.get(f"/{language}/{search_path}", params={"t": query})
                response.raise_for_status()
            except Exception as e:
                logger.warning("canuint_search_error", query=query, error=str(e))
                return

            soup = BeautifulSoup(response.text, "html.parser")

            result_count = 0
            for result in soup.find_all("li", class_="recording"):
                if result_count >= max_results:
                    break

                # Extract recording ID
                recording_link = result.find("a", href=re.compile(r"/[A-Z]+\d+c\d+"))
                if not recording_link:
                    continue

                match = re.search(r"([A-Z]+\d+c\d+)", recording_link["href"])
                if not match:
                    continue

                recording_id = match.group(1)

                # Extract metadata
                is_transcribed = result.get("data-is-transcribed") == "1"

                year = None
                year_elem = result.find("span", class_="year")
                if year_elem:
                    year_text = year_elem.get_text(strip=True)
                    if year_text.isdigit():
                        year = int(year_text)

                # Extract area info
                area_link = result.find("a", class_="area")
                area_name = area_link.get_text(strip=True) if area_link else None

                result_count += 1

                yield {
                    "result_id": f"{query}_{recording_id}",
                    "query": query,
                    "recording_id": recording_id,
                    "area_name": area_name,
                    "year": year,
                    "is_transcribed": is_transcribed,
                    "audio_url": f"{CANUINT_BASE}/sounds/{recording_id}.mp3",
                    "source_url": f"{CANUINT_BASE}/{language}/{search_path}?t={query}",
                }

    yield search_results_resource
