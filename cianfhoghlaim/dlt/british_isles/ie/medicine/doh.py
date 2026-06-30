"""
oideachais.dlt_sources.ie.medicine.doh — Department of Health (Ireland).

Source: `https://www.gov.ie/en/organisation/department-of-health/`
public service pages. Firecrawl crawl over the gov.ie sub-tree.
"""
from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import dlt

from ....ireland.curriculum_source import _crawl_source  # type: ignore[import-not-found]

DOH_URLS = {
    "department": "https://www.gov.ie/en/organisation/department-of-health/",
    "publications": "https://www.gov.ie/en/publication/doh/",
    "press": "https://www.gov.ie/en/news/?organisation=department-of-health",
}


def _crawl_doh(max_pages: int = 30) -> Iterator[dict[str, Any]]:
    for url_key, url in DOH_URLS.items():
        for page in _crawl_source(
            source_name=f"doh.{url_key}",
            base_url=url,
            include_paths=["/en/organisation/department-of-health/**", "/en/news/**", "/en/publication/**"],
            max_pages=max_pages,
            max_depth=2,
        ):
            page["nation"] = "ie"
            page["domain"] = "medicine"
            page["entity"] = "doh"
            yield page


@dlt.source(name="doh")
def doh_source(max_pages: int = 30):
    @dlt.resource(
        name="pages",
        write_disposition="merge",
        primary_key=["url"],
    )
    def pages():
        yield from _crawl_doh(max_pages=max_pages)

    return pages
