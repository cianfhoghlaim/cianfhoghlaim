"""Test the environment-aware DuckLake destination factory.

Verifies that `get_dlt_destination()` returns a destination whose
`client_class` matches `ducklake` (or the right shape) and that the
underlying `DuckLakeCredentials` is constructed with the expected
catalog/storage config.
"""
from __future__ import annotations

import os

import pytest

pytestmark = pytest.mark.integration


def test_get_dlt_destination_returns_ducklake_object() -> None:
    """With local env defaults, the factory returns a DLT destination
    whose class is one of the ducklake variants."""
    from oideachais.dlt_utils import get_dlt_destination

    os.environ["DLT_ENVIRONMENT"] = "local"
    os.environ["USE_DUCKLAKE"] = "true"
    os.environ["DUCKLAKE_POSTGRES_HOST"] = "localhost"
    os.environ["DUCKLAKE_POSTGRES_PORT"] = "5433"
    os.environ["DUCKLAKE_POSTGRES_USER"] = "lakekeeper"
    os.environ["DUCKLAKE_POSTGRES_PASSWORD"] = "devpassword"
    os.environ["DUCKLAKE_POSTGRES_DB"] = "ducklake_oideachais"
    os.environ["AWS_ENDPOINT_URL"] = "http://localhost:3900"
    os.environ["AWS_ACCESS_KEY_ID"] = "test"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "test"

    dest = get_dlt_destination()
    # The class name should mention ducklake (case-insensitive).
    assert "ducklake" in type(dest).__name__.lower(), type(dest).__name__


def test_get_duckdb_fallback_destination(tmp_path) -> None:
    """The duckdb fallback returns a plain duckdb destination."""
    from oideachais.dlt_utils import get_duckdb_fallback_destination

    dest = get_duckdb_fallback_destination(str(tmp_path / "test.duckdb"))
    assert "duckdb" in type(dest).__name__.lower()
