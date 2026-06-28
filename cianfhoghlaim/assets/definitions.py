"""Dagster Definitions — the single consolidated code-location for cianfhoghlaim.

This is the entry point registered in dg.toml as:
    module_name = "cianfhoghlaim.assets.definitions"

It aggregates assets from all sub-trees (Ireland education + leabharlann
active in Plan 1; UK nations + Crown Dependencies as preserved stubs).

Plan 1 (active):
- Ireland education (early_childhood / primary / junior_cycle / senior_cycle
  / leaving_cert) in EN + GA
- leabharlann corpus (6 subdirs: aigne, gaeilge, gemini_deep_research, mata,
  ollscoil_na_gaillimhe, zotero)
- 4 successive independent asset gen pipelines (official_documents,
  subject_assets, language_assets, exporters)
- OCR evaluation harness (11 vision × 4 classical × Ireland syllabus +
  6 leabharlann subdirs)

Plan 2 / Plan 3 / Legacy (preserved as stubs):
- UK 4-nation + Isle of Man — full education + 7 domains
- Jersey + Guernsey (Crown Dependencies) — legacy stubs

See:
    openspec/changes/2026-06-28-consolidate-sruth-into-cianfhoghlaim-v4/proposal.md
"""

from __future__ import annotations

import importlib
import warnings

try:
    from dagster import Definitions
    _DAGSTER_AVAILABLE = True
except ImportError:  # dagster not installed in this env
    Definitions = None  # type: ignore[assignment]
    _DAGSTER_AVAILABLE = False

# ---------------------------------------------------------------------------
# Asset import table — every (module_path, attr_name) tuple is lazy-imported
# so that the module can be loaded even if a sub-tree is missing its package.
# ---------------------------------------------------------------------------

# Plan 1: Ireland + leabharlann (active)
_PLAN_1_ASSETS: list[tuple[str, str]] = [
    # Ireland education (5 stages × 2 languages)
    ("cianfhoghlaim.assets.ireland.education.early_childhood", "all_assets"),
    ("cianfhoghlaim.assets.ireland.education.primary", "all_assets"),
    ("cianfhoghlaim.assets.ireland.education.junior_cycle", "all_assets"),
    ("cianfhoghlaim.assets.ireland.education.senior_cycle", "all_assets"),
    ("cianfhoghlaim.assets.ireland.education.leaving_cert", "all_assets"),
    # leabharlann (6 subdirs)
    ("cianfhoghlaim.assets.leabharlann.aigne", "all_assets"),
    ("cianfhoghlaim.assets.leabharlann.gaeilge", "all_assets"),
    ("cianfhoghlaim.assets.leabharlann.gemini_deep_research", "all_assets"),
    ("cianfhoghlaim.assets.leabharlann.mata", "all_assets"),
    ("cianfhoghlaim.assets.leabharlann.ollscoil_na_gaillimhe", "all_assets"),
    ("cianfhoghlaim.assets.leabharlann.zotero", "all_assets"),
    # 4 successive independent asset gen pipelines
    ("cianfhoghlaim.assets.asset_generation.official_documents", "all_assets"),
    ("cianfhoghlaim.assets.asset_generation.subject_assets", "all_assets"),
    ("cianfhoghlaim.assets.asset_generation.language_assets", "all_assets"),
    ("cianfhoghlaim.assets.asset_generation.exporters", "all_assets"),
    # OCR evaluation harness
    ("cianfhoghlaim.assets.ocr_evaluation", "all_assets"),
    # 12-agent fleet
    ("cianfhoghlaim.assets.agents", "all_assets"),
]

# Plan 2 + 3: UK nations + IoM (preserved as stubs)
_PLAN_2_3_ASSETS: list[tuple[str, str]] = [
    *[
        (f"cianfhoghlaim.assets.uk.{nation}.education", "all_assets")
        for nation in ("en", "ni", "wls", "sct", "iom")
    ],
    *[
        (f"cianfhoghlaim.assets.uk.{nation}.{domain}", "all_assets")
        for nation in ("en", "ni", "wls", "sct", "iom")
        for domain in ("law", "medicine", "culture", "government", "intelligence",
                       "statistics", "geospatial")
    ],
]

# Legacy: Jersey + Guernsey (preserved as stubs)
_LEGACY_ASSETS: list[tuple[str, str]] = [
    ("cianfhoghlaim.assets.legacy.jersey", "all_assets"),
    ("cianfhoghlaim.assets.legacy.guernsey", "all_assets"),
]


def _safe_load(module_path: str, attr_name: str) -> list:
    """Lazy-load a module attribute, suppressing ModuleNotFoundError.

    Used because the Plan 2 / Plan 3 / Legacy sub-trees are stub files that
    may not exist yet; we don't want a missing stub to break Dagster's
    code-location load.
    """
    try:
        module = importlib.import_module(module_path)
    except ModuleNotFoundError as e:
        warnings.warn(
            f"[cianfhoghlaim] skipping {module_path}: {e}",
            stacklevel=2,
        )
        return []
    value = getattr(module, attr_name, [])
    return list(value) if value else []


def _collect_all() -> tuple[list, dict]:
    """Aggregate all assets, resources, sensors, schedules from sub-trees."""
    assets: list = []
    resources: dict = {}
    sensors: list = []
    schedules: list = []
    jobs: list = []

    for entry in (_PLAN_1_ASSETS + _PLAN_2_3_ASSETS + _LEGACY_ASSETS):
        module_path, attr_name = entry
        loaded = _safe_load(module_path, attr_name)
        if isinstance(loaded, list):
            assets.extend(loaded)
        elif isinstance(loaded, dict):
            # Some modules return {"assets": [...], "resources": {...}}
            assets.extend(loaded.get("assets", []))
            resources.update(loaded.get("resources", {}))
            sensors.extend(loaded.get("sensors", []))
            schedules.extend(loaded.get("schedules", []))
            jobs.extend(loaded.get("jobs", []))

    return assets, dict(resources=resources, sensors=sensors,
                        schedules=schedules, jobs=jobs)


def build_definitions() -> Definitions:
    """Construct the consolidated Dagster Definitions for cianfhoghlaim."""
    assets, extras = _collect_all()
    return Definitions(
        assets=assets,
        resources=extras["resources"],
        sensors=extras["sensors"],
        schedules=extras["schedules"],
        jobs=extras["jobs"],
    )


# Dagster's dg CLI expects a top-level `defs` symbol that is itself a
# Definitions instance. We compute it once at module import time
# (only when dagster is available).
if _DAGSTER_AVAILABLE:
    defs = build_definitions()
else:
    defs = None  # type: ignore[assignment]