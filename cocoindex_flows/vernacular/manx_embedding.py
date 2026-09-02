"""manx_embedding — CocoIndex v1 App for Manx (Gaelg) vernacular.

Re-exports the canonical ``vernacular_manx_embedding`` app from
``cocoindex_flows.vernacular.vernacular_factory``.

Per the 2026-09-01-cianfhoghlaim-nua-v7-vernaculars-pipelines-v1
change (Phase 14 of the cianfhoghlaim-nua v6 era plan).
"""
from __future__ import annotations

from .vernacular_factory import VERNACULAR_CONFIG  # noqa: F401
from .vernacular_factory import (  # noqa: F401
    vernacular_manx_embedding as manx_embedding_app,
)

__all__ = ["manx_embedding_app"]
