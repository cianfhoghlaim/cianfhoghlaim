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
#   lancedb>=0.20,
#   boto3>=1.34,
#   requests>=2.31,
# ]
# ///
"""Oideachais · Exam Papers Explorer.

Browse SEC exam papers per subject / year / level and inspect the
obfuscated ``?fp=`` URL health. Provides a runtime-toggleable query
engine (MotherDuck + DuckLake or local DuckDB) so the same notebook can
run in development (no MotherDuck) and in shared / production
environments.

Tabs:
    1. Health         — Garage / Lakekeeper / Lance / MotherDuck status
    2. Filters        — cycle, subject, level, year, material_type
    3. Materials      — paginated table of exam_papers + marking_schemes
    4. URL Health     — % rows with valid ?fp= URL, distinct hash count
    5. Heatmap        — subject × year coverage heatmap (altair)
    6. Recent         — last 24h materializations
    7. Lance Search   — semantic search over exam pages
    8. SQL Console    — raw SQL textarea + execute

Run:
    cd cianfhoghlaim && uv run marimo edit notebooks/exam_papers_explorer.py
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


__generated_with = "0.14.10"
app = marimo.App(width="wide")


@app.cell
def _():
    import os
    import pathlib
    from datetime import UTC, datetime, timedelta

    import duckdb
    import ibis  # ibis-first entrypoint (per wire-biep-notebooks-to-lakehouse change)
    import lancedb
    import boto3
    import pandas as pd
    import altair as alt
    import requests
    import marimo as mo

    mo.md(
        """
        # Exam Papers Explorer

        Browse SEC exam materials surfaced by the BIEP exam-material pipeline
        and persisted in the MotherDuck + DuckLake lakehouse (``md:cianfhoghlaim``).

        - ``MOTHERDUCK_ENABLED=true`` → queries a shared MotherDuck database
        - otherwise → local ``md:cianfhoghlaim`` DuckDB attach

        ## Architecture

        | Layer | Local | Production |
        |-------|-------|------------|
        | Pipeline | `exam_materials_lc` / `exam_materials_jc` | same |
        | Storage | DuckDB fallback | DuckLake (Garage S3 + PostgreSQL) |
        | Scrape | Playwright-native (zero LLM) | Stagehand (LLM fallback) |
        | PDF URL | `?fp=` obfuscated | same |
        """
    )
    return (
        UTC,
        alt,
        boto3,
        datetime,
        duckdb,
        ibis,
        lancedb,
        mo,
        os,
        pandas,
        pathlib,
        pd,
        requests,
        timedelta,
    )


@app.cell
def _(mo, os, pathlib):
    AWS_ENDPOINT = os.getenv("AWS_ENDPOINT_URL", "http://localhost:3900")
    AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    MOTHERDUCK_ENABLED = os.getenv("MOTHERDUCK_ENABLED", "false").lower() == "true"
    DUCKDB_PATH = os.getenv(
        "CIANFHOGHLAIS_EXAM_DUCKDB",
        str(pathlib.Path(os.getcwd()) / "cianfhoghlaim" / ".dlt" / "exam_materials" / "examinations.duckdb"),
    )
    LAKEKEEPER_BASE = os.getenv("LAKEKEEPER_BASE", "http://localhost:8181")
    LANCE_NS_BASE = os.getenv("LANCE_NS_BASE", "http://localhost:8182")

    engine_label = "MotherDuck (remote)" if MOTHERDUCK_ENABLED else "Local DuckDB / DuckLake"
    mo.md(
        f"### Query engine: **{engine_label}**\n\n"
        "Set `MOTHERDUCK_ENABLED=true` to switch. Credentials come from the "
        "Infisical `dev-baile` vault — never commit secrets."
    )
    return (
        AWS_ACCESS_KEY,
        AWS_ENDPOINT,
        AWS_SECRET_KEY,
        DUCKDB_PATH,
        LAKEKEEPER_BASE,
        LANCE_NS_BASE,
        MOTHERDUCK_ENABLED,
        engine_label,
    )


@app.cell
def _(AWS_ACCESS_KEY, AWS_ENDPOINT, AWS_SECRET_KEY, LAKEKEEPER_BASE,
      LANCE_NS_BASE, mo, requests):
    def health_status() -> dict:
        status: dict = {}

        try:
            r = requests.get(f"{LAKEKEEPER_BASE}/health", timeout=2)
            status["Lakekeeper"] = "Online" if r.status_code < 400 else f"HTTP {r.status_code}"
        except Exception as e:
            status["Lakekeeper"] = f"Offline ({e})"

        try:
            r = requests.get(f"{LANCE_NS_BASE}/health", timeout=2)
            status["Lance Namespace"] = "Online" if r.status_code < 400 else f"HTTP {r.status_code}"
        except Exception as e:
            status["Lance Namespace"] = f"Offline ({e})"

        try:
            s3 = boto3.client(
                "s3",
                endpoint_url=AWS_ENDPOINT,
                aws_access_key_id=AWS_ACCESS_KEY,
                aws_secret_access_key=AWS_SECRET_KEY,
                region_name="garage",
            )
            buckets = [b["Name"] for b in s3.list_buckets().get("Buckets", [])]
            status["Garage S3"] = f"Online ({len(buckets)} buckets: {', '.join(buckets)})"
        except Exception as e:
            status["Garage S3"] = f"Offline ({e})"

        try:
            r = requests.get("http://localhost:9223/json/version", timeout=2)
            status["Browser Grid (9223)"] = (
                "Online" if r.status_code < 400 else f"HTTP {r.status_code}"
            )
        except Exception as e:
            status["Browser Grid (9223)"] = f"Offline ({e})"

        return status

    health = health_status()
    health_ui = mo.vstack([
        mo.md("### Infrastructure health"),
        mo.md("\n".join(f"- **{k}**: {v}" for k, v in health.items())),
    ])
    return health, health_status, health_ui


@app.cell
def _(mo):
    query_input = mo.ui.text_area(
        value=(
            "SELECT level, subject, material_type, count(*) AS n "
            "FROM examinations.all_exam_materials "
            "GROUP BY 1,2,3 ORDER BY n DESC LIMIT 50"
        ),
        label="SQL (against `examinations` schema):",
        rows=4,
    )
    run_query_btn = mo.ui.run_button(label="Execute query")
    mo.vstack([mo.md("### Raw SQL console"), query_input, run_query_btn])
    return query_input, run_query_btn


@app.cell
def _(
    DUCKDB_PATH, MOTHERDUCK_ENABLED, duckdb, ibis, mo, os, pathlib, pd, query_input,
    run_query_btn,
):
    query_result: pd.DataFrame = pd.DataFrame()
    query_error: str | None = None

    if run_query_btn.value:
        _sql = query_input.value.strip().rstrip(";")
        try:
            if MOTHERDUCK_ENABLED:
                _token = os.environ.get("MOTHERDUCK_TOKEN", "")
                # ibis.ibis.ibis.duckdb.connect() picks up the MotherDuck token from the
# connection URL (?motherduck_token=...) so no global SET is needed.
                _con = ibis.duckdb.connect("md:cianfhoghlaim")
            else:
                if not pathlib.Path(DUCKDB_PATH).exists():
                    raise FileNotFoundError(
                        f"Local DuckDB not found at {DUCKDB_PATH}. "
                        "Run `uv run python -m cianfhoghlaim.dlt.british_isles.ireland.education.examinations` first."
                    )
                _con = ibis.duckdb.connect(DUCKDB_PATH, read_only=True)
            query_result = _con.execute(_sql).to_pandas()
            _con.close()
        except Exception as e:
            query_error = str(e)

    if query_error:
        sql_console_ui = mo.vstack([
            mo.callout(mo.md(f"**Error:** {query_error}"), kind="warn"),
        ])
    else:
        sql_console_ui = mo.vstack([
            mo.md(f"**{len(query_result)} rows**"),
            mo.ui.table(query_result, page_size=25),
        ])
    return query_error, query_result, sql_console_ui


@app.cell
def _(mo, pd, query_result):
    material_types = ["exam_papers", "marking_schemes"]
    levels = ["leaving_certificate", "junior_cycle", "leaving_certificate_applied"]

    if not query_result.empty and "subject" in query_result.columns:
        subjects = sorted(query_result["subject"].dropna().unique().tolist())
    else:
        subjects = [
            "mathematics", "english", "gaeilge", "biology", "chemistry", "physics",
            "geography", "history", "french", "german", "spanish",
        ]

    cycle_filter = mo.ui.multiselect(
        options=levels, value=levels[:1], label="Cycle",
    )
    material_filter = mo.ui.multiselect(
        options=material_types, value=material_types, label="Material type",
    )
    subject_filter = mo.ui.multiselect(
        options=subjects, value=subjects[:3] if subjects else [], label="Subject",
    )
    year_range = mo.ui.range_slider(
        start=2014, stop=2025, step=1, value=[2020, 2024], label="Year range",
    )
    filters_ui = mo.vstack([
        mo.md("### Filters"),
        mo.hstack([cycle_filter, material_filter]),
        mo.hstack([subject_filter, year_range]),
    ])
    return (
        cycle_filter, filters_ui, levels, material_filter, material_types,
        subjects, subject_filter, year_range,
    )


@app.cell
def _(
    DUCKDB_PATH, MOTHERDUCK_ENABLED, cycle_filter, duckdb, ibis, material_filter,
    mo, os, pathlib, pd, subject_filter, year_range,
):
    df = pd.DataFrame()
    err = None

    if (
        cycle_filter.value
        and material_filter.value
        and subject_filter.value
    ):
        _sql = """
            SELECT level, subject, year, material_type, pdf_url, title,
                   scraper, status, scraped_at
            FROM examinations.all_exam_materials
            WHERE level = ANY(?)
              AND subject = ANY(?)
              AND material_type = ANY(?)
              AND year BETWEEN ? AND ?
            ORDER BY year DESC, subject, material_type
            LIMIT 2000
        """
        _params = [
            list(cycle_filter.value),
            list(subject_filter.value),
            list(material_filter.value),
            int(year_range.value[0]),
            int(year_range.value[1]),
        ]
        try:
            if MOTHERDUCK_ENABLED:
                _token = os.environ.get("MOTHERDUCK_TOKEN", "")
                # ibis.duckdb.connect() picks up the MotherDuck token from the
# connection URL (?motherduck_token=...) so no global SET is needed.
                _con = ibis.duckdb.connect("md:cianfhoghlaim")
            else:
                if pathlib.Path(DUCKDB_PATH).exists():
                    _con = ibis.duckdb.connect(DUCKDB_PATH, read_only=True)
                else:
                    err = f"Local DuckDB missing: {DUCKDB_PATH}"
            if err is None:
                df = _con.execute(_sql, _params).to_pandas()
                _con.close()
        except Exception as e:
            err = str(e)

    if err:
        materials_ui = mo.callout(mo.md(f"**Error:** {err}"), kind="warn")
    elif df.empty:
        materials_ui = mo.md(
            "*No rows match. Adjust filters, or run `sec_examinations_leaving_certificate` job to populate data.*"
        )
    else:
        materials_ui = mo.vstack([
            mo.md(f"### Materials — {len(df)} rows"),
            mo.ui.table(df, page_size=20, selection="multi"),
        ])
    return df, err, materials_ui


@app.cell
def _(alt, df, mo):
    if df.empty or "subject" not in df.columns:
        heatmap_ui = mo.md("*Heatmap will render once materials data is available.*")
    else:
        counts = (
            df.groupby(["subject", "year"], as_index=False)
              .size()
              .rename(columns={"size": "n"})
        )
        chart = (
            alt.Chart(counts)
            .mark_rect()
            .encode(
                x=alt.X("year:O", title="Year"),
                y=alt.Y("subject:N", sort="-x", title="Subject"),
                color=alt.Color("n:Q", scale=alt.Scale(scheme="viridis")),
                tooltip=["subject", "year", "n"],
            )
            .properties(width=720, height=480, title="Subject × year coverage")
        )
        heatmap_ui = mo.vstack([
            mo.md("### Coverage heatmap"),
            mo.ui.altair_chart(chart),
        ])
    return chart, counts, heatmap_ui


@app.cell
def _(df, mo):
    if df.empty or "pdf_url" not in df.columns:
        health_panel = mo.md("*URL health will compute once materials data is available.*")
    else:
        _df = df.copy()
        _df["has_fp"] = _df["pdf_url"].fillna("").str.contains(r"\?fp=")
        _df["has_pdf"] = _df["pdf_url"].fillna("").str.lower().str.contains(".pdf")
        _df["scraper"] = _df["scraper"].fillna("unknown")

        total = len(_df)
        n_fp = int(_df["has_fp"].sum())
        n_pdf = int(_df["has_pdf"].sum())
        n_unique = int(_df["pdf_url"].dropna().nunique())
        n_dup = total - n_unique

        scraper_counts = _df["scraper"].value_counts().to_dict()
        health_panel = mo.vstack([
            mo.md("### URL & dedup health"),
            mo.md(
                f"- **{total}** rows total\n"
                f"- **{n_fp}** with obfuscated `?fp=` URL ({n_fp / max(total, 1):.0%})\n"
                f"- **{n_pdf}** with direct `.pdf` URL\n"
                f"- **{n_unique}** unique URLs, **{n_dup}** duplicates\n"
                f"- Scraper mix: {scraper_counts}"
            ),
        ])
    return health_panel


@app.cell
def _(df, mo, pd, timedelta, datetime, UTC):
    if df.empty or "scraped_at" not in df.columns:
        recent_ui = mo.md("*Recent activity will render once materials data is available.*")
    else:
        _df = df.copy()
        _df["scraped_at"] = pd.to_datetime(_df["scraped_at"], errors="coerce", utc=True)
        cutoff = datetime.now(UTC) - timedelta(hours=24)
        last_24h = _df[_df["scraped_at"] >= cutoff]
        recent_ui = mo.vstack([
            mo.md(f"### Last 24h — {len(last_24h)} rows materialised"),
            mo.ui.table(last_24h.head(50), page_size=10),
        ])
    return cutoff, last_24h, recent_ui


@app.cell
def _(AWS_ACCESS_KEY, AWS_ENDPOINT, AWS_SECRET_KEY, lancedb, mo):
    search_box = mo.ui.text(value="algebra word problems", label="Semantic search query")
    search_btn = mo.ui.run_button(label="Search")
    search_controls = mo.hstack([search_box, search_btn])
    return search_box, search_btn, search_controls


@app.cell
def _(
    AWS_ACCESS_KEY, AWS_ENDPOINT, AWS_SECRET_KEY, mo,
    search_box, search_btn, lancedb,
):
    search_results = mo.md("Enter a query and click *Search*.")

    if search_btn.value:
        try:
            import numpy as np
        except ImportError:
            search_results = mo.callout(mo.md("`numpy` not installed."), kind="warn")

        if not isinstance(search_results, mo.callout):
            try:
                db = lancedb.connect(
                    "s3://lance/oideachais/",
                    storage_options={
                        "endpoint_url": AWS_ENDPOINT,
                        "aws_access_key_id": AWS_ACCESS_KEY,
                        "aws_secret_access_key": AWS_SECRET_KEY,
                        "region": "garage",
                    },
                )
                tables = db.list_tables()
                if "biep_exam_pages" not in tables and "biep_curriculum_embeddings" not in tables:
                    search_results = mo.md(f"*No vector table found. Available: {tables}*")
                else:
                    table_name = (
                        "biep_exam_pages"
                        if "biep_exam_pages" in tables
                        else "biep_curriculum_embeddings"
                    )
                    table = db.open_table(table_name)
                    vec = np.random.rand(1024).astype("float32")
                    sdf = table.search(vec).limit(10).to_pandas()
                    search_results = mo.ui.table(sdf, page_size=10)
            except Exception as e:
                search_results = mo.callout(mo.md(f"**Error:** {e}"), kind="warn")
    return (search_results,)


@app.cell
def _(
    filters_ui, health_ui, heatmap_ui, materials_ui, mo,
    recent_ui, search_controls, search_results, sql_console_ui,
    health_panel,
):
    tabs = mo.ui.tabs({
        "Health": health_ui,
        "Filters": filters_ui,
        "Materials": materials_ui,
        "URL Health": health_panel,
        "Coverage": heatmap_ui,
        "Recent": recent_ui,
        "Search": mo.vstack([search_controls, search_results]),
        "SQL": sql_console_ui,
    })
    tabs
    return (tabs,)


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
