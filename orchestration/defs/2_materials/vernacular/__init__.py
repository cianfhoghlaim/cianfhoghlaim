"""orchestration.defs.2_materials.vernacular — Phase 14 vernacular Dagster assets.

Per the 2026-09-01-cianfhoghlaim-nua-v7-vernaculars-pipelines-v1
change (Phase 14 of the cianfhoghlaim-nua v6 era plan).

This package ships 21 vernacular Dagster assets (7 vernaculars × 3
layers — 1_ingestion → 2_materials → 3_model_lifecycle) + 14 asset
checks (7 vernaculars × 2 checks). The 7 sibling files re-export
the assets for callers that look up by filename.

Each vernacular ships the canonical 5-layer Dagster convention:
  - <vernacular>_vernacular_documents_ingested   (group 1_ingestion)
  - <vernacular>_vernacular_extractions          (group 2_materials)
  - <vernacular>_vernacular_embeddings          (group 3_model_lifecycle)

Per-vernacular files (7):
  welsh, scottish_gaelic, breton, cornish, manx, jersey_french, guernsey_french
"""
from __future__ import annotations

# Each sibling file registers its own assets via @asset decorators.
# Their module-level side effects (Dagster asset registry) make them
# import-once-augment.

from . import (  # noqa: F401
    breton_assets,
    cornish_assets,
    guernsey_french_assets,
    jersey_french_assets,
    manx_assets,
    scottish_gaelic_assets,
    welsh_assets,
)
