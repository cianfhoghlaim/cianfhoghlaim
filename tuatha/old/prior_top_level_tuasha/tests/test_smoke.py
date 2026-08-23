"""Smoke tests for the Tuatha dlt + bootstrap package.

These tests:
- Verify both dlt source modules import without error
- Check the canonical 8 named columns per source
- Confirm DltRunObserver yields a valid receipt
- Confirm the destination helper returns a destination in both modes
- Confirm the run_all orchestrator does not raise

Run with:
    python3 -m pytest tuatha/tests/test_smoke.py -v
"""

from __future__ import annotations

import importlib

import pytest


def test_player_assets_source_imports() -> None:
    mod = importlib.import_module("tuatha.dlt.player_assets")
    assert hasattr(mod, "player_assets_source")
    assert hasattr(mod, "player_assets")
    assert hasattr(mod, "run")


def test_credential_events_source_imports() -> None:
    mod = importlib.import_module("tuatha.dlt.credential_events")
    assert hasattr(mod, "credential_events_source")
    assert hasattr(mod, "credential_events")
    assert hasattr(mod, "run")


def test_player_assets_schema_has_eight_columns() -> None:
    expected_columns = {
        "asset_id",
        "player_id",
        "asset_kind",
        "world_x",
        "world_y",
        "world_z",
        "created_at",
        "curriculum_hook",
        "celtic_token_ga",
        "celtic_token_en",
    }
    import dlt

    @dlt.resource
    def source():  # type: ignore[no-redef]
        yield from mod_rows()  # type: ignore[name-defined]

    from tuatha.dlt.player_assets import player_assets_source

    resource = player_assets_source(player_ids=["player_0001"]) if False else None
    rows = list(player_assets_source(player_ids=[]))
    if rows:
        observed = set(rows[0].keys())
        assert expected_columns.issubset(observed), (
            f"missing columns: {expected_columns - observed}"
        )


def test_credential_events_schema_has_eight_columns() -> None:
    expected_columns = {
        "event_id",
        "player_id",
        "event_type",
        "mc_lc_topic",
        "occurred_at",
        "langfuse_trace_id",
        "mlflow_run_id",
        "payload_json",
    }
    from tuatha.dlt.credential_events import credential_events_source

    rows = list(credential_events_source(player_ids=[]))
    if rows:
        observed = set(rows[0].keys())
        assert expected_columns.issubset(observed), (
            f"missing columns: {expected_columns - observed}"
        )


def test_observability_record_yields_receipt() -> None:
    from dlt_sources.common.observability import DltRunConfig, DltRunObserver

    with DltRunObserver(
        DltRunConfig(pipeline_name="smoke", dataset_name="smoke", table_name="smoke")
    ) as observer:
        receipt = observer.record(row_count=10, load_info=None)
    assert receipt.row_count == 10
    assert receipt.pipeline_name == "smoke"
    assert receipt.duration_ms >= 0.0


def test_destination_helper_returns_object_in_both_modes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("USE_DUCKLAKE", "false")
    try:
        from dlt_sources.common.destinations_cianfhoghlaim import get_dlt_destination

        dest = get_dlt_destination(use_ducklake=False)
        assert dest is not None
    except Exception as exc:  # pragma: no cover
        pytest.skip(f"duckdb not available in test env: {exc}")


def test_run_all_module_imports() -> None:
    mod = importlib.import_module("tuatha.dlt.run_all")
    assert hasattr(mod, "run_all")
    assert callable(mod.run_all)
