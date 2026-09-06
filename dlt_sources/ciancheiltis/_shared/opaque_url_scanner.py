"""PR0.2 — opaque-URL scanner (Requirement §opaque-URL scanner).

Discovers numeric/slug-only URLs that hide their language pair — the
canonical pattern is `legislation.gov.uk/uksi/2007/1484/made` (UK
Statutory Instrument 2007 No. 1484) and `/wsi/2007/2044/made` (Welsh
SI 2007 No. 2044). The URL gives no indication that the body is
Welsh-language content.
"""
from __future__ import annotations

import asyncio
import re
from typing import Any
from urllib.parse import urlparse


_NUMERIC_PATH_RE = re.compile(
    r"^/(?P<topic>[a-z]+)/(?P<year>\d{4})/(?P<number>\d{1,5})(?:/(?P<suffix>[a-z/]+))?$",
    re.IGNORECASE,
)


def classify_url(url: str) -> dict[str, Any]:
    """Return `{kind, ...}` for a single URL — flag opaque numeric ones."""
    parsed = urlparse(url)
    match = _NUMERIC_PATH_RE.match(parsed.path)
    if not match:
        return {"url": url, "kind": "named_slug", "opaque": False}
    return {
        "url": url,
        "kind": "numeric",
        "opaque": True,
        "topic": match.group("topic").lower(),
        "year": int(match.group("year")),
        "number": int(match.group("number")),
        "suffix": (match.group("suffix") or "").lower(),
    }


def filter_opaque(urls: list[str]) -> list[dict[str, Any]]:
    """Return only the opaque numeric URLs from `urls`."""
    return [classify_url(u) for u in urls if classify_url(u)["opaque"]]


async def scan_legislation_gov_uk(
    *,
    base_url: str = "https://www.legislation.gov.uk",
    topic: str = "uksi",
    years_back: int = 25,
    max_pages: int = 200,
) -> list[str]:
    """Discover opaque-URL legislation pages for a topic + year range.

    Use the Firecrawl `firecrawl_map` tool to seed the URL inventory
    for a topic (uksi / wsi / asp / ssi / sdsi / anaw / nisi / nid /
    nia / mwa / ukpga) on legislation.gov.uk.

    Note: This stub returns an empty list. PR0.3 will replace the body
    with a Firecrawl `client.map(base_url + "/<topic>")` call.
    """
    del base_url, topic, years_back, max_pages  # wired in PR0.3
    return []


__all__ = [
    "classify_url",
    "filter_opaque",
    "scan_legislation_gov_uk",
]
