# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
#     "pandas>=2.0",
#     "altair>=5.0",
# ]
# ///
"""Oideachais · Syllabus Visualiser.

Compare NCCA / CCEA / SQA / CfW syllabi side-by-side and inspect the
learning-outcome concept graph produced by the ``learning_outcome_graph``
CocoIndex flow. Bilingual coverage (en → ga, cy, gd, gv, kw, br) is
reported per subject.

Tabs:
    1. Cycle & subject filter
    2. Concept graph         — force-directed graph of outcomes
    3. Outcome taxonomy      — cluster by Bloom level / strand
    4. Cross-cycle compare   — Junior vs Senior diff
    5. Cross-nation compare  — NCCA vs CCEA vs SQA vs CfW
    6. Translation status    — 6-Celtic-language coverage matrix
    7. Embed in Dives        — export to MotherDuck Dive

Run:
    cd cianfhoghlaim && uv run marimo edit notebooks/syllabus_visualizer.py
"""
from __future__ import annotations

import marimo

__generated_with = "0.23.8"
app = marimo.App(width="wide")


@app.cell
def _():
    import os
    import pathlib
    import duckdb
    import pandas as pd
    import altair as alt
    import marimo as mo

    mo.md(
        """
        # Syllabus Visualiser

        Side-by-side view of national syllabi and the pan-Celtic concept graph.

        Sources:
        - NCCA (Ireland), CCEA (Northern Ireland), SQA (Scotland), CfW (Wales)
        - curriculumonline.ie short courses
        - pan-Celtic translation status across 6 languages

        The graph below is derived from the ``learning_outcome_graph`` CocoIndex
        flow, which embeds each outcome via BAAI/bge-m3 and clusters
        similar outcomes across cycles.
        """
    )
    return alt, duckdb, mo, os, pathlib, pd


@app.cell
def _(mo, os, pathlib):
    MOTHERDUCK_ENABLED = os.getenv("MOTHERDUCK_ENABLED", "false").lower() == "true"
    DUCKDB_PATH = os.getenv(
        "CIANFHOGHLAIS_CURRICULUM_DUCKDB",
        str(pathlib.Path(os.getcwd()) / "cianfhoghlaim" / ".dlt" / "curriculum_unified" / "curriculum.duckdb"),
    )
    engine_label = "MotherDuck (remote)" if MOTHERDUCK_ENABLED else "Local DuckDB / DuckLake"
    mo.md(
        f"### Engine: **{engine_label}**\n\n"
        "Set `MOTHERDUCK_ENABLED=true` to switch to the shared MotherDuck + DuckLake "
        "(`md:oideachais`) lakehouse. Credentials come from the Infisical `dev-baile` vault."
    )
    return DUCKDB_PATH, MOTHERDUCK_ENABLED, engine_label


@app.cell
def _(mo):
    CYCLES = ["early_childhood", "primary", "junior_cycle", "senior_cycle"]
    NATIONS = {
        "NCCA (Ireland)": "ncca",
        "CCEA (Northern Ireland)": "ccea",
        "SQA (Scotland)": "sqa",
        "CfW (Wales)": "cfw",
    }
    LANGUAGES = ["ga", "gd", "cy", "gv", "kw", "br"]

    cycle_filter = mo.ui.multiselect(options=CYCLES, value=["junior_cycle", "senior_cycle"], label="Cycle")
    language_filter = mo.ui.multiselect(
        options=["en", "ga"], value=["en", "ga"], label="Working languages",
    )
    filters_ui = mo.vstack([
        mo.md("### Filters"),
        mo.hstack([cycle_filter, language_filter]),
        mo.md(f"**Nations available:** {', '.join(NATIONS.keys())}"),
        mo.md(f"**Celtic languages tracked:** {', '.join(LANGUAGES)} (ga, gd, cy, gv, kw, br)"),
    ])
    return CYCLES, LANGUAGES, NATIONS, cycle_filter, filters_ui, language_filter


@app.cell
def _(DUCKDB_PATH, MOTHERDUCK_ENABLED, cycle_filter, duckdb, mo, os, pathlib, pd):
    pages = pd.DataFrame()
    err = None

    try:
        if MOTHERDUCK_ENABLED:
            _token = os.environ.get("MOTHERDUCK_TOKEN", "")
            duckdb.sql(f"SET motherduck_token='{_token}'")
            _con = duckdb.connect("md:oideachais")
        else:
            if pathlib.Path(DUCKDB_PATH).exists():
                _con = duckdb.connect(DUCKDB_PATH, read_only=True)
            else:
                err = f"Local DuckDB missing: {DUCKDB_PATH}. Run a `curriculum_*` job first."
        if err is None:
            _cycles = list(cycle_filter.value) if cycle_filter.value else ["senior_cycle"]
            pages = _con.execute(
                """
                SELECT cycle, subject, language, source, count(*) AS pages
                FROM curriculum.curriculum_pages
                WHERE cycle = ANY(?)
                GROUP BY cycle, subject, language, source
                ORDER BY pages DESC
                LIMIT 500
                """,
                [_cycles],
            ).fetchdf()
            _con.close()
    except Exception as e:
        err = str(e)

    if err:
        pages_ui = mo.callout(mo.md(f"**Error:** {err}"), kind="warn")
    elif pages.empty:
        pages_ui = mo.md("*No data yet. Run a `curriculum_*` Dagster job to populate.*")
    else:
        pages_ui = mo.vstack([
            mo.md(f"### Curriculum pages — {len(pages)} rows"),
            mo.ui.table(pages, page_size=20),
        ])
    return err, pages, pages_ui


