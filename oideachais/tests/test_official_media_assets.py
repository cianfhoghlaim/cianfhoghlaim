"""Smoke tests for the official-media Dagster assets.

The 5 assets (``extract``, ``resolve_sources``, ``embed``, ``cognify``,
``hmgcc_co_creation``) are tested by invoking them directly with a
``build_asset_context()`` — this exercises the asset body without
requiring a running Dagster instance. All assets should materialise
in offline mode (``USE_LIVE_LOOKUPS`` unset) and return a well-formed
``MaterializeResult``.
"""
from __future__ import annotations

import os

import pytest
from dagster import build_asset_context

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def asset_context():
    """Build a fresh AssetExecutionContext for each test."""
    return build_asset_context()


@pytest.fixture
def export_dir(monkeypatch: pytest.MonkeyPatch, tmp_path):
    """Configure a synthetic Instagram export directory."""
    (tmp_path / "connections" / "followers_and_following").mkdir(parents=True)
    monkeypatch.setenv("OIDEACHAIS_IG_EXPORT_DIR", str(tmp_path))
    return tmp_path


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_official_media_extract_materialises_without_export_dir(
    asset_context,
) -> None:
    """When OIDEACHAIS_IG_EXPORT_DIR is unset, the asset materialises
    with the offline-stub metadata (no exception)."""
    if "OIDEACHAIS_IG_EXPORT_DIR" in os.environ:
        del os.environ["OIDEACHAIS_IG_EXPORT_DIR"]
    from dagster_defs.assets.official_media.extract import official_media_extract

    result = official_media_extract(asset_context)
    assert result.metadata["backend"] == "stub_no_export_dir"
    assert result.metadata["candidates_written"] == 0


def test_official_media_extract_materialises_with_empty_export(
    asset_context, export_dir
) -> None:
    """When the export directory is empty, the asset materialises
    with 0 candidates."""
    from dagster_defs.assets.official_media.extract import official_media_extract

    result = official_media_extract(asset_context)
    assert result.metadata["backend"] == "ducklake"
    assert result.metadata["candidates_written"] == 0
    assert result.metadata["profiles_parsed"] == 0


def test_official_media_resolve_sources_materialises(asset_context) -> None:
    from dagster_defs.assets.official_media.resolve_sources import (
        official_media_resolve_sources,
    )

    result = official_media_resolve_sources(asset_context)
    assert result.metadata["sources_resolved"] == 0


def test_official_media_embed_materialises(asset_context) -> None:
    from dagster_defs.assets.official_media.embed import official_media_embed

    result = official_media_embed(asset_context)
    assert result.metadata["model"] == "BAAI/bge-m3"
    assert result.metadata["vector_dim"] == 1024


def test_official_media_cognify_materialises(asset_context) -> None:
    from dagster_defs.assets.official_media.cognify import official_media_cognify

    result = official_media_cognify(asset_context)
    assert result.metadata["cognee_dataset"] == "oideachais_official_media"
    assert "ig_profile->official_website" in result.metadata["edge_types"]


def test_official_media_hmgcc_co_creation_materialises(asset_context) -> None:
    from dagster_defs.assets.official_media.hmgcc_co_creation import (
        official_media_hmgcc_co_creation,
    )

    result = official_media_hmgcc_co_creation(asset_context)
    assert (
        result.metadata["url"]
        == "https://www.hmgcc.gov.uk/co-creation/"
    )
    assert result.metadata["rolling_window_weeks"] == 12
