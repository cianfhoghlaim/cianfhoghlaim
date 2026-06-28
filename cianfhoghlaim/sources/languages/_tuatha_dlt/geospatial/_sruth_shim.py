"""
tuatha/dlt_sources/geospatial/_sruth_shim.py — Stub for `sruth.shared.http`.

Per https://github.com/cianfhoghlaim/kings_college_galway/issues/18
(the `sruth` package is not installed in the tuatha venv, breaking
the dagster code-location), this module is a shim that
mimics the `sruth.shared.http` API surface used by the 3
geospatial DLT source modules:

    from sruth.shared.http import data_gov_ie_client, osi_client
    from sruth.shared.http import stats_wales_client
    from sruth.shared.http import scotland_stats_client

Each `_client()` returns an `HttpClient` stub. The stub supports
the context manager protocol (`with factory.create_client() as client:`)
so the source modules' use of the API works without modification.

Strategy: try the real `sruth.shared.http` first (in case a future
commit installs the sruth package); fall back to the local stubs.
This means:
  - Development: stubs run (no sruth dep required)
  - Production with sruth installed: real implementation runs
  - Tests: stubs run (no network access required)
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

_REAL_SRUTH_AVAILABLE = False
try:
    from sruth.shared.http import (  # type: ignore[import-not-found]
        data_gov_ie_client as _real_data_gov_ie_client,
    )
    from sruth.shared.http import (
        osi_client as _real_osi_client,
    )
    from sruth.shared.http import (
        scotland_stats_client as _real_scotland_stats_client,
    )
    from sruth.shared.http import (
        stats_wales_client as _real_stats_wales_client,
    )
    _REAL_SRUTH_AVAILABLE = True
except ImportError:
    pass


# ---------------------------------------------------------------------------
# Stub `HttpClient` — supports the context manager + .get / .post
# protocol that the geospatial DLT sources use.
# ---------------------------------------------------------------------------


class _StubHttpClient:
    """A stub HTTP client that returns empty / placeholder responses.

    Supports:
        with factory.create_client() as client:
            client.get("https://...")
            client.post("https://...", json=...)

    The stub's get/post return lists (matching the real `sruth`
    API where paginated endpoints yield lists of records).
    """

    def __enter__(self) -> _StubHttpClient:
        return self

    def __exit__(self, *args: Any) -> None:
        return None

    def get(self, url: str, **kwargs: Any) -> list[dict[str, Any]]:
        logger.debug("sruth_shim: stub GET %s", url)
        return []

    def post(self, url: str, **kwargs: Any) -> list[dict[str, Any]]:
        logger.debug("sruth_shim: stub POST %s", url)
        return []


class _StubHttpClientFactory:
    """Stub factory that yields `_StubHttpClient`s via `create_client()`."""

    def create_client(self) -> _StubHttpClient:
        return _StubHttpClient()


# ---------------------------------------------------------------------------
# Public API: data_gov_ie_client, osi_client, stats_wales_client,
# scotland_stats_client — each is a callable returning a factory.
# When the real sruth is installed, the callables are the real
# factories. Otherwise, the stub factory.
# ---------------------------------------------------------------------------


def data_gov_ie_client() -> _StubHttpClientFactory:
    if _REAL_SRUTH_AVAILABLE:
        return _real_data_gov_ie_client()  # type: ignore[no-any-return]
    return _StubHttpClientFactory()


def osi_client() -> _StubHttpClientFactory:
    if _REAL_SRUTH_AVAILABLE:
        return _real_osi_client()  # type: ignore[no-any-return]
    return _StubHttpClientFactory()


def stats_wales_client() -> _StubHttpClientFactory:
    if _REAL_SRUTH_AVAILABLE:
        return _real_stats_wales_client()  # type: ignore[no-any-return]
    return _StubHttpClientFactory()


def scotland_stats_client() -> _StubHttpClientFactory:
    if _REAL_SRUTH_AVAILABLE:
        return _real_scotland_stats_client()  # type: ignore[no-any-return]
    return _StubHttpClientFactory()


__all__ = [
    "data_gov_ie_client",
    "osi_client",
    "scotland_stats_client",
    "stats_wales_client",
]
