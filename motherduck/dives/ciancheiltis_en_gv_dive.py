"""MotherDuck Dive: ciancheiltis_en_gv_dive.

The Phase 5 (en-gv / Isle of Man) operator dashboard for the
ciancheiltis umbrella. Surfaces:

1. **Per-theme coverage matrix** (T1–T10): rows = theme code, cols =
   source / ingestion status, cells = row count.

   **Phase 5 specific**: Manx (Gaelg) is a REVIVAL language — last
   native speaker Ned Maddrell died 1974. The modern corpus is a
   constructed revival under Culture Vannin + Learn Manx + Bunscoill
   Ghaelgagh + Radio Manx. There is NO statutory bilingual framework
   — pages that DO have a Manx version are a bonus, NOT a baseline.
   The strict gate per
   `dlt_sources/ciancheiltis/en_gv/__init__.py` is "capture what
   bilingual content exists and surface it faithfully". This Dive
   therefore will surface many ZERO-ROW THEMES (T1 legislation,
   T7 courts, T8 local government typically have no Manx public-sector
   content). Zero rows is a Phase 5 CHARACTERISTIC, NOT a regression.
2. **Per-source metadata-language-mismatch rate**: rows = source /
   theme, cols = matched / mismatched / total, derived from
   `dlt_sources/ciancheiltis/_shared/language_detector.metadata_mismatch`.

   **Phase 5 specific**: the mismatch rate will be DRAMATICALLY higher
   than Phase 1 (Wales), Phase 2 (ROI), Phase 3 (NI), and Phase 4
   (Scotland) because Manx coverage is sparse and most IoM government
   pages exist in English only. The `mismatch_reason` taxonomy on
   this Dive is dominated by `en_only_no_pair` (the canonical Phase 5
   reason) rather than the slug-prefix or html-lang-attribute patterns
   seen on Phase 1 / Phase 2 / Phase 3 / Phase 4. The 5%
   anomaly-sensor threshold (per the Phase 5 Dive Scenario in the
   ciancheiltis spec) is an absolute threshold, not a relative one —
   operators should interpret a high base rate as a Phase 5
   characteristic, NOT a regression.
3. **Bilingual-pair coverage** (the RAGAS ≥ 0.70 gate): rows = theme,
   cols = pairs_seeded / pairs_target (500), coverage_pct.

   **Phase 5 specific revival-status caveat**: the ciancheiltis spec
   gates the cross-phase promotion on RAGAS ≥ 0.70 + ≥ 500 bilingual
   pairs seeded, carried verbatim from Phase 1. The 500-pair gate is
   ASPIRATIONAL on Phase 5 because Manx (Gaelg) is a REVIVAL language
   with NO statutory bilingual framework and the corpus is much
   smaller than Welsh / Irish / Scottish Gaelic. A sub-500 pair count
   on Phase 5 is a Phase 5 CHARACTERISTIC, NOT a regression. The
   RAGAS gate (which measures BAML extraction QUALITY) will typically
   fire green on Phase 5 because the few pairs that DO exist score
   HIGH (the Manx few-shot prompt is targeted).

The canonical SQL views live at:

- `md:cianfhoghlaim.ciancheiltis.en_gv.themes` — per-theme row counts
- `md:cianfhoghlaim.ciancheiltis.en_gv.metadata_mismatches` — per-source mismatch
- `md:cianfhoghlaim.ciancheiltis.en_gv.bilingual_pairs` — per-theme RAGAS gate

These views are populated by the L1 ingestion Dagster asset
`sf_ciancheiltis_en_gv_themes` (per
`orchestration/defs/1_ingestion/ciancheiltis/en_gv/defs.yaml`).
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

THEME_COVERAGE_DIVE_GV = DiveSpec(
    name="ciancheiltis_en_gv_theme_coverage",
    description=(
        "Per-theme coverage matrix for the en-gv (Isle of Man) phase "
        "of ciancheiltis. Rows: T1..T10. Cols: source_slug. Cells: "
        "row count. Highlights themes where ingestion is below the "
        "Phase 5 minimum-viable threshold. Note: Phase 5 ships 8 "
        "themes (T1-T8) — T9 (Public broadcasting & culture: Manx "
        "Radio, Radio Manx) and T10 (Statistics & public records: "
        "Isle of Man Government Statistics) land in a later PR. The "
        "8 shipped themes are legislation, policy_consultations, "
        "education, healthcare, language_bodies, terminology, "
        "courts, local_government — mirroring the Phase 1 + Phase 2 "
        "+ Phase 3 + Phase 4 spine.\n\n"
        "**Phase 5 specific revival-status caveat**: Manx (Gaelg) "
        "is a REVIVAL language — last native speaker Ned Maddrell "
        "died 1974; the modern corpus is a constructed revival "
        "under Culture Vannin + Learn Manx + Bunscoill Ghaelgagh + "
        "Radio Manx. There is NO statutory bilingual framework — "
        "pages that DO have a Manx version are a bonus, NOT a "
        "baseline. The strict gate per "
        "`dlt_sources/ciancheiltis/en_gv/__init__.py` is 'capture "
        "what bilingual content exists and surface it faithfully'. "
        "ZERO-ROW THEMES are EXPECTED on Phase 5 (typically T1 "
        "legislation, T7 courts, T8 local government). Zero rows "
        "is a Phase 5 CHARACTERISTIC, NOT a regression. The Dive "
        "renders 'pending' status for zero-row themes so operators "
        "can distinguish a not-yet-ingested theme (which would be "
        "a regression) from a genuinely-absent-theme (which is the "
        "expected Phase 5 pattern for the Manx revival)."
    ),
    sql="""
        CREATE OR REPLACE VIEW md:cianfhoghlaim.dives.ciancheiltis_en_gv_theme_coverage AS
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
        LEFT JOIN md:cianfhoghlaim.ciancheiltis.en_gv.themes s
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
#    (Phase 5 — Isle of Man `en_only_no_pair` dominant + Manx revival
#    corpus is much smaller than ROI/NI/Wales)
# ---------------------------------------------------------------------------

