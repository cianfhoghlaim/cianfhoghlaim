"""Tests for ``dlt_sources.official_media.fediverse``.

Asserts the pure (no-Dagster) Mastodon + Bluesky resolution library
using mocked HTTP responses. The pattern is to define a minimal fake
``httpx.AsyncClient`` class once and parameterise it per test.
"""
from __future__ import annotations

from typing import Any
from unittest.mock import patch

import pytest

from dlt_sources.official_media.fediverse import (
    resolve_bluesky,
    resolve_mastodon,
)

# ---------------------------------------------------------------------------
# Fake httpx.AsyncClient
# ---------------------------------------------------------------------------


def _make_fake_client(
    *,
    status_code: int = 200,
    json_payload: dict[str, Any] | None = None,
    raise_on_get: BaseException | None = None,
) -> type:
    """Build a fake ``httpx.AsyncClient`` class.

    Plays the role of an async context manager whose ``.get`` returns
    a response-like object. For network-failure tests, ``.get`` raises
    the given exception.
    """

    class _FakeResponse:
        def __init__(self) -> None:
            self.status_code = status_code
            self._json = json_payload or {}

        def raise_for_status(self) -> None:
            if 400 <= self.status_code < 600:
                raise RuntimeError(f"HTTP {self.status_code}")

        def json(self) -> dict[str, Any]:
            return self._json

    class _FakeAsyncClient:
        def __init__(self, *a: Any, **kw: Any) -> None:
            pass

        async def __aenter__(self) -> _FakeAsyncClient:
            return self

        async def __aexit__(self, *a: Any) -> bool:
            return False

        async def get(self, *a: Any, **kw: Any) -> Any:
            if raise_on_get is not None:
                raise raise_on_get
            return _FakeResponse()

    return _FakeAsyncClient


# ---------------------------------------------------------------------------
# Mastodon — success
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_resolve_mastodon_success() -> None:
    """A mocked webfinger response yields the canonical self link."""
    payload = {
        "subject": "acct:metpolice@masodon.club",
        "links": [
            {
                "rel": "self",
                "type": "application/activity+json",
                "href": "https://masodon.club/users/metpolice",
            }
        ],
    }
    fake = _make_fake_client(json_payload=payload)
    with patch("httpx.AsyncClient", fake):
        result = await resolve_mastodon("metpolice", host="masodon.club")

    assert result is not None
    assert result["platform"] == "mastodon"
    assert result["handle"] == "@metpolice@masodon.club"
    assert result["url"] == "https://masodon.club/users/metpolice"
    assert "resolved_at" in result


@pytest.mark.asyncio
async def test_resolve_mastodon_falls_back_when_no_self_link() -> None:
    """If the webfinger response has no ``rel=self`` link, the
    resolver reconstructs the URL from the host."""
    payload = {"links": []}
    fake = _make_fake_client(json_payload=payload)
    with patch("httpx.AsyncClient", fake):
        result = await resolve_mastodon("metpolice", host="masodon.club")

    assert result is not None
    assert result["url"] == "https://masodon.club/@metpolice"


# ---------------------------------------------------------------------------
# Mastodon — network failure
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_resolve_mastodon_returns_none_on_connect_error() -> None:
    fake = _make_fake_client(raise_on_get=ConnectionError("DNS failure"))
    with patch("httpx.AsyncClient", fake):
        result = await resolve_mastodon("metpolice", host="deadhost.club")
    assert result is None


# ---------------------------------------------------------------------------
# Bluesky — success
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_resolve_bluesky_success() -> None:
    payload = {
        "actors": [
            {
                "handle": "metpoliceuk.bsky.social",
                "did": "did:plc:abc123",
            }
        ]
    }
    fake = _make_fake_client(json_payload=payload)
    with patch("httpx.AsyncClient", fake):
        result = await resolve_bluesky("metpoliceuk")

    assert result is not None
    assert result["platform"] == "bluesky"
    assert result["handle"] == "metpoliceuk.bsky.social"
    assert result["did"] == "did:plc:abc123"
    assert result["url"] == "https://bsky.app/profile/metpoliceuk.bsky.social"


@pytest.mark.asyncio
async def test_resolve_bluesky_returns_none_when_no_actors() -> None:
    payload = {"actors": []}
    fake = _make_fake_client(json_payload=payload)
    with patch("httpx.AsyncClient", fake):
        result = await resolve_bluesky("nobody_xyz")
    assert result is None
