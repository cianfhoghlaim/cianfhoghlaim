"""Legacy shim for `oideachais.data_platform.*` imports.

Directly registers `data_platform` submodules under `oideachais.*` in
`sys.modules` so `from oideachais.data_platform.dlt_utils import X` works.

Skips modules that have API drift (cocoindex_flows, dagster_assets, etc.),
only registering the stable ones.

Per AGENTS.md rule "Zero Absolute Namespaces in Data Pipelines":
new code MUST use relative imports, not this shim.
"""

from __future__ import annotations

import importlib
import importlib.util
import sys
from pathlib import Path


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
# The leaving_cert asset is loaded directly by file path (bypassing the
# assets/__init__.py which imports modules with from-__future__ issues).
#
# This shim lives at oideachais/oideachais/data_platform/__init__.py — a
# legacy location that pre-dates the repo's oideachais monorepo layout.
# We compute the real oideachais package root (sibling of this shim's
# containing oideachais/) to find the actual leaving_cert asset module.
try:
    # The real oideachais package root is the parent of the parent of this
    # shim file: oideachais/oideachais/data_platform/__init__.py
    #   -> oideachais/oideachais (parent)
    #   -> oideachais (grandparent — real root with data_platform subdir)
    _shim_root = Path(__file__).resolve().parent  # oideachais/oideachais/data_platform
    _real_oideachais_root = _shim_root.parent.parent  # oideachais (real)
    _real_data_platform = _real_oideachais_root / "data_platform"
    _lc_path = _real_data_platform / "dagster_defs" / "assets" / "leaving_cert" / "__init__.py"

    # Import the full dagster_defs package via the real oideachais root
    import data_platform.dagster_defs  # noqa: F401
    sys.modules["oideachais.data_platform.dagster_defs"] = data_platform.dagster_defs

    if _lc_path.exists():
        _lc_spec = importlib.util.spec_from_file_location(
            "data_platform.dagster_defs.assets.leaving_cert",
            str(_lc_path),
            submodule_search_locations=[],
        )
        _lc_mod = importlib.util.module_from_spec(_lc_spec)
        sys.modules["data_platform.dagster_defs.assets.leaving_cert"] = _lc_mod
        sys.modules["oideachais.data_platform.dagster_defs.assets.leaving_cert"] = _lc_mod
        _lc_spec.loader.exec_module(_lc_mod)
    else:
        print(f"[oideachais shim] SKIP leaving_cert: not found at {_lc_path}", file=sys.stderr)
except Exception as e:
    print(f"[oideachais shim] SKIP dagster_defs: {e}", file=sys.stderr)

# oideachais.data_platform itself
sys.modules.setdefault("oideachais.data_platform", sys.modules[__name__])
