"""
croilar — Python asset module for Domain 6.

Wires the 4 Croilar (multi-persona portfolio) functions as Dagster assets:

1. croilar_cv_extraction — extract CV data from portfolio
2. croilar_data_engineering — fetch CV data engineering metrics
3. croilar_portfolio — build portfolio dashboard
4. croilar_devtools_hub — croilar-devtools MCP server hub

This is the Layer 1 + 4 of the 4-layer asset graph for the Croilar
code-location. The Croilar code-location lives at
`infrastructure/stacks/croilar/` and runs on a separate port (3000).

Reference: openspec/specs/croilar-portfolio/spec.md (7 requirements).
"""
from __future__ import annotations

import dagster as dg


def _make_croilar_asset(name: str, module_path: str, fn_name: str) -> dg.AssetsDefinition:
    """Build a Dagster asset for a single Croilar portfolio function."""
    @dg.asset(
        name=name,
        group_name="croilar",
        compute_kind="python",
        description=f"Croilar {name} via {fn_name}",
    )
    def _asset() -> dg.MaterializeResult:
        import importlib
        mod = importlib.import_module(module_path)
        fn = getattr(mod, fn_name)
        result = fn()
        return dg.MaterializeResult(
            metadata={"pipeline": name, "module": module_path, "fn": fn_name}
        )

    return _asset


croilar_assets = [
    _make_croilar_asset(
        "croilar_cv_extraction",
        "cianfhoghlaim.pipelines.ingest._croilar_dlt_sources.cv_extraction",
        "extract_cv",
    ),
    _make_croilar_asset(
        "croilar_data_engineering",
        "cianfhoghlaim.pipelines.ingest._croilar_dlt_sources.data_engineering",
        "fetch_data_engineering",
    ),
    _make_croilar_asset(
        "croilar_portfolio",
        "cianfhoghlaim.pipelines.ingest._croilar_dlt_sources.portfolio",
        "build_portfolio",
    ),
    _make_croilar_asset(
        "croilar_devtools_hub",
        "cianfhoghlaim.agents.croilar.devtools",
        "run_devtools_hub",
    ),
]


__all__ = ["croilar_assets"]
