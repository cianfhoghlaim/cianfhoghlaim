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
    dg list components   # 5 Cianfhoghlaim Components (post [tool.dg] section)
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
# so the 5 Cianfhoghlaim Components are auto-discovered.

_DEFS_LOADED_VIA: str = "unknown"
_DEFS_AVAILABLE: bool = False

try:
    from orchestration import defs as _defs_pkg

    # dg.load_defs() takes the `defs` ModuleType itself (per the installed
    # Dagster 1.13 signature), not a Path — passing Path(_defs_pkg.__file__)
    # made get_project_root() call getattr(<Path>, "__file__", None), which is
    # always None for a Path, masquerading as the "no __init__.py" failure.
    defs = dg.load_defs(defs_root=_defs_pkg)
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


# ============================================================================
# Wave 2: Vertical pipelines (2026-08-24-wave-2-orchestration-vertical-pipelines-v1)
# ============================================================================
# The new `orchestration/pipelines/` namespace mirrors `dlt_sources/`
# domain-first layout. Each per-pipeline `defs.yaml` declares a
# canonical `dagster_dlt.DltLoadCollectionComponent` (per master plan
# §3.3 + the canonical `dagster-pipeline-components` spec) and is
# loaded by `dg.load_defs()` exactly like the horizontal `defs/` tree.
#
# The Cianfhoghlaim customisation is via the shared helpers at
# `orchestration.pipelines._shared.dagster_dlt_integration` (the
# canonical `translation:` defaults) + the Cianfhoghlaim custom Component at
# `orchestration.pipelines._shared.state_helpers.KCGStateBackedDltComponent`
# (the canonical `StateBackedComponent` compositing pattern for the 5
# high-churn sources per master plan §3.3).
#
# To support BOTH the horizontal (`defs/{1_ingestion,...,5_agent_ops}/`)
# AND the vertical (`pipelines/<domain>/<jurisdiction>/`) trees, we
# merge their `Definitions` objects below.

try:
    from orchestration import pipelines as _pipelines_pkg

    _pipelines_defs = dg.load_defs(defs_root=_pipelines_pkg)
    defs = dg.Definitions.merge(defs, _pipelines_defs)
    _DEFS_LOADED_VIA = f"{_DEFS_LOADED_VIA} + pipelines (Wave 2 vertical)"
except AttributeError:
    _DEFS_LOADED_VIA = f"{_DEFS_LOADED_VIA} + pipelines unavailable (Dagster <1.13)"
except Exception as _exc:  # pragma: no cover
    import structlog

    structlog.get_logger().warning(
        f"dg.load_defs_pipelines_failed: {_exc}; continuing without vertical pipelines"
    )


# ============================================================================
# Wave 2: per-pipeline Component shared helpers (canonical translation + state)
# ============================================================================
# Imports the Cianfhoghlaim customisation helpers that every per-pipeline `defs.yaml`
# inherits. The `kcg_default_translation` callable is referenced from each
# `defs.yaml` via:
#
#   translation: orchestration.pipelines._shared.dagster_dlt_integration.kcg_default_translation
#
# The `KCGStateBackedDltComponent` is the canonical Cianfhoghlaim custom Component
# (composition of `dagster_dlt.DltLoadCollectionComponent` +
# `dagster.components.StateBackedComponent`). Per master plan §3.3, the 5
# high-churn sources (NCCA + SEC + CCEA + SQA + WJEC) default to
# `LOCAL_FILESYSTEM` state; everything else defaults to
# `LEGACY_CODE_SERVER_SNAPSHOTS`.
#
# These imports are defensive — they MUST NOT raise at module import time
# (else the entire code location fails to load). The errors are logged
# and the rest of the Definitions merge continues.

try:
    from orchestration.pipelines._shared.dagster_dlt_integration import (  # noqa: F401
        kcg_default_translation,
        build_translation_for_pipeline,
        build_dlt_pipeline,
        high_churn_source_modules,
    )
    _DEFS_LOADED_VIA = f"{_DEFS_LOADED_VIA} + pipelines._shared.dagster_dlt_integration"
except Exception as _exc:  # pragma: no cover
    import structlog

    structlog.get_logger().warning(
        f"kcg_dagster_dlt_integration_load_failed: {_exc}; "
        "per-pipeline Components will fall back to the dagster_dlt default translation"
    )

