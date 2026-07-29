"""
Cianfhoghlaim Dagster Definitions.

The 2026-06-30-dagster-ground-up-rewrite-5-layer-component-architecture
change introduced a 5-layer Component architecture that uses
`dg.load_defs()` (Dagster 1.13+ API). This file is the PRIMARY
definitions mount:

  - PRIMARY: `dg.load_defs()` (Dagster 1.13+) — recursively walks
    `orchestration/defs/<layer>/...` and constructs the Definitions
    object from the 5-layer Component YAML defs (CelticIngestionComponent,
    CelticMaterialsComponent, CelticModelLifecycleComponent,
    CelticAssetGenerationComponent, CelticAgentOpsComponent)
  - FALLBACK: `_defs_walker.load_defs_via_walker()` — a custom
    walker that recursively loads @asset / @asset_check / @job /
    @sensor / @schedule decorators anywhere in the
    `orchestration/defs/` sub-tree. Used if Dagster <1.13 is installed
    or if `load_defs()` fails.

The developer workflow:
    dg list components   # 5 KCG Components (post [tool.dg] section)
    dg list defs         # 833 loadable defs (95 hand-written + 783 YAML
                         # once dg.load_defs() is wired)
    dg check yaml        # validate the 783 YAML defs
    dg dev                # local dev server (port 3000)

Per the 2026-08-13 Phase A plan, this file was previously the
legacy 1.10-fallback path (load_from_defs_folder was unavailable
on 1.10.9; the comment at line 6 still claims "current Dagster
1.10.9 install"). The pyproject.toml dependency at line 15 now
specifies `dagster>=1.13`, so this file uses the canonical 1.13+
load_defs() path.
"""
from __future__ import annotations

from pathlib import Path

# Load environment variables from .env (lakehouse credentials).
# This must happen before importing resources that use env vars.
_locket_env = Path("/run/secrets/locket/secrets.env")
_env_file = Path(__file__).parent.parent / ".env"

if _locket_env.exists():
    from dotenv import load_dotenv

    load_dotenv(_locket_env)

if _env_file.exists():
    from dotenv import load_dotenv

    load_dotenv(_env_file, override=True)

import dagster as dg


# ============================================================================
# PRIMARY: dg.load_defs() (Dagster 1.13+)
# ============================================================================
# load_defs() recursively walks `orchestration/defs/<layer>/...` and
# constructs the Definitions object from the 5-layer Component
# YAML defs (CelticIngestionComponent, CelticMaterialsComponent,
# CelticModelLifecycleComponent, CelticAssetGenerationComponent,
# CelticAgentOpsComponent). Per Dagster 1.13+, this is the canonical
# way to mount definitions in a `defs/` folder.
#
# The [tool.dg] section in pyproject.toml declares:
#   registry_modules = ["orchestration.components"]
# so the 5 KCG Components are auto-discovered.

_DEFS_LOADED_VIA: str = "unknown"
_DEFS_AVAILABLE: bool = False

try:
    from orchestration import defs as _defs_pkg

    defs = dg.load_defs(defs_root=Path(_defs_pkg.__file__).parent)
    _DEFS_AVAILABLE = True
    _DEFS_LOADED_VIA = "dg.load_defs (Dagster 1.13+ canonical)"
except AttributeError:
    # load_defs doesn't exist on Dagster <1.13
    _DEFS_LOADED_VIA = "load_defs unavailable (Dagster <1.13)"
except Exception as _exc:  # pragma: no cover
    import structlog

    structlog.get_logger().warning(
        f"dg.load_defs_failed: {_exc}; falling back to _defs_walker"
    )
    _DEFS_LOADED_VIA = f"load_defs failed: {_exc}"


# ============================================================================
# FALLBACK: custom _defs_walker (Dagster 1.10-compatible)
# ============================================================================
# If dg.load_defs() is unavailable or fails, use the custom walker
# at orchestration/_defs_walker.py. This walker recursively loads
# @asset / @asset_check / @job / @sensor / @schedule decorators
# anywhere in the orchestration/defs/ sub-tree.
#
# Historical note: this walker was the PRIMARY path under the
# 2026-08-13 Phase A plan (when Dagster 1.10.9 was installed). Per
# the 2026-08-14 v8 update, Dagster >=1.13 is canonical and
# dg.load_defs() is the primary path.

if not _DEFS_AVAILABLE:
    try:
        from orchestration._defs_walker import load_defs_via_walker

        defs = load_defs_via_walker(
            defs_root=Path(__file__).parent / "defs",
        )
        _DEFS_AVAILABLE = True
        _DEFS_LOADED_VIA = (
            f"{_DEFS_LOADED_VIA} + load_defs_via_walker (1.10 fallback)"
        )
    except Exception as _exc:  # pragma: no cover
        import structlog

        structlog.get_logger().warning(
            f"load_defs_via_walker_failed: {_exc}; falling back to empty Definitions"
        )
        defs = dg.Definitions(assets=[], asset_checks=[], jobs=[], sensors=[], schedules=[])
        _DEFS_LOADED_VIA = f"{_DEFS_LOADED_VIA} + empty (walker failed)"


# ============================================================================
# Schedules from `orchestration/automation/`
# ============================================================================
# `dg.load_defs()` only walks `orchestration/defs/`. The schedules in
# `orchestration/automation/sync_schedules.py` (the daily sync_health
# cron per the `knowledge-sync-loop` spec) live outside that tree, so
# we merge them in here. Per the 2026-07-29-repo-hygiene-agent-routing-and-sync-wiring-v1
# change (the Daily sync_health cron requirement).

try:
    from orchestration.automation.sync_schedules import sync_schedules

    if sync_schedules:
        defs = dg.Definitions.merge(
            defs,
            dg.Definitions(schedules=sync_schedules),
        )
except Exception as _exc:  # pragma: no cover
    import structlog

    structlog.get_logger().warning(
        f"sync_schedules_load_failed: {_exc}; continuing without the daily sync_health cron"
    )


__all__ = ["defs", "_DEFS_AVAILABLE", "_DEFS_LOADED_VIA"]