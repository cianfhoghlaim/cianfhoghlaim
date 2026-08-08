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
def _connect(duckdb, os):
    con = ibis.duckdb.connect(":memory:")
    token = os.environ.get("MOTHERDUCK_TOKEN", "")
    if token:
        try:
            # ibis.duckdb.connect() picks up the MotherDuck token from the
# connection URL (?motherduck_token=...) so no global SET is needed.
            con.execute("ATTACH 'md:cianfhoghlaim' (TYPE MOTHERDUCK);")
            con.execute("USE oideachais;")
            _kind = "motherduck"
        except Exception:  # noqa: BLE001
            _kind = "local_fallback"
            con.execute("INSTALL ducklake; LOAD ducklake;")
            con.execute(
                "ATTACH 'ducklake' (TYPE DUCKLAKE, "
                "DATA_PATH 's3://ducklake/oideachais/');"
            )
            con.execute("USE oideachais;")
    else:
        try:
            con.execute("INSTALL ducklake; LOAD ducklake;")
            con.execute(
                "ATTACH 'ducklake' (TYPE DUCKLAKE, "
                "DATA_PATH 's3://ducklake/oideachais/');"
            )
            con.execute("USE oideachais;")
            _kind = "local_ducklake"
        except Exception:  # noqa: BLE001
            _kind = "unavailable"
    return (con,)


@app.cell
def _summary(con):
    rows = con.execute(
        """
        SELECT 'ie' AS nation, 'NCCA' AS entity, count(*) AS n
        FROM cianfhoghlaim.education.ie.ncca_pages
        UNION ALL
        SELECT 'ni', 'CCEA', count(*) FROM cianfhoghlaim.education.ni.ccea_pages
        UNION ALL
        SELECT 'en', 'DfE',  count(*) FROM cianfhoghlaim.education.en.dfe_statistics
        UNION ALL
        SELECT 'sct', 'CfE', count(*) FROM cianfhoghlaim.education.sct.cfe_pages
        UNION ALL
        SELECT 'wls', 'CfW', count(*) FROM cianfhoghlaim.education.wls.cfw_pages
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
