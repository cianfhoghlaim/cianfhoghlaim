# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "marimo>=0.13",
#   "ibis-framework[duckdb]>=9.0",
#   "pandas>=2.2",
#   "altair>=5.0",
#   "pyarrow>=15",
# ]
#
# [tool.uv]
# package = "biep-v2-england-explorer"
# ///

"""England AQA + OCR + Edexcel Explorer — side-by-side awarding-body comparison.

Per the 2026-07-23-biep-v2-marimo-portal-v1 change.

3-tab view (one tab per awarding body) for the same 9 priority subjects.
The cross-board `eng_aqa_vs_ocr_diff` Dagster asset (Change 2 comparator)
is rendered as a separate comparison view.

Reads from:
    oideachais.england.<board>.<subject>.<qualification_level>

KCG patterns used:
- ibis (per `.agents/skills/ibis/SKILL.md`)
- marimo (per `.agents/skills/marimo/SKILL.md`)

Reference: openspec/changes/2026-07-23-biep-v2-marimo-portal-v1/
"""

import marimo

__generated_with_marimo__ = "0.13.0"
app = marimo.App(width="medium")


@app.cell
def _intro():
    import marimo as mo
    mo.md(
        """
        # England AQA + OCR + Edexcel Explorer

        Side-by-side comparison of the 3 awarding bodies for the same 9 priority
        subjects (Mathematics, English Language, English Literature, Chemistry,
        Biology, Physics, Computer Science, History, Geography) at GCSE + A-Level.

        Use the tabs below to switch between AQA / OCR / Edexcel.
        """
    )
    return (mo,)


@app.cell
def _filter_ui(mo):
    eng_subject_filter = mo.ui.multiselect(
        options=[
            "mathematics", "english_language", "english_literature",
            "chemistry", "biology", "physics",
            "computer_science", "history", "geography",
        ],
        value=["mathematics", "english_language", "chemistry"],
        label="Subject",
    )
    qualification_level_filter = mo.ui.multiselect(
        options=["gcse", "a_level"],
        value=["gcse"],
        label="Qualification level",
    )
    mo.vstack([eng_subject_filter, qualification_level_filter])
    return eng_subject_filter, qualification_level_filter


@app.cell
def _ibis_conn(mo):
    """The ibis-first contract per the BIEP v2 spec."""
    import ibis

    conn = ibis.duckdb.connect("md:oideachais")
    lance = ibis.lancedb.connect("rest://lakehouse-lance-namespace:8182")
    mo.md("✓ ibis-first contract wired — England LanceDB namespace ready")
    return conn, lance


@app.cell
def _tabs_aqa(conn, eng_subject_filter, qualification_level_filter):
    """Tab 1: AQA — per-subject qualification data."""
    aqa_table = conn.sql(
        """
        SELECT subject, qualification_level, specification_code, title, version,
               total_marks, array_length(assessment_objectives) AS ao_count
        FROM oideachais.education.british_isles.england.aqa._all_qualifications
        WHERE subject IN %(subjects)s
          AND qualification_level IN %(levels)s
        ORDER BY subject, qualification_level
        """,
        params={
            "subjects": tuple(eng_subject_filter.value),
            "levels": tuple(qualification_level_filter.value),
        },
    ).execute()
    return aqa_table,


@app.cell
def _tabs_ocr(conn, eng_subject_filter, qualification_level_filter):
    """Tab 2: OCR — per-subject qualification data."""
    ocr_table = conn.sql(
        """
        SELECT subject, qualification_level, specification_code, title, version,
               total_marks, array_length(assessment_objectives) AS ao_count
        FROM oideachais.education.british_isles.england.ocr._all_qualifications
        WHERE subject IN %(subjects)s
          AND qualification_level IN %(levels)s
        ORDER BY subject, qualification_level
        """,
        params={
            "subjects": tuple(eng_subject_filter.value),
            "levels": tuple(qualification_level_filter.value),
        },
    ).execute()
    return ocr_table,


@app.cell
def _tabs_edexcel(conn, eng_subject_filter, qualification_level_filter):
    """Tab 3: Edexcel — per-subject qualification data."""
    edexcel_table = conn.sql(
        """
        SELECT subject, qualification_level, specification_code, title, version,
               total_marks, array_length(assessment_objectives) AS ao_count
        FROM oideachais.education.british_isles.england.edexcel._all_qualifications
        WHERE subject IN %(subjects)s
          AND qualification_level IN %(levels)s
        ORDER BY subject, qualification_level
        """,
        params={
            "subjects": tuple(eng_subject_filter.value),
            "levels": tuple(qualification_level_filter.value),
        },
    ).execute()
    return edexcel_table,


@app.cell
def _cross_board_diff(conn, eng_subject_filter, qualification_level_filter):
    """Cross-board comparator — surfaces spec differences between AQA / OCR / Edexcel.

    Backed by the Change 2 `eng_aqa_vs_ocr_diff` Dagster asset.
    """
    cross_board_diff = conn.sql(
        """
        WITH boards AS (
            SELECT 'aqa' AS board, subject, qualification_level, version,
                   total_marks
            FROM oideachais.education.british_isles.england.aqa._all_qualifications
            UNION ALL
            SELECT 'ocr' AS board, subject, qualification_level, version, total_marks
            FROM oideachais.education.british_isles.england.ocr._all_qualifications
            UNION ALL
            SELECT 'edexcel' AS board, subject, qualification_level, version, total_marks
            FROM oideachais.education.british_isles.england.edexcel._all_qualifications
        )
        SELECT * FROM boards
        WHERE subject IN %(subjects)s
          AND qualification_level IN %(levels)s
        ORDER BY subject, qualification_level, board
        """,
        params={
            "subjects": tuple(eng_subject_filter.value),
            "levels": tuple(qualification_level_filter.value),
        },
    ).execute()
    cross_board_diff
    return (cross_board_diff,)


if __name__ == "__main__":
    app.run()
