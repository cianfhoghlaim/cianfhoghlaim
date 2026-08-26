"""Tests for the DuckLake destination wiring.

Reference: openspec/changes/2026-08-23-uog-official-docs-and-nui-superset-v1/
            specs/cianfhoghlaim-ducklake-tertiary/spec.md
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Make `sruth_browser` importable in the standalone test env.
_REPO_ROOT = Path(__file__).resolve().parents[2]
_SRUTH_BROWSER_ROOT = _REPO_ROOT / "bonneagar" / "stacks" / "browser"
if (
    _SRUTH_BROWSER_ROOT.is_dir()
    and str(_SRUTH_BROWSER_ROOT) not in sys.path
):
    sys.path.insert(0, str(_SRUTH_BROWSER_ROOT))


def test_local_destination_default_path(monkeypatch):
    """GIVEN no `OOG_LOCAL_DUCKDB_PATH` is set (CI default)
    WHEN LocalDuckLakeDestination is constructed
    THEN the path is `/tmp/cianfhoghlaim.duckdb`."""
    from dlt_sources.lakehouse.destinations import LocalDuckLakeDestination

    monkeypatch.delenv("OOG_LOCAL_DUCKDB_PATH", raising=False)
    dest = LocalDuckLakeDestination()
    assert dest.path == Path("/tmp/cianfhoghlaim.duckdb")


def test_local_destination_override(monkeypatch):
    """GIVEN `OOG_LOCAL_DUCKDB_PATH=/tmp/alt.duckdb`
    WHEN LocalDuckLakeDestination is constructed
    THEN the path reflects the override."""
    from dlt_sources.lakehouse.destinations import LocalDuckLakeDestination

    monkeypatch.setenv("OOG_LOCAL_DUCKDB_PATH", "/tmp/alt.duckdb")
    dest = LocalDuckLakeDestination()
    assert str(dest.path).endswith("alt.duckdb")


def test_motherduck_destination_raises_on_placeholder(monkeypatch):
    """GIVEN a placeholder `MOTHERDUCK_TOKEN`
    WHEN MotherDuckLakeDestination.dlt_target() is invoked
    THEN LakehouseConnectionError is raised."""
    from dlt_sources.lakehouse.destinations import (
        LakehouseConnectionError,
        MotherDuckLakeDestination,
    )

    monkeypatch.setenv("MOTHERDUCK_TOKEN", "fixture-only")
    dest = MotherDuckLakeDestination()
    with pytest.raises(LakehouseConnectionError) as exc:
        dest.dlt_target()
    assert "MOTHERDUCK_TOKEN" in str(exc.value)


def test_motherduck_destination_raises_on_missing(monkeypatch):
    from dlt_sources.lakehouse.destinations import (
        LakehouseConnectionError,
        MotherDuckLakeDestination,
    )

    monkeypatch.delenv("MOTHERDUCK_TOKEN", raising=False)
    dest = MotherDuckLakeDestination()
    with pytest.raises(LakehouseConnectionError):
        dest.dlt_target()


def test_bonneagar_destination_raises_on_placeholder(monkeypatch):
    from dlt_sources.lakehouse.destinations import (
        BonneagarLakehouseDestination,
        LakehouseConnectionError,
    )

    monkeypatch.setenv("BONNEAGAR_LAKEHOUSE_URI", "ducklake:postgres:test")
    monkeypatch.setenv("DUCKLAKE_POSTGRES_PASSWORD", "fixture-only")
    dest = BonneagarLakehouseDestination()
    with pytest.raises(LakehouseConnectionError):
        dest.dlt_target()


def test_get_destination_rejects_unknown():
    from dlt_sources.lakehouse.destinations import get_destination

    with pytest.raises(ValueError):
        get_destination("not-a-destination")


def test_get_destination_local_returns_dlt_target(monkeypatch):
    """GIVEN destination='local'
    WHEN get_destination('local') is called
    THEN a dlt Destination is returned (we just check it doesn't raise)."""
    from dlt_sources.lakehouse.destinations import (
        DESTINATION_CHOICES,
        get_destination,
    )

    assert "local" in DESTINATION_CHOICES
    assert "motherduck" in DESTINATION_CHOICES
    assert "bonneagar" in DESTINATION_CHOICES
    target = get_destination("local")
    assert target is not None


def test_local_destination_dlt_target_returns_duckdb(monkeypatch, tmp_path):
    from dlt_sources.lakehouse.destinations import LocalDuckLakeDestination

    monkeypatch.setenv("OOG_LOCAL_DUCKDB_PATH", str(tmp_path / "test.duckdb"))
    dest = LocalDuckLakeDestination()
    target = dest.dlt_target()
    assert target is not None
