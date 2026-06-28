"""
oideachais.dlt_sources.ie.medicine.hse — Health Service Executive (Ireland).

Source: `https://www.hse.ie` (public service). Crawled with Firecrawl
through the shared firecrawl_source router. Yields one page dict per
URL in `HSE_URLS`.
"""
from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import dlt
import structlog

from ....ireland.curriculum_source import _crawl_source  # type: ignore[import-not-found]

logger = structlog.get_logger(__name__)


HSE_URLS = {
    "homepage": "https://www.hse.ie",
    "about": "https://www.hse.ie/about/",
    "services": "https://www.hse.ie/services/",
    "conditions": "https://www.hse.ie/conditions/",
    "news": "https://www.hse.ie/news/",
}


def _crawl_hse(max_pages: int = 50) -> Iterator[dict[str, Any]]:
    """Crawl HSE.ie under `/services`, `/conditions`, and `/news/`."""
    include_paths = [
        "/services/*",
        "/conditions/*",
        "/news/*",
        "/about/*",
    ]
    for url_key, url in HSE_URLS.items():
        for page in _crawl_source(
            source_name=f"hse.{url_key}",
            base_url=url,
            include_paths=include_paths,
            max_pages=max_pages,
            max_depth=2,
        ):
            page["nation"] = "ie"
            page["domain"] = "medicine"
            page["entity"] = "hse"
            yield page


@dlt.source(name="hse")
def hse_source(max_pages: int = 50):
    """DLT source for HSE.ie (Ireland)."""

    @dlt.resource(
        name="pages",
        write_disposition="merge",
        primary_key=["url"],
    )
    def pages():
        yield from _crawl_hse(max_pages=max_pages)

    return pages
