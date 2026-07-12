# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
#     "pandas>=2.0",
# ]
# ///
"""University Courses Dashboard — Marimo notebook with 4 tabs.

Mounted at ``/dashboards/university-courses`` (per the
``oideachais-marimo-dashboards`` spec). Case study: University of
Galway.

4 tabs:

  1. **M.Sc. AI 25/26 modules** — the primary use case. Pre-filtered to
     `programme_codes = ["MSCAI"]` and `academic_year = 2025`.
  2. **All UoG courses** — searchable + filterable by school, NFQ
     level, ECTS, programme stage.
  3. **Reading lists** — every reading-list item across all modules,
     with a "Group by module" / "Group by ISBN-13" toggle.
  4. **Cross-archive** — the user's `leabharlann/ollscoil_na_gaillimhe/`
     artefacts joined to the matching scraped `CourseDescriptor` rows
     via the new `UoGArtifact-MATCHES-CourseDescriptor` Cognee edge.

The notebook uses ``mo.sql(engine=md:oideachais)`` (the MotherDuck +
DuckLake lakehouse) for the underlying queries. When the MotherDuck
endpoint is unreachable, the notebook falls back to a local DuckDB
file (``/tmp/oideachais.duckdb``) for development.

Reference: openspec/changes/university-of-galway-deep-extraction/
"""
from __future__ import annotations

import marimo

__generated_with = "0.23.10"
app = marimo.App(width="medium")


@app.cell
def _():
    """Setup and imports."""
    import os

    import marimo as mo
    import pandas as pd

    # Primary path: MotherDuck + DuckLake lakehouse. Fall back to local DuckDB.
    try:
        import duckdb
import ibis  # ibis-first entrypoint
        db_path = os.environ.get(
            "CIANFHOGHLAIS_UOG_DUCKDB", "/tmp/oideachais.duckdb"
        )
        if os.path.exists(db_path):
            engine = ibis.duckdb.connect(db_path, read_only=True)
            ENGINE_LABEL = f"local DuckDB ({db_path})"
        else:
            token = os.environ.get("MOTHERDUCK_TOKEN", "")
            if token:
                duckdb.sql(f"SET motherduck_token='{token}'")
                engine = ibis.duckdb.connect("md:oideachais")
                ENGINE_LABEL = "md:oideachais (MotherDuck + DuckLake)"
            else:
                ENGINE_LABEL = "MotherDuck (no token — set MOTHERDUCK_TOKEN)"
                engine = None
    except ImportError:
        engine = None
        ENGINE_LABEL = "duckdb not installed"

    mo.md(
        f"""
        # University Courses Dashboard

        Interactive view of the University of Galway case-study pipeline
        (per the ``oideachais-university-deep-extraction`` spec).

        Backend: **{ENGINE_LABEL}**

        The 4 tabs cover: M.Sc. AI 25/26 modules, all UoG courses,
        reading lists, and the cross-archive join with the user's
        personal UoG artefacts.
        """
    )
    return ENGINE_LABEL, engine, mo, os, pd


@app.cell
def _(mo):
    """Tab selector."""
    tab = mo.ui.tabs(
        {
            "1. M.Sc. AI 25/26 modules": "tab_msc_ai",
            "2. All UoG courses": "tab_all_courses",
            "3. Reading lists": "tab_reading_lists",
            "4. Cross-archive": "tab_cross_archive",
        }
    )
    tab
    return (tab,)


@app.cell
def _(tab):
    """Switch on the selected tab."""
    tab.value
    return


# =============================================================================
# Tab 1: M.Sc. AI 25/26 modules (the primary use case)
# =============================================================================


@app.cell
def _(engine, mo, pd):
    """Tab 1 content — M.Sc. AI 25/26 modules."""
    mo.md(
        """
        ## M.Sc. AI 25/26 modules

        The user's upcoming programme. Pre-filtered to
        `programme_codes = ["MSCAI"]` and `academic_year = 2025`.
        """
    )
    if engine is None:
        return mo.md("*No data backend available — render stub table below.*"), pd.DataFrame()
    try:
        df = engine.execute(
            """
            SELECT
                module_code,
                module_title,
                ects,
                semester,
                programme_codes,
                source_url
            FROM oideachais.education.ie.university_modules
            WHERE programme_codes LIKE '%MSCAI%'
              AND academic_year = 2025
            ORDER BY module_code
            """
        ).to_pandas()
    except Exception as exc:  # noqa: BLE001
        return mo.md(f"*Query failed: {exc}*"), pd.DataFrame()
    if df.empty:
        return mo.md("*No M.Sc. AI 25/26 modules yet — run `uog_extract_modules`.*"), df
    table = mo.ui.table(df, label="M.Sc. AI 25/26 modules")
    return table, df
    return (tab,)


# =============================================================================
# Tab 2: All UoG courses
# =============================================================================


