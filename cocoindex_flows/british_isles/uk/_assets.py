"""Dagster assets wrapper for the ciancheiltis Phase 1 (en-cy) + Phase 2 (en-ga-ROI) + Phase 3 (en-ga-NI) + Phase 4 (en-gd / Scotland) + Phase 5 (en-gv / Isle of Man) + Phase 6 (en-ga / EU level) CocoIndex Apps.

This is the **assets surface** that the L3 Dagster component consumes.
The actual ``defs.yaml`` wiring (at
``orchestration/defs/3_model_lifecycle/cocoindex_v1/ciancheiltis_en_cy_embedding/defs.yaml``
+ the Phase 2 sibling at
``orchestration/defs/3_model_lifecycle/cocoindex_v1/ciancheiltis_en_ga_roi_embedding/defs.yaml``
+ the Phase 3 sibling at
``orchestration/defs/3_model_lifecycle/cocoindex_v1/ciancheiltis_en_ga_ni_embedding/defs.yaml``
+ the Phase 4 sibling at
``orchestration/defs/3_model_lifecycle/cocoindex_v1/ciancheiltis_en_gd_embedding/defs.yaml``
+ the Phase 5 sibling at
``orchestration/defs/3_model_lifecycle/cocoindex_v1/ciancheiltis_en_gv_embedding/defs.yaml``
+ the Phase 6 sibling at
``orchestration/defs/3_model_lifecycle/cocoindex_v1/ciancheiltis_en_ga_eu_embedding/defs.yaml``)
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

4. ``en_ga_roi_chunks`` — the R1-R4 CocoIndex v1 Phase 2 App as a
   ``virtual`` asset (drives the LanceDB table mirror at
   ``lancedb://md:cianfhoghlaim/ciancheiltis/en_ga_roi_chunks``).
5. ``en_ga_roi_pairs_seeded_check`` — the Phase 2 asset check that
   gates ≥ 0.70 RAGAS bilingual-pair coverage + ≥ 500 seeded pairs.
6. ``en_ga_roi_app_health_check`` — the per-cycle Phase 2 compliance
   asset check that re-validates the R1-R4 conformance contract.

7. ``en_ga_ni_chunks`` — the R1-R4 CocoIndex v1 Phase 3 App as a
   ``virtual`` asset (drives the LanceDB table mirror at
   ``lancedb://md:cianfhoghlaim/ciancheiltis/en_ga_ni_chunks``).
8. ``en_ga_ni_pairs_seeded_check`` — the Phase 3 asset check that
   gates ≥ 0.70 RAGAS bilingual-pair coverage + ≥ 500 seeded pairs.
9. ``en_ga_ni_app_health_check`` — the per-cycle Phase 3 compliance
   asset check that re-validates the R1-R4 conformance contract.

10. ``en_gd_chunks`` — the R1-R4 CocoIndex v1 Phase 4 App as a
    ``virtual`` asset (drives the LanceDB table mirror at
    ``lancedb://md:cianfhoghlaim/ciancheiltis/en_gd_chunks``).
11. ``en_gd_pairs_seeded_check`` — the Phase 4 asset check that
    gates ≥ 0.70 RAGAS bilingual-pair coverage + ≥ 500 seeded pairs.
12. ``en_gd_app_health_check`` — the per-cycle Phase 4 compliance
    asset check that re-validates the R1-R4 conformance contract.

13. ``en_gv_chunks`` — the R1-R4 CocoIndex v1 Phase 5 App as a
    ``virtual`` asset (drives the LanceDB table mirror at
    ``lancedb://md:cianfhoghlaim/ciancheiltis/en_gv_chunks``).
14. ``en_gv_pairs_seeded_check`` — the Phase 5 asset check that
    gates ≥ 0.70 RAGAS bilingual-pair coverage + ≥ 500 seeded pairs.
15. ``en_gv_app_health_check`` — the per-cycle Phase 5 compliance
    asset check that re-validates the R1-R4 conformance contract.

16. ``en_ga_eu_chunks`` — the R1-R4 CocoIndex v1 Phase 6 App as a
    ``virtual`` asset (drives the LanceDB table mirror at
    ``lancedb://md:cianfhoghlaim/ciancheiltis/en_ga_eu_chunks``).
    The Phase 6 schema adds a ``language_availability`` ∈
    ``{"full", "partial", "summary_only"}`` first-class column per
    the umbrella spec's Phase 6 § first-class-column rule (EU-level
    coverage is **partial** for Irish — many EU documents exist
    only in English plus a "summary in Irish" rather than a full
    Irish translation; the ``language_availability`` tag is the
    critical signal here).
17. ``en_ga_eu_pairs_seeded_check`` — the Phase 6 asset check that
    gates ≥ 0.70 RAGAS bilingual-pair coverage + ≥ 500 seeded pairs.
18. ``en_ga_eu_app_health_check`` — the per-cycle Phase 6 compliance
    asset check that re-validates the R1-R4 conformance contract.

Reference: ``openspec/changes/2026-09-06-ciancheiltis-v1/`` + the
Phase 5 + Phase 6 extension at
``openspec/changes/2026-09-12-ciancheiltis-v2/``.
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
    en_cy_embedding,
    en_cy_embedding_flow,
)
from .ciancheiltis_en_cy_embedding import (  # noqa: E402 — module-level
    PHASE_LANGUAGE_PAIR as PHASE_LANGUAGE_PAIR_CY,
)
from .ciancheiltis_en_cy_embedding import (  # noqa: E402 — module-level
    PHASE_TABLE_URL as PHASE_TABLE_URL_CY,
)
from .ciancheiltis_en_ga_roi_embedding import (  # noqa: E402 — module-level
    CIANCHEILTIS_EN_GA_ROI_DUCKLAKE_TABLES,
    CIANCHEILTIS_EN_GA_ROI_THEMES,
    COCOINDEX_AVAILABLE,
    PHASE_LANGUAGE_PAIR_GA_ROI,
    PHASE_TABLE_URL_GA_ROI,
    en_ga_roi_embedding,
    en_ga_roi_embedding_flow,
    flow,
)
from .ciancheiltis_en_ga_ni_embedding import (  # noqa: E402 — module-level
    CIANCHEILTIS_EN_GA_NI_DUCKLAKE_TABLES,
    CIANCHEILTIS_EN_GA_NI_THEMES,
    EnGaNiChunk,
    PHASE_LANGUAGE_PAIR_GA_NI,
    PHASE_TABLE_URL_GA_NI,
    ciancheiltis_en_ga_ni_embedding,
    en_ga_ni_embedding_flow,
)
from .ciancheiltis_en_gd_embedding import (  # noqa: E402 — module-level
    CIANCHEILTIS_EN_GD_DUCKLAKE_TABLES,
    CIANCHEILTIS_EN_GD_THEMES,
    EnGdChunk,
    PHASE_LANGUAGE_PAIR_GD,
    PHASE_TABLE_URL_GD,
    ciancheiltis_en_gd_embedding,
    en_gd_embedding_flow,
)
from .ciancheiltis_en_gv_embedding import (  # noqa: E402 — module-level
    CIANCHEILTIS_EN_GV_DUCKLAKE_TABLES,
    CIANCHEILTIS_EN_GV_THEMES,
    EnGvChunk,
    PHASE_LANGUAGE_PAIR_GV,
    PHASE_TABLE_URL_GV,
    ciancheiltis_en_gv_embedding,
    en_gv_embedding_flow,
)
from .ciancheiltis_en_ga_eu_embedding import (  # noqa: E402 — module-level
    CIANCHEILTIS_EN_GA_EU_DUCKLAKE_TABLES,
    CIANCHEILTIS_EN_GA_EU_THEMES,
    EnGaEuChunk,
    PHASE_LANGUAGE_AVAILABILITY,
    PHASE_LANGUAGE_PAIR_GA_EU,
    PHASE_TABLE_URL_GA_EU,
    ciancheiltis_en_ga_eu_embedding,
    en_ga_eu_embedding_flow,
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
        "lance_table": PHASE_TABLE_URL_CY,
        "language_pair": PHASE_LANGUAGE_PAIR_CY,
        "themes": list(CIANCHEILTIS_EN_CY_THEMES),
        "ducklake_tables": dict(CIANCHEILTIS_EN_CY_DUCKLAKE_TABLES),
    }


def build_en_ga_roi_chunks_asset_spec() -> dict[str, Any]:
    """Build the Phase 2 asset spec dict for the L3 Component to wrap.

    Consumed by ``orchestration/defs/3_model_lifecycle/cocoindex_v1/
    ciancheiltis_en_ga_roi_embedding/defs.yaml`` (subagent 3's
    territory). Added by PR0.6 — mirrors
    ``build_en_cy_chunks_asset_spec`` for the Phase 2 en-ga / ROI
    CocoIndex App.
    """
    return {
        "app_name": "CiancheiltisEnGaRoiEmbedding",
        "module": "cocoindex_flows.british_isles.uk.ciancheiltis_en_ga_roi_embedding",
        "source": "ciancheiltis",
        "lance_table": PHASE_TABLE_URL_GA_ROI,
        "language_pair": PHASE_LANGUAGE_PAIR_GA_ROI,
        "themes": list(CIANCHEILTIS_EN_GA_ROI_THEMES),
        "ducklake_tables": dict(CIANCHEILTIS_EN_GA_ROI_DUCKLAKE_TABLES),
    }


def build_en_ga_ni_chunks_asset_spec() -> dict[str, Any]:
    """Build the Phase 3 asset spec dict for the L3 Component to wrap.

    Consumed by ``orchestration/defs/3_model_lifecycle/cocoindex_v1/
    ciancheiltis_en_ga_ni_embedding/defs.yaml`` (subagent 3's
    territory). Added by PR0.7 — mirrors
    ``build_en_ga_roi_chunks_asset_spec`` for the Phase 3 en-ga / NI
    CocoIndex App.

    Canonical example (per the umbrella spec's Northern Ireland row):
    ``https://www.legislation.gov.uk/uksi/2022/15/contents/made`` — the
    *Identity and Language (Northern Ireland) Act 2022*.
    """
    return {
        "app_name": "CiancheiltisEnGaNiEmbedding",
        "module": "cocoindex_flows.british_isles.uk.ciancheiltis_en_ga_ni_embedding",
        "source": "ciancheiltis",
        "lance_table": PHASE_TABLE_URL_GA_NI,
        "language_pair": PHASE_LANGUAGE_PAIR_GA_NI,
        "themes": list(CIANCHEILTIS_EN_GA_NI_THEMES),
        "ducklake_tables": dict(CIANCHEILTIS_EN_GA_NI_DUCKLAKE_TABLES),
    }


def build_en_gd_chunks_asset_spec() -> dict[str, Any]:
    """Build the Phase 4 asset spec dict for the L3 Component to wrap.

    Consumed by ``orchestration/defs/3_model_lifecycle/cocoindex_v1/
    ciancheiltis_en_gd_embedding/defs.yaml`` (subagent 3's territory).
    Added by PR0.8 — mirrors ``build_en_ga_ni_chunks_asset_spec`` for
    the Phase 4 en-gd / Scotland CocoIndex App.

    Canonical example (per the umbrella spec's Scotland row):
    ``https://www.gaidhlig.scot/bord-na-gaidhlig/naidheachdan/`` —
    Bòrd na Gàidhlig under the Gaelic Language (Scotland) Act 2005
    (``https://www.legislation.gov.uk/asp/2005/7/contents``).
    """
    return {
        "app_name": "CiancheiltisEnGdEmbedding",
        "module": "cocoindex_flows.british_isles.uk.ciancheiltis_en_gd_embedding",
        "source": "ciancheiltis",
        "lance_table": PHASE_TABLE_URL_GD,
        "language_pair": PHASE_LANGUAGE_PAIR_GD,
        "themes": list(CIANCHEILTIS_EN_GD_THEMES),
        "ducklake_tables": dict(CIANCHEILTIS_EN_GD_DUCKLAKE_TABLES),
    }


def build_en_gv_chunks_asset_spec() -> dict[str, Any]:
    """Build the Phase 5 asset spec dict for the L3 Component to wrap.

    Consumed by ``orchestration/defs/3_model_lifecycle/cocoindex_v1/
    ciancheiltis_en_gv_embedding/defs.yaml`` (subagent 3's territory).
    Added by PR0.9 — mirrors ``build_en_gd_chunks_asset_spec`` for
    the Phase 5 en-gv / Isle of Man CocoIndex App.

    Canonical example (per the umbrella spec's Isle of Man row +
    ``dlt_sources/ciancheiltis/en_gv/__init__.py``):
    ``https://www.culturevannin.im/learn-gaelg/`` — Culture Vannin,
    the Manx cultural foundation. Manx (Gaelg) is in **revival
    status** — no statutory bilingual publication duty and no
    statutory commissioner. The Phase 5 strict-gate is "capture what
    bilingual content exists and surface it faithfully".
    """
    return {
        "app_name": "CiancheiltisEnGvEmbedding",
        "module": "cocoindex_flows.british_isles.uk.ciancheiltis_en_gv_embedding",
        "source": "ciancheiltis",
        "lance_table": PHASE_TABLE_URL_GV,
        "language_pair": PHASE_LANGUAGE_PAIR_GV,
        "themes": list(CIANCHEILTIS_EN_GV_THEMES),
        "ducklake_tables": dict(CIANCHEILTIS_EN_GV_DUCKLAKE_TABLES),
    }


def build_en_ga_eu_chunks_asset_spec() -> dict[str, Any]:
    """Build the Phase 6 asset spec dict for the L3 Component to wrap.

    Consumed by ``orchestration/defs/3_model_lifecycle/cocoindex_v1/
    ciancheiltis_en_ga_eu_embedding/defs.yaml`` (subagent 3's
    territory). Added by PR0.10 — mirrors
    ``build_en_gv_chunks_asset_spec`` for the Phase 6 en-ga / EU
    level CocoIndex App.

    The Phase 6 schema adds a ``language_availability`` ∈
    ``{"full", "partial", "summary_only"}`` first-class column per
    the umbrella spec's Phase 6 § first-class-column rule; this is
    exposed in the asset spec dict via the ``language_availability``
    key so subagent 3 can wire it into the Phase 6 Dagster asset
    + asset checks (the column is the critical signal for the
    partial EU-level Irish coverage).

    Canonical example (per the umbrella spec's EU level row +
    ``dlt_sources/ciancheiltis/en_ga_eu/__init__.py``):
    ``https://eur-lex.europa.eu/legal-content/GA/TXT/?uri=CELEX:12012E``
    — the Treaty on European Union, Irish-language edition. EU-level
    coverage is **partial** for Irish — many EU documents exist
    only in English plus a "summary in Irish" rather than a full
    Irish translation.
    """
    return {
        "app_name": "CiancheiltisEnGaEuEmbedding",
        "module": "cocoindex_flows.british_isles.uk.ciancheiltis_en_ga_eu_embedding",
        "source": "ciancheiltis",
        "lance_table": PHASE_TABLE_URL_GA_EU,
        "language_pair": PHASE_LANGUAGE_PAIR_GA_EU,
        "themes": list(CIANCHEILTIS_EN_GA_EU_THEMES),
        "ducklake_tables": dict(CIANCHEILTIS_EN_GA_EU_DUCKLAKE_TABLES),
        "language_availability": PHASE_LANGUAGE_AVAILABILITY,
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


def iter_en_ga_roi_bilingual_pages() -> Iterator[dict[str, Any]]:
    """Re-export the Phase 2 bilingual-page yielder for the L2 materials layer.

    Phase 2 mirror of ``iter_bilingual_pages`` (which is Phase 1
    en-cy / Wales). Added by PR0.6.
    """
    # Local import to avoid a top-level side effect when CocoIndex is
    # absent.
    from .ciancheiltis_en_ga_roi_embedding import _yield_bilingual_pages

    yield from _yield_bilingual_pages()


def iter_en_ga_ni_bilingual_pages() -> Iterator[dict[str, Any]]:
    """Re-export the Phase 3 bilingual-page yielder for the L2 materials layer.

    Phase 3 mirror of ``iter_bilingual_pages`` (Phase 1 en-cy / Wales)
    + ``iter_en_ga_roi_bilingual_pages`` (Phase 2 en-ga / ROI). Added
    by PR0.7.
    """
    # Local import to avoid a top-level side effect when CocoIndex is
    # absent.
    from .ciancheiltis_en_ga_ni_embedding import _yield_bilingual_pages

    yield from _yield_bilingual_pages()


def iter_en_gd_bilingual_pages() -> Iterator[dict[str, Any]]:
    """Re-export the Phase 4 bilingual-page yielder for the L2 materials layer.

    Phase 4 mirror of ``iter_bilingual_pages`` (Phase 1 en-cy / Wales)
    + ``iter_en_ga_roi_bilingual_pages`` (Phase 2 en-ga / ROI) +
    ``iter_en_ga_ni_bilingual_pages`` (Phase 3 en-ga / NI). Added
    by PR0.8.
    """
    # Local import to avoid a top-level side effect when CocoIndex is
    # absent.
    from .ciancheiltis_en_gd_embedding import _yield_bilingual_pages

    yield from _yield_bilingual_pages()


def iter_en_gv_bilingual_pages() -> Iterator[dict[str, Any]]:
    """Re-export the Phase 5 bilingual-page yielder for the L2 materials layer.

    Phase 5 mirror of ``iter_bilingual_pages`` (Phase 1 en-cy / Wales)
    + ``iter_en_ga_roi_bilingual_pages`` (Phase 2 en-ga / ROI) +
    ``iter_en_ga_ni_bilingual_pages`` (Phase 3 en-ga / NI) +
    ``iter_en_gd_bilingual_pages`` (Phase 4 en-gd / Scotland). Added
    by PR0.9.
    """
    # Local import to avoid a top-level side effect when CocoIndex is
    # absent.
    from .ciancheiltis_en_gv_embedding import _yield_bilingual_pages

    yield from _yield_bilingual_pages()


def iter_en_ga_eu_bilingual_pages() -> Iterator[dict[str, Any]]:
    """Re-export the Phase 6 bilingual-page yielder for the L2 materials layer.

    Phase 6 mirror of ``iter_bilingual_pages`` (Phase 1 en-cy / Wales)
    + ``iter_en_ga_roi_bilingual_pages`` (Phase 2 en-ga / ROI) +
    ``iter_en_ga_ni_bilingual_pages`` (Phase 3 en-ga / NI) +
    ``iter_en_gd_bilingual_pages`` (Phase 4 en-gd / Scotland) +
    ``iter_en_gv_bilingual_pages`` (Phase 5 en-gv / Isle of Man).
    Added by PR0.10.

    Note: the Phase 6 yielder carries the ``language_availability``
    ∈ ``{"full", "partial", "summary_only"}`` tag per the umbrella
    spec's Phase 6 § first-class-column rule (EU-level coverage is
    **partial** for Irish — many EU documents exist only in English
    plus a "summary in Irish" rather than a full Irish translation).
    """
    # Local import to avoid a top-level side effect when CocoIndex is
    # absent.
    from .ciancheiltis_en_ga_eu_embedding import _yield_bilingual_pages

    yield from _yield_bilingual_pages()


__all__ = [
    "CIANCHEILTIS_EN_CY_DUCKLAKE_TABLES",
    "CIANCHEILTIS_EN_CY_THEMES",
    "CIANCHEILTIS_EN_GA_EU_DUCKLAKE_TABLES",
    "CIANCHEILTIS_EN_GA_EU_THEMES",
    "CIANCHEILTIS_EN_GA_NI_DUCKLAKE_TABLES",
    "CIANCHEILTIS_EN_GA_NI_THEMES",
    "CIANCHEILTIS_EN_GA_ROI_DUCKLAKE_TABLES",
    "CIANCHEILTIS_EN_GA_ROI_THEMES",
    "CIANCHEILTIS_EN_GD_DUCKLAKE_TABLES",
    "CIANCHEILTIS_EN_GD_THEMES",
    "CIANCHEILTIS_EN_GV_DUCKLAKE_TABLES",
    "CIANCHEILTIS_EN_GV_THEMES",
    "COCOINDEX_AVAILABLE",
    "EnGaEuChunk",
    "EnGaNiChunk",
    "EnGdChunk",
    "EnGvChunk",
    "PHASE_LANGUAGE_AVAILABILITY",
    "PHASE_LANGUAGE_PAIR_CY",
    "PHASE_LANGUAGE_PAIR_GA_EU",
    "PHASE_LANGUAGE_PAIR_GA_NI",
    "PHASE_LANGUAGE_PAIR_GA_ROI",
    "PHASE_LANGUAGE_PAIR_GD",
    "PHASE_LANGUAGE_PAIR_GV",
    "PHASE_TABLE_URL_CY",
    "PHASE_TABLE_URL_GA_EU",
    "PHASE_TABLE_URL_GA_NI",
    "PHASE_TABLE_URL_GA_ROI",
    "PHASE_TABLE_URL_GD",
    "PHASE_TABLE_URL_GV",
    "build_en_cy_chunks_asset_spec",
    "build_en_ga_eu_chunks_asset_spec",
    "build_en_ga_ni_chunks_asset_spec",
    "build_en_ga_roi_chunks_asset_spec",
    "build_en_gd_chunks_asset_spec",
    "build_en_gv_chunks_asset_spec",
    "ciancheiltis_en_ga_eu_embedding",
    "ciancheiltis_en_ga_ni_embedding",
    "ciancheiltis_en_gd_embedding",
    "ciancheiltis_en_gv_embedding",
    "en_cy_embedding",
    "en_cy_embedding_flow",
    "en_ga_eu_embedding_flow",
    "en_ga_ni_embedding_flow",
    "en_ga_roi_embedding",
    "en_ga_roi_embedding_flow",
    "en_gd_embedding_flow",
    "en_gv_embedding_flow",
    "flow",
    "iter_bilingual_pages",
    "iter_en_ga_eu_bilingual_pages",
    "iter_en_ga_ni_bilingual_pages",
    "iter_en_ga_roi_bilingual_pages",
    "iter_en_gd_bilingual_pages",
    "iter_en_gv_bilingual_pages",
]
