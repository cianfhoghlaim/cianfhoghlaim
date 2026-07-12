"""
oideachais.cianfhoghlaim.dlt.british_isles.wales.medicine — Wales medicine (NHS Wales / PHW).
Phase 7 of the openspec change.
"""
from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import dlt

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

NHS_WALES_URLS = {
    "phw": "https://phw.nhs.wales",
    "publications": "https://phw.nhs.wales/publications/",
    "news": "https://phw.nhs.wales/news/",
}


def _crawl_nhs_wales(max_pages: int = 30) -> Iterator[dict[str, Any]]:
    for url_key, url in NHS_WALES_URLS.items():
        for page in _crawl_source(
            source_name=f"nhs_wales.{url_key}",
            base_url=url,
            include_paths=["/publications/*", "/news/*", "/services-and-teams/*"],
            max_pages=max_pages,
            max_depth=2,
        ):
            page["nation"] = "wls"
            page["domain"] = "medicine"
            page["entity"] = "nhs_wales"
            yield page


@dlt.source(name="nhs_wales")
def nhs_wales_source(max_pages: int = 30):
    @dlt.resource(name="pages", write_disposition="merge", primary_key=["url"])
    def pages():
        yield from _crawl_nhs_wales(max_pages=max_pages)

    return pages
