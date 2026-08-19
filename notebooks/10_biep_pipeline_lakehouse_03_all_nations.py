from notebooks._shared._pep723_template import CANONICAL_DEPENDENCIES  # canonical PEP 723 template (per the 2026-11-25-mega-3c-marimo-and-integration-v1 change)
"""cianfhoghlaim.notebooks.dashboards.education.all_nations — Marimo
notebook that compares Irish, NI, EN, SCT, WLS education pipelines
side-by-side.

Phase 8 of the openspec change. Reads from
``cianfhoghlaim.education.<nation>.<entity>`` (MotherDuck + DuckLake lakehouse
via the ``md:cianfhoghlaim`` alias; falls back to a local DuckLake attach
when ``MOTHERDUCK_TOKEN`` is unset).
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
app = marimo.App(width="medium")


@app.cell
def _imports():
    import os
    import marimo as mo
    import duckdb
    import ibis  # ibis-first entrypoint (per wire-biep-notebooks-to-lakehouse change)
    return duckdb, mo, os


@app.cell
def _header(mo):
    mo.md(
        r"""
        # Education — All Nations (Phase 8)

        Cross-nation view of the unified MotherDuck + DuckLake lakehouse
        ``md:cianfhoghlaim`` — table ``cianfhoghlaim.education.<nation>.<entity>``.
        Filter by cycle and subject; charts render on the same x-axis.
        """
    )
    return ()


@app.cell
def _connect():
    # Per the 2026-08-08-lakehouse-extensive-hydration-v1 change: this
    # cell's own hand-rolled DuckLake ATTACH (`ATTACH 'ducklake' (TYPE
    # DUCKLAKE, DATA_PATH ...)`) used a syntax that requires a
    # pre-created DuckDB SECRET named "ducklake" that never existed here
    # (confirmed live: `Secret "ducklake" was not found`) -- on top of
    # the separate `.execute()` vs `.raw_sql()` bug already fixed above.
    # Rather than debug a 3rd, notebook-specific ATTACH variant, this
    # now uses the real, live-verified canonical connection helper
    # (`notebooks/_shared/db.py::connect_local_lakehouse()`, tries the
    # real local DuckLake stack first, falls back to `connect_md()` for
    # MotherDuck, matching this notebook's own original docstring
    # intent) rather than reinventing per-notebook ATTACH logic.
    from notebooks._shared.db import connect_local_lakehouse

    # No `USE <schema>` needed -- the query below (`_summary`) already
    # fully-qualifies every table as `cianfhoghlaim.education.<nation>.
    # <entity>`. The `USE oideachais;` this cell used to run doesn't
    # correspond to any schema in the real catalog (confirmed live:
    # a raw DuckDB parser error) and served no purpose given the
    # already-qualified queries below.
    con = connect_local_lakehouse(read_only=True)
    return (con,)


@app.cell
def _summary(con):
    # Per the 2026-08-08-lakehouse-extensive-hydration-v1 change: the
    # original query referenced `cianfhoghlaim.education.<nation>.
    # <entity>` -- a 4-part catalog.schema.subschema.table name DuckDB's
    # parser can't handle at all (confirmed live: "NameListToString NOT
    # IMPLEMENTED"), against per-nation sub-schemas/tables
    # (`ncca_pages`, `ccea_pages`, `dfe_statistics`, ...) that don't
    # exist in the real catalog either -- the catalog alias
    # (`cianfhoghlaim.` — the real one, attached by
    # connect_local_lakehouse(), is `lakehouse.`) was also wrong.
    # Rewritten against the REAL live schema
    # (`lakehouse.education.subjects`, one row per jurisdiction/subject,
    # live-verified to hold real BIEP registry data) to give the same
    # "rows per nation" summary this cell is meant to show.
    rows = con.raw_sql(
        """
        SELECT jurisdiction AS nation, count(*) AS n
        FROM lakehouse.education.subjects
        GROUP BY jurisdiction
        ORDER BY jurisdiction
        """
    ).fetchall()
    return (rows,)


@app.cell
def _render(rows, mo):
    mo.md(f"**Rows per nation/agency (snapshot):** {rows}")
    return ()


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
