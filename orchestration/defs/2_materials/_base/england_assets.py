"""England jurisdiction Dagster assets — JurisdictionAssetsBase subclass.

Per the `centralized-model-registry` capability + the
`dagster-5-layer-component-architecture` spec. This module is a thin
subclass of `JurisdictionAssetsBase` that emits a single
``england_documents_ingested`` asset backed by the canonical
``england_jurisdiction_pipeline``.

The legacy `orchestration/defs/2_materials/england_education/generic_england_assets.py`
(519 LOC) contains the per-board-specific assets (AQA / OCR / Edexcel)
that are NOT yet migrated. This module complements the legacy file
by providing the canonical jurisdiction-level asset for the v3
generic pipeline.

Reference: openspec/changes/2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1
"""
from __future__ import annotations

from .jurisdiction_assets_base import make_jurisdiction_assets


def _pipeline_factory():
    """Lazy-imported factory for the England jurisdiction pipeline."""
    from dlt_sources.british_isles.england.education.england_jurisdiction_pipeline import (
        england_jurisdiction_pipeline,
    )
    return england_jurisdiction_pipeline()


england_documents_ingested = make_jurisdiction_assets(
    jurisdiction_name="england",
    pipeline_factory=_pipeline_factory,
).build_asset()