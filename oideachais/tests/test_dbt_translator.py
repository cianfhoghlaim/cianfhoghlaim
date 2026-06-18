"""Tests for `oideachais.dagster_defs.dbt_translator.CelticDagsterDbtTranslator`.

The 2 `celtic-data-engineering-pipeline` scenarios that exercise the dbt
translator are validated here:

- "dbt assets inherit the prepared group" → see `test_dbt_assets_inherit_prepared_group`
- (The translator is also exercised by the 3 dbt models in
  `oideachais/dbt_project/models/` which the scenario describes.)
"""

from __future__ import annotations

from dagster import AssetKey

from oideachais.dagster_defs.dbt_translator import CelticDagsterDbtTranslator


def _make_props(name: str) -> dict:
    """Build the minimal dbt_resource_props dict the translator reads."""
    return {
        "name": name,
        "resource_type": "model",
        "schema": "main",
        "database": "oideachais_dbt",
        "meta": {},
        "tags": [],
    }


def test_get_asset_key_flattens_to_single_segment() -> None:
    """The translator returns AssetKey(["<name>"]), NOT the dbt 3-segment default."""
    key = CelticDagsterDbtTranslator.get_asset_key(_make_props("weekly_downloads"))
    assert key == AssetKey(["weekly_downloads"])
    assert len(key.path) == 1


def test_get_asset_key_does_not_leak_project_name() -> None:
    """Regression: default translator returns AssetKey([project, type, name]) — we do NOT."""
    key = CelticDagsterDbtTranslator.get_asset_key(_make_props("language_distribution"))
    # The default would be AssetKey(["oideachais_dbt", "model", "language_distribution"])
    # (3 segments). We must NOT include "oideachais_dbt" or "model".
    assert "oideachais_dbt" not in key.path
    assert "model" not in key.path


def test_get_group_name_pins_prepared() -> None:
    """Every dbt asset lands in the `prepared` group."""
    translator = CelticDagsterDbtTranslator()
    for name in ("weekly_downloads", "language_distribution", "ocr_confidence_by_model"):
        assert translator.get_group_name(_make_props(name)) == "prepared"


def test_translator_handles_all_three_oideachais_models() -> None:
    """Regression: the 3 declared models in oideachais/dbt_project/models/ all translate."""
    translator = CelticDagsterDbtTranslator()
    expected = {
        "weekly_downloads": AssetKey(["weekly_downloads"]),
        "language_distribution": AssetKey(["language_distribution"]),
        "ocr_confidence_by_model": AssetKey(["ocr_confidence_by_model"]),
    }
    for name, want in expected.items():
        got = CelticDagsterDbtTranslator.get_asset_key(_make_props(name))
        assert got == want
        assert translator.get_group_name(_make_props(name)) == "prepared"


def test_source_resources_get_dbt_source_prefix() -> None:
    """Source resources (dlt-ingested upstream tables) get a `dbt_source` prefix.

    Regression: when the source `leabharlann.books` and the seed
    `books` had the same key (`['books']`), Dagster raised
    `DagsterInvalidDefinitionError: The following dbt resources are
    configured with identical Dagster asset keys`. The fix: prefix
    sources with `dbt_source` so they don't collide with seeds/models.
    """
    props = _make_props("books")
    props["resource_type"] = "source"
    # The `name` for a source includes the schema: "leabharlann.books"
    props["name"] = "leabharlann.books"
    key = CelticDagsterDbtTranslator.get_asset_key(props)
    assert key == AssetKey(["dbt_source", "books"])


def test_source_resources_go_to_external_group() -> None:
    """Source resources go to the `external` group, not `prepared`."""
    translator = CelticDagsterDbtTranslator()
    props = _make_props("books")
    props["resource_type"] = "source"
    props["name"] = "leabharlann.books"
    assert translator.get_group_name(props) == "external"
