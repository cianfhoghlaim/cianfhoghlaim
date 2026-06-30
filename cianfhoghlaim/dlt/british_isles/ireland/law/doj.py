"""
oideachais.cianfhoghlaim.dlt.british_isles.ireland.law.doj — Department of Justice (Ireland).

Source: `https://www.gov.ie/en/organisation/department-of-justice/`
public service pages.
"""
from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import dlt

from cianfhoghlaim.dlt.common.incremental import crawl_source  # type: ignore[import-not-found]

DOJ_URLS = {
    "department": "https://www.gov.ie/en/organisation/department-of-justice/",
    "press": "https://www.gov.ie/en/news/?organisation=department-of-justice",
    "publications": "https://www.gov.ie/en/publication/?organisation=department-of-justice",
}


def _crawl_doj(max_pages: int = 30) -> Iterator[dict[str, Any]]:
    for url_key, url in DOJ_URLS.items():
        for page in _crawl_source(
            source_name=f"doj.{url_key}",
            base_url=url,
            include_paths=["/en/organisation/department-of-justice/**", "/en/news/**", "/en/publication/**"],
            max_pages=max_pages,
            max_depth=2,
        ):
            page["nation"] = "ie"
            page["domain"] = "law"
            page["entity"] = "doj"
            yield page


@dlt.source(name="doj")
def doj_source(max_pages: int = 30):
    @dlt.resource(
        name="pages",
        write_disposition="merge",
        primary_key=["url"],
    )
    def pages():
        yield from _crawl_doj(max_pages=max_pages)

    return pages
