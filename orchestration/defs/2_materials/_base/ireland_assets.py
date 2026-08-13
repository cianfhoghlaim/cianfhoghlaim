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

# DISABLED 2026-08-13 — was a module-level asset constant. See the identical
# note in the sibling `<jurisdiction>_assets.py` files: `dg.load_defs()`
# auto-discovers module-scope AssetsDefinitions, and this duplicated the key
# owned by `2_materials/ireland_education/generic_ireland_assets.py`, making
# `Definitions.validate_loadable()` raise. This copy is also the broken one
# (`TypeError: 'IrelandJurisdictionPipeline' object is not callable`).
#
# The reference implementation: IrelandAssets is the explicit subclass.
def build_ireland_documents_ingested():
    return IrelandAssets.build_asset()
