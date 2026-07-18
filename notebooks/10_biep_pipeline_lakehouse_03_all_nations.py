# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
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

__generated_with = "0.17.2"
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