"""
cianfhoghlaim.cianfhoghlaim.dlt.british_isles.northern_ireland.medicine — Northern Ireland medicine.

Phase 7 of the openspec change. nidirect Health & Social Care pages.
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

NIDIRECT_HEALTH_URLS = {
    "main": "https://www.nidirect.gov.uk/articles/health-and-social-care",
    "services": "https://www.nidirect.gov.uk/articles/find-your-local-doctor",
    "publications": "https://www.nidirect.gov.uk/publications/health-and-social-care",
}


def _crawl_nidirect(max_pages: int = 30) -> Iterator[dict[str, Any]]:
    for url_key, url in NIDIRECT_HEALTH_URLS.items():
        for page in _crawl_source(
            source_name=f"nidirect.{url_key}",
            base_url=url,
            include_paths=["/articles/health-and-social-care/*", "/publications/health*"],
            max_pages=max_pages,
            max_depth=2,
        ):
            page["nation"] = "ni"
            page["domain"] = "medicine"
            page["entity"] = "nidirect"
            yield page


@dlt.source(name="nidirect_medicine")
def nidirect_medicine_source(max_pages: int = 30):
    @dlt.resource(name="pages", write_disposition="merge", primary_key=["url"])
    def pages():
        yield from _crawl_nidirect(max_pages=max_pages)

    return pages
