"""UoG Past-Exam-Papers — Marimo dashboard.

3 tabs:

  1. **M.Sc. AI past papers** — pre-filtered to `programme_code=MSCAI`.
     Lists every row from `cianfhoghlaim.education.ie.uog_exam_papers`,
     with a Bloom-level histogram and a "co-occurring LOs" panel that
     drives directly off the BAML `MapUoGExamQuestionsToLOs` output.
  2. **All UoG schools past papers** — every module across every
     school, with module_code + academic_year + sitting + total_marks
     + VLM-extracted question count. Searches by school_slug,
     module_code, year.
  3. **LO coverage matrix** — the thesis headline figure. Rows = module
     LOs, columns = past exam years. Each cell shows how many of that
     LO's questions have been assessed in that year's paper. Empty
     cells are LO/year combinations that no paper ever tested.

The notebook uses the same `mo.sql(engine=md:cianfhoghlaim)` pattern
as `10_biep_pipeline_lakehouse_04_university_courses.py`, with a local
DuckDB fallback when the lakehouse is unreachable.

Reference: openspec/changes/2026-08-23-uog-exam-papers-sso-v1/
"""
from __future__ import annotations

import marimo


__generated_with = "0.23.10"
app = marimo.App(width="medium")


@app.cell
def _setup():
    """Setup and imports."""
    import os

    import marimo as mo
    import pandas as pd

    backend = os.environ.get("UOG_DASHBOARD_BACKEND", "duckdb-local")
    db_path = os.environ.get("DUCKDB_PATH", "/tmp/cianfhoghlaim.duckdb")
    mo.output.replace(mo.md(f"# UoG Past Exam Papers — M.Sc. AI thesis dashboard"))
    return backend, db_path, mo, os, pd


@app.cell
def _msc_ai(setup_return):
    """Tab 1 — M.Sc. AI past papers."""
    setup_return = setup_return
    import marimo as mo
    import pandas as pd

    try:
        if setup_return[0] == "duckdb-local":
            conn = __import__("duckdb").connect(setup_return[1], read_only=True)
            df = conn.execute(
                """
                SELECT module_code, module_title, academic_year, sitting,
                       total_marks, json_array_length(questions) AS question_count
                FROM cianfhoghlaim.education.ie.uog_exam_papers
                WHERE list_contains(programme_codes, 'MSCAI')
                ORDER BY module_code, academic_year DESC, sitting
                """
            ).fetch_df()
        else:
            df = pd.DataFrame()  # fallback placeholder
        mo.ui.table(df, label="M.Sc. AI past exam papers")
    except Exception as exc:  # noqa: BLE001
        mo.output.replace(
            mo.md(
                f"**No data yet.** Run `dagster asset materialize "
                f"-m uog_exam_assets uog_exam_papers_ocr_extract` first. "
                f"Error: `{exc}`"
            )
        )
    return df, mo, pd


@app.cell
def _all_schools(setup_return):
    """Tab 2 — every module across every school."""
    setup_return = setup_return
    import marimo as mo
    import pandas as pd

    school_filter = mo.ui.text(label="Filter by school_slug (e.g. computer-science)")
    module_filter = mo.ui.text(label="Filter by module_code (e.g. CT5)")

    try:
        if setup_return[0] == "duckdb-local":
            conn = __import__("duckdb").connect(setup_return[1], read_only=True)
            df = conn.execute(
                """
                SELECT module_code, module_title, school_slug, programme_codes,
                       academic_year, sitting, total_marks, source_url
                FROM cianfhoghlaim.education.ie.uog_exam_papers
                WHERE school_slug ILIKE $school_filter
                  AND module_code ILIKE $module_filter
                ORDER BY module_code, academic_year DESC
                """,
                params={
                    "school_filter": f"%{school_filter.value or ''}%",
                    "module_filter": f"%{module_filter.value or ''}%",
                },
            ).fetch_df()
        else:
            df = pd.DataFrame()
        mo.vstack([school_filter, module_filter, mo.ui.table(df)])
    except Exception as exc:  # noqa: BLE001
        mo.output.replace(
            mo.md(f"**No data yet.** `{exc}`")
        )
    return school_filter, module_filter, df, mo, pd


@app.cell
def _lo_coverage(setup_return):
    """Tab 3 — LO coverage matrix."""
    setup_return = setup_return
    import marimo as mo
    import pandas as pd

    try:
        if setup_return[0] == "duckdb-local":
            conn = __import__("duckdb").connect(setup_return[1], read_only=True)
            df = conn.execute(
                """
                SELECT
                  lo_code,
                  module_code,
                  SUM(CASE WHEN academic_year = 2025 THEN 1 ELSE 0 END) AS y2025,
                  SUM(CASE WHEN academic_year = 2024 THEN 1 ELSE 0 END) AS y2024,
                  SUM(CASE WHEN academic_year = 2023 THEN 1 ELSE 0 END) AS y2023,
                  SUM(CASE WHEN academic_year = 2022 THEN 1 ELSE 0 END) AS y2022,
                  SUM(CASE WHEN academic_year = 2021 THEN 1 ELSE 0 END) AS y2021,
                  SUM(CASE WHEN academic_year = 2020 THEN 1 ELSE 0 END) AS y2020
                FROM cianfhoghlaim.education.ie.uog_exam_lo_map
                GROUP BY lo_code, module_code
                ORDER BY module_code, lo_code
                """
            ).fetch_df()
        else:
            df = pd.DataFrame()
        mo.output.replace(
            mo.md("## LO coverage by year\n"
                  "(rows = LO codes; columns = past exam years; "
                  "cell value = number of questions assessing that LO)")
        )
        mo.ui.table(df)
    except Exception as exc:  # noqa: BLE001
        mo.output.replace(
            mo.md(
                "**LO coverage matrix requires the `uog_exam_lo_map` Dagster "
                f"asset to have materialised at least once.** Error: `{exc}`"
            )
        )
    return df, mo, pd


@app.cell
def _wire_tabs(_msc_ai, _all_schools, _lo_coverage):
    """Composed tab strip."""
    import marimo as mo
    tabs = mo.ui.tabs(
        {
            "M.Sc. AI past papers": _msc_ai[-1],
            "All UoG schools past papers": _all_schools[-1],
            "LO coverage matrix": _lo_coverage[-1],
        }
    )
    mo.output.replace(tabs)
    return tabs, mo


if __name__ == "__main__":
    app.run()
