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


# DISABLED 2026-08-13 — was a module-level asset constant.
#
# `dg.load_defs()` auto-discovers every AssetsDefinition at module scope in
# the defs tree. This module defines the SAME asset key as the working
# definition in `2_materials/<jurisdiction>_education/`, so having both at
# module scope produced a duplicate key, which made
# `Definitions.validate_loadable()` raise and the code location show ZERO
# assets.
#
# This copy is also the broken one: `_pipeline_factory()` calls a pipeline
# INSTANCE, and `JurisdictionPipelineBase` defines no `__call__`, so the
# asset body raises `TypeError: object is not callable` on its first line.
#
# Kept as a builder FUNCTION so the factory shape survives for the Wave 1
# repair while staying invisible to auto-discovery.
def build_guernsey_documents_ingested():
    return make_jurisdiction_assets(
        jurisdiction_name="guernsey",
        pipeline_factory=_pipeline_factory,
    ).build_asset()
