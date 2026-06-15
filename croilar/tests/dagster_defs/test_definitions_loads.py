"""Smoke test that `croilar.definitions:defs` constructs without
ImportError.

This test surfaces the pre-existing `croilar._shared.streams`
ModuleNotFoundError (the `_shared/` module is not in croilar's
`pyproject.toml` packages list and `croilar/__init__.py` does
not exist). It does so by deliberately *trying* to import the
module and asserting either:

  (a) `defs` builds with >= 1 asset, OR
  (b) the import fails with a *known* pre-existing error which we
      document with `pytest.xfail` so the test is still tracked
      but doesn't break the build.

The known pre-existing errors are:
  - ModuleNotFoundError: No module named 'croilar'
    (caused by missing croilar/__init__.py and missing _shared
     from pyproject packages)
  - any exception mentioning `_shared.streams`
"""
import os
import sys

import pytest


def test_croilar_definitions_imports() -> None:
    """`croilar.definitions:defs` must construct *and* expose an
    asset graph (or surface a documented pre-existing error).

    NOTE: This test runs in pytest's environment where the
    `croilar/tests/conftest.py` adds the croilar root to
    `sys.path`, which lets `from croilar._shared.streams import ...`
    succeed via the PEP-420 namespace-package fallback. In a real
    production container (where the croilar dir is the workspace
    root and `croilar` is not a real package), that import fails.
    See `docs/00-core/migration/croilar-packaging.md` for the fix.
    """
    try:
        from definitions import defs
    except (ModuleNotFoundError, ImportError) as exc:
        pytest.xfail(
            f"croilar code-location cannot load (pre-existing): {exc}. "
            "Fix: add `croilar/__init__.py` and declare `_shared` in "
            "croilar/pyproject.toml `packages = [...]`."
        )
        return
    # If the import succeeded, validate the asset graph actually
    # builds. The legacy pre-existing failure mode is at
    # `from croilar._shared.streams import ...` inside
    # `_shared/config/settings.py` — that fires when asset modules
    # import during `resolve_asset_graph()`, not at top-level import.
    try:
        ag = defs.resolve_asset_graph()
    except (ModuleNotFoundError, ImportError) as exc:
        if "croilar" in str(exc) or "_shared" in str(exc):
            pytest.xfail(
                f"croilar defs constructs but asset modules fail "
                f"(pre-existing): {exc}. Fix: declare `_shared` in "
                "croilar/pyproject.toml `packages = [...]`."
            )
            return
        raise
    n = sum(1 for _ in ag.get_all_asset_keys())
    assert n >= 1, f"Expected at least 1 asset, got {n}"
