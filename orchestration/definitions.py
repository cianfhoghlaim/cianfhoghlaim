"""
Cianfhoghlaim Dagster Definitions — 5-Layer Component architecture.

The 2026-06 refactor (openspec/changes/2026-06-30-dagster-ground-up-rewrite-5-layer-component-architecture)
collapses the 619-line legacy definitions.py to a 30-line bootstrap
that delegates to `load_defs()` for the new 5-layer defs/ tree:

    defs/1_ingestion/         CelticIngestionComponent
    defs/2_materials/         CelticMaterialsComponent + DbtProjectComponent
    defs/3_model_lifecycle/   CelticModelLifecycleComponent (17 v1 Apps)
    defs/4_asset_generation/  CelticAssetGenerationComponent
    defs/5_agent_ops/         CelticAgentOpsComponent (12 agents × 5 assets)

Legacy 6-sub-folder shape (defs/{cianfhoghlaim_pipeline, celtic_asset_generation,
cognify, croilar, meaisinfhoghlaim_platform, tuatha}) is preserved
through the `dg.load_from_defs_folder()` legacy merge for backwards
compatibility, but is scheduled for removal in Phase 4 of the same
openspec change.

The developer workflow is now:
    dg list defs        # 5 nested groups + 260+ assets
    dg list components  # 5 KCG Components (L1-L5)
    dg scaffold defs <Component> <name> --attr1 ... --attr2 ...
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
try:
    import cianfhoghlaim.orchestration.defs as _defs_pkg
    defs = dg.load_defs(defs_root=_defs_pkg)
    _DEFS_AVAILABLE = True
except Exception as _exc:  # pragma: no cover
    import structlog
    structlog.get_logger().warning(
        f"load_defs_failed: {_exc}; falling back to empty Definitions"
    )
    defs = dg.Definitions(assets=[], asset_checks=[], jobs=[], sensors=[], schedules=[])
    _DEFS_AVAILABLE = False


# ============================================================================
# Legacy 6-sub-folder shape (preserved for backwards compatibility)
# ============================================================================
# The 6 legacy sub-folders (cianfhoghlaim_pipeline, celtic_asset_generation,
# cognify, croilar, meaisinfhoghlaim_platform, tuatha) are merged into
# the new defs to keep the 200+ legacy assets visible in the UI.
# Phase 4 of the same openspec change retires them.
try:
    _DEFS_FOLDER = dg.load_from_defs_folder(project_root=Path(__file__).parent)
except Exception:  # pragma: no cover
    _DEFS_FOLDER = None

if _DEFS_FOLDER is not None:
    defs = defs.merge(_DEFS_FOLDER)
