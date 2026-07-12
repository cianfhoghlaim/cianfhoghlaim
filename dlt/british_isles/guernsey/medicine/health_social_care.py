"""oideachais.cianfhoghlaim.dlt.british_isles.guernsey.medicine.health_social_care — States of Guernsey Health & Social Care.

Source: `https://www.gov.gg/health-social-care` (States of Guernsey).
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

GGY_URLS = {
    "health_social_care": "https://www.gov.gg/health-social-care",
    "public_health": "https://www.gov.gg/public-health",
    "mental_health": "https://www.gov.gg/mental-health",
    "health_community": "https://www.gov.gg/health-community",
    "news": "https://www.gov.gg/news",
}


def _crawl_ggy_health(max_pages: int = 30) -> Iterator[dict[str, Any]]:
    """Crawl the States of Guernsey Health & Social Care pages."""
    for url_key, url in GGY_URLS.items():
        for page in _crawl_source(
            source_name=f"ggy.health.{url_key}",
            base_url=url,
            include_paths=[
                "/health-social-care/*",
                "/public-health/*",
                "/mental-health/*",
                "/news/*",
            ],
            max_pages=max_pages,
            max_depth=2,
        ):
            page["nation"] = "ggy"
            page["domain"] = "medicine"
            page["entity"] = "ggy_health_social_care"
            yield page


@dlt.source(name="ggy_health_social_care")
def ggy_health_social_care_source(max_pages: int = 30):
    """DLT source for States of Guernsey Health & Social Care."""

    @dlt.resource(
        name="pages",
        write_disposition="merge",
        primary_key=["url"],
    )
    def pages():
        for page in _crawl_ggy_health(max_pages=max_pages):
            page["fetched_at"] = datetime.now(UTC).isoformat()
            page["status"] = "success"
            yield page

    return pages
