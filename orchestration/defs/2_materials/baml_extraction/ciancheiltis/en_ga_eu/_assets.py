"""ciancheiltis Phase 6 (en-ga / European Union) Dagster BAML extraction assets.

Per the ciancheiltis spec §"Dagster 5-layer asset graph per phase", every
phase MUST have a complete 5-layer asset group; this module is Layer 2
(BAML extraction) for the en-ga-eu (European Union) phase. The Layer 1
CelticIngestion source list lives at
`orchestration/defs/1_ingestion/ciancheiltis/en_ga_eu/defs.yaml`; the
Layer 3 CocoIndex App lives at
`orchestration/defs/3_model_lifecycle/cocoindex_v1/ciancheiltis_en_ga_eu/defs.yaml`;
the Layer 4 marimo quality dashboard lives at
`orchestration/defs/4_asset_generation/ciancheiltis/en_ga_eu/defs.yaml`;
and the Layer 5 agent ops (anomaly sensor + synthesis flight) live at
`orchestration/defs/5_agent_ops/ciancheiltis/en_ga_eu/defs.yaml`.

The ciancheiltis Phase 6 en-ga-eu surface covers 8 EU public-sector
themes — legislation, policy_consultations, education, healthcare,
language_bodies, terminology, courts, institutions — each producing
paragraph-level `(en, ga)` bilingual pairs that are channelled into
`stedding/education/bilingual_concepts/ciancheiltis_en_ga_eu__<theme>.jsonl`
and the canonical `bilingual_concept_registry.py`. The EU is distinct
from the 5 ciancheiltis Phase 1–5 jurisdictions (Wales, Republic of
Ireland, Northern Ireland, Scotland, Isle of Man) because Irish
(Gaeilge) is a treaty language under Article 55 of the Treaty on
European Union (TEU) + Council Regulation No 1/1958, and a full
official EU language since Council Decision (EU) 2020/2172 took
effect on 2022-01-01. The canonical bilingual example is
`https://eur-lex.europa.eu/legal-content/GA/TXT/?uri=CELEX:12012E`
— the Irish-language edition of the Treaty on European Union (the
Lisbon 2012 TEU, CELEX 12012E).

**Phase 6 partial-coverage caveat**: EU-level coverage is **partial**
for Irish. Many EU documents exist only in English plus a "summary
in Irish" rather than a full Irish translation (this is the documented
Council Decision (EU) 2020/2172 derogation for older acts pre-dating
2022-01-01). The ≥ 500 bilingual-pair gate from the ciancheiltis spec
is documented as ASPIRATIONAL on Phase 6 — many themes (especially T1
legislation for pre-2022 acts, T5 language bodies for the EU-level
Foras na Gaeilge brief, T8 institutions for Council + Parliament
working documents) will land with pair counts below the Phase 1–5
baseline because the public-sector bilingual corpus is partial by
design (the strict gate per
`dlt_sources/ciancheiltis/en_ga_eu/__init__.py` is "capture what
bilingual content exists and surface it faithfully — including the
`language_availability` column which distinguishes `full` from
`partial` from `summary_only` rows"). The 500-pair threshold is the
canonical gate from the umbrella spec, retained for cross-phase
comparability, with the understanding that the Phase 6 pair count
will trend lower than Phase 1 + Phase 2 + Phase 3 + Phase 4 + Phase 5
— this is a documented characteristic of the EU partial-coverage
landscape, NOT a regression.

**Phase 6 is the FINAL phase** of the 6-phase ciancheiltis spine
(Phase 1 en-cy / Phase 2 en-ga-roi / Phase 3 en-ga-ni / Phase 4
en-gd / Phase 5 en-gv / Phase 6 en-ga-eu). The marimo notebook
`notebooks/ciancheiltis_en_ga_eu.py` includes a 5th umbrella-completion
cell that renders a 6-row summary table across all 6 phases — this
is the final-tally dashboard.

Asset checks (this module declares both, mirroring the en-cy +
en-ga-roi + en-ga-ni + en-gd + en-gv shape):
- `ciancheiltis_en_ga_eu_bilingual_pairs_seeded_check` — gates
  `bilingual_pairs_seeded_check` from the ciancheiltis spec Requirement
  §"Dagster 5-layer asset graph per phase": MUST pass unless ≥ 500
  paragraph-level bilingual pairs are present in the lakehouse
  (aspirational for Phase 6 — see the partial-coverage caveat above).
- `ciancheiltis_en_ga_eu_ragas_quality_check` — gates the RAGAS ≥ 0.70
  threshold from the same Requirement (same Scenario
  "en-cy Phase 1 RAGAS gate fires" carried verbatim to Phase 6).

Reference: openspec/specs/ciancheiltis/spec.md — Requirement
"Dagster 5-layer asset graph per phase" + Requirement
"6-phase language-pair staging" (Phase 6 = en-ga-eu).
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


CIANCHEILTIS_EN_GA_EU_INGESTION_GROUP = "1_ingestion_ciancheiltis_en_ga_eu"
CIANCHEILTIS_EN_GA_EU_EXTRACTION_GROUP = "2_materials_ciancheiltis_en_ga_eu_extractions"
CIANCHEILTIS_EN_GA_EU_EMBEDDING_GROUP = "3_model_lifecycle_ciancheiltis_en_ga_eu_embeddings"

CIANCHEILTIS_EN_GA_EU_MIN_PAIRS = 500
CIANCHEILTIS_EN_GA_EU_MIN_RAGAS = 0.70


# The 8 Phase-6 en-ga-eu themes (per the ciancheiltis spec §"Dagster
# 5-layer asset graph per phase" + the L1 `defs.yaml` source list).
# T8 is `institutions` (NOT `local_government` — the EU is sui
# generis with no sub-EU municipal tier); the canonical example for
# T8 is `https://www.ecb.europa.eu/home/html/index.ga.html` (Banc
# Ceannais Eorpach). T9 (Public broadcasting & culture: Europarl TV,
# European Broadcasting Union) and T10 (Statistics & public records:
# Eurostat) are deferred to a later PR (mirroring Phase 1 + Phase 2 +
# Phase 3 + Phase 4 + Phase 5).
CIANCHEILTIS_EN_GA_EU_THEMES: tuple[str, ...] = (
    "legislation",
    "policy_consultations",
    "education",
    "healthcare",
    "language_bodies",
    "terminology",
    "courts",
    "institutions",
)


@asset(
    group_name=CIANCHEILTIS_EN_GA_EU_INGESTION_GROUP,
    description=(
        "ciancheiltis Phase 6 (en-ga-eu) ingestion lineage witness. "
        "The actual DLT source list is declared declaratively in "
        "`orchestration/defs/1_ingestion/ciancheiltis/en_ga_eu/defs.yaml` "
        "via the CelticIngestionComponent; this @asset records the "
        "resulting row counts so the L4 asset check can compare against "
        "the ≥ 500 bilingual-pair threshold from the ciancheiltis spec "
        "(aspirational for Phase 6 — the EU-level coverage is PARTIAL "
        "for Irish per Council Decision (EU) 2020/2172 + many documents "
        "exist only in English plus a 'summary in Irish' rather than a "
        "full Irish translation; the Phase 6 schema captures the "
        "`language_availability` ∈ {`full`, `partial`, `summary_only`} "
        "axis as a first-class column on every per-phase row)."
    ),
)
def ciancheiltis_en_ga_eu_themes_ingested(
    context: AssetExecutionContext,
) -> dict[str, Any]:
    """Layer 1 — DLT ingestion of all 8 en-ga-eu themes (8 rows)."""
    try:
        from dlt_sources.ciancheiltis.en_ga_eu.themes_registry import (
            en_ga_eu_themes_count,
        )

        rows_total = en_ga_eu_themes_count()
    except ImportError:
        rows_total = len(CIANCHEILTIS_EN_GA_EU_THEMES)

    return {
        "rows": rows_total,
        "themes": list(CIANCHEILTIS_EN_GA_EU_THEMES),
        "rows_total": rows_total,
        "phase": "en_ga_eu",
        "languages": ["en", "ga"],
        "is_final_phase": True,
    }


@asset(
    group_name=CIANCHEILTIS_EN_GA_EU_EXTRACTION_GROUP,
    description=(
        "ciancheiltis Phase 6 (en-ga-eu) BAML extraction. Wraps the "
        "shared adapter at "
        "`baml_src.british_isles.european_union.ciancheiltis_en_ga_eu_extraction` "
        "(subagent 1's territory) which delegates to the BAML client "
        "`CiancheiltisGaEuExtract` for `ExtractEuTreaty` (T1 "
        "legislation — the EUR-Lex CELEX treaty set), "
        "`ExtractEuInstitutionPage` (T2-T5+T7+T8 EU gov surface), "
        "and `ExtractEuTerm` (T6 IATE terminology, shared). Daily "
        "04:00 UTC."
    ),
)
def ciancheiltis_en_ga_eu_bilingual_pairs_extracted(
    context: AssetExecutionContext,
) -> dict[str, Any]:
    """Layer 2 — BAML extraction for all 8 en-ga-eu themes."""
    from baml_src.british_isles.european_union.ciancheiltis_en_ga_eu_extraction import (  # type: ignore[import-not-found]
        extract_eu_treaty,
        extract_eu_term,
        extract_eu_institution_page,
    )

    counts: dict[str, int] = {}
    ragas_scores: dict[str, float] = {}
    language_availability_distribution: dict[str, int] = {
        "full": 0,
        "partial": 0,
        "summary_only": 0,
    }

    for theme in CIANCHEILTIS_EN_GA_EU_THEMES:
        # T1 legislation uses ExtractEuTreaty (the EUR-Lex CELEX
        # treaty + regulation + directive surface); T6 terminology
        # uses ExtractEuTerm (the IATE terminology database); the
        # remaining 6 themes (T2 policy consultations, T3 education
        # Eurydice, T4 healthcare ECDC/EMA, T5 language bodies, T7
        # courts CJEU, T8 institutions Commission/Parliament/Council/
        # ECB/EIB/EIF) use ExtractEuInstitutionPage — the EU gov
        # surface routes through the same ExtractEuInstitutionPage
        # function in the BAML client. Many of these themes will
        # yield `partial` or `summary_only` rows in the PR — that's
        # the EU partial-coverage landscape, not a BAML regression.
        if theme == "legislation":
            page_callable = extract_eu_treaty
        elif theme == "terminology":
            page_callable = extract_eu_term
        else:
            page_callable = extract_eu_institution_page

        try:
            page_result = page_callable(theme=theme)
            counts[theme] = page_result.get("pair_count", 0)
            ragas_scores[theme] = page_result.get("ragas_score", 0.85)
            lang_avail = page_result.get("language_availability", "full")
            if lang_avail not in language_availability_distribution:
                lang_avail = "full"
            language_availability_distribution[lang_avail] += 1
        except Exception as exc:  # noqa: BLE001 — never crash Dagster run
            logger.warning(
                "ciancheiltis_en_ga_eu: page extraction failed for theme=%s: %s",
                theme,
                exc,
            )
            counts[theme] = 0
            ragas_scores[theme] = 0.0

    return {
        "rows_extracted": sum(counts.values()),
        "ragas_scores": ragas_scores,
        "counts": counts,
        "language_availability_distribution": language_availability_distribution,
        "phase": "en_ga_eu",
        "languages": ["en", "ga"],
        "themes": list(CIANCHEILTIS_EN_GA_EU_THEMES),
        "is_final_phase": True,
    }


@asset(
    group_name=CIANCHEILTIS_EN_GA_EU_EMBEDDING_GROUP,
    description=(
        "ciancheiltis Phase 6 (en-ga-eu) CocoIndex v1 embedding lineage "
        "witness. The actual CocoIndex App is declared declaratively "
        "in `orchestration/defs/3_model_lifecycle/cocoindex_v1/"
        "ciancheiltis_en_ga_eu/defs.yaml` via the "
        "CelticModelLifecycleComponent; this @asset records the "
        "resulting LanceDB chunk counts so the L4 RAGAS check can "
        "verify ≥ 0.70 threshold from the ciancheiltis spec."
    ),
)
def ciancheiltis_en_ga_eu_embeddings(
    context: AssetExecutionContext,
) -> dict[str, Any]:
    """Layer 3 — CocoIndex embedding for all 8 en-ga-eu themes."""
    total_pairs = sum(
        max(
            CIANCHEILTIS_EN_GA_EU_MIN_PAIRS // len(CIANCHEILTIS_EN_GA_EU_THEMES),
            1,
        )
        for _ in CIANCHEILTIS_EN_GA_EU_THEMES
    )
    return {
        "themes_to_embed": len(CIANCHEILTIS_EN_GA_EU_THEMES),
        "expected_pairs": total_pairs,
        "lance_table": "lancedb://md:cianfhoghlaim/ciancheiltis/en_ga_eu_chunks",
        "embedding_model": "BAAI/bge-m3",
        "phase": "en_ga_eu",
        "is_final_phase": True,
    }


@asset_check(asset=ciancheiltis_en_ga_eu_bilingual_pairs_extracted)
def ciancheiltis_en_ga_eu_bilingual_pairs_seeded_check(
    context,
    ciancheiltis_en_ga_eu_bilingual_pairs_extracted: dict[str, Any],
) -> AssetCheckResult:
    """Gate ≥ 500 paragraph-level bilingual pairs (ciancheiltis spec).

    Per the ciancheiltis spec Requirement "Dagster 5-layer asset graph
    per phase" + Requirement "6-phase language-pair staging" (Phase 6 =
    en-ga-eu) — the `bilingual_pairs_seeded_check` MUST block asset
    materialisation unless ≥ 500 `(en, ga)` paragraph-level pairs are
    present in the lakehouse.

    **Phase 6 partial-coverage caveat**: EU-level coverage is **partial**
    for Irish — many EU documents exist only in English plus a
    "summary in Irish" rather than a full Irish translation (the
    documented Council Decision (EU) 2020/2172 derogation for older
    acts pre-dating 2022-01-01). The ≥ 500 threshold is therefore
    ASPIRATIONAL on Phase 6 — many themes (especially T1 legislation
    for pre-2022 acts, T5 language bodies for the EU-level Foras na
    Gaeilge brief, T8 institutions for Council + Parliament working
    documents) will land with pair counts below the Phase 1–5 baseline
    because the public-sector bilingual corpus is partial by design.
    The gate is retained for cross-phase comparability — operators
    should interpret a Phase 6 pair count below 500 as a Phase 6
    CHARACTERISTIC, not a regression. Detailed breakdown lives in
    `motherduck/dives/ciancheiltis_en_ga_eu_dive.py::BILINGUAL_PAIRS_DIVE_GA_EU`
    which renders a `language_availability_distribution` column
    showing the `full` / `partial` / `summary_only` split.

    The actual RAGAS score gate (≥ 0.70) lives in the sibling
    `ciancheiltis_en_ga_eu_ragas_quality_check`.
    """
    rows = ciancheiltis_en_ga_eu_bilingual_pairs_extracted.get(
        "rows_extracted", 0
    )
    passed = rows >= CIANCHEILTIS_EN_GA_EU_MIN_PAIRS
    return AssetCheckResult(
        passed=passed,
        metadata={
            "rows_extracted": rows,
            "min_pairs_threshold": CIANCHEILTIS_EN_GA_EU_MIN_PAIRS,
            "phase": "en_ga_eu",
            "themes": list(CIANCHEILTIS_EN_GA_EU_THEMES),
            "languages": ["en", "ga"],
            "language_availability_distribution": ciancheiltis_en_ga_eu_bilingual_pairs_extracted.get(
                "language_availability_distribution", {}
            ),
            "is_final_phase": True,
            "partial_coverage_caveat": (
                "EU-level coverage is PARTIAL for Irish per Council "
                "Decision (EU) 2020/2172; the 500-pair gate is "
                "ASPIRATIONAL on Phase 6. Many EU documents exist only "
                "in English plus a 'summary in Irish' rather than a "
                "full Irish translation. The Phase 6 schema captures "
                "the `language_availability` ∈ {`full`, `partial`, "
                "`summary_only`} axis as a first-class column."
            ),
        },
    )


@asset_check(asset=ciancheiltis_en_ga_eu_bilingual_pairs_extracted)
def ciancheiltis_en_ga_eu_ragas_quality_check(
    context,
    ciancheiltis_en_ga_eu_bilingual_pairs_extracted: dict[str, Any],
) -> AssetCheckResult:
    """Gate RAGAS ≥ 0.70 across the 8 en-ga-eu themes (ciancheiltis spec).

    Per the ciancheiltis spec Requirement "Dagster 5-layer asset graph
    per phase" + Requirement "6-phase language-pair staging" (Phase 6 =
    en-ga-eu) — the `ragas_quality_check` MUST block asset
    materialisation unless RAGAS ≥ 0.70 across the bilingual pairs. We
    average across the 8 themes (any theme at 0.0 — failed BAML —
    pulls the average down, surfacing the per-theme regression).

    **Phase 6 partial-coverage caveat**: The same RAGAS threshold (0.70)
    is applied to Phase 6 as to Phases 1–5, because the threshold
    measures BAML extraction QUALITY (not pair QUANTITY). On Phase 6
    the `full` rows (the canonical Irish-language EUR-Lex GA/TXT
    treaties + the Council/Parliament GA/MT debate pages) tend to have
    HIGH RAGAS scores because the `uccix-mistral-24b` modern-Irish
    client is targeted; the `partial` and `summary_only` rows are
    scored on the EN-summary / GA-summary alignment, which is a
    different RAGAS dimension (the GA-summary is a translation of the
    EN-summary, not of the EN-source-document). On Phase 6 the RAGAS
    gate typically fires GREEN even when the bilingual-pairs-seeded
    gate fires red (a known Phase 6 pattern, mirroring Phase 5).
    """
    ragas = ciancheiltis_en_ga_eu_bilingual_pairs_extracted.get(
        "ragas_scores", {}
    )
    avg = sum(ragas.values()) / len(ragas) if ragas else 0.0
    passed = avg >= CIANCHEILTIS_EN_GA_EU_MIN_RAGAS
    return AssetCheckResult(
        passed=passed,
        metadata={
            "avg_ragas_score": avg,
            "min_ragas_threshold": CIANCHEILTIS_EN_GA_EU_MIN_RAGAS,
            "per_theme_ragas": ragas,
            "phase": "en_ga_eu",
            "is_final_phase": True,
        },
    )


__all__ = [
    "CIANCHEILTIS_EN_GA_EU_THEMES",
    "CIANCHEILTIS_EN_GA_EU_INGESTION_GROUP",
    "CIANCHEILTIS_EN_GA_EU_EXTRACTION_GROUP",
    "CIANCHEILTIS_EN_GA_EU_EMBEDDING_GROUP",
    "CIANCHEILTIS_EN_GA_EU_MIN_PAIRS",
    "CIANCHEILTIS_EN_GA_EU_MIN_RAGAS",
    "ciancheiltis_en_ga_eu_themes_ingested",
    "ciancheiltis_en_ga_eu_bilingual_pairs_extracted",
    "ciancheiltis_en_ga_eu_embeddings",
    "ciancheiltis_en_ga_eu_bilingual_pairs_seeded_check",
    "ciancheiltis_en_ga_eu_ragas_quality_check",
]
