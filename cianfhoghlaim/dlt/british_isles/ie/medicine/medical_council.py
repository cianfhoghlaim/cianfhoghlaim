"""
oideachais.dlt_sources.ie.medicine.medical_council — Medical Council of Ireland.

Source: `https://www.medicalcouncil.ie/register/` (public search).
This is a *public search* source (not the authenticated register
download — that is reserved for the future
`domain-source-registry/v2` change).
"""
from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any

import dlt
import structlog

logger = structlog.get_logger(__name__)


MEDICAL_COUNCIL_URLS = {
    "register_search": "https://www.medicalcouncil.ie/register/",
    "doctors_search": "https://www.medicalcouncil.ie/public-information/register-of-medical-practitioners/",
}


def _scrape_register(max_pages: int = 20) -> Iterator[dict[str, Any]]:
    """Scrape the public register page. Per-record practitioner lookups
    require authenticated access; the public search page yields the
    searchable structure."""
    for url_key, url in MEDICAL_COUNCIL_URLS.items():
        try:
            import httpx

            response = httpx.get(url, timeout=30.0)
            response.raise_for_status()
        except (httpx.HTTPError, httpx.TimeoutException) as exc:
            logger.warning(
                "medical_council_fetch_failed",
                url=url,
                error=str(exc),
            )
            yield {
                "url": url,
                "status": "error",
                "error": str(exc),
                "nation": "ie",
                "domain": "medicine",
                "entity": "medical_council",
                "fetched_at": datetime.now(UTC).isoformat(),
            }
            continue
        yield {
            "url": url,
            "page_key": url_key,
            "title": "Medical Council of Ireland — Public register",
            "html": response.text,
            "status": "success",
            "nation": "ie",
            "domain": "medicine",
            "entity": "medical_council",
            "fetched_at": datetime.now(UTC).isoformat(),
        }


@dlt.source(name="medical_council_ie")
def medical_council_source(max_pages: int = 20):
    """DLT source for the Medical Council of Ireland (public search)."""

    @dlt.resource(
        name="register_pages",
        write_disposition="merge",
        primary_key=["url"],
    )
    def register_pages():
        yield from _scrape_register(max_pages=max_pages)

    return register_pages
