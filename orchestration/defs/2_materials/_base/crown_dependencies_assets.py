"""Crown Dependencies jurisdiction Dagster assets — JurisdictionAssetsBase subclass.

Per the `centralized-model-registry` capability. This module is a
thin subclass of `JurisdictionAssetsBase` that emits a single
``crown_dependencies_documents_ingested`` asset backed by the
canonical ``crown_dependencies_jurisdiction_pipeline``.

Reference: openspec/changes/2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1
"""
from __future__ import annotations

from .jurisdiction_assets_base import make_jurisdiction_assets


def _pipeline_factory():
    """Lazy-imported factory for the Crown Dependencies pipeline."""
    from dlt_sources.british_isles.crown_dependencies.education.crown_dependencies_jurisdiction_pipeline import (
        crown_dependencies_jurisdiction_pipeline,
    )
    return crown_dependencies_jurisdiction_pipeline()


crown_dependencies_documents_ingested = make_jurisdiction_assets(
    jurisdiction_name="crown_dependencies",
    pipeline_factory=_pipeline_factory,
).build_asset()