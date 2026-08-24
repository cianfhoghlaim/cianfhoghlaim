"""
cianfhoghlaim.cianfhoghlaim.dlt.british_isles.ireland.medicine.hpsc — Health Protection Surveillance Centre.

Source: `https://www.hpsc.ie` (public service). Yields the
surveillance pages (notifiable diseases, outbreaks, etc.).
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

HPSC_URLS = {
    "homepage": "https://www.hpsc.ie",
    "notifiablediseases": "https://www.hpsc.ie/notifiablediseases/",
    "outbreaks": "https://www.hpsc.ie/outbreaks/",
    "publications": "https://www.hpsc.ie/publications/",
}


def _crawl_hpsc(max_pages: int = 30) -> Iterator[dict[str, Any]]:
    for url_key, url in HPSC_URLS.items():
        for page in _crawl_source(
            source_name=f"hpsc.{url_key}",
            base_url=url,
            include_paths=["/notifiablediseases/*", "/outbreaks/*", "/publications/*"],
            max_pages=max_pages,
            max_depth=2,
        ):
            page["nation"] = "ie"
            page["domain"] = "medicine"
            page["entity"] = "hpsc"
            yield page


@dlt.source(name="hpsc")
def hpsc_source(max_pages: int = 30):
    @dlt.resource(
        name="pages",
        write_disposition="merge",
        primary_key=["url"],
    )
    def pages():
        yield from _crawl_hpsc(max_pages=max_pages)

    return pages
