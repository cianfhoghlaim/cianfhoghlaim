"""cianfhoghlaim.cianfhoghlaim.dlt.british_isles.isle_of_man.medicine.health_social_care — Isle of Man Health & Social Care.

Source: `https://www.gov.im/categories/health-and-social-care/`.
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

from cianfhoghlaim.dlt.common.site_crawler import crawl_site

IOM_RECOVERY_STRATEGY = "stealth"
"""Phase 1 fix: ``www.gov.im`` returns 403 to plain HTTP + sitemap.xml.
Routes via the Firecrawl stealth proxy with a 10s wait_for; falls
back to the Wayback Machine on stealth failure. See the
:mod:`cianfhoghlaim.dlt.common.endpoint_recovery` helper for the
operational probe."""


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

IOM_URLS = {
    "health_social_care": "https://www.gov.im/categories/health-and-social-care/",
    "public_health": "https://www.gov.im/categories/health-and-social-care/public-health/",
    "mental_health": "https://www.gov.im/categories/health-and-social-care/mental-health/",
    "social_services": "https://www.gov.im/categories/health-and-social-care/social-services/",
    "news": "https://www.gov.im/news/",
}


def _crawl_iom_health(max_pages: int = 30) -> Iterator[dict[str, Any]]:
    """Crawl the Isle of Man Health & Social Care pages."""
    for url_key, url in IOM_URLS.items():
        for page in _crawl_source(
            source_name=f"iom.health.{url_key}",
            base_url=url,
            include_paths=[
                "/categories/health-and-social-care/*",
                "/about-the-government/departments/health-and-care/*",
                "/news/*",
            ],
            max_pages=max_pages,
            max_depth=2,
        ):
            page["nation"] = "iom"
            page["domain"] = "medicine"
            page["entity"] = "iom_health_social_care"
            yield page


@dlt.source(name="iom_health_social_care")
def iom_health_social_care_source(max_pages: int = 30):
    """DLT source for Isle of Man Health & Social Care."""

    @dlt.resource(
        name="pages",
        write_disposition="merge",
        primary_key=["url"],
    )
    def pages():
        for page in _crawl_iom_health(max_pages=max_pages):
            page["fetched_at"] = datetime.now(UTC).isoformat()
            page["status"] = "success"
            yield page

    return pages
