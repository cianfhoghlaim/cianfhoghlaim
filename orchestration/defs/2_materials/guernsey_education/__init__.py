"""Guernsey jurisdiction Dagster assets (BIEP v3).

Per the 2026-07-31-biep-v3-crown-dependencies-v1 change +
2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

This package contains the 120 Guernsey cohorts (30 subjects × 4 levels:
GCSE + A-Level + IB + Local). YEARLY automation (1st September 00:00 UTC)
per the BIEP v3 scheduling.

Companion: orchestration/defs/2_materials/_base/guernsey_assets.py is
the canonical `JurisdictionAssetsBase` subclass for the jurisdiction-level
asset (per the centralized-model-registry refactor).
"""
