"""Dagster assets wrapper for the ciancheiltis Phase 1 (en-cy) CocoIndex App.

This is the **assets surface** that the L3 Dagster component consumes.
The actual ``defs.yaml`` wiring (at
``orchestration/defs/3_model_lifecycle/cocoindex_v1/ciancheiltis_en_cy_embedding/defs.yaml``)
lives in subagent 3's territory — this file ships the Python asset
factory functions only.

Wiring contract (per the ``oideachais-cocoindex-v1`` skill):

1. ``en_cy_chunks`` — the R1-R4 CocoIndex v1 App as a ``virtual`` asset
   (drives the LanceDB table mirror at
   ``lancedb://md:cianfhoghlaim/ciancheiltis/en_cy_chunks``).
2. ``en_cy_pairs_seeded_check`` — the asset check that gates ≥ 0.70
   RAGAS bilingual-pair coverage + ≥ 500 seeded pairs (per the
   ``openspec/specs/ciancheiltis/spec.md`` § RAGAS-gate scenario).
3. ``en_cy_app_health_check`` — the per-cycle compliance asset check
   that re-validates the R1-R4 conformance contract (per the
   ``oideachais-cocoindex-v1`` skill § R1-R4-contract).

Reference: ``openspec/changes/2026-09-06-ciancheiltis-v1/``.
"""
from __future__ import annotations

import logging
from collections.abc import Iterator
from typing import Any

logger = logging.getLogger(__name__)

# Subagent 3 owns the ``defs.yaml`` wiring; we only export the asset
# factory functions here so the L3 Component can pick them up via the
# canonical ``apps:`` list pattern.
from .ciancheiltis_en_cy_embedding import (  # noqa: E402 — module-level
    CIANCHEILTIS_EN_CY_DUCKLAKE_TABLES,
    CIANCHEILTIS_EN_CY_THEMES,
    COCOINDEX_AVAILABLE,
    PHASE_LANGUAGE_PAIR,
    PHASE_TABLE_URL,
    en_cy_embedding,
    en_cy_embedding_flow,
    flow,
)


def build_en_cy_chunks_asset_spec() -> dict[str, Any]:
    """Build the asset spec dict for the L3 Component to wrap.

    Consumed by ``orchestration/defs/3_model_lifecycle/cocoindex_v1/
    ciancheiltis_en_cy_embedding/defs.yaml`` (subagent 3's territory).

    Returns:
        A dict with the 3 required L3 keys: ``app_name``, ``module``,
        ``lance_table`` — matching the shape accepted by
        ``CelticModelLifecycleComponent`` in
        ``orchestration/components/layer3_model_lifecycle.py``.
    """
    return {
        "app_name": "CiancheiltisEnCyEmbedding",
        "module": "cocoindex_flows.british_isles.uk.ciancheiltis_en_cy_embedding",
        "source": "ciancheiltis",
        "lance_table": PHASE_TABLE_URL,
        "language_pair": PHASE_LANGUAGE_PAIR,
        "themes": list(CIANCHEILTIS_EN_CY_THEMES),
        "ducklake_tables": dict(CIANCHEILTIS_EN_CY_DUCKLAKE_TABLES),
    }


def iter_bilingual_pages() -> Iterator[dict[str, Any]]:
    """Re-export the bilingual-page yielder for the L2 materials layer.

    The L2 materials component (``orchestration/components/layer2_materials.py``)
    reads the bilingual page rows from the canonical yielder. This
    thin wrapper keeps the symbol import-safe even when CocoIndex is
    not installed.
    """
    # Local import to avoid a top-level side effect when CocoIndex is
    # absent.
    from .ciancheiltis_en_cy_embedding import _yield_bilingual_pages

    yield from _yield_bilingual_pages()


__all__ = [
    "CIANCHEILTIS_EN_CY_DUCKLAKE_TABLES",
    "CIANCHEILTIS_EN_CY_THEMES",
    "COCOINDEX_AVAILABLE",
    "PHASE_LANGUAGE_PAIR",
    "PHASE_TABLE_URL",
    "build_en_cy_chunks_asset_spec",
    "en_cy_embedding",
    "en_cy_embedding_flow",
    "flow",
    "iter_bilingual_pages",
]
