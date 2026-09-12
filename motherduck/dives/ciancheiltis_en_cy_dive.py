"""MotherDuck Dive: ciancheiltis_en_cy_dive.

The Phase 1 (en-cy / Wales) operator dashboard for the ciancheiltis
umbrella. Surfaces:

1. **Per-theme coverage matrix** (T1–T10): rows = theme code, cols =
   source / ingestion status, cells = row count.
2. **Per-source metadata-language-mismatch rate**: rows = source /
   theme, cols = matched / mismatched / total, derived from
   `dlt_sources/ciancheiltis/_shared/language_detector.metadata_mismatch`.
3. **Bilingual-pair coverage** (the RAGAS ≥ 0.70 gate): rows = theme,
   cols = pairs_seeded / pairs_target (500), coverage_pct.

The canonical SQL views live at:

- `md:cianfhoghlaim.ciancheiltis.en_cy.themes` — per-theme row counts
- `md:cianfhoghlaim.ciancheiltis.en_cy.metadata_mismatches` — per-source mismatch
- `md:cianfhoghlaim.ciancheiltis.en_cy.bilingual_pairs` — per-theme RAGAS gate

These views are populated by the L1 ingestion Dagster asset
`sf_ciancheiltis_en_cy_themes` (per
`orchestration/defs/1_ingestion/ciancheiltis/en_cy/defs.yaml`).
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

THEME_COVERAGE_DIVE = DiveSpec(
    name="ciancheiltis_en_cy_theme_coverage",
    description=(
        "Per-theme coverage matrix for the en-cy (Wales) phase of "
        "ciancheiltis. Rows: T1..T10. Cols: source_slug. Cells: row count. "
        "Highlights themes where ingestion is below the Phase 1 "
        "minimum-viable threshold."
    ),
    sql="""
        CREATE OR REPLACE VIEW md:cianfhoghlaim.dives.ciancheiltis_en_cy_theme_coverage AS
        WITH themes AS (
            SELECT 'T1' AS theme_code, 'Legislation'           AS theme_name UNION ALL
            SELECT 'T2',                          'Policy / consultations'       UNION ALL
            SELECT 'T3',                          'Education'                   UNION ALL
            SELECT 'T4',                          'Healthcare'                  UNION ALL
            SELECT 'T5',                          'Language bodies'             UNION ALL
            SELECT 'T6',                          'Terminology'                 UNION ALL
            SELECT 'T7',                          'Courts & Tribunals'          UNION ALL
            SELECT 'T8',                          'Local government'            UNION ALL
            SELECT 'T9',                          'Public broadcasting & culture' UNION ALL
            SELECT 'T10',                         'Statistics & public records'
        )
        SELECT
            t.theme_code,
            t.theme_name,
            COALESCE(SUM(s.row_count), 0) AS row_count,
            CASE WHEN COALESCE(SUM(s.row_count), 0) > 0 THEN 'populated' ELSE 'pending' END AS status
        FROM themes t
        LEFT JOIN md:cianfhoghlaim.ciancheiltis.en_cy.themes s
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
# 2. Per-source metadata-language-mismatch rate (the SI 2007/1484 lesson)
# ---------------------------------------------------------------------------

METADATA_MISMATCH_DIVE = DiveSpec(
    name="ciancheiltis_en_cy_metadata_mismatch",
    description=(
        "Per-source metadata-language-mismatch rate for the en-cy (Wales) "
        "phase. The page metadata `language` tag is unreliable (see "
        "`legislation.gov.uk/uksi/2007/1484/made` — `metadata.language = 'eng'` "
        "but the body is Welsh). The ciancheiltis pipeline uses "
        "content-based detection via "
        "`dlt_sources/ciancheiltis/_shared/language_detector.py`."
    ),
    sql="""
        CREATE OR REPLACE VIEW md:cianfhoghlaim.dives.ciancheiltis_en_cy_metadata_mismatch AS
        SELECT
            source_slug,
            theme_code,
            url,
            metadata_language,
            detected_language,
            is_mismatch,
            mismatch_reason
        FROM md:cianfhoghlaim.ciancheiltis.en_cy.metadata_mismatches
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
    ],
    filters=[
        {"column": "theme_code", "type": "multi_select", "options": [f"T{i}" for i in range(1, 11)]},
        {"column": "source_slug", "type": "search"},
    ],
)


# ---------------------------------------------------------------------------
# 3. RAGAS bilingual-pair coverage gate
# ---------------------------------------------------------------------------

BILINGUAL_PAIRS_DIVE = DiveSpec(
    name="ciancheiltis_en_cy_bilingual_pairs",
    description=(
        "Per-theme RAGAS bilingual-pair coverage for the en-cy (Wales) "
        "phase. The Phase 1 acceptance gate is ≥ 0.70 RAGAS score AND "
        "≥ 500 bilingual pairs seeded. This Dive is the canonical "
        "indicator of Phase 1 readiness."
    ),
    sql="""
        CREATE OR REPLACE VIEW md:cianfhoghlaim.dives.ciancheiltis_en_cy_bilingual_pairs AS
        WITH pair_stats AS (
            SELECT
                theme_code,
                COUNT(*) AS pairs_seeded,
                AVG(ragas_score) AS avg_ragas_score,
                MIN(ragas_score) AS min_ragas_score,
                MAX(ragas_score) AS max_ragas_score
            FROM md:cianfhoghlaim.ciancheiltis.en_cy.bilingual_pairs
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


CIANCHEILTIS_EN_CY_DIVES: tuple[DiveSpec, ...] = (
    THEME_COVERAGE_DIVE,
    METADATA_MISMATCH_DIVE,
    BILINGUAL_PAIRS_DIVE,
)


def build_ciancheiltis_en_cy_dive() -> None:
    """Persist all 3 MotherDuck Dives for the en-cy phase."""
    from motherduck.dives import save_dive

    for dive in CIANCHEILTIS_EN_CY_DIVES:
        save_dive(name=dive.name, sql=dive.sql)


__all__ = [
    "DiveSpec",
    "THEME_COVERAGE_DIVE",
    "METADATA_MISMATCH_DIVE",
    "BILINGUAL_PAIRS_DIVE",
    "CIANCHEILTIS_EN_CY_DIVES",
    "build_ciancheiltis_en_cy_dive",
]
