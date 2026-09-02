"""guernsey_french_embedding — CocoIndex v1 App for Guernsey French (Guernésiais) vernacular.

Re-exports the canonical ``vernacular_guernsey_french_embedding`` app
from ``cocoindex_flows.vernacular.vernacular_factory``.

Per the 2026-09-01-cianfhoghlaim-nua-v7-vernaculars-pipelines-v1
change (Phase 14 of the cianfhoghlaim-nua v6 era plan).
"""
from __future__ import annotations

from .vernacular_factory import VERNACULAR_CONFIG  # noqa: F401
from .vernacular_factory import (  # noqa: F401
    vernacular_guernsey_french_embedding as guernsey_french_embedding_app,
)

__all__ = ["guernsey_french_embedding_app"]
