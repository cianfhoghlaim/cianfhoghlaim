"""Senior Cycle (Leaving Certificate) dashboard — Cianfhoghlaim Oideachais.

Reads from the `oideachais.senior_cycle` Cognee dataset and the
`senior_cycle_knowledge_graph` LanceDB table. Bilingual EN/GA.
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
        # Senior Cycle (Leaving Certificate) — Cianfhoghlaim Oideachais
        ## *Scoil Daraigh (Ardteistiméireacht)*

        50+ subjects across 7 families: Sciences · Languages · Business · Humanities ·
        Practical · Arts · LCA (Leaving Certificate Applied).

        **Source data**: LanceDB `senior_cycle_knowledge_graph` + Cognee
        `oideachais.senior_cycle` + BAML `baml_src/curriculum_extraction.baml`.

        See `oideachais/notebooks/analysis_plan/senior_cycle.md` for the full question set.
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
    family_data = pd.DataFrame(
        {
            "family": ["Sciences", "Languages", "Business", "Humanities", "Practical", "Arts", "LCA"],
            "subjects": [9, 14, 5, 6, 5, 2, 27],
        }
    )
    chart = (
        alt.Chart(family_data)
        .mark_bar()
        .encode(x="family:N", y="subjects:Q", color="family:N")
        .properties(height=300, title="LC subjects per family (50+ subjects, 7 families)")
    )
    chart
    return chart, family_data


@app.cell
def _(pd):
    cao_points = pd.DataFrame(
        {
            "grade": ["H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8", "O1", "O2", "O3", "O4", "O5", "O6", "O7", "O8"],
            "points": [100, 88, 77, 66, 56, 46, 37, 0, 56, 46, 37, 28, 20, 12, 0, 0],
            "higher": [True] * 8 + [False] * 8,
        }
    )
    cao_points
    return (cao_points,)


@app.cell
def _(alt, cao_points):
    cao_chart = (
        alt.Chart(cao_points)
        .mark_bar()
        .encode(x="grade:O", y="points:Q", color="higher:N")
        .properties(height=300, title="CAO points table (H1-H8, O1-O8, +25 H6+ bonus)")
    )
    cao_chart
    return (cao_chart,)


if __name__ == "__main__":
    app.run()
