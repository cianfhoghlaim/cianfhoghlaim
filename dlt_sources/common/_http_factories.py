"""
cianfhoghlaim.cianfhoghlaim.dlt.common._http_factories — in-tree replacement
for the missing `shared.http` module.

Background
----------
The DLT source modules under `cianfhoghlaim/dlt_sources/{uk,celtic,geospatial,ireland,tearma}/`
import HTTP client factories from `shared.http` (e.g.
`from shared.http import dfe_explore_client`). The `shared` package is
not present in this monorepo (it was a planned sibling project that
was never implemented), so the imports fail at module load and
break the `cianfhoghlaim.dlt_sources.uk.__init__` chain (which eagerly
imports every UK sub-module).

This module re-implements the 13 `*_client()` factories as a tiny
`HttpClientFactory` that wraps `httpx.Client` with the right base URL,
default headers, and a configurable timeout. The public API matches
the contract that the call sites depend on:

    factory = <name>_client()               # a HttpClientFactory
    with factory.create_client() as client:    # yields httpx.Client
        response = client.get("/path", params={...})
        response.raise_for_status()

There is no behaviour change for any consumer — the existing
`from shared.http import dfe_explore_client` lines keep working
because `_shared.py` registers `shared.http` as a sys.modules alias
to this module.
"""
from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

import httpx
import structlog

logger = structlog.get_logger()


class HttpClientFactory:
    """Tiny in-tree replacement for the missing `shared.http.HttpClientFactory`.

    Public API:
        factory = HttpClientFactory(base_url=..., headers=..., timeout=...)
        with factory.create_client() as client:   # yields httpx.Client
            response = client.get(...)
    """

    def __init__(
        self,
        base_url: str,
        *,
        headers: dict[str, str] | None = None,
        timeout: float = 30.0,
        default_params: dict[str, Any] | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.headers = dict(headers or {})
        self.timeout = timeout
        self.default_params = dict(default_params or {})

    @contextmanager
    def create_client(self) -> Iterator[httpx.Client]:
        client = httpx.Client(
            base_url=self.base_url,
            headers=self.headers,
            timeout=self.timeout,
        )
        try:
            yield client
        finally:
            client.close()


def _factory(
    base_url: str,
    *,
    headers: dict[str, str] | None = None,
    timeout: float | None = None,
) -> HttpClientFactory:
    return HttpClientFactory(
        base_url=base_url,
        headers=headers,
        timeout=timeout or float(os.environ.get("OIDEACHAIS_HTTP_TIMEOUT", "30")),
    )


# ---------------------------------------------------------------------------
# Public factories — the names match `from shared.http import <name>`.
# ---------------------------------------------------------------------------


def tearma_client() -> HttpClientFactory:
    return _factory(
        "https://www.tearma.ie",
        headers={"User-Agent": "cianfhoghlaim-dlt/1.0", "Accept": "application/json"},
    )


def logainm_client() -> HttpClientFactory:
    return _factory(
        "https://www.logainm.ie",
        headers={"User-Agent": "cianfhoghlaim-dlt/1.0", "Accept": "application/json"},
    )


def ainm_client() -> HttpClientFactory:
    return _factory(
        "https://www.ainm.ie",
        headers={"User-Agent": "cianfhoghlaim-dlt/1.0", "Accept": "application/json"},
    )


def canuint_client() -> HttpClientFactory:
    return _factory("https://www.canuint.ie", timeout=60.0)


def duchas_client() -> HttpClientFactory:
    return _factory("https://www.duchas.ie", timeout=60.0)


def doras_client() -> HttpClientFactory:
    return _factory("https://www.doras.ie", timeout=60.0)


def met_office_climate_client() -> HttpClientFactory:
    return _factory("https://www.metoffice.gov.uk", timeout=60.0)


def met_office_datahub_client() -> HttpClientFactory:
    api_key = os.environ.get("MET_OFFICE_DATAHUB_API_KEY", "")
    return _factory(
        "https://data.hub.api.metoffice.gov.uk",
        headers={"apikey": api_key} if api_key else {},
        timeout=60.0,
    )


def arcgis_geohive_client() -> HttpClientFactory:
    return _factory("https://geohive.ie", timeout=60.0)


def cso_pxstat_client() -> HttpClientFactory:
    return _factory("https://ws.cso.ie", timeout=60.0)


def data_gov_ie_client() -> HttpClientFactory:
    return _factory("https://data.gov.ie", timeout=60.0)


def dfe_explore_client() -> HttpClientFactory:
    return _factory(
        "https://explore-education-statistics.service.gov.uk",
        headers={"Accept": "application/json"},
    )


def get_info_schools_client() -> HttpClientFactory:
    return _factory(
        "https://get-information-schools.service.gov.uk",
        headers={"Accept": "text/csv,application/json"},
    )


def nisra_client() -> HttpClientFactory:
    return _factory(
        "https://data.nisra.gov.uk",
        headers={"Accept": "application/json"},
    )


def stats_wales_odata_client() -> HttpClientFactory:
    return _factory("https://statswales.gov.wales", timeout=60.0)


__all__ = [
    "HttpClientFactory",
    "ainm_client",
    "arcgis_geohive_client",
    "canuint_client",
    "cso_pxstat_client",
    "data_gov_ie_client",
    "dfe_explore_client",
    "doras_client",
    "duchas_client",
    "get_info_schools_client",
    "logainm_client",
    "met_office_climate_client",
    "met_office_datahub_client",
    "nisra_client",
    "stats_wales_odata_client",
    "tearma_client",
]
