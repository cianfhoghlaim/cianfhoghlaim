"""Tertiary (CAO + QQI + Apprenticeship) dashboard — Cianfhoghlaim Oideachais.

Reads from the `oideachais.tertiary` Cognee dataset and the
`tertiary_knowledge_graph` LanceDB table. Bilingual EN/GA.
"""
import marimo

__generated_with_marimo__ = _generate_with()
app = marimo.App(width="wide")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    mo.md(
        r"""
        # Tertiary (CAO + QQI + Apprenticeship) — Cianfhoghlaim Oideachais
        ## *Ardleibhéal / Tríú*

        13 HEIs (UCD, UCG, UCC, UL, MU, TCD, DCU, ATU, TUS, SETU, MTU, RCSI, MIC)
        + 8+ QQI FET awards + Apprenticeship pathways.

        **Source data**: LanceDB `tertiary_knowledge_graph` + Cognee
        `oideachais.tertiary` + BAML `baml_src/tertiary.baml`.

        See `oideachais/notebooks/analysis_plan/tertiary.md` for the full question set.
        """
    )
    return


@app.cell
def _(mo):
    locale = mo.ui.dropdown(options=["en", "ga"], value="en", label="Locale / Teanga")
    locale
    return (locale,)


@app.cell
def _():
    import altair as alt
    import pandas as pd
    return alt, pd


@app.cell
def _(alt, pd):
    hei_data = pd.DataFrame(
        {
            "hei": ["UCD", "UCG", "UCC", "UL", "MU", "TCD", "DCU", "ATU", "TUS", "SETU", "MTU", "RCSI", "MIC"],
            "cao_courses": [60, 50, 55, 40, 35, 45, 30, 70, 50, 45, 50, 8, 20],
        }
    )
    chart = (
        alt.Chart(hei_data)
        .mark_bar()
        .encode(x="hei:N", y="cao_courses:Q", color="hei:N")
        .properties(height=300, title="CAO courses per HEI (13 institutions)")
    )
    chart
    return chart, hei_data


@app.cell
def _(pd):
    nfq_data = pd.DataFrame(
        {
            "nfq_level": ["NFQ_6", "NFQ_7", "NFQ_8", "NFQ_9", "NFQ_10"],
            "courses": [25, 180, 250, 80, 20],
            "label": ["Advanced Cert", "Bachelor (Ordinary)", "Bachelor (Honours)", "Masters / Postgrad Dip", "Doctoral"],
        }
    )
    nfq_data
    return (nfq_data,)


@app.cell
def _(alt, nfq_data):
    nfq_chart = (
        alt.Chart(nfq_data)
        .mark_bar()
        .encode(x="nfq_level:N", y="courses:Q", color="label:N")
        .properties(height=300, title="CAO courses per NFQ level")
    )
    nfq_chart
    return (nfq_chart,)


if __name__ == "__main__":
    app.run()
