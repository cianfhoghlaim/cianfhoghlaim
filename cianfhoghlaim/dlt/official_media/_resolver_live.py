"""oideachais.cianfhoghlaim.dlt.official_media._resolver_live — live network lookups.

Lazy-loaded by ``SourceResolver`` only when ``USE_LIVE_LOOKUPS=true``.
In test mode these are stubbed out by the test fixtures
``oideachais/dlt_sources/official_media/tests/_live_stubs.py``.

The 5 functions mirror the public protocol contracts:

  lookup_wikipedia(title)        -> {wikipedia_url, extract} | None
  lookup_companies_house(name)   -> {companies_house_id, company_name, company_status} | None
  lookup_cro(name)               -> {cro_number, company_name} | None
  lookup_mastodon(ig_username)   -> {handle, url}              | None  (from fediverse.resolve_mastodon)
  lookup_bluesky(ig_username)    -> {handle, did, url}         | None  (from fediverse.resolve_bluesky)
"""
from __future__ import annotations

from typing import Any

import structlog

logger = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# Wikipedia REST summary
# ---------------------------------------------------------------------------


async def lookup_wikipedia(title: str) -> dict[str, Any] | None:
    """Fetch the Wikipedia REST summary for ``title``.

    Endpoint: ``https://en.wikipedia.org/api/rest_v1/page/summary/{title}``.
    """
    try:
        import httpx
    except ImportError as exc:  # pragma: no cover
        logger.warning("httpx_missing", error=str(exc))
        return None
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                url, headers={"Accept": "application/json"}
            )
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            data = resp.json()
    except Exception as exc:
        logger.warning("wikipedia_failed", title=title, error=str(exc))
        return None
    return {
        "wikipedia_url": data.get("content_urls", {}).get("desktop", {}).get("page"),
        "extract": data.get("extract"),
    }


# ---------------------------------------------------------------------------
# Companies House (UK)
# ---------------------------------------------------------------------------


async def lookup_companies_house(name: str) -> dict[str, Any] | None:
    """Search Companies House for ``name`` and return the first match.

    Endpoint:
    ``https://api.company-information.service.gov.uk/search/companies?q={name}``
    Auth: HTTP Basic with ``COMPANIES_HOUSE_API_KEY`` as the username
    and an empty password.
    """
    import os

    api_key = os.environ.get("COMPANIES_HOUSE_API_KEY")
    if not api_key:
        logger.debug("companies_house_no_api_key")
        return None
    try:
        import httpx
    except ImportError as exc:  # pragma: no cover
        logger.warning("httpx_missing", error=str(exc))
        return None
    url = "https://api.company-information.service.gov.uk/search/companies"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                url,
                params={"q": name},
                auth=(api_key, ""),
            )
            resp.raise_for_status()
            data = resp.json()
    except Exception as exc:
        logger.warning("companies_house_failed", name=name, error=str(exc))
        return None
    items = data.get("items") or []
    if not items:
        return None
    first = items[0]
    return {
        "companies_house_id": first.get("company_number"),
        "company_name": first.get("title"),
        "company_status": first.get("company_status"),
    }


# ---------------------------------------------------------------------------
# CRO (Ireland) — public CRO search
# ---------------------------------------------------------------------------


async def lookup_cro(name: str) -> dict[str, Any] | None:
    """Search the Irish Companies Registration Office for ``name``.

    The CRO public search is a server-rendered HTML page; we do a
    minimal text scrape. Auth not required.
    """
    try:
        import httpx
    except ImportError as exc:  # pragma: no cover
        logger.warning("httpx_missing", error=str(exc))
        return None
    url = "https://search.cro.ie/company/search"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                url,
                params={"searchText": name, "searchType": "companyName"},
                headers={"Accept": "text/html"},
            )
            resp.raise_for_status()
    except Exception as exc:
        logger.warning("cro_failed", name=name, error=str(exc))
        return None
    # Minimal text extraction — the CRO search page embeds company
    # numbers and names in <a href="/company/{number}"> links.
    import re

    m = re.search(
        r'href="/company/(\d+)"[^>]*>([^<]+)<',
        resp.text,
    )
    if not m:
        return None
    return {
        "cro_number": m.group(1),
        "company_name": m.group(2).strip(),
    }


# ---------------------------------------------------------------------------
# Mastodon + Bluesky re-exports (the real implementations live in fediverse.py)
# ---------------------------------------------------------------------------


async def lookup_mastodon(ig_username: str) -> dict[str, Any] | None:
    """Look up the Mastodon handle for ``ig_username``.

    Heuristic: try the ``.social`` host first; if that fails, try
    ``masodon.club``. Real production code would scrape the bio or
    cross-reference the official website's webfinger record.
    """
    from cianfhoghlaim.dlt.official_media.fediverse import resolve_mastodon

    for host in ("mastodon.social", "masodon.club"):
        result = await resolve_mastodon(ig_username, host=host)
        if result is not None:
            return result
    return None


async def lookup_bluesky(ig_username: str) -> dict[str, Any] | None:
    """Look up the Bluesky handle for ``ig_username``."""
    from cianfhoghlaim.dlt.official_media.fediverse import resolve_bluesky

    return await resolve_bluesky(ig_username)
