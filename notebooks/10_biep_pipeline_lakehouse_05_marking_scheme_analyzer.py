# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
#     "pandas>=2.0",
#     "altair>=5.0",
# ]
# ///
"""Oideachais · Marking Scheme Analyser.

Aggregate SEC marking scheme patterns by subject. Surfaces per-subject
rubrics (PCLM for English, SRPs for Geography / History, equation steps
for Mathematics) and exposes the same query-engine toggle as the rest
of the dashboard suite.

Tabs:
    1. Filters         — subject, year, level
    2. Patterns        — per-subject rubric patterns (PCLM, SRPs, equation steps)
    3. Mark dist.      — histogram of marks per question (extracted text)
    4. Keywords        — LLM-assisted keyword extraction via mo.ui.chat
    5. Cross-year      — compare rubric across years
    6. Export          — push to R2 / trigger Dagster pdf_extracted_text job

Run:
    cd cianfhoghlaim && uv run marimo edit notebooks/marking_scheme_analyzer.py
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
import ibis  # ibis-first entrypoint (per wire-biep-notebooks-to-lakehouse change)
    import pandas as pd
    import altair as alt
    import marimo as mo

    mo.md(
        """
        # Marking Scheme Analyser

        Visualise SEC marking-scheme patterns by subject and year.

        The notebook is dual-engine: ``MOTHERDUCK_ENABLED=true`` swaps the
        local DuckDB fallback for the shared MotherDuck + DuckLake
        (``md:cianfhoghlaim``) attach. Marking-scheme text is sourced from
        ``curriculum.pdf_extracted_text`` (populated by the `pdf_processing`
        Dagster asset via OCR / ColPali).

        ## Subject rubrics

        | Subject | Rubric | Notes |
        |---------|--------|-------|
        | English | PCLM (Purpose, Coherence, Language, Mechanics) | Each band ~25% |
        | Gaeilge | Cumarsáid, Léamhthuiscint, Litríocht, Gramadach | |
        | Mathematics | Equation steps + final numerical answer | |
        | Geography / History | SRPs (Significant Relevant Points) | 2 marks per SRP |
        | Biology / Chemistry | Mandatory keywords + experiment steps | |
        """
    )
    return alt, duckdb, mo, os, pathlib, pd


@app.cell
def _(mo, os, pathlib):
    MOTHERDUCK_ENABLED = os.getenv("MOTHERDUCK_ENABLED", "false").lower() == "true"
    DUCKDB_PATH = os.getenv(
        "CIANFHOGHLAIS_MARKING_DUCKDB",
        str(pathlib.Path(os.getcwd()) / "cianfhoghlaim" / ".dlt" / "curriculum_unified" / "curriculum.duckdb"),
    )
    LITELLM_ENDPOINT = os.getenv("LITELLM_ENDPOINT", "http://localhost:4000/v1")

    engine_label = "MotherDuck (remote)" if MOTHERDUCK_ENABLED else "Local DuckDB / DuckLake"
    mo.md(
        f"### Engine: **{engine_label}** &nbsp;·&nbsp; LLM endpoint: `{LITELLM_ENDPOINT}`\n\n"
        "Set `MOTHERDUCK_ENABLED=true` to switch. Credentials come from the "
        "Infisical `dev-baile` vault."
    )
    return DUCKDB_PATH, LITELLM_ENDPOINT, MOTHERDUCK_ENABLED, engine_label


@app.cell
def _(mo, pd):
    SUBJECTS = [
        "english", "gaeilge", "mathematics", "biology", "chemistry", "physics",
        "geography", "history", "french", "german", "spanish", "irish",
        "accounting", "business", "economics", "art", "music",
    ]

    SUBJECT_RUBRIC = {
        "english": "PCLM: Purpose, Coherence, Language, Mechanics",
        "gaeilge": "Cumarsáid · Léamhthuiscint · Litríocht · Gramadach",
        "mathematics": "Equation steps + final numerical answer (mark per step)",
        "biology": "Mandatory keywords (10+) · experiment steps · diagram labels",
        "chemistry": "Balanced equations · state symbols · calculation steps",
        "physics": "Definitions · units · formula manipulation · significant figures",
        "geography": "SRPs (Significant Relevant Points): 2 marks per distinct factual point",
        "history": "SRPs · historiographical perspective · primary source citation",
        "french": "Compréhension écrite · expression écrite · grammaire · vocabulaire",
        "german": "Leseverstehen · Schreiben · Grammatik · Wortschatz",
        "spanish": "Comprensión lectora · expresión escrita · gramática · vocabulario",
        "irish": "Léamh · Scríbhneoireacht · Gramadach · Líofacht",
    }

    subject_filter = mo.ui.dropdown(
        options=SUBJECTS, value="english", label="Subject",
    )
    level_filter = mo.ui.dropdown(
        options=["leaving_certificate", "junior_cycle", "leaving_certificate_applied"],
        value="leaving_certificate", label="Level",
    )
    year_range = mo.ui.range_slider(
        start=2014, stop=2025, step=1, value=[2020, 2024], label="Year range",
    )
    filters_ui = mo.vstack([
        mo.md("### Filters"),
        mo.hstack([subject_filter, level_filter, year_range]),
    ])
    return SUBJECT_RUBRIC, SUBJECTS, filters_ui, level_filter, subject_filter, year_range


@app.cell
def _(
    DUCKDB_PATH, MOTHERDUCK_ENABLED, duckdb, mo, os, pathlib, pd, subject_filter,
    level_filter, year_range,
):
    schemes = pd.DataFrame()
    err = None

    try:
        if MOTHERDUCK_ENABLED:
            _token = os.environ.get("MOTHERDUCK_TOKEN", "")
            # ibis.ibis.duckdb.connect() picks up the MotherDuck token from the
# connection URL (?motherduck_token=...) so no global SET is needed.
            _con = ibis.duckdb.connect("md:cianfhoghlaim")
        else:
            if not pathlib.Path(DUCKDB_PATH).exists():
                err = (
                    f"Local DuckDB missing at {DUCKDB_PATH}. "
                    "Run a `curriculum_*` job first to materialise pdf_extracted_text."
                )
            else:
                _con = ibis.duckdb.connect(DUCKDB_PATH, read_only=True)

        if err is None:
            schemes = _con.execute(
                """
                SELECT subject, level, year, material_type, pdf_url, title,
                       scraper, status, scraped_at
                FROM examinations.all_exam_materials
                WHERE material_type = 'marking_schemes'
                  AND subject = ?
                  AND level = ?
                  AND year BETWEEN ? AND ?
                ORDER BY year DESC
                LIMIT 500
                """,
                [
                    subject_filter.value,
                    level_filter.value,
                    int(year_range.value[0]),
                    int(year_range.value[1]),
                ],
            ).to_pandas()
            _con.close()
    except Exception as e:
        err = str(e)

    if err:
        patterns_ui = mo.callout(mo.md(f"**Error:** {err}"), kind="warn")
    else:
        patterns_ui = mo.vstack([
            mo.md(f"### Marking schemes — {len(schemes)} rows for `{subject_filter.value}`"),
            mo.ui.table(schemes, page_size=15),
        ])
    return err, patterns_ui, schemes


@app.cell
def _(SUBJECT_RUBRIC, mo, subject_filter):
    rubric = SUBJECT_RUBRIC.get(subject_filter.value, "Generic SRPs and keyword markers")
    rubric_ui = mo.vstack([
        mo.md("### Rubric for selected subject"),
        mo.callout(mo.md(f"**{subject_filter.value}**: {rubric}"), kind="info"),
        mo.md(
            "*Compare against other subjects by changing the dropdown above. "
            "The same SRP framework is used across Geography, History, and CSPE; "
            "PCLM is the standard English marker shorthand.*"
        ),
    ])
    return rubric, rubric_ui


@app.cell
def _(alt, mo, pd, schemes):
    if schemes.empty:
        mark_dist_ui = mo.md("*No data to plot yet.*")
    else:
        counts = schemes.groupby("year", as_index=False).size().rename(columns={"size": "n"})
        chart = (
            alt.Chart(counts)
            .mark_bar(color="#10b981")
            .encode(
                x=alt.X("year:O", title="Year"),
                y=alt.Y("n:Q", title="Marking schemes"),
                tooltip=["year", "n"],
            )
            .properties(width=600, height=300, title="Marking schemes per year")
        )
        mark_dist_ui = mo.ui.altair_chart(chart)
    return chart, counts, mark_dist_ui


@app.cell
def _(mo, subject_filter):
    try:
        chat = mo.ui.chat(
            mo.ai.llm.openai(
                model="gpt-4o-mini",
                system_message=(
                    f"You are an expert SEC `{subject_filter.value}` marker. "
                    "Extract the 5 most-tested rubric keywords from the user's "
                    "marking scheme snippet. Return as a numbered list."
                ),
            ),
            prompts=[
                "Extract the PCLM weighting from this English H1 paper",
                "List SRPs that recur in this Geography marking scheme",
                "Pull mandatory keywords from this Biology experiment question",
            ],
            show_configuration_controls=False,
        )
        chat_ui = mo.vstack([mo.md("### Keyword extraction (LLM)"), chat])
    except Exception as e:
        chat_ui = mo.callout(mo.md(f"LLM unavailable: {e}"), kind="warn")
    return chat, chat_ui


@app.cell
def _(mo, pd, schemes, year_range):
    if schemes.empty:
        cross_year_ui = mo.md("*No data to compare yet.*")
    else:
        pivot = (
            schemes.groupby(["year", "scraper"], as_index=False)
                   .size()
                   .pivot_table(index="year", columns="scraper", values="size", fill_value=0)
        )
        cross_year_ui = mo.vstack([
            mo.md(f"### Scrapers by year ({year_range.value[0]}–{year_range.value[1]})"),
            mo.ui.table(pivot.reset_index(), page_size=15),
        ])
    return cross_year_ui, pivot


@app.cell
def _(mo, os, subject_filter):
    dagster_url = os.getenv("DAGSTER_URL", "http://localhost:3000")
    export_btn = mo.ui.run_button(label="Trigger pdf_extracted_text materialisation")
    mo.vstack([
        mo.md("### Export & Dagster trigger"),
        mo.md(
            f"Launch the `pdf_processing` job in Dagster at "
            f"[{dagster_url}]({dagster_url}) to refresh `pdf_extracted_text` "
            "and push extracted pages to R2."
        ),
        export_btn,
    ])
    return dagster_url, export_btn


@app.cell
def _(
    SUBJECT_RUBRIC, chat_ui, export_btn, filters_ui, mark_dist_ui, mo,
    patterns_ui, rubric_ui, cross_year_ui,
):
    tabs = mo.ui.tabs({
        "Filters": filters_ui,
        "Patterns": mo.vstack([patterns_ui, rubric_ui]),
        "Marks/year": mark_dist_ui,
        "Keywords": chat_ui,
        "Cross-year": cross_year_ui,
        "Export": export_btn if isinstance(export_btn, mo.ui.run_button) else mo.vstack([export_btn, mo.md("")]),
    })
    tabs
    return (tabs,)


if __name__ == "__main__":
    app.run()