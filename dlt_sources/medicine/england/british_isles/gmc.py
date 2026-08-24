"""
cianfhoghlaim.cianfhoghlaim.dlt.british_isles.england.medicine.gmc — General Medical Council (UK register).

Public search endpoint at `https://www.gmc-uk.org/registration-and-licensing/medical-register`.
Per-practitioner lookups behind authenticated API are reserved for
the future `domain-source-registry/v2` change.
"""
from __future__ import annotations
import dlt


from collections.abc import Iterator
from typing import Any

import dlt_sources

from dlt_sources.common.site_crawler import crawl_site

GMC_RECOVERY_STRATEGY = "stealth"
"""Phase 1 fix: gmc-uk.org returns 403 to plain HTTP. Routes via the
Firecrawl stealth proxy with a 10s wait_for; falls back to the
Wayback Machine if stealth also 403s.

The ``fetch`` / ``crawl_site`` calls already pick up this strategy
via the new :mod:`cianfhoghlaim.dlt_sources.common.endpoint_recovery`
helper — see the ``endpoint_recovery_sink`` L2 asset for the
operational probe that detects regressions."""

def _crawl_source(*args, **kwargs):
    # The legacy _crawl_source took (source_name, base_url, ...) — source_name
    # was used only for logging in the legacy helper. The new crawl_site
    # primitive has no source_name, so we drop it if present.
    if args and isinstance(args[0], str) and args[0] == kwargs.get("source_name"):
        args = args[1:]
    kwargs.pop("source_name", None)
    for page in crawl_site(*args, **kwargs):
        yield page.to_dict()

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
