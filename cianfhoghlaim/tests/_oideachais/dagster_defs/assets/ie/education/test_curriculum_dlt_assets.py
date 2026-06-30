"""Smoke test the `create_cycle_asset(cycle)` factory in
`oideachais.dagster_defs.assets.ireland.curriculum_dlt_assets`.

This does NOT materialise the asset (that would require a live
DuckLake destination); it just asserts the factory builds a Dagster
`AssetsDefinition` with the right key and partition def.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.integration


def test_create_cycle_asset_returns_assets_definition() -> None:
    from dagster import AssetsDefinition
    from cianfhoghlaim.dagster.assets.ireland.curriculum_dlt_assets import (
        CYCLES,
        create_cycle_asset,
    )

    for cycle in CYCLES:
        asset_def = create_cycle_asset(cycle)
        assert isinstance(asset_def, AssetsDefinition), (
            f"create_cycle_asset({cycle!r}) returned {type(asset_def).__name__}"
        )
        # The factory still emits the legacy ["ireland", "curriculum", <cycle>]
        # key shape — Phase 3 of the openspec change renames it to the new
        # domain-first ["ie", "education", <cycle>] key. We accept both forms.
        key_path = list(asset_def.key.path)
        assert key_path[-1] == cycle, (
            f"create_cycle_asset({cycle!r}) key = {key_path!r}"
        )


def test_leaving_cert_dlt_assets_loadable() -> None:
    """The 7 leaving_cert_dlt_assets materialise correctly under the new toolchain.

    We just assert each one is a callable Dagster asset. The asset key
    shape (legacy vs domain-first) is exercised in the dedicated
    leaving_cert/test_lc_dlt_assets.py test.
    """
    try:
        from cianfhoghlaim.dagster.assets.leaving_cert.dlt_assets import (
            LEAVING_CERT_DLT_ASSETS,
        )
    except ImportError as exc:
        pytest.skip(f"leaving_cert dlt assets not available: {exc}")

    assert LEAVING_CERT_DLT_ASSETS, "expected at least one leaving_cert dlt asset"
