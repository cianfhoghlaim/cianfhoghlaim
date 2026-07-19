"""
cianfhoghlaim.cianfhoghlaim.dlt.british_isles.ireland.medicine.hse — Health Service Executive (Ireland).

Source: `https://www.hse.ie` (public service). Crawled with Firecrawl
through the shared firecrawl_source router. Yields one page dict per
URL in `HSE_URLS`.
"""
from __future__ import annotations

from collections.abc import Iterator
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
