"""
Cianfhoghlaim Dagster Definitions.

The 2026-06 refactor (openspec/changes/2026-06-30-dagster-ground-up-rewrite-5-layer-component-architecture)
introduced a 5-layer Component architecture that uses `dg.load_defs()`
(Dagster 1.13+ API). On the current Dagster 1.10.9 install,
load_defs() is unavailable, so the legacy `dg.load_from_defs_folder()`
is used as PRIMARY. This loads:

  - 81 hand-written @asset decorators (defs/2_materials/*, etc.)
  - 7 dagster.DefsFolderComponent entries
  - 1 dagster.schedule
  - 1 dagster_dbt.DbtProjectComponent (if dagster_dbt installed)

When we upgrade to Dagster 1.13+ + dagster-components 0.27+, the
component-based defs.yaml entries (614 L1, 94 L3, 21 L5, 13 L2,
10 L4 = 752 more) will become loadable via load_defs() and will be
merged in.

The developer workflow is now:
    dg list defs        # 91+ loadable defs
    dg list components  # (deferred until Dagster 1.13+ upgrade)
    dg dev              # local dev server
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
# Primary: the 5-layer defs/ tree (load_defs)
# ============================================================================
# load_defs() recursively walks cianfhoghlaim.orchestration.defs/<layer>/...
# and constructs the Definitions object from the 5-layer Component
# YAML defs (CelticIngestionComponent, CelticMaterialsComponent,
# CelticModelLifecycleComponent, CelticAssetGenerationComponent,
# CelticAgentOpsComponent). Per Dagster 1.13+, this is the canonical
# way to mount definitions in a `defs/` folder.
#
# Per the 2026-08-13 Phase A plan: on Dagster 1.10.9 (current), we can't
# use load_defs() (1.13+ API). We promote the legacy
# load_from_defs_folder() to PRIMARY so the 88 loadable defs (81
# hand-written @asset decorators + 7 dagster.DefsFolderComponent
# entries + 1 dagster.schedule + 1 dagster_dbt.DbtProjectComponent)
# are visible. When we upgrade to Dagster 1.13+ + dagster-components
# 0.27+, the component-based defs.yaml entries will become loadable
# and the load_from_defs_folder will move back to legacy.

# PRIMARY: legacy load_from_defs_folder (Dagster 1.10 compatible)
# Use a custom defs/ walker (since Dagster 1.10.9 doesn't have
# `load_defs()` 1.13+ or `load_from_defs_folder()` 1.11+). The walker
# recursively loads @asset / @asset_check / @job / @sensor / @schedule
# decorators anywhere in the `orchestration/defs/` sub-tree.
# Per the 2026-08-13 Phase A plan, this is the PRIMARY load path
# until we upgrade to Dagster 1.13+ (which adds load_defs()).
try:
    import orchestration.defs as _defs_pkg
    from orchestration._defs_walker import load_defs_via_walker
    defs = load_defs_via_walker(
        defs_root=Path(_defs_pkg.__file__).parent if _defs_pkg.__file__ else Path(__file__).parent / "defs"
    )
    _DEFS_AVAILABLE = True
    _DEFS_LOADED_VIA = "load_defs_via_walker (Dagster 1.10 compatible)"
except Exception as _exc:  # pragma: no cover
    import structlog
    structlog.get_logger().warning(
        f"load_defs_via_walker_failed: {_exc}; falling back to empty Definitions"
    )
    defs = dg.Definitions(assets=[], asset_checks=[], jobs=[], sensors=[], schedules=[])
    _DEFS_AVAILABLE = False
    _DEFS_LOADED_VIA = "empty (load_defs_via_walker failed)"


# ============================================================================
# TRY: component-based load_defs (Dagster 1.13+ only)
# ============================================================================
# If we're running Dagster 1.13+, prefer the 5-layer Component
# architecture. The legacy load result is merged in to keep the
# 200+ legacy assets visible.
try:
    _COMPONENT_DEFS = dg.load_defs(defs_root=_defs_pkg)
    defs = defs.merge(_COMPONENT_DEFS)
    _DEFS_LOADED_VIA = (
        f"{_DEFS_LOADED_VIA} + load_defs (1.13+ components)"
    )
except AttributeError:
    # load_defs doesn't exist on Dagster <1.13
    pass
except Exception:  # pragma: no cover
    pass

if _DEFS_AVAILABLE:
    # The defs object already has the legacy result + any 1.13+ result
    # merged. Nothing more to do.
    pass

