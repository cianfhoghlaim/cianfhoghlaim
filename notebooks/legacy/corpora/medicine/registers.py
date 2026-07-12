"""
oideachais.notebooks.dashboards.medicine.registers — Marimo notebook
for the medicine registers (HSE, Medical Council, GMC, NHS).

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
        # Medicine — Registers (Phase 8)

        Joint view of the medical register pages for IE, NI, EN, SCT, WLS.
        """
    )
    return ()


@app.cell
def _summary(duckdb):
    con = duckdb.connect(":memory:")
    rows = []
    for table in [
        "oideachais.medicine.ie.hse_pages",
        "oideachais.medicine.ie.medicalcouncil_register",
        "oideachais.medicine.ni.nidirect_pages",
        "oideachais.medicine.en.nhs_england_pages",
        "oideachais.medicine.en.gmc_pages",
        "oideachais.medicine.en.nice_guidelines_pages",
        "oideachais.medicine.sct.nhs_scotland_pages",
        "oideachais.medicine.wls.nhs_wales_pages",
    ]:
        try:
            n = con.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
            rows.append((table, n))
        except Exception:
            rows.append((table, 0))
    return (rows,)


@app.cell
def _render(rows, mo):
    mo.md(f"**Medicine register row counts:** {rows}")
    return ()


if __name__ == "__main__":
    app.run()
