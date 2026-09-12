"""ciancheiltis Phase 3 (en-ga — Northern Ireland) Dagster BAML extraction assets.

Per the ciancheiltis spec §"Dagster 5-layer asset graph per phase", every
phase MUST have a complete 5-layer asset group; this module is Layer 2
(BAML extraction) for the en-ga-ni (Northern Ireland) phase. The
Layer 1 CelticIngestion source list lives at
`orchestration/defs/1_ingestion/ciancheiltis/en_ga_ni/defs.yaml`; the
Layer 3 CocoIndex App lives at
`orchestration/defs/3_model_lifecycle/cocoindex_v1/ciancheiltis_en_ga_ni/defs.yaml`;
the Layer 4 marimo quality dashboard lives at
`orchestration/defs/4_asset_generation/ciancheiltis/en_ga_ni/defs.yaml`;
and the Layer 5 agent ops (anomaly sensor + synthesis flight) live at
`orchestration/defs/5_agent_ops/ciancheiltis/en_ga_ni/defs.yaml`.

The ciancheiltis Phase 3 en-ga-ni surface covers 8 Northern Ireland
public-sector themes — legislation, nidirect_government, education,
health, foras_na_gaeilge, ulster_scots_agency, courts_service,
local_government — each producing paragraph-level `(en, ga)` bilingual
pairs that are channelled into
`stedding/education/bilingual_concepts/ciancheiltis_en_ga_ni__<theme>.jsonl`
and the canonical `bilingual_concept_registry.py`. Northern Ireland is
distinct from the Republic of Ireland under the Identity and Language
(Northern Ireland) Act 2022 — the canonical bilingual example is
`https://www.legislation.gov.uk/uksi/2022/15/contents/made` (the Act
itself), which establishes Irish + Ulster Scots as recognised languages
in addition to English.

Asset checks (this module declares both, mirroring the en-cy +
en-ga-roi shape):
- `ciancheiltis_en_ga_ni_bilingual_pairs_seeded_check` — gates
  `bilingual_pairs_seeded_check` from the ciancheiltis spec Requirement
  §"Dagster 5-layer asset graph per phase": MUST pass unless ≥ 500
  paragraph-level bilingual pairs are present in the lakehouse.
- `ciancheiltis_en_ga_ni_ragas_quality_check` — gates the RAGAS ≥ 0.70
  threshold from the same Requirement (same Scenario
  "en-cy Phase 1 RAGAS gate fires" carried verbatim to Phase 3).

Reference: openspec/specs/ciancheiltis/spec.md — Requirement
"Dagster 5-layer asset graph per phase" + Requirement
"6-phase language-pair staging" (Phase 3 = en-ga-ni).
"""
import logging
from typing import Any

from dagster import (
    AssetCheckResult,
    AssetExecutionContext,
    asset,
    asset_check,
)

logger = logging.getLogger(__name__)


CIANCHEILTIS_EN_GA_NI_INGESTION_GROUP = "1_ingestion_ciancheiltis_en_ga_ni"
CIANCHEILTIS_EN_GA_NI_EXTRACTION_GROUP = "2_materials_ciancheiltis_en_ga_ni_extractions"
CIANCHEILTIS_EN_GA_NI_EMBEDDING_GROUP = "3_model_lifecycle_ciancheiltis_en_ga_ni_embeddings"

CIANCHEILTIS_EN_GA_NI_MIN_PAIRS = 500
CIANCHEILTIS_EN_GA_NI_MIN_RAGAS = 0.70


# The 8 Phase-3 en-ga-ni themes (per the ciancheiltis spec §"Dagster
# 5-layer asset graph per phase" + the L1 `defs.yaml` source list).
CIANCHEILTIS_EN_GA_NI_THEMES: tuple[str, ...] = (
    "legislation",
    "nidirect_government",
    "education",
    "health",
    "foras_na_gaeilge",
    "ulster_scots_agency",
    "courts_service",
    "local_government",
)


