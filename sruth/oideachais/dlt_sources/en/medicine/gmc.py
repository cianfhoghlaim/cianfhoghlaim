"""
oideachais.dlt_sources.en.medicine.gmc — General Medical Council (UK register).

Public search endpoint at `https://www.gmc-uk.org/registration-and-licensing/medical-register`.
Per-practitioner lookups behind authenticated API are reserved for
the future `domain-source-registry/v2` change.
"""
from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import dlt

from ....ireland.curriculum_source import _crawl_source  # type: ignore[import-not-found]

GMC_URLS = {
    "register": "https://www.gmc-uk.org/registration-and-licensing/the-medical-register",
    "guidance": "https://www.gmc-uk.org/professional-standards",
    "news": "https://www.gmc-uk.org/news",
}


def _crawl_gmc(max_pages: int = 30) -> Iterator[dict[str, Any]]:
    for url_key, url in GMC_URLS.items():
        for page in _crawl_source(
            source_name=f"gmc.{url_key}",
            base_url=url,
            include_paths=["/registration-and-licensing/*", "/professional-standards/*", "/news/*"],
            max_pages=max_pages,
            max_depth=2,
        ):
            page["nation"] = "en"
            page["domain"] = "medicine"
            page["entity"] = "gmc"
            yield page


@dlt.source(name="gmc")
def gmc_source(max_pages: int = 30):
    @dlt.resource(name="pages", write_disposition="merge", primary_key=["url"])
    def pages():
        yield from _crawl_gmc(max_pages=max_pages)

    return pages
