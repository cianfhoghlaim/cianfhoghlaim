"""
oideachais.dlt_sources.domains.medicine.wls — Wales medicine (NHS Wales / PHW).
Phase 7 of the openspec change.
"""
from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import dlt

from ....ireland.curriculum_source import _crawl_source  # type: ignore[import-not-found]

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