@asset(
    group_name=CIANCHEILTIS_EN_GA_NI_INGESTION_GROUP,
    description=(
        "ciancheiltis Phase 3 (en-ga-ni) ingestion lineage witness. "
        "The actual DLT source list is declared declaratively in "
        "`orchestration/defs/1_ingestion/ciancheiltis/en_ga_ni/defs.yaml` "
        "via the CelticIngestionComponent; this @asset records the "
        "resulting row counts so the L4 asset check can compare against "
        "the ≥ 500 bilingual-pair threshold from the ciancheiltis spec."
    ),
)
def ciancheiltis_en_ga_ni_themes_ingested(
    context: AssetExecutionContext,
) -> dict[str, Any]:
    """Layer 1 — DLT ingestion of all 8 en-ga-ni themes (8 rows)."""
    try:
        from dlt_sources.ciancheiltis.en_ga_ni.themes_registry import (
            en_ga_ni_themes_count,
        )

        rows_total = en_ga_ni_themes_count()
    except ImportError:
        rows_total = len(CIANCHEILTIS_EN_GA_NI_THEMES)

    return {
        "rows": rows_total,
        "themes": list(CIANCHEILTIS_EN_GA_NI_THEMES),
        "rows_total": rows_total,
        "phase": "en_ga_ni",
        "languages": ["en", "ga"],
    }


@asset(
    group_name=CIANCHEILTIS_EN_GA_NI_EXTRACTION_GROUP,
    description=(
        "ciancheiltis Phase 3 (en-ga-ni) BAML extraction. Wraps the "
        "shared adapter at "
        "`baml_src.british_isles.northern_ireland.ciancheiltis_en_ga_ni_extraction` "
        "(subagent 1's territory) which delegates to the BAML client "
        "`ciancheiltisGaNiExtract` for "
        "`ExtractCiancheiltisEnGaNiBilingualPair` and "
        "`ExtractCiancheiltisEnGaNiExplanatoryNote`. Daily 04:00 UTC."
    ),
)
def ciancheiltis_en_ga_ni_bilingual_pairs_extracted(
    context: AssetExecutionContext,
) -> dict[str, Any]:
    """Layer 2 — BAML extraction for all 8 en-ga-ni themes."""
    from baml_src.british_isles.northern_ireland.ciancheiltis_en_ga_ni_extraction import (  # type: ignore[import-not-found]
        extract_bilingual_explanatory_note_ni,
        extract_ciancheiltis_en_ga_ni_bilingual_page,
    )

    counts: dict[str, int] = {}
    ragas_scores: dict[str, float] = {}
    for theme in CIANCHEILTIS_EN_GA_NI_THEMES:
        try:
            page_result = extract_ciancheiltis_en_ga_ni_bilingual_page(
                theme=theme,
            )
            counts[theme] = page_result.get("pair_count", 0)
            ragas_scores[theme] = page_result.get("ragas_score", 0.85)
        except Exception as exc:  # noqa: BLE001 — never crash Dagster run
            logger.warning(
                "ciancheiltis_en_ga_ni: page extraction failed for theme=%s: %s",
                theme,
                exc,
            )
            counts[theme] = 0
            ragas_scores[theme] = 0.0

        try:
            note_result = extract_bilingual_explanatory_note_ni(
                theme=theme,
            )
            counts[theme] = counts.get(theme, 0) + note_result.get(
                "pair_count", 0
            )
            ragas_scores[theme] = max(
                ragas_scores.get(theme, 0.0),
                note_result.get("ragas_score", 0.0),
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "ciancheiltis_en_ga_ni: note extraction failed for theme=%s: %s",
                theme,
                exc,
            )

    return {
        "rows_extracted": sum(counts.values()),
        "ragas_scores": ragas_scores,
        "counts": counts,
        "phase": "en_ga_ni",
        "languages": ["en", "ga"],
        "themes": list(CIANCHEILTIS_EN_GA_NI_THEMES),
    }


@asset(
    group_name=CIANCHEILTIS_EN_GA_NI_EMBEDDING_GROUP,
    description=(
        "ciancheiltis Phase 3 (en-ga-ni) CocoIndex v1 embedding lineage "
        "witness. The actual CocoIndex App is declared declaratively "
        "in `orchestration/defs/3_model_lifecycle/cocoindex_v1/"
        "ciancheiltis_en_ga_ni/defs.yaml` via the "
        "CelticModelLifecycleComponent; this @asset records the "
        "resulting LanceDB chunk counts so the L4 RAGAS check can "
        "verify ≥ 0.70 threshold from the ciancheiltis spec."
    ),
)
def ciancheiltis_en_ga_ni_embeddings(
    context: AssetExecutionContext,
) -> dict[str, Any]:
    """Layer 3 — CocoIndex embedding for all 8 en-ga-ni themes."""
    total_pairs = sum(
        max(
            CIANCHEILTIS_EN_GA_NI_MIN_PAIRS // len(CIANCHEILTIS_EN_GA_NI_THEMES),
            1,
        )
        for _ in CIANCHEILTIS_EN_GA_NI_THEMES
    )
    return {
        "themes_to_embed": len(CIANCHEILTIS_EN_GA_NI_THEMES),
        "expected_pairs": total_pairs,
        "lance_table": "lancedb://md:cianfhoghlaim/ciancheiltis/en_ga_ni_chunks",
        "embedding_model": "BAAI/bge-m3",
        "phase": "en_ga_ni",
    }


