"""
cianfhoghlaim.cianfhoghlaim.dlt.british_isles.scotland.medicine — Scotland medicine (NHS Scotland).
Phase 7 of the openspec change.
"""
from __future__ import annotations
import dlt


from collections.abc import Iterator
from typing import Any

import dlt_sources

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

NHS_SCOTLAND_URLS = {
    "main": "https://www.scot.nhs.uk",
    "publications": "https://www.scot.nhs.uk/publications/",
    "news": "https://www.scot.nhs.uk/news/",
}


def _crawl_nhs_scotland(max_pages: int = 30) -> Iterator[dict[str, Any]]:
    for url_key, url in NHS_SCOTLAND_URLS.items():
        for page in _crawl_source(
            source_name=f"nhs_scotland.{url_key}",
            base_url=url,
            include_paths=["/publications/*", "/news/*", "/about/*"],
            max_pages=max_pages,
            max_depth=2,
        ):
            page["nation"] = "sct"
            page["domain"] = "medicine"
            page["entity"] = "nhs_scotland"
            yield page


@dlt.source(name="nhs_scotland")
def nhs_scotland_source(max_pages: int = 30):
    @dlt.resource(name="pages", write_disposition="merge", primary_key=["url"])
    def pages():
        yield from _crawl_nhs_scotland(max_pages=max_pages)

    return pages
