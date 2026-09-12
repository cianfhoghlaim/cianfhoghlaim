"""MotherDuck Dive: ciancheiltis_en_gd_dive.

The Phase 4 (en-gd / Scotland) operator dashboard for the
ciancheiltis umbrella. Surfaces:

1. **Per-theme coverage matrix** (T1–T10): rows = theme code, cols =
   source / ingestion status, cells = row count.
2. **Per-source metadata-language-mismatch rate**: rows = source /
   theme, cols = matched / mismatched / total, derived from
   `dlt_sources/ciancheiltis/_shared/language_detector.metadata_mismatch`.

   **Phase 4 specific**: Scotland has a DIFFERENT mismatch pattern
   than Phase 1 (Wales — `legislation.gov.uk` metadata.language
   mismatch), Phase 2 (ROI — gov.ie `/en/` ↔ `/ga/` infix pair
   signal), and Phase 3 (NI — nidirect.gov.uk `/articles/` ↔
   `/gaeilge/airteagal/` slug PREFIX pair signal). On gov.scot the
   `<html lang="gd">` attribute is the canonical pair signal — there
   is NO `/gd/` slug variant (the CMS does NOT enforce a GD
   prefix); the `metadata.language` is generally `eng` even when the
   body is partially GD. This makes Phase 4's BASE MISMATCH RATE
   HIGHER than Phase 1 + Phase 2 + Phase 3 by design — fewer gov.scot
   pages have full GD translations, and many
   `legislation.gov.uk/asp/<year>/<num>/contents` pages exist in
   English only (a smaller canonical GD set than the Welsh Acts set
   in Phase 1). The `mismatch_reason` taxonomy on this Dive
   therefore includes `html_lang_attribute_mismatch`, `metadata.language`,
   and `gd_only_no_pair` (a Scottish page that's GD-only with no EN
   mirror — VALID bilingual content per the Gaelic Language
   (Scotland) Act 2005 but flagged at the `gd_only_no_pair` level
   because Phase 4 enforces ≥ 500 `(en, gd)` PAIRS, not GD-only
   rows).
3. **Bilingual-pair coverage** (the RAGAS ≥ 0.70 gate): rows = theme,
   cols = pairs_seeded / pairs_target (500), coverage_pct.

The canonical SQL views live at:

- `md:cianfhoghlaim.ciancheiltis.en_gd.themes` — per-theme row counts
- `md:cianfhoghlaim.ciancheiltis.en_gd.metadata_mismatches` — per-source mismatch
- `md:cianfhoghlaim.ciancheiltis.en_gd.bilingual_pairs` — per-theme RAGAS gate

These views are populated by the L1 ingestion Dagster asset
`sf_ciancheiltis_en_gd_themes` (per
`orchestration/defs/1_ingestion/ciancheiltis/en_gd/defs.yaml`).
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

THEME_COVERAGE_DIVE_GD = DiveSpec(
    name="ciancheiltis_en_gd_theme_coverage",
    description=(
        "Per-theme coverage matrix for the en-gd (Scotland) phase of "
        "ciancheiltis. Rows: T1..T10. Cols: source_slug. Cells: row "
        "count. Highlights themes where ingestion is below the Phase 4 "
        "minimum-viable threshold. Note: Phase 4 ships 8 themes "
        "(T1-T8) — T9 (Public broadcasting & culture: BBC ALBA, BBC "
        "Radio nan Gàidheal) and T10 (Statistics & public records: "
        "NRS Scottish Gaelic tables) land in a later PR. The 8 "
        "shipped themes are legislation, policy_consultations, "
        "education, healthcare, language_bodies, terminology, courts, "
        "local_government — mirroring the Phase 1 + Phase 2 + Phase 3 "
        "spine."
    ),
    sql="""
        CREATE OR REPLACE VIEW md:cianfhoghlaim.dives.ciancheiltis_en_gd_theme_coverage AS
        WITH themes AS (
            SELECT 'T1' AS theme_code, 'Legislation'           AS theme_name UNION ALL
            SELECT 'T2',                          'Policy / consultations'     UNION ALL
            SELECT 'T3',                          'Education'                  UNION ALL
            SELECT 'T4',                          'Healthcare'                 UNION ALL
            SELECT 'T5',                          'Language bodies'            UNION ALL
            SELECT 'T6',                          'Terminology'                UNION ALL
            SELECT 'T7',                          'Courts & Tribunals'         UNION ALL
            SELECT 'T8',                          'Local government'           UNION ALL
            SELECT 'T9',                          'Public broadcasting & culture' UNION ALL
            SELECT 'T10',                         'Statistics & public records'
        )
        SELECT
            t.theme_code,
            t.theme_name,
            COALESCE(SUM(s.row_count), 0) AS row_count,
            CASE WHEN COALESCE(SUM(s.row_count), 0) > 0 THEN 'populated' ELSE 'pending' END AS status
        FROM themes t
        LEFT JOIN md:cianfhoghlaim.ciancheiltis.en_gd.themes s
          ON s.theme_code = t.theme_code
        GROUP BY t.theme_code, t.theme_name
        ORDER BY t.theme_code;
    """,
    charts=[
        {
            "type": "bar",
            "title": "Row count per theme (T1–T10)",
            "x_axis": "theme_name",
            "y_axis": "row_count",
        },
    ],
    filters=[
        {"column": "theme_code", "type": "multi_select", "options": [f"T{i}" for i in range(1, 11)]},
        {"column": "status", "type": "multi_select", "options": ["populated", "pending"]},
    ],
)


# ---------------------------------------------------------------------------
# 2. Per-source metadata-language-mismatch rate
#    (Phase 4 — Scotland `<html lang="gd">` attribute + `gd_only_no_pair`)
# ---------------------------------------------------------------------------

METADATA_MISMATCH_DIVE_GD = DiveSpec(
    name="ciancheiltis_en_gd_metadata_mismatch",
    description=(
        "Per-source metadata-language-mismatch rate for the en-gd "
        "(Scotland) phase. Unlike Phase 1 (Wales) where "
        "`legislation.gov.uk` ships `metadata.language='eng'` on "
        "predominantly-Welsh bodies, Phase 2 (ROI) where gov.ie uses "
        "an `/en/` ↔ `/ga/` infix pair signal, and Phase 3 (NI) where "
        "nidirect.gov.uk uses a SLUG PREFIX `/articles/` ↔ "
        "`/gaeilge/airteagal/`, Phase 4 (Scotland) has a FOURTH "
        "mismatch pattern: gov.scot paired pages do NOT use a "
        "slug-prefix or a `/gd/` infix — the `<html lang=\"gd\">` "
        "attribute is the canonical pair signal, and the "
        "`metadata.language` is generally `eng` even when the body is "
        "partially GD. This Dive surfaces all 3 mismatch reasons: "
        "`html_lang_attribute_mismatch` (gov.scot pattern), "
        "`metadata.language` mismatch (rare on gov.scot; more common "
        "on legislation.gov.uk UK-wide Acts + SSI + SDSI), and "
        "`gd_only_no_pair` (a Scottish page that's GD-only with no "
        "EN mirror — VALID bilingual content per the Gaelic Language "
        "(Scotland) Act 2005 but flagged at the `gd_only_no_pair` "
        "level because Phase 4 enforces ≥ 500 `(en, gd)` PAIRS, not "
        "GD-only rows).\n\n"
        "**IMPORTANT — Phase 4 baseline mismatch rate is EXPECTED to "
        "be HIGHER than Phase 1 + Phase 2 + Phase 3.** Scottish Gaelic "
        "coverage is partial on most government sites: fewer gov.scot "
        "pages have full GD translations, and many "
        "`legislation.gov.uk/asp/<year>/<num>/contents` pages exist "
        "in English only (a smaller canonical GD set than the Welsh "
        "Acts set in Phase 1). This is NOT a regression — the 5% "
        "anomaly-sensor threshold (per the Phase 4 Dive Scenario in "
        "the ciancheiltis spec) is an absolute threshold, not a "
        "relative one. Operators should interpret per-theme "
        "mismatch > 5% as a BAML regression or a "
        "language_detector.content drift, NOT as a Phase 4 "
        "characteristic."
    ),
    sql="""
        CREATE OR REPLACE VIEW md:cianfhoghlaim.dives.ciancheiltis_en_gd_metadata_mismatch AS
        SELECT
            source_slug,
            theme_code,
            url,
            metadata_language,
            detected_language,
            html_lang_attribute,
            is_mismatch,
            mismatch_reason
        FROM md:cianfhoghlaim.ciancheiltis.en_gd.metadata_mismatches
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
            "title": "Mismatch reason breakdown",
            "x_axis": "mismatch_reason",
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
                "html_lang_attribute_mismatch",
                "metadata.language",
                "gd_only_no_pair",
            ],
        },
    ],
)


