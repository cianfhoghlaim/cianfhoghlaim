"""Dagster asset defs for the LC subject pilot factory (C3).

Per the 2026-08-10-baml-extraction-completion-v1 change.

This file registers 6 subjects × 3 assets + 3 checks = 36 Dagster objects
when loaded by the `definitions.py` orchestrator.

Usage:
    from orchestration.defs.2_materials.lc_extraction.lc_subjects import lc_subject_pilot_factory
    for subject in LC_SUBJECTS:
        ingested, ingested_check, cross_checked, cross_checked_check, loaded, loaded_check = lc_subject_pilot_factory(subject)
        assets = [ingested, cross_checked, loaded]
        asset_checks = [ingested_check, cross_checked_check, loaded_check]
"""
from __future__ import annotations

from .lc_subjects import LC_SUBJECTS, lc_subject_pilot_factory


def get_lc_subject_assets() -> list:
    """Return all LC subject pilot assets (6 subjects × 3 = 18 assets)."""
    assets = []
    for subject in LC_SUBJECTS:
        ingested, _, cross_checked, _, loaded, _ = lc_subject_pilot_factory(subject)
        assets.extend([ingested, cross_checked, loaded])
    return assets


def get_lc_subject_asset_checks() -> list:
    """Return all LC subject pilot asset checks (6 subjects × 3 = 18 checks)."""
    checks = []
    for subject in LC_SUBJECTS:
        # `lc_subject_pilot_factory` returns
        # (ingested, ingested_check, cross_checked, cross_checked_check,
        # loaded, loaded_check) — a previous version of this unpacking
        # grabbed positions 0/2/4 (the assets) into variables misleadingly
        # named `*_check`, and silently discarded the real checks
        # (positions 1/3/5) via `_`.
        _, ingested_check, _, cross_checked_check, _, loaded_check = lc_subject_pilot_factory(subject)
        checks.extend([ingested_check, cross_checked_check, loaded_check])
    return checks


# Module-level bindings so `dg.load_assets_from_modules`/
# `load_asset_checks_from_modules` — which scan for module-level
# AssetsDefinition/AssetChecksDefinition objects (including lists of
# them, see `find_objects_in_module_of_types`) — can actually discover
# these. The two getters above were previously never invoked by anything,
# so no LC-subject asset was ever registered.
LC_SUBJECT_ASSETS: list = get_lc_subject_assets()
LC_SUBJECT_ASSET_CHECKS: list = get_lc_subject_asset_checks()
