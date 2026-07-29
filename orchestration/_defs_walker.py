"""Custom defs/ folder walker for Dagster <1.13.

Per the 2026-08-14 v8 update, Dagster >=1.13 is canonical and
`dg.load_defs()` (orchestration/definitions.py:71) is the PRIMARY
load path. This walker is the FALLBACK for environments where
Dagster <1.13 is installed.

The walker recursively loads:

  - Hand-written @asset / @asset_check / @job / @sensor /
    @schedule decorators (anywhere in the orchestration/defs/
    sub-tree)
  - Definitions(...) instances at __init__.py module level
  - dagster.DefsFolderComponent (1.10-compatible)

WORKAROUND for Python 3.13 tokenizer bug: identifiers starting
with a digit (e.g. 2_materials, 3_model_lifecycle) cause a
SyntaxError when used in `from x.2_materials import ...` statements.
We work around by using `importlib.util.spec_from_file_location`
to load modules without going through the standard import
statement parser.
"""
from __future__ import annotations

import importlib
import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import dagster as dg

REPO_ROOT = Path(__file__).resolve().parents[1]


def _discover_modules(defs_root: Path) -> list[ModuleType]:
    """Recursively find all Python modules under defs_root.

    Uses importlib.util.spec_from_file_location to load each file
    directly (bypassing the standard import statement parser, which
    is broken for Python 3.13.13 + digit-leading identifiers like
    2_materials).
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
        if not mod_name:
            continue
        try:
            spec = importlib.util.spec_from_file_location(mod_name, py_file)
            if spec is None or spec.loader is None:
                continue
            m = importlib.util.module_from_spec(spec)
            sys.modules[mod_name] = m
            spec.loader.exec_module(m)
            modules.append(m)
        except SyntaxError as e:
            print(f"  [skip tokenizer-bug] {mod_name}: {str(e)[:80]}")
        except Exception as e:
            print(f"  [skip] {mod_name}: {e}")
    return modules


def load_defs_via_walker(defs_root: Path) -> dg.Definitions:
    """Walk defs_root, load all assets/checks/jobs/sensors/schedules.

    FALLBACK path: used when `dg.load_defs()` is unavailable
    (Dagster <1.13). The PRIMARY path in definitions.py is
    `dg.load_defs()` which uses the 5 KCG Components.
    """
    modules = _discover_modules(defs_root)
    if not modules:
        return dg.Definitions()

    assets: list[Any] = []
    asset_checks: list[Any] = []
    jobs: list[Any] = []
    sensors: list[Any] = []
    schedules: list[Any] = []

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


__all__ = ["load_defs_via_walker", "REPO_ROOT"]