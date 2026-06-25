"""
oideachais.notebooks.dashboards.education.all_nations — Marimo
notebook that compares Irish, NI, EN, SCT, WLS education pipelines
side-by-side.

Phase 8 of the openspec change. Reads from
`oideachais.education.<nation>.curriculum_pages` (DuckLake via the
MotherDuck MCP `mcp__motherduck__query` or a local DuckLake attach).
"""
import marimo

__generated_with = "0.17.2"
app = marimo.App(width="medium")


@app.cell
def _imports():
    import marimo as mo
    import duckdb
    return duckdb, mo


@app.cell
def _header(mo):
    mo.md(
        r"""
        # Education — All Nations (Phase 8)

        Cross-nation view of the unified lakehouse table
        `oideachais.education.<nation>.<entity>`. Filter by cycle and
        subject; charts render on the same x-axis.
        """
    )
    return ()


@app.cell
def _connect(duckdb):
    con = duckdb.connect(":memory:")
    # Local DuckLake attach (uses the env var DUCKLAKE_DATA_PATH).
    try:
        con.execute("INSTALL ducklake; LOAD ducklake;")
        con.execute(
            "ATTACH 'ducklake' (TYPE DUCKLAKE, "
            "DATA_PATH 's3://ducklake/oideachais/');"
        )
        con.execute("USE oideachais;")
    except Exception as exc:  # noqa: BLE001
        # Fall back to MotherDuck (set MOTHERDUCK_TOKEN in env).
        try:
            con.execute("INSTALL motherduck; LOAD motherduck;")
            con.execute("ATTACH 'md:oideachais' (TYPE MOTHERDUCK);")
            con.execute("USE oideachais;")
        except Exception as exc2:  # noqa: BLE001
            print(f"could not attach: {exc}; {exc2}")
    return (con,)


@app.cell
def _summary(con):
    rows = con.execute(
        """
        SELECT 'ie' AS nation, 'NCCA' AS entity, count(*) AS n
        FROM oideachais.education.ie.ncca_pages
        UNION ALL
        SELECT 'ni', 'CCEA', count(*) FROM oideachais.education.ni.ccea_pages
        UNION ALL
        SELECT 'en', 'DfE',  count(*) FROM oideachais.education.en.dfe_statistics
        UNION ALL
        SELECT 'sct', 'CfE', count(*) FROM oideachais.education.sct.cfe_pages
        UNION ALL
        SELECT 'wls', 'CfW', count(*) FROM oideachais.education.wls.cfw_pages
        """
    ).fetchall()
    return (rows,)


@app.cell
def _render(rows, mo):
    mo.md(f"**Rows per nation/agency (snapshot):** {rows}")
    return ()


if __name__ == "__main__":
    app.run()
