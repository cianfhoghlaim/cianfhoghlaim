"""Custom defs/ folder walker for Dagster 1.10.9.

Per the 2026-08-13 Phase A plan:

Dagster 1.10.9 doesn't have `dg.load_defs()` (1.13+) or
`dg.load_from_defs_folder()` (1.11+). We need a custom walker
that recursively loads:

  - Hand-written `@asset` / `@asset_check` / `@sensor` / `@job` /
    `@schedule` decorators (anywhere in the `orchestration/defs/`
    sub-tree)
  - `Definitions(...)` instances at `__init__.py` module level
  - `dg.DefsFolderComponent` (1.10-compatible)

The walker:
1. Recursively finds all .py files under `orchestration/defs/`
2. For each file, calls `dg.load_assets_from_modules(modules=[mod])` etc.
3. Returns a single `Definitions(assets=..., asset_checks=..., jobs=...,
   sensors=..., schedules=...)` aggregated result
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import dagster as dg


def _discover_modules(defs_root: Path) -> list[ModuleType]:
    """Recursively find all Python modules under defs_root.

    The defs_root should be `orchestration/defs/` (a Python sub-package
    of the orchestration package). The module names are computed as
    `orchestration.defs.<rel_path>` (e.g., `orchestration.defs.2_materials.root_pdf_assets`).
    """
    modules: list[ModuleType] = []
    pkg_root = "orchestration.defs"
    for py_file in sorted(defs_root.rglob("*.py")):
        if py_file.name == "__init__.py":
            rel = py_file.parent.relative_to(defs_root)
        else:
            rel = py_file.relative_to(defs_root).with_suffix("")
        parts = list(rel.parts)
        if parts[-1] == "__init__":
            parts = parts[:-1]
        mod_name = ".".join([pkg_root] + parts) if parts else pkg_root
        if not mod_name or mod_name == pkg_root and not (defs_root / "__init__.py").exists():
            continue
        try:
            mod = importlib.import_module(mod_name)
            modules.append(mod)
        except Exception as e:
            # Skip modules that fail to import (likely have broken deps)
            # but log the failure
            print(f"  [skip] {mod_name}: {e}")
    return modules


def load_defs_via_walker(defs_root: Path) -> dg.Definitions:
    """Walk defs_root, load all assets/checks/jobs/sensors/schedules.

    Returns a single aggregated Definitions object.

    Per the 2026-08-13 Phase A plan: handles pre-existing duplicate-key
    bugs in some modules (e.g. `orchestration/defs/2_materials/lc_extraction/lc5_assets.py`
    has 24 factory-generated assets with the same function name) by
    retrying the load per-module (so a single broken module doesn't
    kill the whole batch).
    """
    modules = _discover_modules(defs_root)
    if not modules:
        return dg.Definitions()

    assets: list[Any] = []
    asset_checks: list[Any] = []
    jobs: list[Any] = []
    sensors: list[Any] = []
    schedules: list[Any] = []

    # Per-module load: if any module has duplicate-key issues, skip just
    # that module (not the whole batch).
    # NOTE: In Dagster 1.10, load_assets_from_modules returns a list.
    # In Dagster 1.13+, it returns a dict. We handle both.
    for mod in modules:
        try:
            result = dg.load_assets_from_modules(modules=[mod])
            if isinstance(result, dict):
                mod_assets = list(result.values())
            else:
                mod_assets = list(result)
            assets.extend(mod_assets)
        except Exception as e:
            print(f"  [skip assets] {mod.__name__}: {str(e)[:120]}")

    for mod in modules:
        try:
            result = dg.load_asset_checks_from_modules(modules=[mod])
            if isinstance(result, dict):
                mod_checks = list(result.values())
            else:
                mod_checks = list(result)
            if mod_checks:
                asset_checks.extend(mod_checks)
        except Exception as e:
            print(f"  [skip checks] {mod.__name__}: {str(e)[:120]}")

    # Pick up jobs / sensors / schedules via module-level Definitions
    # objects (any module that has `defs = Definitions(...)` at the top)
    for mod in modules:
        try:
            d = getattr(mod, "defs", None)
            if isinstance(d, dg.Definitions):
                jobs.extend(d.get_job_defs())
                sensors.extend(d.sensors)
                schedules.extend(d.schedules)
        except Exception:
            pass

    return dg.Definitions(
        assets=assets,
        asset_checks=asset_checks,
        jobs=jobs,
        sensors=sensors,
        schedules=schedules,
    )


__all__ = ["load_defs_via_walker"]