try:
    from orchestration.pipelines._shared.state_helpers import (  # noqa: F401
        LOCAL_FILESYSTEM_DEFAULTS,
        default_state_block_for,
        local_defs_state_root,
    )
    _DEFS_LOADED_VIA = f"{_DEFS_LOADED_VIA} + pipelines._shared.state_helpers"
except Exception as _exc:  # pragma: no cover
    import structlog

    structlog.get_logger().warning(
        f"kcg_state_helpers_load_failed: {_exc}; "
        "per-pipeline Components will use the dagster StateBackedComponent defaults"
    )


# ============================================================================
# Jurisdiction-level ingestion assets (post-2026-08-15)
# ============================================================================
# Per the `centralized-model-registry` + `dagster-5-layer-component-architecture`
# capabilities (commits 0b731f3fd + 2e142f64c + 4ea9c1eed + 64659a6ad),
# the 10 per-jurisdiction ingestion assets live as thin 30-LOC
# `JurisdictionAssetsBase` subclasses at
# `orchestration/defs/2_materials/_base/<jurisdiction>_assets.py`. These
# subclass `jurisdiction_assets_base.py:JurisdictionAssetsBase` and
# emit one canonical `<jurisdiction>_documents_ingested` Dagster asset
# per jurisdiction. They are explicitly constructed + added to the
# `Definitions` here (not via `load_defs()`, since the base class is
# defined inline rather than via the standard `dg.asset` decorator).

try:
    # NOTE: The static `from orchestration.defs.2_materials._base import ...`
    # is intentionally NOT used because `2_materials` is an invalid Python
    # identifier (the `2_` is parsed as an incomplete PEP 515 underscore-
    # separated numeric literal). Use a dynamic import via `importlib`
    # to bypass the tokenizer. Per the 2026-07-30-cascading-registry-integration-v1
    # commit that introduced the static form (regressed at parse time).
    #
    # Each jurisdiction file (e.g. `ireland_assets.py`) is a SUBMODULE of
    # `_base`, not an attribute of the `_base` package. Import each
    # submodule dynamically + reference its canonical
    # `<jurisdiction>_documents_ingested` attribute.
    import importlib

    _jurisdiction_names = [
        "ireland", "england", "scotland", "wales", "northern_ireland",
        "sct_wls_ni", "isle_of_man", "jersey", "guernsey",
        "crown_dependencies",
    ]

    # DISABLED 2026-08-13. This merge is now redundant AND harmful.
    #
    # It was written when `dg.load_defs()` always failed and everything came
    # from the `_defs_walker` fallback. The primary path now works, and it
    # auto-discovers these same `_base` modules — so merging them again
    # produced duplicate asset keys, which made
    # `Definitions.validate_loadable()` raise and the code location show
    # ZERO assets in `dagster dev`.
    #
    # It is also the WRONG copy: the `_base` assets are broken at runtime.
    # `_base/{ireland,england}_assets.py` pass a pipeline INSTANCE where
    # `jurisdiction_assets_base.py` expects a factory, so their asset bodies
    # raise `TypeError: 'IrelandJurisdictionPipeline' object is not callable`
    # on their first line. The working definitions of the same keys live in
    # `2_materials/<jurisdiction>_education/generic_*_assets.py`.
    #
    # Left in place (not deleted) because the `_base` factory is still the
    # intended long-term shape — repairing it is Wave 1 of the Cianfhoghlaim roadmap.
    _jurisdiction_assets: list = []
except Exception as _exc:  # pragma: no cover
    import structlog

    structlog.get_logger().warning(
        f"jurisdiction_assets_load_failed: {_exc}; continuing without the 10 jurisdiction assets"
    )


# ============================================================================
# Layer 9 — Centralized-model-registry drift alert (per the
# 2026-08-15-cascading-registry-integration-v2 spec delta on
# dagster-5-layer-component-architecture). Wires the FULL sensor + job +
# asset that the cascading-registry-integration-v1 commit (9f4391bcd)
# deferred. The definitions live in `orchestration/defs/sync_assets.py`
# (next to the sibling Layer 1-8 sync_health surface) and are merged in
# here defensively even though `dg.load_defs()` already auto-discovers
# them — the explicit merge is the canonical wiring per the task spec.
# ============================================================================

