"""Legacy shim for `oideachais.data_platform.*` imports.

Directly registers `data_platform` submodules under `oideachais.*` in
`sys.modules` so `from oideachais.data_platform.dlt_utils import X` works.

Skips modules that have API drift (cocoindex_flows, dagster_assets, etc.),
only registering the stable ones.

Per AGENTS.md rule "Zero Absolute Namespaces in Data Pipelines":
new code MUST use relative imports, not this shim.
"""

from __future__ import annotations

import sys
import types


def _register(module_name: str) -> None:
    """Register `data_platform.module_name` as `oideachais.data_platform.module_name`."""
    try:
        mod = __import__(f"data_platform.{module_name}", fromlist=["_"])
    except (ImportError, AttributeError) as e:
        print(f"[oideachais shim] SKIP data_platform.{module_name}: {e}", file=sys.stderr)
        return
    sys.modules[f"oideachais.data_platform.{module_name}"] = mod


# Stable submodules (known to import cleanly)
_register("dlt_utils")
_register("dlt_sources")
_register("baml_src")

# Potentially unstable — register only if they import cleanly
_register("cocoindex_flows")
_register("agents")
_register("api")
_register("subjects")
_register("memory")
_register("graph")
_register("cognee_integration")
_register("dagster_assets")

# dagster_defs is the biggest tree — register top-level + leaving_cert only.
# We import the leaving_cert module directly (bypassing assets/__init__.py
# which has grammar_validation and other broken modules).
try:
    import importlib
    # Import the full dagster_defs package to get the top-level module
    import data_platform.dagster_defs  # noqa: F401
    sys.modules["oideachais.data_platform.dagster_defs"] = data_platform.dagster_defs

    # Import leaving_cert directly (bypasses assets/__init__.py)
    _lc_spec = importlib.util.spec_from_file_location(
        "data_platform.dagster_defs.assets.leaving_cert",
        __file__.rsplit("/", 2)[0] + "/data_platform/dagster_defs/assets/leaving_cert/__init__.py",
        submodule_search_locations=[],
    )
    _lc_mod = importlib.util.module_from_spec(_lc_spec)
    sys.modules["data_platform.dagster_defs.assets.leaving_cert"] = _lc_mod
    sys.modules["oideachais.data_platform.dagster_defs.assets.leaving_cert"] = _lc_mod
    _lc_spec.loader.exec_module(_lc_mod)
except ImportError as e:
    print(f"[oideachais shim] SKIP dagster_defs: {e}", file=sys.stderr)

# oideachais.data_platform itself
sys.modules.setdefault("oideachais.data_platform", sys.modules[__name__])
