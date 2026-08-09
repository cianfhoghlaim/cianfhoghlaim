# /// script
# requires-python = ">=3.12"
# dependencies = [
#   marimo>=0.13,
#   duckdb>=1.0,
#   ibis-framework[duckdb]>=9.0,
#   pandas>=2.2,
#   altair>=5.0,
#   pyarrow>=15,
#   anywidget>=0.9,
#   traitlets>=5.14,
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

The notebook uses ``mo.sql(engine=md:cianfhoghlaim)`` (the MotherDuck +
DuckLake lakehouse) for the underlying queries. When the MotherDuck
endpoint is unreachable, the notebook falls back to a local DuckDB
file (``/tmp/cianfhoghlaim.duckdb``) for development.

Reference: openspec/changes/university-of-galway-deep-extraction/
"""
from __future__ import annotations

import marimo


# R1 — `setup_biep_registry_header()` collapses the 14-line header
# (per the 2026-08-10-marimo-v14-ireland-england-dashboards-refactor-v1 change)
from notebooks._shared.marimo_patterns import (
    cli_argparser_biep,
    cli_main_if_argv,
    cli_payload_to_output,
    llm_chat_with_prompts,
    setup_biep_registry_header,
)


__generated_with = "0.23.10"
app = marimo.App(width="medium")


@app.cell
def _():
    """Setup and imports."""
    import os

    import marimo as mo
    import pandas as pd

    # Per the 2026-08-08-lakehouse-extensive-hydration-v1 change: the
    # old MotherDuck path called `duckdb.sql(f"SET motherduck_token=...")`
    # against DuckDB's implicit global default connection -- a DIFFERENT
    # connection object than the one `ibis.duckdb.connect("md:cianfhoghlaim")`
    # creates right after, so the SET never actually reached the
    # connection that needed it (confirmed live: "unrecognized
    # configuration parameter motherduck_token", since the local-only
    # `ibis.duckdb.connect(":memory:")` fallback doesn't have the
    # motherduck extension loaded either). Replaced with the real,
    # live-verified canonical connection helper (`notebooks/_shared/
    # db.py`), which tries the real local DuckLake stack first.
    # NOTE: a merge (2026-08-09) reintroduced the actual buggy code below
    # this comment while keeping the comment describing the fix -- the
    # other concurrent session's notebook rewrite carried the old
    # duckdb.sql(f"SET motherduck_token=...") pattern forward. Re-applying
    # the same fix as before.
    try:
        from notebooks._shared.db import connect_local_lakehouse

        engine = connect_local_lakehouse(read_only=True)
        ENGINE_LABEL = "local DuckLake (Garage + Postgres)"
    except ImportError:
        engine = None
        ENGINE_LABEL = "ibis not installed"

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
    # Per the 2026-08-08-lakehouse-extensive-hydration-v1 change: this
    # cell used to have 3 mid-cell `return` statements plus a dead,
    # unreachable `return (tab,)` after the real return (referencing
    # `tab`, a name from a different cell entirely) -- marimo requires
    # a single unconditional return at the end of a cell (confirmed
    # live: "SyntaxError: 'return' outside function"). Also fixed
    # `engine.execute(<raw sql>)` -> `engine.sql(<raw sql>)` (ibis's
    # `.execute()` expects an expression object, not a raw string; see
    # the identical fix in 03_all_nations.py).
    mo.md(
        """
        ## M.Sc. AI 25/26 modules

        The user's upcoming programme. Pre-filtered to
        `programme_codes = ["MSCAI"]` and `academic_year = 2025`.
        """
    )
    if engine is None:
        _table = mo.md("*No data backend available — render stub table below.*")
    else:
        try:
            _df = engine.sql(
                """
                SELECT
                    module_code,
                    module_title,
                    ects,
                    semester,
                    programme_codes,
                    source_url
                FROM cianfhoghlaim.education.ie.university_modules
                WHERE programme_codes LIKE '%MSCAI%'
                  AND academic_year = 2025
                ORDER BY module_code
                """
            ).to_pandas()
        except Exception as exc:  # noqa: BLE001
            _table = mo.md(f"*Query failed: {exc}*")
        else:
            if _df.empty:
                _table = mo.md("*No M.Sc. AI 25/26 modules yet — run `uog_extract_modules`.*")
            else:
                _table = mo.ui.table(_df, label="M.Sc. AI 25/26 modules")
    _table
    return


# =============================================================================
# Tab 2: All UoG courses
# =============================================================================


@app.cell
def _(engine, mo, pd):
    """Tab 2 content — all UoG courses with search + filter."""
    # Per the 2026-08-08-lakehouse-extensive-hydration-v1 change: same
    # multi-return / engine.execute() / dead-trailing-return fixes as
    # Tab 1 above. `search`/`school_filter`/`nfq_filter`/`filtered`/
    # `table` weren't consumed by any other cell, so all are now
    # cell-local.
    mo.md(
        """
        ## All UoG courses

        Searchable + filterable by school, NFQ level, ECTS, programme
        stage.
        """
    )
    if engine is None:
        mo.md("*No data backend available.*")
    else:
        try:
            _df = engine.sql(
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
                FROM cianfhoghlaim.education.ie.university_courses
                ORDER BY school, course_code
                """
            ).to_pandas()
        except Exception as exc:  # noqa: BLE001
            mo.md(f"*Query failed: {exc}*")
        else:
            _search = mo.ui.text(placeholder="search title/code…", value="")
            _school_filter = mo.ui.multiselect(
                options=sorted(_df["school"].dropna().unique().tolist()) if not _df.empty else [],
                value=[],
                label="School",
            )
            _nfq_filter = mo.ui.multiselect(
                options=sorted(_df["nfq_level"].dropna().unique().tolist()) if not _df.empty else [],
                value=[],
                label="NFQ Level",
            )
            _filtered = _df
            if _search.value:
                _mask = (
                    _df["course_title"].str.contains(_search.value, case=False, na=False)
                    | _df["course_code"].astype(str).str.contains(_search.value, case=False, na=False)
                )
                _filtered = _filtered[_mask]
            if _school_filter.value:
                _filtered = _filtered[_filtered["school"].isin(_school_filter.value)]
            if _nfq_filter.value:
                _filtered = _filtered[_filtered["nfq_level"].isin(_nfq_filter.value)]
            mo.ui.table(_filtered, label=f"All UoG courses ({len(_filtered)} rows)")
    return


