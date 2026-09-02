"""cocoindex_flows.vernacular — the 7 vernacular language CocoIndex v1 Apps.

Per the 2026-09-01-cianfhoghlaim-nua-v7-vernaculars-pipelines-v1
change (Phase 14 of the cianfhoghlaim-nua v6 era plan).

This package ships 7 CocoIndex v1 Apps (one per British Isles
vernacular language beyond EN + GA):

  - welsh_embedding, scottish_gaelic_embedding, breton_embedding,
    cornish_embedding, manx_embedding, jersey_french_embedding,
    guernsey_french_embedding

The single canonical factory lives in ``vernacular_factory.py``.
The 7 sibling files re-export the same App objects for callers
that look up by filename.
"""
from __future__ import annotations

from .vernacular_factory import (
    VERNACULAR_CONFIG,
    VernacularConfig,
    shared_lifespan,
    # The 7 individual Apps (registered as module-level globals
    # inside vernacular_factory.py at import time).
    vernacular_welsh_embedding,
    vernacular_scottish_gaelic_embedding,
    vernacular_breton_embedding,
    vernacular_cornish_embedding,
    vernacular_manx_embedding,
    vernacular_jersey_french_embedding,
    vernacular_guernsey_french_embedding,
)

__all__ = [
    "VERNACULAR_CONFIG",
    "VernacularConfig",
    "shared_lifespan",
    "vernacular_welsh_embedding",
    "vernacular_scottish_gaelic_embedding",
    "vernacular_breton_embedding",
    "vernacular_cornish_embedding",
    "vernacular_manx_embedding",
    "vernacular_jersey_french_embedding",
    "vernacular_guernsey_french_embedding",
]