@app.cell
def _(engine, mo, pd):
    """Tab 2 content — all UoG courses with search + filter."""
    mo.md(
        """
        ## All UoG courses

        Searchable + filterable by school, NFQ level, ECTS, programme
        stage.
        """
    )
    if engine is None:
        return (
            mo.md("*No data backend available.*"),
            mo.ui.text(placeholder="search…"),
            pd.DataFrame(),
        )
    try:
        df = engine.execute(
            """
            SELECT
                course_code,
                course_title,
                nfq_level,
                stage,
                school,
                ects,
                programme_codes,
                source_url
            FROM oideachais.education.ie.university_courses
            ORDER BY school, course_code
            """
        ).to_pandas()
    except Exception as exc:  # noqa: BLE001
        return (
            mo.md(f"*Query failed: {exc}*"),
            mo.ui.text(placeholder="search…"),
            pd.DataFrame(),
        )
    search = mo.ui.text(placeholder="search title/code…", value="")
    school_filter = mo.ui.multiselect(
        options=sorted(df["school"].dropna().unique().tolist()) if not df.empty else [],
        value=[],
        label="School",
    )
    nfq_filter = mo.ui.multiselect(
        options=sorted(df["nfq_level"].dropna().unique().tolist()) if not df.empty else [],
        value=[],
        label="NFQ Level",
    )
    filtered = df
    if search.value:
        mask = (
            df["course_title"].str.contains(search.value, case=False, na=False)
            | df["course_code"].astype(str).str.contains(search.value, case=False, na=False)
        )
        filtered = filtered[mask]
    if school_filter.value:
        filtered = filtered[filtered["school"].isin(school_filter.value)]
    if nfq_filter.value:
        filtered = filtered[filtered["nfq_level"].isin(nfq_filter.value)]
    table = mo.ui.table(filtered, label=f"All UoG courses ({len(filtered)} rows)")
    return (
        filtered,
        nfq_filter,
        school_filter,
        search,
        table,
    )
    return (tab,)


# =============================================================================
# Tab 3: Reading lists
# =============================================================================


@app.cell
def _(engine, mo, pd):
    """Tab 3 content — reading lists with group-by toggle."""
    mo.md(
        """
        ## Reading lists

        Every reading-list item across all modules, with a "Group by
        module" vs "Group by ISBN-13" toggle.
        """
    )
    if engine is None:
        return (
            mo.md("*No data backend available.*"),
            mo.ui.radio(options=["module", "isbn"]),
            pd.DataFrame(),
        )
    group_by = mo.ui.radio(
        options=["module", "isbn"],
        value="module",
        label="Group by",
    )
    try:
        df = engine.execute(
            """
            SELECT
                m.module_code,
                m.module_title,
                m.recommended_reading
            FROM oideachais.education.ie.university_modules m
            WHERE m.recommended_reading IS NOT NULL
              AND m.recommended_reading != ''
            ORDER BY m.module_code
            """
        ).to_pandas()
    except Exception as exc:  # noqa: BLE001
        return mo.md(f"*Query failed: {exc}*"), group_by, pd.DataFrame()
    if df.empty:
        return mo.md("*No reading lists yet — run `uog_extract_modules`.*"), group_by, df
    rows: list[dict[str, str]] = []
    for _, r in df.iterrows():
        rows.append(
            {
                "module_code": r["module_code"],
                "module_title": r["module_title"],
                "reading_summary": str(r["recommended_reading"])[:200],
            }
        )
    flat = pd.DataFrame(rows)
    if group_by.value == "isbn":
        flat = flat.rename(columns={"module_code": "module_count_per_book"})
    table = mo.ui.table(flat, label=f"Reading lists (grouped by {group_by.value})")
    return df, flat, group_by, rows, table
    return (tab,)


# =============================================================================
# Tab 4: Cross-archive (the user's UoG artefacts joined to scraped descriptors)
# =============================================================================


@app.cell
def _(engine, mo, pd):
    """Tab 4 content — the cross-archive join via the new Cognee edge."""
    mo.md(
        """
        ## Cross-archive

        The user's personal UoG artefacts (from
        `leabharlann/ollscoil_na_gaillimhe/`) joined to the matching
        scraped `CourseDescriptor` rows via the new
        `UoGArtifact-MATCHES-CourseDescriptor` Cognee edge.

        The edge is computed by the
        `populate_cross_archive_edges` rule in
        `cianfhoghlaim/cognify/rules/university_cross_archive.py` and
        stored in FalkorDB.
        """
    )
    if engine is None:
        return mo.md("*No data backend available.*"), pd.DataFrame()
    try:
        uog = engine.execute(
            """
            SELECT file_hash, course_code, module_title, document_kind
            FROM author_archive_uog_artifact
            ORDER BY course_code
            """
        ).to_pandas()
    except Exception as exc:  # noqa: BLE001
        uog = pd.DataFrame({"info": [f"UoG artefacts query failed: {exc}"]})
    try:
        courses = engine.execute(
            """
            SELECT course_code, course_title, school, source_url
            FROM oideachais.education.ie.university_courses
            ORDER BY course_code
            """
        ).to_pandas()
    except Exception as exc:  # noqa: BLE001
        courses = pd.DataFrame({"info": [f"Course descriptors query failed: {exc}"]})
    mo.vstack(
        [
            mo.md("### Personal UoG artefacts (left)"),
            mo.ui.table(uog, label="UoG artefacts"),
            mo.md("### Scraped UoG course descriptors (right)"),
            mo.ui.table(courses, label="Course descriptors"),
            mo.md(
                "*The new `UoGArtifact-MATCHES-CourseDescriptor` Cognee "
                "edge joins these two tables on `course_code` (exact) "
                "or title fuzzy match (> 0.85). Run "
                "`populate_cross_archive_edges(course_descriptors=...)` "
                "to populate the edges.*"
            ),
        ]
    )
    return courses, uog
    return (tab,)


if __name__ == "__main__":
    app.run()