METADATA_MISMATCH_DIVE_GV = DiveSpec(
    name="ciancheiltis_en_gv_metadata_mismatch",
    description=(
        "Per-source metadata-language-mismatch rate for the en-gv "
        "(Isle of Man) phase. Unlike Phase 1 (Wales) where "
        "`legislation.gov.uk` ships `metadata.language='eng'` on "
        "predominantly-Welsh bodies, Phase 2 (ROI) where gov.ie uses "
        "an `/en/` ↔ `/ga/` infix pair signal, Phase 3 (NI) where "
        "nidirect.gov.uk uses a SLUG PREFIX `/articles/` ↔ "
        "`/gaeilge/airteagal/`, and Phase 4 (Scotland) where gov.scot "
        "uses a `<html lang=\"gd\">` attribute as the canonical pair "
        "signal, Phase 5 (Isle of Man) has a FIFTH mismatch pattern: "
        "the DOMINANT tag is `en_only_no_pair` — most IoM government "
        "pages exist in English only, and there is effectively NO "
        "structural pairing signal to leverage (no slug-prefix, no "
        "`/gv/` infix, no consistent `<html lang=\"gv\">` attribute). "
        "Pairing is corroborated from body content via the lingua-py "
        "detector.\n\n"
        "This Dive surfaces all 4 mismatch reasons: `en_only_no_pair` "
        "(the DOMINANT Phase 5 reason — most IoM public-sector pages "
        "are English-only because Manx is a REVIVAL language with NO "
        "statutory bilingual framework), `gv_only_no_pair` (a Manx "
        "page that's GV-only with no EN mirror — VALID content per "
        "the Culture Vannin brief but flagged because Phase 5 "
        "enforces ≥ 500 `(en, gv)` PAIRS, not GV-only rows), "
        "`metadata.language` mismatch (rare on IoM sites), and "
        "`slug_prefix_or_infix_mismatch` (rare — IoM sites lack the "
        "structural pairing of Phase 1 + Phase 2 + Phase 3 + Phase 4).\n\n"
        "**IMPORTANT — Phase 5 baseline mismatch rate is EXPECTED "
        "to be DRAMATICALLY HIGHER than Phase 1 + Phase 2 + Phase 3 "
        "+ Phase 4.** Manx coverage is so sparse that most IoM public-"
        "sector pages exist in English only, and many themes (T1 "
        "legislation, T7 courts, T8 local government) will land with "
        "zero Manx content because the public-sector bilingual "
        "corpus is partial by design (the strict gate per "
        "`dlt_sources/ciancheiltis/en_gv/__init__.py` is 'capture "
        "what bilingual content exists and surface it faithfully'). "
        "This is NOT a regression — the 5% anomaly-sensor threshold "
        "(per the Phase 5 Dive Scenario in the ciancheiltis spec) is "
        "an absolute threshold, not a relative one. Operators should "
        "interpret per-theme mismatch > 5% as a BAML regression or "
        "a `language_detector.content` drift, NOT as a Phase 5 "
        "characteristic. The Phase 5 baseline WILL trend much "
        "higher than the 5% threshold — that's the revival-language "
        "landscape, not a quality issue.\n\n"
        "**Note on Manx corpus size**: the Manx (Gaelg) public-sector "
        "corpus is significantly SMALLER than Welsh (Phase 1), Irish "
        "(Phase 2/3), or Scottish Gaelic (Phase 4). This is documented "
        "here so operators have the operational context when "
        "reviewing Phase 5 mismatch rates against Phase 1 / Phase 2 "
        "/ Phase 3 / Phase 4 baselines."
    ),
    sql="""
        CREATE OR REPLACE VIEW md:cianfhoghlaim.dives.ciancheiltis_en_gv_metadata_mismatch AS
        SELECT
            source_slug,
            theme_code,
            url,
            metadata_language,
            detected_language,
            html_lang_attribute,
            is_mismatch,
            mismatch_reason
        FROM md:cianfhoghlaim.ciancheiltis.en_gv.metadata_mismatches
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
                "en_only_no_pair",
                "gv_only_no_pair",
                "metadata.language",
                "slug_prefix_or_infix_mismatch",
            ],
        },
    ],
)


# ---------------------------------------------------------------------------
# 3. RAGAS bilingual-pair coverage gate
#    (Phase 5 specific — Manx revival-language strict gate)
# ---------------------------------------------------------------------------

BILINGUAL_PAIRS_DIVE_GV = DiveSpec(
    name="ciancheiltis_en_gv_bilingual_pairs",
    description=(
        "Per-theme RAGAS bilingual-pair coverage for the en-gv (Isle "
        "of Man) phase. The ciancheiltis spec gate is "
        "≥ 0.70 RAGAS score AND ≥ 500 bilingual pairs seeded — "
        "identical to Phase 1 + Phase 2 + Phase 3 + Phase 4, carried "
        "verbatim per the ciancheiltis spec §6-phase language-pair "
        "staging. **Phase 5 revival-status caveat**: this gate is "
        "ASPIRATIONAL on Phase 5 because Manx (Gaelg) is a REVIVAL "
        "language with NO statutory bilingual framework — last "
        "native speaker Ned Maddrell died 1974; the modern corpus "
        "is a constructed revival under Culture Vannin + Learn Manx "
        "+ Bunscoill Ghaelgagh + Radio Manx, and is MUCH SMALLER "
        "than the Welsh / Irish / Scottish Gaelic corpora. A sub-500 "
        "pair count on Phase 5 is a Phase 5 CHARACTERISTIC, NOT a "
        "regression. The few pairs that DO exist on Phase 5 (concentrated "
        "in T5 Culture Vannin and T6 Learn Manx terminology) tend to "
        "score HIGH on RAGAS because the Manx few-shot prompt is "
        "targeted — so the RAGAS gate (≥ 0.70) will typically fire "
        "GREEN on Phase 5 even when the bilingual-pairs-seeded gate "
        "(≥ 500) fires red. This is the known Phase 5 RAGAS pattern.\n\n"
        "This Dive is the canonical indicator of Phase 5 readiness — "
        "operators should interpret the `phase_status = 'pending'` "
        "output as a Phase 5 characteristic during the revival-language "
        "window, with the understanding that the 500-pair gate will "
        "trend upward as Culture Vannin + Learn Manx + Bunscoill "
        "Ghaelgagh + Radio Manx continue to grow the public Manx "
        "corpus over time. The RAGAS gate is the more reliable "
        "Phase 5 health signal."
    ),
    sql="""
        CREATE OR REPLACE VIEW md:cianfhoghlaim.dives.ciancheiltis_en_gv_bilingual_pairs AS
        WITH pair_stats AS (
            SELECT
                theme_code,
                COUNT(*) AS pairs_seeded,
                AVG(ragas_score) AS avg_ragas_score,
                MIN(ragas_score) AS min_ragas_score,
                MAX(ragas_score) AS max_ragas_score
            FROM md:cianfhoghlaim.ciancheiltis.en_gv.bilingual_pairs
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
            SELECT 'T8', 'Local government' UNION ALL
            SELECT 'T9', 'Public broadcasting & culture' UNION ALL
            SELECT 'T10', 'Statistics & public records'
        ) t ON s.theme_code = t.theme_code
        ORDER BY t.theme_code;
    """,
    charts=[
        {
            "type": "bar",
            "title": "Pairs seeded per theme (target: 500 — ASPIRATIONAL on Phase 5)",
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
        {"column": "ragas_gate_only", "type": "multi_select", "options": [True, False]},
    ],
)


CIANCHEILTIS_EN_GV_DIVES: tuple[DiveSpec, ...] = (
    THEME_COVERAGE_DIVE_GV,
    METADATA_MISMATCH_DIVE_GV,
    BILINGUAL_PAIRS_DIVE_GV,
)


def build_ciancheiltis_en_gv_dive() -> None:
    """Persist all 3 MotherDuck Dives for the en-gv phase."""
    from motherduck.dives import save_dive

    for dive in CIANCHEILTIS_EN_GV_DIVES:
        save_dive(name=dive.name, sql=dive.sql)


__all__ = [
    "DiveSpec",
    "THEME_COVERAGE_DIVE_GV",
    "METADATA_MISMATCH_DIVE_GV",
    "BILINGUAL_PAIRS_DIVE_GV",
    "CIANCHEILTIS_EN_GV_DIVES",
    "build_ciancheiltis_en_gv_dive",
]
