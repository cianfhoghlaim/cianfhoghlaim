"""MotherDuck Dive: ciancheiltis_en_ga_ni_dive.

The Phase 3 (en-ga / Northern Ireland) operator dashboard for the
ciancheiltis umbrella. Surfaces:

1. **Per-theme coverage matrix** (T1–T10): rows = theme code, cols =
   source / ingestion status, cells = row count.
2. **Per-source metadata-language-mismatch rate**: rows = source /
   theme, cols = matched / mismatched / total, derived from
   `dlt_sources/ciancheiltis/_shared/language_detector.metadata_mismatch`.

   **Phase 3 specific**: Northern Ireland has a DIFFERENT mismatch
   pattern than Phase 1 (Wales — `legislation.gov.uk` metadata.language
   mismatch) and Phase 2 (ROI — gov.ie `/en/` ↔ `/ga/` infix pair
   signal). On nidirect.gov.uk the metadata tag is generally correct;
   the canonical pair signal is the URL SLUG PREFIX (`/articles/` vs
   `/gaeilge/airteagal/`). The `mismatch_reason` taxonomy on this
   Dive therefore includes
   `slug_prefix_/_articles/_vs_/_gaeilge/airteagal/`,
   `metadata.language`, and `body_dual_language` (a page that's
   mostly EN with a GA sidebar / footnote — valid under the Identity
   and Language (Northern Ireland) Act 2022 but flagged at the
   `body_dual_language` level).
3. **Bilingual-pair coverage** (the RAGAS ≥ 0.70 gate): rows = theme,
   cols = pairs_seeded / pairs_target (500), coverage_pct.

The canonical SQL views live at:

- `md:cianfhoghlaim.ciancheiltis.en_ga_ni.themes` — per-theme row counts
- `md:cianfhoghlaim.ciancheiltis.en_ga_ni.metadata_mismatches` — per-source mismatch
- `md:cianfhoghlaim.ciancheiltis.en_ga_ni.bilingual_pairs` — per-theme RAGAS gate

These views are populated by the L1 ingestion Dagster asset
`sf_ciancheiltis_en_ga_ni_themes` (per
`orchestration/defs/1_ingestion/ciancheiltis/en_ga_ni/defs.yaml`).
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

THEME_COVERAGE_DIVE_GA_NI = DiveSpec(
    name="ciancheiltis_en_ga_ni_theme_coverage",
    description=(
        "Per-theme coverage matrix for the en-ga-ni (Northern Ireland) "
        "phase of ciancheiltis. Rows: T1..T10. Cols: source_slug. "
        "Cells: row count. Highlights themes where ingestion is below "
        "the Phase 3 minimum-viable threshold."
    ),
    sql="""
        CREATE OR REPLACE VIEW md:cianfhoghlaim.dives.ciancheiltis_en_ga_ni_theme_coverage AS
        WITH themes AS (
            SELECT 'T1' AS theme_code, 'Legislation'           AS theme_name UNION ALL
            SELECT 'T2',                          'Policy / nidirect'         UNION ALL
            SELECT 'T3',                          'Education'                 UNION ALL
            SELECT 'T4',                          'Healthcare'                UNION ALL
            SELECT 'T5',                          'Language bodies'           UNION ALL
            SELECT 'T6',                          'Ulster Scots / terminology' UNION ALL
            SELECT 'T7',                          'Courts & Tribunals'        UNION ALL
            SELECT 'T8',                          'Local government'          UNION ALL
            SELECT 'T9',                          'Public broadcasting & culture' UNION ALL
            SELECT 'T10',                         'Statistics & public records'
        )
        SELECT
            t.theme_code,
            t.theme_name,
            COALESCE(SUM(s.row_count), 0) AS row_count,
            CASE WHEN COALESCE(SUM(s.row_count), 0) > 0 THEN 'populated' ELSE 'pending' END AS status
        FROM themes t
        LEFT JOIN md:cianfhoghlaim.ciancheiltis.en_ga_ni.themes s
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
# 2. Per-source metadata-language-mismatch rate (the nidirect slug prefix)
# ---------------------------------------------------------------------------

