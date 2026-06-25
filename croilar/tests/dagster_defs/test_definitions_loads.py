"""Smoke test that `croilar.definitions:defs` constructs without
ImportError.

This test loads the croilar dagster code-location and
verifies the asset graph builds. It is the canonical CI
gate for the croilar code-location.

History (per issue #17, closed 2026-06-15):
  - Pre-cleanup, `croilar/__init__.py` did not exist and the
    `_shared` + `dagster_assets` subdirs were missing from
    `croilar/pyproject.toml`'s `[tool.hatch.build.targets.wheel]
    packages`. The dagster code-location at `croilar/definitions.py`
    used `from croilar._shared.X import ...`, which failed.
  - The fix:
      1. Added `croilar/__init__.py` (so `croilar` is a real
         Python package, not a PEP-420 namespace package)
      2. Changed `croilar/pyproject.toml` to declare
         `packages = ["."]` (the project root) so hatch's
         auto-detection picks up `_shared/`, `dagster_assets/`,
         `pipelines/`, `notebooks/` as sub-packages
      3. Wrote `croilar/scripts/fix-pth.sh` which rewrites
         uv's broken editable-install `_editable_impl_croilar.pth`
         file (4 lines, all pointing to the project root) to a
         single line pointing to the project root's parent.
         This is a post-install script; invoke it after every
         `uv sync` via `mise run croilar:fix-pth`.
      4. Removed the `croilar_str` sys.path insertion from
         `croilar/tests/conftest.py` (no longer needed).
  - This test now passes cleanly (no more `pytest.xfail`).
"""
import os
import sys

import pytest


def test_croilar_definitions_imports() -> None:
    """`croilar.definitions:defs` must construct and expose an
    asset graph with >= 1 asset.

    The import path `from definitions import defs` works
    because the cwd is `croilar/`, AND the `croilar/__init__.py`
    we added (per issue #17) makes `croilar` a real package,
    AND the `croilar/scripts/fix-pth.sh` script has been run
    so the venv's `.pth` file puts the project root's parent
    on `sys.path`.
    """
    # Sanity: the repo root should be on sys.path (the conftest
    # inserts it; the fix-pth.sh script also does via the .pth
    # file). This is the cross-quadrant path — used by tests that
    # import sibling packages like `from sruth.oideachais.X import Y`.
    repo_root = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )
    assert repo_root in sys.path, (
        f"Expected {repo_root} in sys.path (set by conftest.py). "
        "If this fails, run `mise run croilar:fix-pth` to repair the "
        "_editable_impl_croilar.pth file (per issue #17)."
    )

    # Production: try the bare import (works because cwd is croilar/)
    try:
        from definitions import defs
    except (ModuleNotFoundError, ImportError) as exc:
        pytest.fail(
            f"croilar code-location cannot load: {exc}. "
            "The fix from issue #17 (croilar/__init__.py + "
            "_shared in pyproject packages) has regressed."
        )

    # Validate the asset graph actually builds. The
    # `from croilar._shared.X import` chain inside
    # `_shared/config/settings.py` must resolve cleanly.
    ag = defs.resolve_asset_graph()
    n = sum(1 for _ in ag.get_all_asset_keys())
    assert n >= 1, f"Expected at least 1 asset, got {n}"