# ---------------------------------------------------------------------------
# 3. RAGAS bilingual-pair coverage gate
# ---------------------------------------------------------------------------

BILINGUAL_PAIRS_DIVE_GD = DiveSpec(
    name="ciancheiltis_en_gd_bilingual_pairs",
    description=(
        "Per-theme RAGAS bilingual-pair coverage for the en-gd "
        "(Scotland) phase. The Phase 4 acceptance gate is "
        "≥ 0.70 RAGAS score AND ≥ 500 bilingual pairs seeded — "
        "identical to Phase 1 + Phase 2 + Phase 3, carried verbatim "
        "per the ciancheiltis spec §6-phase language-pair staging. "
        "This Dive is the canonical indicator of Phase 4 readiness."
    ),
    sql="""
        CREATE OR REPLACE VIEW md:cianfhoghlaim.dives.ciancheiltis_en_gd_bilingual_pairs AS
        WITH pair_stats AS (
            SELECT
                theme_code,
                COUNT(*) AS pairs_seeded,
                AVG(ragas_score) AS avg_ragas_score,
                MIN(ragas_score) AS min_ragas_score,
                MAX(ragas_score) AS max_ragas_score
            FROM md:cianfhoghlaim.ciancheiltis.en_gd.bilingual_pairs
            GROUP BY theme_code
        )
        SELECT
            s.theme_code,
            t.theme_name,
            COALESCE(s.pairs_seeded, 0) AS pairs_seeded,
            500 AS pairs_target,
            ROUND(100.0 * COALESCE(s.pairs_seeded, 0) / 500.0, 2) AS coverage_pct,
            ROUND(COALESCE(s.avg_ragas_score, 0.0), 4) AS avg_ragas_score,
            CASE
                WHEN COALESCE(s.pairs_seeded, 0) >= 500
                 AND COALESCE(s.avg_ragas_score, 0.0) >= 0.70
                THEN 'ready'
                ELSE 'pending'
            END AS phase_status
        FROM pair_stats s
        RIGHT JOIN (
            SELECT 'T1' AS theme_code, 'Legislation' AS theme_name UNION ALL
            SELECT 'T2', 'Policy / consultations' UNION ALL
            SELECT 'T3', 'Education' UNION ALL
            SELECT 'T4', 'Healthcare' UNION ALL
            SELECT 'T5', 'Language bodies' UNION ALL
            SELECT 'T6', 'Terminology' UNION ALL
            SELECT 'T7', 'Courts & Tribunals' UNION ALL
            SELECT 'T8', 'Local government' UNION ALL
            SELECT 'T9', 'Public broadcasting & culture' UNION ALL
            SELECT 'T10', 'Statistics & public records'
        ) t ON s.theme_code = t.theme_code
        ORDER BY t.theme_code;
    """,
    charts=[
        {
            "type": "bar",
            "title": "Pairs seeded per theme (target: 500)",
            "x_axis": "theme_name",
            "y_axis": "pairs_seeded",
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
    ],
)


CIANCHEILTIS_EN_GD_DIVES: tuple[DiveSpec, ...] = (
    THEME_COVERAGE_DIVE_GD,
    METADATA_MISMATCH_DIVE_GD,
    BILINGUAL_PAIRS_DIVE_GD,
)


def build_ciancheiltis_en_gd_dive() -> None:
    """Persist all 3 MotherDuck Dives for the en-gd phase."""
    from motherduck.dives import save_dive

    for dive in CIANCHEILTIS_EN_GD_DIVES:
        save_dive(name=dive.name, sql=dive.sql)


__all__ = [
    "DiveSpec",
    "THEME_COVERAGE_DIVE_GD",
    "METADATA_MISMATCH_DIVE_GD",
    "BILINGUAL_PAIRS_DIVE_GD",
    "CIANCHEILTIS_EN_GD_DIVES",
    "build_ciancheiltis_en_gd_dive",
]
