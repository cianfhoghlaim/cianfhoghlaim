"""Scotland + Wales + Northern Ireland jurisdiction Dagster assets.

Per the `centralized-model-registry` capability. This module is a
thin subclass of `JurisdictionAssetsBase` that emits a single
``sct_wls_ni_documents_ingested`` asset backed by the canonical
``sct_wls_ni_jurisdiction_pipeline``.

Reference: openspec/changes/2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1
"""
from __future__ import annotations

from .jurisdiction_assets_base import make_jurisdiction_assets


def _pipeline_factory():
    """Lazy-imported factory for the sct_wls_ni pipeline."""
    from dlt_sources.british_isles.sct_wls_ni.education.sct_wls_ni_jurisdiction_pipeline import (
        sct_wls_ni_jurisdiction_pipeline,
    )
    return sct_wls_ni_jurisdiction_pipeline()


sct_wls_ni_documents_ingested = make_jurisdiction_assets(
    jurisdiction_name="sct_wls_ni",
    pipeline_factory=_pipeline_factory,
).build_asset()