try:
    from orchestration.defs.sync_assets import (
        materialize_registry_drift_alert_job,
        registry_drift_alert,
        registry_drift_alert_sensor,
    )

    # Assets omitted: `dg.load_defs()` already auto-discovers
    # `registry_drift_alert` from `orchestration/defs/sync_assets.py` (as the
    # comment above notes), so merging it again duplicated the
    # `registry/drift_alert` key. Only the job + sensor are merged, which
    # the auto-discovery does NOT pick up — the walker only collected
    # jobs/sensors from a module-level `defs` attribute that no module
    # defines.
    defs = dg.Definitions.merge(
        defs,
        dg.Definitions(
            jobs=[materialize_registry_drift_alert_job],
            sensors=[registry_drift_alert_sensor],
        ),
    )
except Exception as _exc:  # pragma: no cover
    import structlog

    structlog.get_logger().warning(
        f"registry_drift_alert_load_failed: {_exc}; continuing without the Layer 9 drift alert"
    )


# ============================================================================
# `dagster-dlt` resource — required by any `@dlt_assets`-decorated asset
# (e.g. `orchestration/defs/2_materials/endpoint_health/sink.py`, the
# Phase 5 reference migration off the hand-rolled `dlt.pipeline().run()`
# pattern). `orchestration/resources.py`'s `all_resources` dict already
# builds a `DagsterDltResource()` instance under the "dlt" key, but that
# dict was never actually consumed by any `Definitions` construction —
# every `@dlt_assets` asset would fail at runtime with a missing required
# resource. This merge is the fix: it's what actually supplies the "dlt"
# resource key at runtime.
# ============================================================================

try:
    from dagster_dlt import DagsterDltResource

    defs = dg.Definitions.merge(
        defs,
        dg.Definitions(resources={"dlt": DagsterDltResource()}),
    )
except Exception as _exc:  # pragma: no cover
    import structlog

    structlog.get_logger().warning(
        f"dlt_resource_wiring_failed: {_exc}; @dlt_assets-decorated assets "
        "will fail at runtime with a missing 'dlt' resource"
    )


# ============================================================================
# UoG exam-papers pipeline (M.Sc. AI thesis)
# ============================================================================
# Mounts the 5-asset `uog_exam_papers` group + the STOPPED-by-default
# nightly schedule via `orchestration/defs/uog_exam.py`. The schedule is
# OFF by default; flip it on with `dg launch schedule uog_exam_papers_nightly`
# once you have set INFISICAL_TOKEN + OOG_STUDENT_PASSWORD.
# Reference: openspec/changes/2026-08-23-uog-exam-papers-sso-v1/
# ============================================================================

try:
    from orchestration.defs.uog_exam import build_uog_exam_definitions

    defs = dg.Definitions.merge(defs, build_uog_exam_definitions())
except Exception as _exc:  # pragma: no cover
    import structlog

    structlog.get_logger().warning(
        f"uog_exam_assets_load_failed: {_exc}; "
        "the 5 uog_exam_papers assets will not be discoverable in Dagster"
    )


# ============================================================================
# UoG official-docs + NUI federation + Students' Union + British Isles
# tertiary pipeline (M.Sc. AI thesis deliverable 2)
# ============================================================================
# Mounts the 4 new groups:
#  - orchestration/defs/uog_official_docs.py   (5 assets)
#  - orchestration/defs/nui_federation.py       (3 assets)
#  - orchestration/defs/uog_students_union.py  (2 assets)
#  - orchestration/defs/british_isles_tertiary.py (5 assets, off-by-default)
#
# Reference: openspec/changes/2026-08-23-uog-official-docs-and-nui-superset-v1/
# ============================================================================

for _uog_official_docs_group_module in (
    "orchestration.defs.uog_official_docs",
    "orchestration.defs.nui_federation",
    "orchestration.defs.uog_students_union",
    "orchestration.defs.british_isles_tertiary",
    "orchestration.defs.uog_personal_archive",
):
    try:
        _mod = __import__(
            _uog_official_docs_group_module, fromlist=["__all__"]
        )
        _assets = [
            getattr(_mod, name)
            for name in getattr(_mod, "__all__", [])
            if hasattr(_mod, name) and callable(getattr(_mod, name))
        ]
        if _assets:
            defs = dg.Definitions.merge(
                defs,
                dg.Definitions(assets=_assets),
            )
    except Exception as _exc:  # pragma: no cover
        import structlog

        structlog.get_logger().warning(
            f"{_uog_official_docs_group_module}_load_failed: {_exc}"
        )


__all__ = ["defs", "_DEFS_AVAILABLE", "_DEFS_LOADED_VIA"]