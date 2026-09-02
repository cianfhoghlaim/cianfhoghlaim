"""cianfhoghlaim.cianfhoghlaim.dlt.british_isles.jersey.medicine.health_community_services — Jersey Health & Community Services.

Source: `https://www.gov.je/health/` (Government of Jersey).
Per
https://github.com/cianfhoghlaim/cianfhoghlaim/issues/19
(closed 2026-06-15) the lateralise change wired this as one of the
6 crown-dependencies (IOM/JEY/GGY) medicine + law DLT sources.
"""
from __future__ import annotations
import dlt


from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any

import dlt_sources
import structlog

from dlt_sources.common.site_crawler import crawl_site

def _crawl_source(*args, **kwargs):
    # The legacy _crawl_source took (source_name, base_url, ...) — source_name
    # was used only for logging in the legacy helper. The new crawl_site
    # primitive has no source_name, so we drop it if present.
    if args and isinstance(args[0], str) and args[0] == kwargs.get("source_name"):
        args = args[1:]
    kwargs.pop("source_name", None)
    for page in crawl_site(*args, **kwargs):
        yield page.to_dict()

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
