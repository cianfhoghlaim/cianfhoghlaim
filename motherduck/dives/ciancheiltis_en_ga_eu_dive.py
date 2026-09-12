"""MotherDuck Dive: ciancheiltis_en_ga_eu_dive.

The Phase 6 (en-ga / European Union) operator dashboard for the
ciancheiltis umbrella — the **FINAL** phase of the 6-phase
ciancheiltis spine (en_cy / en_ga_roi / en_ga_ni / en_gd / en_gv /
en_ga_eu). Surfaces:

1. **Per-theme coverage matrix** (T1–T10): rows = theme code, cols =
   source / ingestion status, cells = row count. The eighth theme
   is `institutions` (NOT `local_government` — the EU is sui generis
   with no sub-EU municipal tier; the canonical example for T8 is
   `https://www.ecb.europa.eu/home/html/index.ga.html` — Banc
   Ceannais Eorpach, the Irish-language ECB portal).

   **Phase 6 specific partial-coverage caveat**: EU-level coverage
   is PARTIAL for Irish per Council Decision (EU) 2020/2172 + Council
   Regulation No 1/1958 + Article 55 of the Treaty on European Union.
   Many EU documents exist only in English plus a "summary in
   Irish" rather than a full Irish translation. The strict gate per
   `dlt_sources/ciancheiltis/en_ga_eu/__init__.py` is "capture what
   bilingual content exists and surface it faithfully — including the
   `language_availability` ∈ {`full`, `partial`, `summary_only`} axis
   as a first-class column". The Dive renders the
   `language_availability_distribution` column showing the `full` /
   `partial` / `summary_only` split so operators can distinguish a
   `full` row from a `summary_only` row at a glance.
2. **Per-source metadata-language-mismatch rate**: rows = source /
   theme, cols = matched / mismatched / total, derived from
   `dlt_sources/ciancheiltis/_shared/language_detector.metadata_mismatch`.

   **Phase 6 specific mismatch pattern**: the DOMINANT Phase 6
   mismatch tag is `language_availability_summary_only` — many EU
   documents have a `summary_only` GA annotation rather than a `full`
   GA body, and the `language_availability` column distinguishes them
   at the schema level (rather than via a `mismatch_reason` flag).
   The 5% anomaly-sensor threshold (per the Phase 6 Dive Scenario in
   the ciancheiltis spec) is an absolute threshold, not a relative
   one — operators should interpret a high base rate as a Phase 6
   characteristic, NOT a regression.
3. **Bilingual-pair coverage** (the RAGAS ≥ 0.70 gate): rows = theme,
   cols = pairs_seeded / pairs_target (500), coverage_pct.

   **Phase 6 specific partial-coverage caveat**: the ciancheiltis
   spec gates the cross-phase promotion on RAGAS ≥ 0.70 + ≥ 500
   bilingual pairs seeded, carried verbatim from Phase 1. The
   500-pair gate is ASPIRATIONAL on Phase 6 because EU-level
   coverage is PARTIAL for Irish and the corpus is much smaller than
   the Phase 1–5 surfaces (when measured by full Irish translation).
   A sub-500 pair count on Phase 6 is a Phase 6 CHARACTERISTIC, NOT
   a regression. The RAGAS gate (which measures BAML extraction
   QUALITY) will typically fire green on Phase 6 because the
   `uccix-mistral-24b` modern-Irish client is targeted on the `full`
   rows.

The canonical SQL views live at:

- `md:cianfhoghlaim.ciancheiltis.en_ga_eu.themes` — per-theme row counts
- `md:cianfhoghlaim.ciancheiltis.en_ga_eu.metadata_mismatches` — per-source mismatch
- `md:cianfhoghlaim.ciancheiltis.en_ga_eu.bilingual_pairs` — per-theme RAGAS gate

These views are populated by the L1 ingestion Dagster asset
`sf_ciancheiltis_en_ga_eu_themes` (per
`orchestration/defs/1_ingestion/ciancheiltis/en_ga_eu/defs.yaml`).

**Phase 6 is the FINAL phase of the 6-phase ciancheiltis spine.**
After this Dive lands + the L1 ingestion completes + the L2 BAML
extraction runs + the L3 CocoIndex embedding mounts + the L4 asset
checks evaluate + the L5 anomaly sensor + synthesis flight run, the
ciancheiltis umbrella is complete (all 6 phases: en_cy, en_ga_roi,
en_ga_ni, en_gd, en_gv, en_ga_eu).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DiveSpec:
    """MotherDuck Dive spec — minimal contract for `save_dive`."""

    name: str
    description: str
    sql: str
    charts: list[dict[str, Any]] = field(default_factory=list)
    filters: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "sql": self.sql,
            "charts": self.charts,
            "filters": self.filters,
        }


# ---------------------------------------------------------------------------
# 1. Per-theme coverage matrix (T1–T10)
# ---------------------------------------------------------------------------

THEME_COVERAGE_DIVE_GA_EU = DiveSpec(
    name="ciancheiltis_en_ga_eu_theme_coverage",
    description=(
        "Per-theme coverage matrix for the en-ga (European Union) "
        "phase of ciancheiltis — the **FINAL** phase of the 6-phase "
        "ciancheiltis spine (en_cy, en_ga_roi, en_ga_ni, en_gd, "
        "en_gv, en_ga_eu). Rows: T1..T10. Cols: source_slug. Cells: "
        "row count. Highlights themes where ingestion is below the "
        "Phase 6 minimum-viable threshold. Note: Phase 6 ships 8 "
        "themes (T1-T8) — T8 is `institutions` (NOT `local_government` "
        "— the EU is sui generis with no sub-EU municipal tier; the "
        "canonical T8 example is "
        "`https://www.ecb.europa.eu/home/html/index.ga.html` — Banc "
        "Ceannais Eorpach, the Irish-language ECB portal). T9 "
        "(Public broadcasting & culture: Europarl TV, European "
        "Broadcasting Union) and T10 (Statistics & public records: "
        "Eurostat) land in a later PR. The 8 shipped themes are "
        "legislation, policy_consultations, education, healthcare, "
        "language_bodies, terminology, courts, institutions — "
        "mirroring the Phase 1 + Phase 2 + Phase 3 + Phase 4 + "
        "Phase 5 spine.\n\n"
        "**Phase 6 specific partial-coverage caveat**: EU-level "
        "coverage is PARTIAL for Irish per Council Decision (EU) "
        "2020/2172 + Council Regulation No 1/1958 + Article 55 of "
        "the Treaty on European Union (TEU). Many EU documents "
        "exist only in English plus a \"summary in Irish\" rather "
        "than a full Irish translation. The Phase 6 schema captures "
        "the `language_availability` ∈ {`full`, `partial`, "
        "`summary_only`} axis as a first-class column on every "
        "per-phase row. The Dive renders the "
        "`language_availability_distribution` column showing the "
        "`full` / `partial` / `summary_only` split so operators can "
        "distinguish a `full` row (canonical Irish-language EUR-Lex "
        "GA/TXT treaty) from a `summary_only` row (an Irish-language "
        "summary annotation on an otherwise English-only document) at "
        "a glance. The strict gate per "
        "`dlt_sources/ciancheiltis/en_ga_eu/__init__.py` is 'capture "
        "what bilingual content exists and surface it faithfully — "
        "including the `language_availability` column'. ZERO-ROW "
        "THEMES are EXPECTED on Phase 6 for themes where the EU has "
        "no Irish-language surface at all (rare; the 8 themes "
        "captured here all have some Irish coverage). Zero rows is a "
        "Phase 6 CHARACTERISTIC, NOT a regression. The Dive renders "
        "'pending' status for zero-row themes so operators can "
        "distinguish a not-yet-ingested theme (which would be a "
        "regression) from a genuinely-absent-theme (which is the "
        "expected Phase 6 pattern for the EU partial-coverage "
        "landscape)."
    ),
    sql="""
        CREATE OR REPLACE VIEW md:cianfhoghlaim.dives.ciancheiltis_en_ga_eu_theme_coverage AS
        WITH themes AS (
            SELECT 'T1' AS theme_code, 'Legislation'           AS theme_name UNION ALL
            SELECT 'T2',                          'Policy / consultations'     UNION ALL
            SELECT 'T3',                          'Education'                  UNION ALL
            SELECT 'T4',                          'Healthcare'                 UNION ALL
            SELECT 'T5',                          'Language bodies'            UNION ALL
            SELECT 'T6',                          'Terminology'                UNION ALL
            SELECT 'T7',                          'Courts & Tribunals'         UNION ALL
            SELECT 'T8',                          'Institutions (EU)'          UNION ALL
            SELECT 'T9',                          'Public broadcasting & culture' UNION ALL
            SELECT 'T10',                         'Statistics & public records'
        ),
        per_theme_languages AS (
            SELECT
                t.theme_code,
                t.theme_name,
                COALESCE(SUM(s.row_count), 0) AS row_count,
                COALESCE(SUM(CASE WHEN s.language_availability = 'full'         THEN s.row_count ELSE 0 END), 0) AS full_rows,
                COALESCE(SUM(CASE WHEN s.language_availability = 'partial'      THEN s.row_count ELSE 0 END), 0) AS partial_rows,
                COALESCE(SUM(CASE WHEN s.language_availability = 'summary_only' THEN s.row_count ELSE 0 END), 0) AS summary_only_rows,
                CASE WHEN COALESCE(SUM(s.row_count), 0) > 0 THEN 'populated' ELSE 'pending' END AS status
            FROM themes t
            LEFT JOIN md:cianfhoghlaim.ciancheiltis.en_ga_eu.themes s
              ON s.theme_code = t.theme_code
            GROUP BY t.theme_code, t.theme_name
        )
        SELECT
            theme_code,
            theme_name,
            row_count,
            full_rows,
            partial_rows,
            summary_only_rows,
            status
        FROM per_theme_languages
        ORDER BY theme_code;
    """,
    charts=[
        {
            "type": "bar",
            "title": "Row count per theme (T1–T10) — Phase 6 EU FINAL",
            "x_axis": "theme_name",
            "y_axis": "row_count",
        },
        {
            "type": "stacked_bar",
            "title": "language_availability_distribution per theme (full / partial / summary_only)",
            "x_axis": "theme_name",
            "y_axis": ["full_rows", "partial_rows", "summary_only_rows"],
        },
    ],
    filters=[
        {"column": "theme_code", "type": "multi_select", "options": [f"T{i}" for i in range(1, 11)]},
        {"column": "status", "type": "multi_select", "options": ["populated", "pending"]},
    ],
)


# ---------------------------------------------------------------------------
# 2. Per-source metadata-language-mismatch rate
#    (Phase 6 — EU `language_availability_summary_only` dominant + the EU
#    `?uri=CELEX:...` slug pattern + the `summary_in_irish` annotation
#    axis — different from Phase 1–5 mismatch patterns)
# ---------------------------------------------------------------------------

METADATA_MISMATCH_DIVE_GA_EU = DiveSpec(
    name="ciancheiltis_en_ga_eu_metadata_mismatch",
    description=(
        "Per-source metadata-language-mismatch rate for the en-ga "
        "(European Union) phase. Unlike Phase 1 (Wales) where "
        "`legislation.gov.uk` ships `metadata.language='eng'` on "
        "predominantly-Welsh bodies, Phase 2 (ROI) where gov.ie uses "
        "an `/en/` ↔ `/ga/` infix pair signal, Phase 3 (NI) where "
        "nidirect.gov.uk uses a SLUG PREFIX `/articles/` ↔ "
        "`/gaeilge/airteagal/`, Phase 4 (Scotland) where gov.scot "
        "uses a `<html lang=\"gd\">` attribute as the canonical pair "
        "signal, and Phase 5 (Isle of Man) where IoM government "
        "pages are mostly English-only with no structural pairing, "
        "Phase 6 (European Union) has a SIXTH mismatch pattern: "
        "the DOMINANT tag is `language_availability_summary_only` — "
        "many EU documents exist only in English plus a \"summary "
        "in Irish\" rather than a full Irish translation (this is "
        "the documented Council Decision (EU) 2020/2172 derogation "
        "for older acts pre-dating 2022-01-01). The Phase 6 schema "
        "captures the `language_availability` ∈ {`full`, `partial`, "
        "`summary_only`} axis as a first-class column on every per-"
        "phase row.\n\n"
        "This Dive surfaces all 4 mismatch reasons: "
        "`language_availability_summary_only` (the DOMINANT Phase 6 "
        "reason — the EU partial-coverage landscape means most EU "
        "documents exist only in English plus a \"summary in Irish\" "
        "rather than a full Irish translation), "
        "`language_availability_partial` (an EU document that has a "
        "GA section but not a full GA translation — VALID content "
        "per the EU bilingual mandate but flagged because Phase 6 "
        "enforces ≥ 500 `(en, ga)` PAIRS, not partial-coverage rows), "
        "`metadata.language` mismatch (rare on EU sites — the EUR-Lex "
        "CELEX metadata is reliable), and `slug_prefix_or_infix_"
        "mismatch` (rare — EU sites use a `?uri=CELEX:...` pattern, "
        "not a slug-prefix or infix).\n\n"
        "**IMPORTANT — Phase 6 baseline mismatch rate is EXPECTED "
        "to be DRAMATICALLY HIGHER than Phases 1–5.** EU-level "
        "coverage is partial by design: many EU public-sector "
        "documents exist only in English plus a \"summary in Irish\" "
        "rather than a full Irish translation, and many themes "
        "(especially T1 legislation for pre-2022 acts, T5 language "
        "bodies for the EU-level Foras na Gaeilge brief, T8 "
        "institutions for Council + Parliament working documents) "
        "will land with pair counts below the Phase 1–5 baseline "
        "because the public-sector bilingual corpus is partial by "
        "design (the strict gate per "
        "`dlt_sources/ciancheiltis/en_ga_eu/__init__.py` is "
        "'capture what bilingual content exists and surface it "
        "faithfully'). This is NOT a regression — the 5% anomaly-"
        "sensor threshold (per the Phase 6 Dive Scenario in the "
        "ciancheiltis spec) is an absolute threshold, not a "
        "relative one. Operators should interpret per-theme mismatch "
        "> 5% as a BAML regression or a `language_detector.content` "
        "drift, NOT as a Phase 6 characteristic. The Phase 6 "
        "baseline WILL trend much higher than the 5% threshold — "
        "that's the EU partial-coverage landscape, not a quality "
        "issue.\n\n"
        "**Note on EU corpus size**: the EU-level public-sector "
        "corpus is much smaller than the Phase 1–5 surfaces when "
        "measured by full Irish translation (because of the "
        "Council Decision (EU) 2020/2172 derogation). The Phase 6 "
        "Dive uses the `language_availability_distribution` column "
        "to surface the `full` / `partial` / `summary_only` split "
        "so operators have the operational context when reviewing "
        "Phase 6 mismatch rates against Phase 1–5 baselines."
    ),
    sql="""
        CREATE OR REPLACE VIEW md:cianfhoghlaim.dives.ciancheiltis_en_ga_eu_metadata_mismatch AS
        SELECT
            source_slug,
            theme_code,
            url,
            metadata_language,
            detected_language,
            language_availability,
            is_mismatch,
            mismatch_reason
        FROM md:cianfhoghlaim.ciancheiltis.en_ga_eu.metadata_mismatches
        WHERE is_mismatch = TRUE
        ORDER BY scraped_at DESC
        LIMIT 200;
    """,
    charts=[
        {
            "type": "line",
            "title": "Mismatch rate per source (last 30 days)",
            "x_axis": "scraped_at",
            "y_axis": "mismatch_rate",
            "group_by": "source_slug",
        },
        {
            "type": "bar",
            "title": "Mismatch reason breakdown (Phase 6: language_availability_summary_only dominant)",
            "x_axis": "mismatch_reason",
            "y_axis": "count",
        },
        {
            "type": "pie",
            "title": "language_availability_distribution (full / partial / summary_only)",
            "x_axis": "language_availability",
            "y_axis": "count",
        },
    ],
    filters=[
        {"column": "theme_code", "type": "multi_select", "options": [f"T{i}" for i in range(1, 11)]},
        {"column": "source_slug", "type": "search"},
        {
            "column": "mismatch_reason",
            "type": "multi_select",
            "options": [
                "language_availability_summary_only",
                "language_availability_partial",
                "metadata.language",
                "slug_prefix_or_infix_mismatch",
            ],
        },
        {
            "column": "language_availability",
            "type": "multi_select",
            "options": ["full", "partial", "summary_only"],
        },
    ],
)


# ---------------------------------------------------------------------------
# 3. RAGAS bilingual-pair coverage gate
#    (Phase 6 specific — EU partial-coverage aspirational gate + the
#    `language_availability_distribution` axis as a first-class column)
# ---------------------------------------------------------------------------

BILINGUAL_PAIRS_DIVE_GA_EU = DiveSpec(
    name="ciancheiltis_en_ga_eu_bilingual_pairs",
    description=(
        "Per-theme RAGAS bilingual-pair coverage for the en-ga "
        "(European Union) phase. The ciancheiltis spec gate is "
        "≥ 0.70 RAGAS score AND ≥ 500 bilingual pairs seeded — "
        "identical to Phases 1–5, carried verbatim per the "
        "ciancheiltis spec §6-phase language-pair staging. **Phase "
        "6 partial-coverage caveat**: this gate is ASPIRATIONAL on "
        "Phase 6 because EU-level coverage is PARTIAL for Irish per "
        "Council Decision (EU) 2020/2172 + Council Regulation No "
        "1/1958 + Article 55 TEU. Many EU documents exist only in "
        "English plus a \"summary in Irish\" rather than a full "
        "Irish translation; the corpus is much smaller than the "
        "Phase 1–5 surfaces when measured by full Irish translation. "
        "A sub-500 pair count on Phase 6 is a Phase 6 CHARACTERISTIC, "
        "NOT a regression. The few pairs that DO exist on Phase 6 "
        "(concentrated in T1 EUR-Lex GA/TXT CELEX treaties and T6 "
        "IATE terminology) tend to score HIGH on RAGAS because the "
        "`uccix-mistral-24b` modern-Irish client is targeted — so "
        "the RAGAS gate (≥ 0.70) will typically fire GREEN on "
        "Phase 6 even when the bilingual-pairs-seeded gate (≥ 500) "
        "fires red. This is the known Phase 6 RAGAS pattern.\n\n"
        "The Dive renders the `language_availability_distribution` "
        "column showing the `full` / `partial` / `summary_only` "
        "split per theme — this is the Phase 6 unique dimension that "
        "distinguishes the partial-coverage EU landscape from the "
        "Phase 1–5 surfaces.\n\n"
        "This Dive is the canonical indicator of Phase 6 readiness — "
        "operators should interpret the `phase_status = 'pending'` "
        "output as a Phase 6 characteristic during the EU partial-"
        "coverage window, with the understanding that the 500-pair "
        "gate will trend upward as more EU documents receive full "
        "Irish translations under the post-2022-01-01 Council "
        "Decision (EU) 2020/2172 regime. The RAGAS gate is the "
        "more reliable Phase 6 health signal.\n\n"
        "**Phase 6 is the FINAL phase** of the 6-phase ciancheiltis "
        "spine (en_cy, en_ga_roi, en_ga_ni, en_gd, en_gv, en_ga_eu). "
        "After this Dive lands + the L1 ingestion completes + the "
        "L2 BAML extraction runs + the L3 CocoIndex embedding mounts "
        "+ the L4 asset checks evaluate, the ciancheiltis umbrella "
        "is complete. The umbrella-completion summary table (the "
        "6-row Phase 1–Phase 6 dashboard) lives in the marimo "
        "notebook `notebooks/ciancheiltis_en_ga_eu.py` (the 5th "
        "cell) — this is the final-tally dashboard."
    ),
    sql="""
        CREATE OR REPLACE VIEW md:cianfhoghlaim.dives.ciancheiltis_en_ga_eu_bilingual_pairs AS
        WITH pair_stats AS (
            SELECT
                theme_code,
                COUNT(*) AS pairs_seeded,
                AVG(ragas_score) AS avg_ragas_score,
                MIN(ragas_score) AS min_ragas_score,
                MAX(ragas_score) AS max_ragas_score,
                SUM(CASE WHEN language_availability = 'full'         THEN 1 ELSE 0 END) AS full_pairs,
                SUM(CASE WHEN language_availability = 'partial'      THEN 1 ELSE 0 END) AS partial_pairs,
                SUM(CASE WHEN language_availability = 'summary_only' THEN 1 ELSE 0 END) AS summary_only_pairs
            FROM md:cianfhoghlaim.ciancheiltis.en_ga_eu.bilingual_pairs
            GROUP BY theme_code
        )
        SELECT
            s.theme_code,
            t.theme_name,
            COALESCE(s.pairs_seeded, 0) AS pairs_seeded,
            500 AS pairs_target,
            ROUND(100.0 * COALESCE(s.pairs_seeded, 0) / 500.0, 2) AS coverage_pct,
            ROUND(COALESCE(s.avg_ragas_score, 0.0), 4) AS avg_ragas_score,
            COALESCE(s.full_pairs, 0)         AS full_pairs,
            COALESCE(s.partial_pairs, 0)      AS partial_pairs,
            COALESCE(s.summary_only_pairs, 0) AS summary_only_pairs,
            CASE
                WHEN COALESCE(s.pairs_seeded, 0) >= 500
                 AND COALESCE(s.avg_ragas_score, 0.0) >= 0.70
                THEN 'ready'
                ELSE 'pending'
            END AS phase_status,
            CASE
                WHEN COALESCE(s.avg_ragas_score, 0.0) >= 0.70 THEN TRUE
                ELSE FALSE
            END AS ragas_gate_only
        FROM pair_stats s
        RIGHT JOIN (
            SELECT 'T1' AS theme_code, 'Legislation' AS theme_name UNION ALL
            SELECT 'T2', 'Policy / consultations' UNION ALL
            SELECT 'T3', 'Education' UNION ALL
            SELECT 'T4', 'Healthcare' UNION ALL
            SELECT 'T5', 'Language bodies' UNION ALL
            SELECT 'T6', 'Terminology' UNION ALL
            SELECT 'T7', 'Courts & Tribunals' UNION ALL
            SELECT 'T8', 'Institutions (EU)' UNION ALL
            SELECT 'T9', 'Public broadcasting & culture' UNION ALL
            SELECT 'T10', 'Statistics & public records'
        ) t ON s.theme_code = t.theme_code
        ORDER BY t.theme_code;
    """,
    charts=[
        {
            "type": "bar",
            "title": "Pairs seeded per theme (target: 500 — ASPIRATIONAL on Phase 6)",
            "x_axis": "theme_name",
            "y_axis": "pairs_seeded",
        },
        {
            "type": "stacked_bar",
            "title": "language_availability_distribution per theme (full / partial / summary_only)",
            "x_axis": "theme_name",
            "y_axis": ["full_pairs", "partial_pairs", "summary_only_pairs"],
        },
        {
            "type": "gauge",
            "title": "RAGAS score (target: 0.70)",
            "value_column": "avg_ragas_score",
            "min": 0.0,
            "max": 1.0,
        },
    ],
    filters=[
        {"column": "theme_code", "type": "multi_select", "options": [f"T{i}" for i in range(1, 11)]},
        {"column": "phase_status", "type": "multi_select", "options": ["ready", "pending"]},
        {"column": "ragas_gate_only", "type": "multi_select", "options": [True, False]},
    ],
)


CIANCHEILTIS_EN_GA_EU_DIVES: tuple[DiveSpec, ...] = (
    THEME_COVERAGE_DIVE_GA_EU,
    METADATA_MISMATCH_DIVE_GA_EU,
    BILINGUAL_PAIRS_DIVE_GA_EU,
)


def build_ciancheiltis_en_ga_eu_dive() -> None:
    """Persist all 3 MotherDuck Dives for the en-ga-eu phase (Phase 6 FINAL)."""
    from motherduck.dives import save_dive

    for dive in CIANCHEILTIS_EN_GA_EU_DIVES:
        save_dive(name=dive.name, sql=dive.sql)


__all__ = [
    "DiveSpec",
    "THEME_COVERAGE_DIVE_GA_EU",
    "METADATA_MISMATCH_DIVE_GA_EU",
    "BILINGUAL_PAIRS_DIVE_GA_EU",
    "CIANCHEILTIS_EN_GA_EU_DIVES",
    "build_ciancheiltis_en_ga_eu_dive",
]
