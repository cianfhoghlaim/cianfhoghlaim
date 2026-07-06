"""
oideachais.notebooks.dashboards.law.statute_book — Marimo notebook
for the statutory law corpus (Irish Statute Book, legislation.gov.uk).

Phase 8 of the openspec change.
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
        # Law — Statute Book (Phase 8)

        Counts of statutory acts per nation. Uses the unified lakehouse
        `oideachais.law.<nation>.acts` tables.
        """
    )
    return ()


@app.cell
def _summary(duckdb):
    con = duckdb.connect(":memory:")
    rows = []
    for table in [
        "oideachais.law.ie.acts",
        "oideachais.law.ni.acts",
        "oideachais.law.en.acts",
        "oideachais.law.sct.acts",
        "oideachais.law.wls.acts",
    ]:
        try:
            n = con.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
            rows.append((table, n))
        except Exception:
            rows.append((table, 0))
    return (rows,)


@app.cell
def _render(rows, mo):
    mo.md(f"**Statutory act row counts:** {rows}")
    return ()


if __name__ == "__main__":
    app.run()
