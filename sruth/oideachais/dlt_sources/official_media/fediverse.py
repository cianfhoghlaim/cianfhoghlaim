"""oideachais.dlt_sources.official_media.fediverse — pure Mastodon + Bluesky library.

No Dagster dependency. Used by ``SourceResolver`` and reusable by the
side-loadable-app phase.

The public API:

    resolve_mastodon(username, host, *, rate_limit_per_sec=1) -> dict | None
    resolve_bluesky(query, *, rate_limit_per_sec=1) -> dict | None

Both return ``None`` on any network failure (logged, not raised).
"""
from __future__ import annotations

import asyncio
import time
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# Rate limiter (1 req/sec per host by default)
# ---------------------------------------------------------------------------


class _RateLimiter:
    def __init__(self, per_sec: float = 1.0) -> None:
        self._min_interval = 1.0 / per_sec
        self._last: dict[str, float] = {}

    async def wait(self, key: str) -> None:
        last = self._last.get(key, 0.0)
        elapsed = time.monotonic() - last
        if elapsed < self._min_interval:
            await asyncio.sleep(self._min_interval - elapsed)
        self._last[key] = time.monotonic()


_mastodon_limiter = _RateLimiter(per_sec=1.0)
_bluesky_limiter = _RateLimiter(per_sec=1.0)


# ---------------------------------------------------------------------------
# Mastodon — webfinger
# ---------------------------------------------------------------------------


async def resolve_mastodon(
    username: str,
    host: str,
    *,
    rate_limit_per_sec: float = 1.0,
) -> dict[str, Any] | None:
    """Resolve a Mastodon handle ``@user@host`` to its canonical URL.

    Uses the public WebFinger protocol at
    ``https://host/.well-known/webfinger?resource=acct:user@host``.
    """
    resource = f"acct:{username}@{host}"
    url = f"https://{host}/.well-known/webfinger"
    params = {"resource": resource}

    await _mastodon_limiter.wait(host)
    try:
        import httpx  # local import — keeps this module importable in CI
    except ImportError as exc:  # pragma: no cover
        logger.warning("httpx_missing", error=str(exc))
        return None

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params=params, headers={"Accept": "application/jrd+json"})
            resp.raise_for_status()
            data = resp.json()
    except Exception as exc:  # noqa: BLE001
        logger.warning("webfinger_failed", host=host, username=username, error=str(exc))
        return None

    for link in data.get("links", []):
        if link.get("rel") == "self" and "activity+json" in (link.get("type") or ""):
            return {
                "platform": "mastodon",
                "handle": f"@{username}@{host}",
                "url": link.get("href"),
                "resolved_at": _now_iso(),
            }
    # Fallback: try to reconstruct the URL from the host
    return {
        "platform": "mastodon",
        "handle": f"@{username}@{host}",
        "url": f"https://{host}/@{username}",
        "resolved_at": _now_iso(),
    }


# ---------------------------------------------------------------------------
# Bluesky — public xrpc
# ---------------------------------------------------------------------------


async def resolve_bluesky(
    query: str,
    *,
    rate_limit_per_sec: float = 1.0,
) -> dict[str, Any] | None:
    """Resolve a Bluesky handle via the public
    ``public.api.bsky.app/xrpc/app.bsky.actor.searchActors?q=...`` API.
    """
    await _bluesky_limiter.wait("bsky_app")
    try:
        import httpx
    except ImportError as exc:  # pragma: no cover
        logger.warning("httpx_missing", error=str(exc))
        return None

    url = "https://public.api.bsky.app/xrpc/app.bsky.actor.searchActors"
    params = {"q": query, "limit": 5}
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
    except Exception as exc:  # noqa: BLE001
        logger.warning("bsky_xrpc_failed", query=query, error=str(exc))
        return None

    actors = data.get("actors") or []
    if not actors:
        return None
    actor = actors[0]
    handle = actor.get("handle")
    did = actor.get("did")
    if not handle:
        return None
    return {
        "platform": "bluesky",
        "handle": handle,
        "url": f"https://bsky.app/profile/{handle}",
        "did": did,
        "resolved_at": _now_iso(),
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _now_iso() -> str:
    from datetime import UTC, datetime

    return datetime.now(UTC).isoformat()
