"""
oideachais.dlt_sources.ie.law.lawreform — Law Reform Commission (Ireland).

Source: `https://www.lawreform.ie` — reports and consultation
papers on Irish statute reform.
"""
from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import dlt

from ....ireland.curriculum_source import _crawl_source  # type: ignore[import-not-found]

LAWREFORM_URLS = {
    "homepage": "https://www.lawreform.ie",
    "reports": "https://www.lawreform.ie/reports-and-publications/",
    "consultation": "https://www.lawreform.ie/consultation-papers/",
}


def _crawl_lawreform(max_pages: int = 30) -> Iterator[dict[str, Any]]:
    for url_key, url in LAWREFORM_URLS.items():
        for page in _crawl_source(
            source_name=f"lawreform.{url_key}",
            base_url=url,
            include_paths=["/reports-and-publications/*", "/consultation-papers/*", "/about-us/*"],
            max_pages=max_pages,
            max_depth=2,
        ):
            page["nation"] = "ie"
            page["domain"] = "law"
            page["entity"] = "lawreform"
            yield page


@dlt.source(name="lawreform")
def lawreform_source(max_pages: int = 30):
    @dlt.resource(
        name="pages",
        write_disposition="merge",
        primary_key=["url"],
    )
    def pages():
        yield from _crawl_lawreform(max_pages=max_pages)

    return pages
