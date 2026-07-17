"""
cianfhoghlaim.cianfhoghlaim.dlt.british_isles.ireland.medicine.doh — Department of Health (Ireland).

Source: `https://www.gov.ie/en/organisation/department-of-health/`
public service pages. Firecrawl crawl over the gov.ie sub-tree.
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
