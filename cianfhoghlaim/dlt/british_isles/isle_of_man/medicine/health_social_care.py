"""oideachais.dlt_sources.iom.medicine.health_social_care — Isle of Man Health & Social Care.

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

from cianfhoghlaim.dlt.common.incremental import crawl_source  # type: ignore[import-not-found]

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
