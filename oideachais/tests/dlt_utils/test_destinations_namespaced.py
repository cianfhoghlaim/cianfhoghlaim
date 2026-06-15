"""Tests for `dlt_utils.destinations.with_namespace()`.

Phase 2.3 of the lateralise change: the destinations factory is
parameterised by `namespace`. Sibling quadrants (`tuatha`,
`croilar`) re-export a namespaced view through their shim.

These tests assert:
  1. The default namespace is `"oideachais"`.
  2. `with_namespace("tuath")` produces a `_NamespacedDestinations`
     whose helpers all carry the right namespace.
  3. The shim's `re_export_into(globals())` injects the correct
     symbols into a module's namespace.
  4. The pre-existing `NAMESPACE` constant still resolves (back-
     compat for any historical imports).
  5. The pipeline helpers actually pick up the right namespace
     (the S3 prefix and Postgres DB name).
"""
from __future__ import annotations

import os

import pytest

from dlt_utils.destinations import (
    DEFAULT_NAMESPACE,
    NAMESPACE,
    _build_local_destination,
    _build_production_destination,
    create_pipeline,
    get_dlt_destination,
    get_duckdb_fallback_destination,
    with_namespace,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
def test_default_namespace_is_oideachais() -> None:
    assert DEFAULT_NAMESPACE == "oideachais"


def test_legacy_namespace_alias_still_resolves() -> None:
    """The pre-Phase-2.3 constant `NAMESPACE` must still be defined
    and equal to the default — historical imports use it."""
    assert NAMESPACE == DEFAULT_NAMESPACE == "oideachais"


# ---------------------------------------------------------------------------
# Parameterised helpers
# ---------------------------------------------------------------------------
def test_build_local_destination_uses_namespace_in_s3_prefix() -> None:
    """The local DuckLake destination's S3 prefix must include the
    namespace. We don't call the real Garage endpoint; we inspect
    the generated credentials via the dlt Destination object."""
    dest = _build_local_destination("tuath")
    creds = dest.config_params["credentials"]
    assert creds.ducklake_name == "tuath"
    # bucket_url should be s3://ducklake/tuath/
    storage = creds.storage
    assert "tuath" in storage["bucket_url"]
    # catalog is a ConnectionStringCredentials object; check via to_url()
    assert "ducklake_tuath" in creds.catalog.to_url()


def test_build_local_destination_default_uses_oideachais() -> None:
    dest = _build_local_destination("oideachais")
    creds = dest.config_params["credentials"]
    assert creds.ducklake_name == "oideachais"
    assert "oideachais" in creds.storage["bucket_url"]


# ---------------------------------------------------------------------------
# with_namespace
# ---------------------------------------------------------------------------
def test_with_namespace_returns_namespaced_view() -> None:
    ns = with_namespace("croilar")
    assert ns.NAMESPACE == "croilar"


def test_with_namespace_re_exports_into_globals() -> None:
    """`re_export_into({...})` injects NAMESPACE + the 3 helpers."""
    fake_globals: dict = {}
    ns = with_namespace("tuath")
    ns.re_export_into(fake_globals)
    assert fake_globals["NAMESPACE"] == "tuath"
    assert callable(fake_globals["get_dlt_destination"])
    assert callable(fake_globals["get_duckdb_fallback_destination"])
    assert callable(fake_globals["create_pipeline"])


def test_namespaced_create_pipeline_does_not_crash() -> None:
    """The namespaced `create_pipeline` must produce a dlt.Pipeline
    without raising (we use use_ducklake=False so no real DuckLake
    endpoint is touched)."""
    ns = with_namespace("tuath")
    p = ns.create_pipeline(
        "test_pipeline", "test_data", use_ducklake=False
    )
    assert p is not None
    assert p.dataset_name == "test_data"


def test_namespaced_get_duckdb_fallback_uses_namespace_path() -> None:
    """The DuckDB-fallback path defaults to `./data/{namespace}.duckdb`."""
    ns = with_namespace("croilar")
    dest = ns.get_duckdb_fallback_destination()
    # The credentials are a path string at dest.config_params
    creds = dest.config_params["credentials"]
    assert "croilar" in str(creds)


# ---------------------------------------------------------------------------
# End-to-end: get_dlt_destination
# ---------------------------------------------------------------------------
def test_get_dlt_destination_explicit_namespace(monkeypatch) -> None:
    """`get_dlt_destination(namespace='tuath')` must produce a
    destination whose credentials carry the namespace."""
    monkeypatch.setenv("USE_DUCKLAKE", "true")
    monkeypatch.setenv("DLT_ENVIRONMENT", "local")
    dest = get_dlt_destination(namespace="tuath")
    creds = dest.config_params["credentials"]
    assert creds.ducklake_name == "tuath"


def test_get_dlt_destination_fallback(monkeypatch) -> None:
    """`get_dlt_destination(use_ducklake=False)` returns a DuckDB
    destination, not a DuckLake one."""
    dest = get_dlt_destination(use_ducklake=False, namespace="oideachais")
    assert "duckdb" in str(type(dest)).lower()
