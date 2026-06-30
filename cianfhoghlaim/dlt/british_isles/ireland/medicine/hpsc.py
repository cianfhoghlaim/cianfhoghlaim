"""
oideachais.cianfhoghlaim.dlt.british_isles.ireland.medicine.hpsc — Health Protection Surveillance Centre.

Source: `https://www.hpsc.ie` (public service). Yields the
surveillance pages (notifiable diseases, outbreaks, etc.).
"""
from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import dlt

from cianfhoghlaim.dlt.common.incremental import crawl_source  # type: ignore[import-not-found]

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
