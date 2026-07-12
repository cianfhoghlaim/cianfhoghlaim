"""
oideachais.cianfhoghlaim.dlt.british_isles.england.medicine.nice — NICE clinical guidelines.

Source: `https://www.nice.org.uk/guidance` (publicly browseable,
bulk-download behind auth).
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

NICE_URLS = {
    "guidance_published": "https://www.nice.org.uk/guidance/published",
    "guidance_in_development": "https://www.nice.org.uk/guidance/in-development",
    "about": "https://www.nice.org.uk/about",
}


def _crawl_nice(max_pages: int = 30) -> Iterator[dict[str, Any]]:
    for url_key, url in NICE_URLS.items():
        for page in _crawl_source(
            source_name=f"nice.{url_key}",
            base_url=url,
            include_paths=["/guidance/published/*", "/guidance/in-development/*", "/about/*"],
            max_pages=max_pages,
            max_depth=2,
        ):
            page["nation"] = "en"
            page["domain"] = "medicine"
            page["entity"] = "nice"
            yield page


@dlt.source(name="nice")
def nice_source(max_pages: int = 30):
    @dlt.resource(name="guidelines_pages", write_disposition="merge", primary_key=["url"])
    def pages():
        yield from _crawl_nice(max_pages=max_pages)

    return pages
