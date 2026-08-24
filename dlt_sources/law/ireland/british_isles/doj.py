"""
cianfhoghlaim.cianfhoghlaim.dlt.british_isles.ireland.law.doj — Department of Justice (Ireland).

Source: `https://www.gov.ie/en/organisation/department-of-justice/`
public service pages.
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
