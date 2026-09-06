"""PR0.2 — gov.wales WAF bypass (Requirement §gov.wales WAF bypass).

`gov.wales` is behind CloudFront + AWS WAF + a CAPTCHA challenge
(confirmed per `openspec/research/2026-06-28-browserbase-program-2/SHARED_DISCOVERY_LOG.md:492`).
Plain HTTP requests return 403 or a CAPTCHA page.

This module implements the canonical fallback chain:

1. Try `firecrawl_interact` with the `gov_wales_waf_bypass` profile
   (browser-aware, profile persists cookies for repeated calls).
2. On failure, fall back to the `hwb.gov.wales` mirror — Hwb is the
   Welsh Government's digital-learning platform that carries the
   same content with a different (less-protected) cache layer.
3. Log the WAF event to `stedding/waf_events/gov_wales.jsonl`.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any


_LOG = logging.getLogger(__name__)

MIRROR_HOSTS = {
    "gov.wales": "hwb.gov.wales",
    "llyw.cymru": "hwb.gov.wales",
    "www.wales.gov.uk": "hwb.gov.wales",
}

_WAF_EVENT_LOG = Path("stedding/waf_events/gov_wales.jsonl")


def is_gov_wales(url: str) -> bool:
    """True if `url` is hosted on the protected gov.wales / llyw.cymru family."""
    from urllib.parse import urlparse

    host = urlparse(url).hostname or ""
    return any(host == h or host.endswith("." + h) for h in MIRROR_HOSTS)


def mirror_for(url: str) -> str | None:
    """Return the Hwb mirror URL for a protected gov.wales URL, or None."""
    from urllib.parse import urlparse, urlunparse

    parsed = urlparse(url)
    for protected, mirror in MIRROR_HOSTS.items():
        if parsed.hostname == protected or (parsed.hostname or "").endswith("." + protected):
            return urlunparse(parsed._replace(netloc=mirror))
    return None


def log_waf_event(*, url: str, error: str, mirror_used: bool) -> None:
    """Append a WAF bypass event to the canonical log file."""
    _WAF_EVENT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with _WAF_EVENT_LOG.open("a", encoding="utf-8") as fh:
        fh.write(
            json.dumps(
                {
                    "url": url,
                    "error": error,
                    "mirror_used": mirror_used,
                }
            )
            + "\n"
        )


async def fetch(url: str, *, client: Any | None = None) -> dict[str, Any]:
    """Fetch a protected gov.wales URL via the fallback chain.

    PR0.3 will wire this up to the actual `FirecrawlMCPClient.interact`
    call. The current stub returns a placeholder so the import surface
    is stable.
    """
    if not is_gov_wales(url):
        raise ValueError(
            f"`fetch` only accepts gov.wales / llyw.cymru URLs — got {url!r}"
        )

    if client is None:
        _LOG.debug(
            "ciancheiltis:gov_wales_bypass no client provided; "
            "PR0.3 will resolve to FirecrawlMCPClient.interact"
        )

    mirror = mirror_for(url)
    log_waf_event(url=url, error="stub:no_client", mirror_used=mirror is not None)
    return {
        "url": url,
        "mirror_used": mirror,
        "fetched": False,
        "stub": True,
    }


__all__ = [
    "is_gov_wales",
    "mirror_for",
    "log_waf_event",
    "fetch",
    "MIRROR_HOSTS",
]