# =============================================================================
# Tab 3: Reading lists
# =============================================================================


@app.cell
def _(engine, mo, pd):
    """Tab 3 content — reading lists with group-by toggle."""
    # Per the 2026-08-08-lakehouse-extensive-hydration-v1 change: same
    # multi-return / engine.execute() / dead-trailing-return fixes as
    # Tabs 1-2 above. Nothing downstream consumed
    # df/flat/group_by/rows/table, so all are now cell-local.
    mo.md(
        """
        ## Reading lists

        Every reading-list item across all modules, with a "Group by
        module" vs "Group by ISBN-13" toggle.
        """
    )
    if engine is None:
        mo.md("*No data backend available.*")
    else:
        _group_by = mo.ui.radio(
            options=["module", "isbn"],
            value="module",
            label="Group by",
        )
        try:
            _df = engine.sql(
                """
                SELECT
                    m.module_code,
                    m.module_title,
                    m.recommended_reading
                FROM cianfhoghlaim.education.ie.university_modules m
                WHERE m.recommended_reading IS NOT NULL
                  AND m.recommended_reading != ''
                ORDER BY m.module_code
                """
            ).to_pandas()
        except Exception as exc:  # noqa: BLE001
            mo.md(f"*Query failed: {exc}*")
        else:
            if _df.empty:
                mo.md("*No reading lists yet — run `uog_extract_modules`.*")
            else:
                _rows: list[dict[str, str]] = []
                for _, _r in _df.iterrows():
                    _rows.append(
                        {
                            "module_code": _r["module_code"],
                            "module_title": _r["module_title"],
                            "reading_summary": str(_r["recommended_reading"])[:200],
                        }
                    )
                _flat = pd.DataFrame(_rows)
                if _group_by.value == "isbn":
                    _flat = _flat.rename(columns={"module_code": "module_count_per_book"})
                mo.ui.table(_flat, label=f"Reading lists (grouped by {_group_by.value})")
    return


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
    # Per the 2026-08-08-lakehouse-extensive-hydration-v1 change: same
    # multi-return / engine.execute() / dead-trailing-return fixes as
    # Tabs 1-3 above. Nothing downstream consumed courses/uog, so both
    # are now cell-local.
    if engine is None:
        mo.md("*No data backend available.*")
    else:
        try:
            _uog = engine.sql(
                """
                SELECT file_hash, course_code, module_title, document_kind
                FROM author_archive_uog_artifact
                ORDER BY course_code
                """
            ).to_pandas()
        except Exception as exc:  # noqa: BLE001
            _uog = pd.DataFrame({"info": [f"UoG artefacts query failed: {exc}"]})
        try:
            _courses = engine.sql(
                """
                SELECT course_code, course_title, school, source_url
                FROM cianfhoghlaim.education.ie.university_courses
                ORDER BY course_code
                """
            ).to_pandas()
        except Exception as exc:  # noqa: BLE001
            _courses = pd.DataFrame({"info": [f"Course descriptors query failed: {exc}"]})
        mo.vstack(
            [
                mo.md("### Personal UoG artefacts (left)"),
                mo.ui.table(_uog, label="UoG artefacts"),
                mo.md("### Scraped UoG course descriptors (right)"),
                mo.ui.table(_courses, label="Course descriptors"),
                mo.md(
                    "*The new `UoGArtifact-MATCHES-CourseDescriptor` Cognee "
                    "edge joins these two tables on `course_code` (exact) "
                    "or title fuzzy match (> 0.85). Run "
                    "`populate_cross_archive_edges(course_descriptors=...)` "
                    "to populate the edges.*"
                ),
            ]
        )
    return


