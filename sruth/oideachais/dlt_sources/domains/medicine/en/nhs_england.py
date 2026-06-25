"""
oideachais.dlt_sources.domains.medicine.en — England medicine (NHS England,
GMC, NICE). Phase 7 of the openspec change.
"""
from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import dlt

from ....ireland.curriculum_source import _crawl_source  # type: ignore[import-not-found]

NHS_ENGLAND_URLS = {
    "main": "https://www.england.nhs.uk",
    "about": "https://www.england.nhs.uk/about/",
    "publications": "https://www.england.nhs.uk/publications/",
}


def _crawl_nhs_england(max_pages: int = 30) -> Iterator[dict[str, Any]]:
    for url_key, url in NHS_ENGLAND_URLS.items():
        for page in _crawl_source(
            source_name=f"nhs_england.{url_key}",
            base_url=url,
            include_paths=["/about/*", "/publications/*", "/commissioning/*"],
            max_pages=max_pages,
            max_depth=2,
        ):
            page["nation"] = "en"
            page["domain"] = "medicine"
            page["entity"] = "nhs_england"
            yield page


@dlt.source(name="nhs_england")
def nhs_england_source(max_pages: int = 30):
    @dlt.resource(name="pages", write_disposition="merge", primary_key=["url"])
    def pages():
        yield from _crawl_nhs_england(max_pages=max_pages)

    return pages
