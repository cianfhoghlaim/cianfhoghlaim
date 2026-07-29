"""Ireland jurisdiction Dagster assets — JurisdictionAssetsBase subclass.

Per the `centralized-model-registry` capability. The Ireland
jurisdiction is the canonical reference for the
``JurisdictionAssetsBase`` pattern. The reference subclass
``IrelandAssets`` (defined in
orchestration/defs/2_materials/_base/jurisdiction_assets_base.py) is
emitted as the ``ireland_documents_ingested`` asset via the
``ireland_jurisdiction_pipeline``.

Reference: openspec/changes/2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1
"""
from __future__ import annotations

from .jurisdiction_assets_base import IrelandAssets

# The reference implementation: IrelandAssets is the explicit subclass.
ireland_documents_ingested = IrelandAssets.build_asset()