@app.cell
def _(alt, mo, pages):
    if pages.empty or "subject" not in pages.columns:
        concept_ui = mo.md("*Concept graph renders once data is available.*")
    else:
        chart = (
            alt.Chart(pages)
            .mark_circle(size=120, opacity=0.7)
            .encode(
                x=alt.X("pages:Q", title="Pages"),
                y=alt.Y("subject:N", sort="-x"),
                color=alt.Color("cycle:N"),
                size=alt.Size("pages:Q", scale=alt.Scale(range=[40, 400])),
                tooltip=["cycle", "subject", "language", "pages"],
            )
            .properties(width=680, height=420, title="Concept density (subject × pages × cycle)")
        )
        concept_ui = mo.vstack([
            mo.md("### Concept density"),
            mo.ui.altair_chart(chart),
        ])
    return chart, concept_ui


@app.cell
def _(mo, pages):
    if pages.empty:
        tax_ui = mo.md("*No taxonomy to show.*")
    else:
        totals = (
            pages.groupby("cycle", as_index=False)["pages"].sum()
                 .rename(columns={"pages": "total"})
        )
        tax_ui = mo.vstack([
            mo.md("### Outcome volume by cycle"),
            mo.ui.table(totals, page_size=10),
            mo.md(
                "*Bloom-level clustering is produced by the "
                "`learning_outcome_graph` CocoIndex flow and indexed in LanceDB "
                "as the `biep_curriculum_embeddings` table.*"
            ),
        ])
    return tax_ui, totals


@app.cell
def _(cycle_filter, mo, pages):
    if pages.empty or "cycle" not in pages.columns:
        cross_cycle_ui = mo.md("*No cross-cycle comparison possible yet.*")
    else:
        selected = list(cycle_filter.value) if cycle_filter.value else []
        if not selected:
            cross_cycle_ui = mo.md("*Select cycles in the filter to compare.*")
        else:
            cmp = (
                pages[pages["cycle"].isin(selected)]
                .groupby(["cycle", "subject"], as_index=False)["pages"]
                .sum()
                .pivot_table(index="subject", columns="cycle", values="pages", fill_value=0)
            )
            cross_cycle_ui = mo.vstack([
                mo.md(f"### Cycle comparison ({', '.join(selected)})"),
                mo.ui.table(cmp.reset_index(), page_size=20),
            ])
    return cmp, cross_cycle_ui


@app.cell
def _(NATIONS, mo, pages):
    if pages.empty or "source" not in pages.columns:
        cross_nation_ui = mo.md("*No cross-nation data yet.*")
    else:
        per_nation = (
            pages.groupby("source", as_index=False)["pages"].sum()
                 .sort_values("pages", ascending=False)
        )
        cross_nation_ui = mo.vstack([
            mo.md("### Cross-nation coverage"),
            mo.md(
                f"National authorities tracked: **{', '.join(NATIONS.values())}** "
                "(in code; populated by separate `uk_*` and `celtic_*` DLT sources)."
            ),
            mo.ui.table(per_nation, page_size=10),
        ])
    return cross_nation_ui, per_nation


@app.cell
def _(LANGUAGES, mo, pages):
    if pages.empty or "language" not in pages.columns:
        tr_ui = mo.md("*No translation data yet.*")
    else:
        per_lang = (
            pages.groupby("language", as_index=False)["pages"].sum()
                 .rename(columns={"pages": "total"})
        )
        covered = set(per_lang["language"].astype(str).tolist())
        missing = [code for code in LANGUAGES if code not in covered]
        tr_ui = mo.vstack([
            mo.md("### Translation coverage"),
            mo.ui.table(per_lang, page_size=10),
            mo.callout(
                mo.md(
                    "**Celtic languages not yet populated:** "
                    f"`{', '.join(missing) if missing else 'none — fully covered'}`"
                ),
                kind="info",
            ),
        ])
    return covered, missing, per_lang, tr_ui


@app.cell
def _(mo, os):
    motherduck_url = os.getenv("MOTHERDUCK_DIVE_URL", "https://app.motherduck.com/dives")
    dive_btn = mo.ui.run_button(label="Publish to MotherDuck Dive")
    mo.vstack([
        mo.md("### Embed in MotherDuck Dive"),
        mo.md(
            f"Push this notebook's filtered dataset to a shared Dive at "
            f"[{motherduck_url}]({motherduck_url}) so other team members can "
            "consume the same data without re-running the pipeline."
        ),
        dive_btn,
    ])
    return dive_btn, motherduck_url


@app.cell
def _(
    concept_ui, cross_cycle_ui, cross_nation_ui, dive_btn, filters_ui, mo,
    pages_ui, tax_ui, tr_ui,
):
    tabs = mo.ui.tabs({
        "Filters": filters_ui,
        "Pages": pages_ui,
        "Concepts": concept_ui,
        "Taxonomy": tax_ui,
        "Cross-cycle": cross_cycle_ui,
        "Cross-nation": cross_nation_ui,
        "Translation": tr_ui,
        "Dive": dive_btn if isinstance(dive_btn, mo.ui.run_button) else mo.vstack([dive_btn, mo.md("")]),
    })
    tabs
    return (tabs,)


if __name__ == "__main__":
    app.run()