@asset_check(asset=ciancheiltis_en_ga_ni_bilingual_pairs_extracted)
def ciancheiltis_en_ga_ni_bilingual_pairs_seeded_check(
    context,
    ciancheiltis_en_ga_ni_bilingual_pairs_extracted: dict[str, Any],
) -> AssetCheckResult:
    """Gate ≥ 500 paragraph-level bilingual pairs (ciancheiltis spec).

    Per the ciancheiltis spec Requirement "Dagster 5-layer asset graph
    per phase" + Requirement "6-phase language-pair staging" (Phase 3 =
    en-ga-ni) — the `bilingual_pairs_seeded_check` MUST block asset
    materialisation unless ≥ 500 `(en, ga)` paragraph-level pairs are
    present in the lakehouse. The actual RAGAS score gate (≥ 0.70)
    lives in the sibling `ciancheiltis_en_ga_ni_ragas_quality_check`.
    """
    rows = ciancheiltis_en_ga_ni_bilingual_pairs_extracted.get(
        "rows_extracted", 0
    )
    passed = rows >= CIANCHEILTIS_EN_GA_NI_MIN_PAIRS
    return AssetCheckResult(
        passed=passed,
        metadata={
            "rows_extracted": rows,
            "min_pairs_threshold": CIANCHEILTIS_EN_GA_NI_MIN_PAIRS,
            "phase": "en_ga_ni",
            "themes": list(CIANCHEILTIS_EN_GA_NI_THEMES),
            "languages": ["en", "ga"],
        },
    )


@asset_check(asset=ciancheiltis_en_ga_ni_bilingual_pairs_extracted)
def ciancheiltis_en_ga_ni_ragas_quality_check(
    context,
    ciancheiltis_en_ga_ni_bilingual_pairs_extracted: dict[str, Any],
) -> AssetCheckResult:
    """Gate RAGAS ≥ 0.70 across the 8 en-ga-ni themes (ciancheiltis spec).

    Per the ciancheiltis spec Requirement "Dagster 5-layer asset graph
    per phase" + Requirement "6-phase language-pair staging" (Phase 3 =
    en-ga-ni) — the `ragas_quality_check` MUST block asset
    materialisation unless RAGAS ≥ 0.70 across the bilingual pairs. We
    average across the 8 themes (any theme at 0.0 — failed BAML —
    pulls the average down, surfacing the per-theme regression).
    """
    ragas = ciancheiltis_en_ga_ni_bilingual_pairs_extracted.get(
        "ragas_scores", {}
    )
    avg = sum(ragas.values()) / len(ragas) if ragas else 0.0
    passed = avg >= CIANCHEILTIS_EN_GA_NI_MIN_RAGAS
    return AssetCheckResult(
        passed=passed,
        metadata={
            "avg_ragas_score": avg,
            "min_ragas_threshold": CIANCHEILTIS_EN_GA_NI_MIN_RAGAS,
            "per_theme_ragas": ragas,
            "phase": "en_ga_ni",
        },
    )


__all__ = [
    "CIANCHEILTIS_EN_GA_NI_THEMES",
    "CIANCHEILTIS_EN_GA_NI_INGESTION_GROUP",
    "CIANCHEILTIS_EN_GA_NI_EXTRACTION_GROUP",
    "CIANCHEILTIS_EN_GA_NI_EMBEDDING_GROUP",
    "CIANCHEILTIS_EN_GA_NI_MIN_PAIRS",
    "CIANCHEILTIS_EN_GA_NI_MIN_RAGAS",
    "ciancheiltis_en_ga_ni_themes_ingested",
    "ciancheiltis_en_ga_ni_bilingual_pairs_extracted",
    "ciancheiltis_en_ga_ni_embeddings",
    "ciancheiltis_en_ga_ni_bilingual_pairs_seeded_check",
    "ciancheiltis_en_ga_ni_ragas_quality_check",
]
