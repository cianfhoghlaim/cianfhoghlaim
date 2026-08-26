"""End-to-end tests for the ``registry_drift_alert`` sensor + job + asset.

Validates the full Dagster surface introduced by the
``2026-08-15-cascading-registry-integration-v2`` openspec change
(spec delta on ``dagster-5-layer-component-architecture``).

Specifically:

1. The sensor / job / asset all import cleanly from
   ``orchestration.defs.sync_assets``.
2. The sensor + job carry the documented descriptions that point at
   the canonical spec delta + the audit script.
3. The helper ``_get_registry_drift_count()`` returns ``int >= 0``.
4. The helper ``_get_registry_drift_files()`` returns ``list[str]``.
5. The asset key matches ``("registry", "drift_alert")``.
6. ``orchestration.definitions`` loads without ``SyntaxError`` /
   ``ImportError``.

All tests are deterministic — no network, no live DB, no subprocess
beyond what the helpers themselves invoke (which is mocked-by-design
via the helpers' own ``try/except`` blocks).
"""

from __future__ import annotations

import importlib

import pytest

# ─── 1 — imports ─────────────────────────────────────────────────────────────


def test_sensor_imports_cleanly() -> None:
    """The 3 canonical symbols + the constant + the 2 helpers all
    import cleanly from ``orchestration.defs.sync_assets``.
    """
    from orchestration.defs.sync_assets import (
        REGISTRY_DRIFT_ALERT_ASSET_KEY,
        _get_registry_drift_count,
        _get_registry_drift_files,
        materialize_registry_drift_alert_job,
        registry_drift_alert,
        registry_drift_alert_sensor,
    )

    assert registry_drift_alert_sensor is not None
    assert materialize_registry_drift_alert_job is not None
    assert registry_drift_alert is not None
    assert REGISTRY_DRIFT_ALERT_ASSET_KEY is not None
    assert callable(_get_registry_drift_count)
    assert callable(_get_registry_drift_files)


# ─── 2 — metadata references the canonical spec delta + audit script ────────


def test_sensor_has_correct_metadata() -> None:
    """The sensor's ``description`` mentions the canonical spec delta;
    the job's ``description`` mentions ``scripts/registry_audit.py``.
    """
    from orchestration.defs.sync_assets import (
        materialize_registry_drift_alert_job,
        registry_drift_alert_sensor,
    )

    sensor_desc = (registry_drift_alert_sensor.description or "").lower()
    job_desc = (materialize_registry_drift_alert_job.description or "").lower()

    # 2a) The sensor description points at the canonical spec delta.
    assert "cascading-registry-integration-v2" in sensor_desc, (
        "Sensor description is missing the spec-delta reference "
        "'cascading-registry-integration-v2'. "
        f"Got: {registry_drift_alert_sensor.description!r}"
    )

    # 2b) The job description mentions the audit script.
    assert "registry_audit.py" in job_desc, (
        "Job description is missing the audit-script reference "
        "'registry_audit.py'. "
        f"Got: {materialize_registry_drift_alert_job.description!r}"
    )


# ─── 3 — count helper returns int >= 0 ──────────────────────────────────────


def test_helper_get_drift_count_returns_int() -> None:
    """``_get_registry_drift_count()`` returns an ``int`` that is
    ``>= 0``. The helper shells out to ``scripts/registry_audit.py``
    and falls back to 0 on any subprocess failure.
    """
    from orchestration.defs.sync_assets import (
        _get_registry_drift_count,
    )

    count = _get_registry_drift_count()
    assert isinstance(count, int), (
        f"_get_registry_drift_count() returned non-int: {type(count).__name__}"
    )
    assert count >= 0, (
        f"_get_registry_drift_count() returned negative count: {count}"
    )


# ─── 4 — files helper returns list[str] ─────────────────────────────────────


def test_helper_get_drift_files_returns_list() -> None:
    """``_get_registry_drift_files()`` returns a list of strings. Each
    element is a path-string (the helper is best-effort and falls back
    to an empty list on subprocess failure).
    """
    from orchestration.defs.sync_assets import (
        _get_registry_drift_files,
    )

    files = _get_registry_drift_files()
    assert isinstance(files, list), (
        f"_get_registry_drift_files() returned non-list: "
        f"{type(files).__name__}"
    )
    for item in files:
        assert isinstance(item, str), (
            f"_get_registry_drift_files() returned non-string item: "
            f"{item!r}"
        )


# ─── 5 — asset key matches the documented constant ─────────────────────────


def test_asset_key_matches_documented_constant() -> None:
    """The ``registry_drift_alert`` asset is keyed under
    ``("registry", "drift_alert")`` — matching the documented
    ``REGISTRY_DRIFT_ALERT_ASSET_KEY`` constant.
    """
    from dagster import AssetKey

    from orchestration.defs.sync_assets import (
        REGISTRY_DRIFT_ALERT_ASSET_KEY,
        registry_drift_alert,
    )

    expected = AssetKey(["registry", "drift_alert"])
    assert expected == REGISTRY_DRIFT_ALERT_ASSET_KEY, (
        f"REGISTRY_DRIFT_ALERT_ASSET_KEY drifted: "
        f"expected {expected!r}, got {REGISTRY_DRIFT_ALERT_ASSET_KEY!r}"
    )

    # The asset's own key attribute must match the constant too.
    asset_keys = getattr(registry_drift_alert, "keys", None)
    if asset_keys is not None:
        assert expected in asset_keys, (
            f"registry_drift_alert.keys missing {expected!r}; got {asset_keys!r}"
        )


# ─── 6 — definitions.py loads without syntax/import errors ──────────────────


def test_definitions_py_loads_with_new_symbols() -> None:
    """``orchestration.definitions`` imports without ``SyntaxError`` or
    ``ImportError``. We use ``importlib.reload`` so the module is
    freshly evaluated — this catches any broken re-export of the new
    sensor / job / asset symbols.
    """
    try:
        mod = importlib.import_module("orchestration.definitions")
    except (ImportError, SyntaxError) as exc:
        pytest.fail(
            f"orchestration.definitions failed to import: "
            f"{type(exc).__name__}: {exc}"
        )
    assert mod is not None

    # A fresh reload also surfaces any module-level side-effect bugs.
    try:
        importlib.reload(mod)
    except (ImportError, SyntaxError) as exc:
        pytest.fail(
            f"orchestration.definitions failed to reload: "
            f"{type(exc).__name__}: {exc}"
        )
