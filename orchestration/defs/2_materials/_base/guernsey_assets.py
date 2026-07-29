"""Guernsey jurisdiction Dagster assets — JurisdictionAssetsBase subclass.

Per the `centralized-model-registry` capability + the
`dagster-5-layer-component-architecture` spec. This module is a thin
subclass of `JurisdictionAssetsBase` that emits a single
``guernsey_documents_ingested`` asset backed by the canonical
``guernsey_jurisdiction_pipeline``.

Reference: openspec/changes/2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1
"""
from __future__ import annotations

from .jurisdiction_assets_base import make_jurisdiction_assets


def _pipeline_factory():
    """Lazy-imported factory for the Guernsey jurisdiction pipeline."""
    from dlt_sources.british_isles.guernsey.education.guernsey_jurisdiction_pipeline import (
        guernsey_jurisdiction_pipeline,
    )
    return guernsey_jurisdiction_pipeline()


guernsey_documents_ingested = make_jurisdiction_assets(
    jurisdiction_name="guernsey",
    pipeline_factory=_pipeline_factory,
).build_asset()
