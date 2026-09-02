"""welsh_embedding — CocoIndex v1 App for Welsh (Cymraeg) vernacular.

Re-exports the canonical ``vernacular_welsh_embedding`` app from
``cocoindex_flows.vernacular.vernacular_factory`` for backwards
compatibility (per the Phase 14 §2 spec — individual files per
vernacular).

Per the 2026-09-01-cianfhoghlaim-nua-v7-vernaculars-pipelines-v1
change (Phase 14 of the cianfhoghlaim-nua v6 era plan).
"""
from __future__ import annotations

from .vernacular_factory import VERNACULAR_CONFIG  # noqa: F401

# Build / re-export the WELSH app from the factory.
from .vernacular_factory import vernacular_welsh_embedding as welsh_embedding_app  # noqa: F401

__all__ = ["welsh_embedding_app"]
