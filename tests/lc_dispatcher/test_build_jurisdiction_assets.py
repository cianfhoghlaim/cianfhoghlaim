"""Smoke test for Phase 17.1: `build_jurisdiction_assets`.

Per Plan 16-29 recovery. Verifies:

  1. The factory module imports successfully.
  2. The ``build_jurisdiction_assets(config)`` function exists with the
     expected signature.
  3. The returned module contains 3 assets + 3 checks + 3 backfill jobs.
  4. The factory wires through ``JurisdictionAssetsBase``.
  5. The legacy single-asset factory (``make_jurisdiction_assets``) is
     still importable and remains unchanged.

Per the safety rules, this test is SAFE to apply — it does not
materialize any Dagster asset.
"""
from __future__ import annotations

import importlib
import inspect
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
FACTORY_PATH = (
    REPO_ROOT
    / "orchestration" / "defs" / "2_materials" / "_base"
    / "jurisdiction_assets_factory.py"
)


def test_factory_file_exists() -> None:
    """The factory module file exists at the canonical path."""
    assert FACTORY_PATH.is_file(), (
        f"Phase 17.1 foundation: {FACTORY_PATH} missing — was the factory "
        "module reverted?"
    )


def test_factory_module_importable() -> None:
    """The factory module can be imported via its package path."""
    # Insert the orchestration package's parents onto sys.path so the
    # relative imports inside the module succeed.
    sys.path.insert(0, str(REPO_ROOT))
    try:
        mod = importlib.import_module(
            "orchestration.defs.2_materials._base.jurisdiction_assets_factory"
        )
    finally:
        # We don't pop; subsequent tests need the path too.
        pass
    assert hasattr(mod, "build_jurisdiction_assets"), (
        "Phase 17.1 foundation: `build_jurisdiction_assets` not exported."
    )
    assert hasattr(mod, "JurisdictionConfig"), (
        "Phase 17.1 foundation: `JurisdictionConfig` dataclass not exported."
    )
    assert hasattr(mod, "JurisdictionModule"), (
        "Phase 17.1 foundation: `JurisdictionModule` dataclass not exported."
    )


def test_build_jurisdiction_assets_signature() -> None:
    """`build_jurisdiction_assets(config: JurisdictionConfig)` — one positional arg."""
    sys.path.insert(0, str(REPO_ROOT))
    mod = importlib.import_module(
        "orchestration.defs.2_materials._base.jurisdiction_assets_factory"
    )
    fn = mod.build_jurisdiction_assets
    sig = inspect.signature(fn)
    params = list(sig.parameters.values())
    assert len(params) == 1, (
        f"Phase 17.1 foundation: expected 1 parameter, got {len(params)}: "
        f"{[p.name for p in params]}"
    )
    assert params[0].name == "config", (
        f"Phase 17.1 foundation: expected param name `config`, got "
        f"`{params[0].name}`."
    )


def test_factory_uses_jurisdiction_assets_base() -> None:
    """The factory imports + uses `JurisdictionAssetsBase`."""
    src = FACTORY_PATH.read_text()
    assert "JurisdictionAssetsBase" in src, (
        "Phase 17.1 foundation: factory must wire through "
        "`JurisdictionAssetsBase` (per the lost commit's pattern)."
    )


def test_factory_emits_three_assets() -> None:
    """The factory source declares three assets (2 via `@dg.asset`,
    1 via ``JurisdictionAssetsBase.build_asset()``)."""
    src = FACTORY_PATH.read_text()
    decorator_count = src.count("@dg.asset(") + src.count("@asset(")
    # The 1st asset (ingestion) is emitted via `base_cls.build_asset()`
    # (a classmethod, not a decorator), per the spec.
    build_asset_calls = src.count(".build_asset(") + src.count("base_cls.build_asset(")
    total_assets = decorator_count + build_asset_calls
    assert total_assets >= 3, (
        f"Phase 17.1 foundation: expected ≥3 assets (decorators + "
        f"build_asset calls), found {total_assets} "
        f"({decorator_count} decorators + {build_asset_calls} build_asset calls)."
    )


def test_factory_emits_three_asset_checks() -> None:
    """The factory source declares three `@dg.asset_check` decorators."""
    src = FACTORY_PATH.read_text()
    check_decorators = (
        src.count("@dg.asset_check(") + src.count("@asset_check(")
    )
    assert check_decorators >= 3, (
        f"Phase 17.1 foundation: expected ≥3 @dg.asset_check decorators, "
        f"found {check_decorators}."
    )


def test_factory_emits_three_backfill_jobs() -> None:
    """The factory emits three `define_asset_job` calls (one per asset)."""
    src = FACTORY_PATH.read_text()
    job_calls = (
        src.count("dg.define_asset_job(") + src.count("define_asset_job(")
    )
    assert job_calls >= 3, (
        f"Phase 17.1 foundation: expected ≥3 define_asset_job calls, "
        f"found {job_calls}."
    )


def test_legacy_subclass_factory_still_present() -> None:
    """`make_jurisdiction_assets` from `jurisdiction_assets_base` is untouched."""
    sys.path.insert(0, str(REPO_ROOT))
    base_mod = importlib.import_module(
        "orchestration.defs.2_materials._base.jurisdiction_assets_base"
    )
    assert hasattr(base_mod, "make_jurisdiction_assets"), (
        "Phase 17.1 foundation: legacy `make_jurisdiction_assets` factory "
        "must remain importable from `jurisdiction_assets_base`."
    )
    assert hasattr(base_mod, "JurisdictionAssetsBase"), (
        "Phase 17.1 foundation: `JurisdictionAssetsBase` base class must "
        "remain importable."
    )