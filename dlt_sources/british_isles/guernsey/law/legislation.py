"""cianfhoghlaim.cianfhoghlaim.dlt.british_isles.guernsey.law.legislation — Laws of Guernsey.

Source: `https://www.guernseylegalresources.gg` (Royal Court of
Guernsey legal resources portal) and the official Guernsey
Government legislation pages.

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

GGY_LEGISLATION_URLS = {
    "homepage": "https://www.gov.gg/legislation",
    "laws": "https://www.gov.gg/legislation/laws",
    "ordinances": "https://www.gov.gg/legislation/ordinances",
    "regulations": "https://www.gov.gg/legislation/regulations",
    "orders": "https://www.gov.gg/legislation/orders",
}


def _crawl_ggy_legislation(max_pages: int = 50) -> Iterator[dict[str, Any]]:
    """Crawl the Laws of Guernsey portal."""
    for url_key, url in GGY_LEGISLATION_URLS.items():
        for page in _crawl_source(
            source_name=f"ggy.legislation.{url_key}",
            base_url=url,
            include_paths=[
                "/legislation/*",
                "/government/*",
                "/legal/*",
            ],
            max_pages=max_pages,
            max_depth=2,
        ):
            page["nation"] = "ggy"
            page["domain"] = "law"
            page["entity"] = "ggy_legislation"
            page["jurisdiction_path"] = url_key
            yield page


@dlt.source(name="ggy_legislation")
def ggy_legislation_source(max_pages: int = 50):
    """DLT source for Laws of Guernsey."""

    @dlt.resource(
        name="acts",
        write_disposition="merge",
        primary_key=["url"],
    )
    def acts():
        for page in _crawl_ggy_legislation(max_pages=max_pages):
            page["fetched_at"] = datetime.now(UTC).isoformat()
            page["status"] = "success"
            yield page

    return acts
