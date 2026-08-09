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
        ingested_check, _, cross_checked_check, _, loaded_check, _ = lc_subject_pilot_factory(subject)
        checks.extend([ingested_check, cross_checked_check, loaded_check])
    return checks
