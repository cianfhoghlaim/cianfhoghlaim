"""Wales jurisdiction Dagster assets — JurisdictionAssetsBase subclass.

Per the `centralized-model-registry` capability + the
`dagster-5-layer-component-architecture` spec. This module is a thin
subclass of `JurisdictionAssetsBase` that emits a single
``wales_documents_ingested`` asset backed by the canonical
``wales_jurisdiction_pipeline``.

Reference: openspec/changes/2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1
"""
from __future__ import annotations

from .jurisdiction_assets_base import make_jurisdiction_assets


def _pipeline_factory():
    """Lazy-imported factory for the Wales jurisdiction pipeline."""
    from dlt_sources.british_isles.wales.education.wales_jurisdiction_pipeline import (
        wales_jurisdiction_pipeline,
    )
    return wales_jurisdiction_pipeline()


wales_documents_ingested = make_jurisdiction_assets(
    jurisdiction_name="wales",
    pipeline_factory=_pipeline_factory,
).build_asset()
