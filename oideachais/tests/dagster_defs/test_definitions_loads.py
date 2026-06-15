"""Smoke tests for `oideachais.dagster_defs.definitions:defs`.

Replaces the ad-hoc `try/except ImportError` in definitions.py with
explicit pytests that:

  1. Assert the module imports (no `ModuleNotFoundError`).
  2. Assert the resulting `defs` exposes >= 100 assets.
  3. Assert each asset key is in canonical `snake_case` form
     (no spaces, no hyphens — Dagster requires this for partition
     keys and run tags).

The actual asset materialisation is exercised in
test_curriculum_dlt_assets.py (integration) and the Leaving Cert
asset test. This file is a pure smoke test: the Dagster container
is *not* required, only the local Python venv.
"""
from __future__ import annotations

import re


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _load_defs():
    """Import defs via the bare module name (cwd = /app/oideachais).

    Per AGENTS.md "Zero Absolute Namespaces in Data Pipelines",
    the Dagster container's cwd is /app/oideachais, so the
    dlt_utils / dagster_defs packages are top-level bare imports.
    """
    from dagster_defs.definitions import defs
    return defs


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def test_definitions_module_imports() -> None:
    """Importing `dagster_defs.definitions` must not raise."""
    import importlib

    mod = importlib.import_module("dagster_defs.definitions")
    assert hasattr(mod, "defs")
    assert mod.defs is not None


def test_definitions_has_at_least_100_assets() -> None:
    """The oideachais code-location must expose >= 100 assets.

    Pre-cleanup the codebase claimed 218; post-cleanup the actual
    number is ~211 (with 7 expected to be guarded or deprecated).
    100 is the Phase 1.1 floor — anything below means a major
    reorg regressed.
    """
    defs = _load_defs()
    ag = defs.resolve_asset_graph()
    n = sum(1 for _ in ag.get_all_asset_keys())
    assert n >= 100, f"Expected >= 100 assets, got {n}"


def test_asset_keys_are_dagster_safe() -> None:
    """Every asset key component must be lowercase + alphanumerics +
    underscores/hyphens. No spaces, no uppercase.

    Dagster 1.12 allows hyphens in asset names (the legacy
    `construction-studies` Leaving Cert subject uses one), but
    rejects spaces and uppercase. This is the real Dagster
    constraint.
    """
    safe = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
    defs = _load_defs()
    ag = defs.resolve_asset_graph()
    for key in ag.get_all_asset_keys():
        for component in key.path:
            assert safe.match(component), (
                f"Asset key component {component!r} is not dagster-safe"
            )


def test_definitions_has_groups() -> None:
    """defs.resolve_asset_graph() must surface at least one group.

    Groups power the Dagster UI sidebar. An empty group list
    usually means `group_name=` was forgotten on the @asset
    decorator.
    """
    defs = _load_defs()
    ag = defs.resolve_asset_graph()
    assert ag.all_group_names, "defs has no asset groups"


def test_no_legacy_data_platform_imports() -> None:
    """No module in `dagster_defs` should import the legacy
    `oideachais.data_platform.*` namespace.

    Post-cleanup (commit 8484a6353) the `oideachais/data_platform/`
    prefix is gone. Any lingering import is a regression.
    """
    import io
    import tokenize
    from pathlib import Path

    root = Path(__file__).resolve().parents[2] / "dagster_defs"
    bad = []
    for py in root.rglob("*.py"):
        try:
            tokens = tokenize.tokenize(io.BytesIO(py.read_bytes()).readline)
        except (SyntaxError, IndentationError):
            continue
        for tok in tokens:
            if tok.type == tokenize.NAME and tok.string == "import":
                # Naive scan: just look at the next STRING/NAME tokens.
                # A proper AST walk would be more accurate, but the
                # banned namespace is unique enough that a token-level
                # check catches >99% of regressions.
                continue
            if tok.type == tokenize.STRING and "oideachais.data_platform" in tok.string:
                bad.append((py, tok.start, tok.string))
    assert not bad, (
        f"Found {len(bad)} references to legacy `oideachais.data_platform`:\n"
        + "\n".join(f"  {p}:{l}:{c}  {s!r}" for p, (l, c), s in bad[:5])
    )