if __name__ == "__main__":
    app.run()

# ────────────────────────────────────────────────────────────────────────────
# P3 — LLM-assisted analysis tab (the "Ask BAML" tab)
# ────────────────────────────────────────────────────────────────────────────

@app.cell
def _llm_tab(mo):
    """P3 — LLM-assisted analysis tab via mo.ui.chat + mo.ai.llm.openai()."""
    _chat = llm_chat_with_prompts(
        system_message=(
            "You are the BIEP v3 lakehouse explorer assistant. You help "
            "operators query the DuckLake / MotherDuck / LanceDB lakehouse. "
            "When the user asks about a table or column, refer to the DLT "
            "schema introspection in information_schema.tables."
        ),
        prompts=[
            "📚 How many tables are in this schema?",
            "🔍 Show me the schema for the most recently materialised table",
            "📊 What are the top 10 most frequent values in <column_name>?",
            "🎯 How do I query for a specific subject's curriculum_pages?",
        ],
    )
    mo.vstack([mo.md("## 🤖 Ask BAML (via litellm → minimax-m3)"), _chat])
    return (_chat,)


# ────────────────────────────────────────────────────────────────────────────
# Dual-mode CLI (per https://docs.marimo.io/guides/scripts/)
# ────────────────────────────────────────────────────────────────────────────

def _cli_main(argv=None):
    """CLI entry point — emits a JSON summary payload (per marimo scripts guide)."""
    parser = cli_argparser_biep("BIEP lakehouse explorer")
    args = parser.parse_args(argv)

    payload = {
        "notebook": __name__,
        "milestone": args.milestone,
        "asset_check": args.asset_check,
        "status": "ok",
        "exit_code": 0,
        "note": (
            "Run `dagster dev -m oideachais` to start the pipeline, then "
            "re-run this CLI to see the latest status."
        ),
    }
    print(cli_payload_to_output(payload, args.output))
    return 0


if __name__ == "__main__":
    cli_main_if_argv(_cli_main, app)
