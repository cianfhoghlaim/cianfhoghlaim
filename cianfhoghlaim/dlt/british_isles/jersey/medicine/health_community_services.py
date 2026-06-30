"""oideachais.dlt_sources.jey.medicine.health_community_services — Jersey Health & Community Services.

Source: `https://www.gov.je/health/` (Government of Jersey).
Per
https://github.com/cianfhoghlaim/kings_college_galway/issues/19
(closed 2026-06-15) the lateralise change wired this as one of the
6 crown-dependencies (IOM/JEY/GGY) medicine + law DLT sources.
"""
from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any

import dlt
import structlog

from cianfhoghlaim.dlt.common.incremental import crawl_source  # type: ignore[import-not-found]

logger = structlog.get_logger(__name__)

JEY_URLS = {
    "health": "https://www.gov.je/health/",
    "health_community": "https://www.gov.je/health/healthcommunity/",
    "public_health": "https://www.gov.je/health/publichealth/",
    "mental_health": "https://www.gov.je/health/mentalhealth/",
    "news": "https://www.gov.je/news/",
}


def _crawl_jey_health(max_pages: int = 30) -> Iterator[dict[str, Any]]:
    """Crawl the Jersey Health & Community Services pages."""
    for url_key, url in JEY_URLS.items():
        for page in _crawl_source(
            source_name=f"jey.health.{url_key}",
            base_url=url,
            include_paths=[
                "/health/*",
                "/government/departments/health-and-community-services/*",
                "/news/*",
            ],
            max_pages=max_pages,
            max_depth=2,
        ):
            page["nation"] = "jey"
            page["domain"] = "medicine"
            page["entity"] = "jey_health_community_services"
            yield page


@dlt.source(name="jey_health_community_services")
def jey_health_community_services_source(max_pages: int = 30):
    """DLT source for Jersey Health & Community Services."""

    @dlt.resource(
        name="pages",
        write_disposition="merge",
        primary_key=["url"],
    )
    def pages():
        for page in _crawl_jey_health(max_pages=max_pages):
            page["fetched_at"] = datetime.now(UTC).isoformat()
            page["status"] = "success"
            yield page

    return pages
