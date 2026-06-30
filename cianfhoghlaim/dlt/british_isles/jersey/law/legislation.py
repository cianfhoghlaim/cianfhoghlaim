"""oideachais.dlt_sources.jey.law.legislation — Jersey Law (Jersey Legal Information Board).

Source: `https://www.jerseylaw.je` (Jersey Legal Information Board).

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

JEY_LEGISLATION_URLS = {
    "homepage": "https://www.jerseylaw.je",
    "acts": "https://www.jerseylaw.je/laws/Acts",
    "statutory_instruments": "https://www.jerseylaw.je/laws/StatutoryInstruments",
    "orders": "https://www.jerseylaw.je/laws/Orders",
    "regulations": "https://www.jerseylaw.je/laws/Regulations",
}


def _crawl_jey_legislation(max_pages: int = 50) -> Iterator[dict[str, Any]]:
    """Crawl the Jersey Law portal."""
    for url_key, url in JEY_LEGISLATION_URLS.items():
        for page in _crawl_source(
            source_name=f"jey.legislation.{url_key}",
            base_url=url,
            include_paths=[
                "/laws/*",
                "/primary-legislation/*",
                "/secondary-legislation/*",
            ],
            max_pages=max_pages,
            max_depth=2,
        ):
            page["nation"] = "jey"
            page["domain"] = "law"
            page["entity"] = "jey_legislation"
            page["jurisdiction_path"] = url_key
            yield page


@dlt.source(name="jey_legislation")
def jey_legislation_source(max_pages: int = 50):
    """DLT source for Jersey Law."""

    @dlt.resource(
        name="acts",
        write_disposition="merge",
        primary_key=["url"],
    )
    def acts():
        for page in _crawl_jey_legislation(max_pages=max_pages):
            page["fetched_at"] = datetime.now(UTC).isoformat()
            page["status"] = "success"
            yield page

    return acts
