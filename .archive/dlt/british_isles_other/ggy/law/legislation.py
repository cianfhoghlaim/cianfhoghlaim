"""oideachais.dlt_sources.ggy.law.legislation — Laws of Guernsey.

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

from ....ireland.curriculum_source import _crawl_source  # type: ignore[import-not-found]

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
