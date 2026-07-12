"""oideachais.cianfhoghlaim.dlt.british_isles.jersey.law.legislation — Jersey Law (Jersey Legal Information Board).

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