METADATA_MISMATCH_DIVE_GA_NI = DiveSpec(
    name="ciancheiltis_en_ga_ni_metadata_mismatch",
    description=(
        "Per-source metadata-language-mismatch rate for the en-ga-ni "
        "(Northern Ireland) phase. Unlike Phase 1 (Wales) where "
        "`legislation.gov.uk` ships `metadata.language='eng'` on "
        "predominantly-Welsh bodies, and Phase 2 (ROI) where gov.ie "
        "uses an `/en/` ↔ `/ga/` infix pair signal, Phase 3 (NI) has "
        "a DIFFERENT mismatch pattern: the nidirect.gov.uk `/articles/` "
        "↔ `/gaeilge/airteagal/` paired pages use a SLUG PREFIX rather "
        "than an infix or a metadata tag. Generally the metadata tag is "
        "correct on nidirect.gov.uk — the canonical pair signal is the "
        "URL slug prefix itself. This Dive surfaces all 3 mismatch "
        "reasons: `slug_prefix_/_articles/_vs_/_gaeilge/airteagal/`, "
        "`metadata.language` mismatch, and `body_dual_language` "
        "(mostly-EN pages with a GA sidebar / footnote — valid under "
        "the Identity and Language (Northern Ireland) Act 2022 but "
        "flagged)."
    ),
    sql="""
        CREATE OR REPLACE VIEW md:cianfhoghlaim.dives.ciancheiltis_en_ga_ni_metadata_mismatch AS
        SELECT
            source_slug,
            theme_code,
            url,
            metadata_language,
            detected_language,
            is_mismatch,
            mismatch_reason
        FROM md:cianfhoghlaim.ciancheiltis.en_ga_ni.metadata_mismatches
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
                "slug_prefix_/_articles/_vs_/_gaeilge/airteagal/",
                "metadata.language",
                "body_dual_language",
            ],
        },
    ],
)


# ---------------------------------------------------------------------------
# 3. RAGAS bilingual-pair coverage gate
# ---------------------------------------------------------------------------

BILINGUAL_PAIRS_DIVE_GA_NI = DiveSpec(
    name="ciancheiltis_en_ga_ni_bilingual_pairs",
    description=(
        "Per-theme RAGAS bilingual-pair coverage for the en-ga-ni "
        "(Northern Ireland) phase. The Phase 3 acceptance gate is "
        "≥ 0.70 RAGAS score AND ≥ 500 bilingual pairs seeded — "
        "identical to Phase 1 + Phase 2, carried verbatim per the "
        "ciancheiltis spec §6-phase language-pair staging. This Dive "
        "is the canonical indicator of Phase 3 readiness."
    ),
    sql="""
        CREATE OR REPLACE VIEW md:cianfhoghlaim.dives.ciancheiltis_en_ga_ni_bilingual_pairs AS
        WITH pair_stats AS (
            SELECT
                theme_code,
                COUNT(*) AS pairs_seeded,
                AVG(ragas_score) AS avg_ragas_score,
                MIN(ragas_score) AS min_ragas_score,
                MAX(ragas_score) AS max_ragas_score
            FROM md:cianfhoghlaim.ciancheiltis.en_ga_ni.bilingual_pairs
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
            SELECT 'T2', 'Policy / nidirect' UNION ALL
            SELECT 'T3', 'Education' UNION ALL
            SELECT 'T4', 'Healthcare' UNION ALL
            SELECT 'T5', 'Language bodies' UNION ALL
            SELECT 'T6', 'Ulster Scots / terminology' UNION ALL
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


CIANCHEILTIS_EN_GA_NI_DIVES: tuple[DiveSpec, ...] = (
    THEME_COVERAGE_DIVE_GA_NI,
    METADATA_MISMATCH_DIVE_GA_NI,
    BILINGUAL_PAIRS_DIVE_GA_NI,
)


def build_ciancheiltis_en_ga_ni_dive() -> None:
    """Persist all 3 MotherDuck Dives for the en-ga-ni phase."""
    from motherduck.dives import save_dive

    for dive in CIANCHEILTIS_EN_GA_NI_DIVES:
        save_dive(name=dive.name, sql=dive.sql)


__all__ = [
    "DiveSpec",
    "THEME_COVERAGE_DIVE_GA_NI",
    "METADATA_MISMATCH_DIVE_GA_NI",
    "BILINGUAL_PAIRS_DIVE_GA_NI",
    "CIANCHEILTIS_EN_GA_NI_DIVES",
    "build_ciancheiltis_en_ga_ni_dive",
]
