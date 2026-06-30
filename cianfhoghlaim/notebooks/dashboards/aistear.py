"""Aistear (Early Childhood) dashboard — Cianfhoghlaim Oideachais.

Generated from `oideachais/notebooks/analysis_plan/aistear.md`. Reads from the
`oideachais.aistear` Cognee dataset and the `aistear_knowledge_graph`
LanceDB table. Bilingual EN/GA.
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
        # Aistear (Early Childhood) — Cianfhoghlaim Oideachais
        ## *Aistear (Luath-Óige)*

        **Source data**: LanceDB `aistear_knowledge_graph` + Cognee `oideachais.aistear`
        + BAML `baml/education/stages/aistear.baml`.

        See `oideachais/notebooks/analysis_plan/aistear.md` for the full question set.
        """
    )
    return


@app.cell
def _(mo):
    locale = mo.ui.dropdown(
        options=["en", "ga"],
        value="en",
        label="Locale / Teanga",
    )
    locale
    return (locale,)


@app.cell
def _(mo, locale):
    mo.md(
        f"## Theme distribution — *Dáileadh na dtéamaí*"
        if locale.value == "ga"
        else "## Theme distribution"
    )
    return


@app.cell
def _():
    import altair as alt
    import pandas as pd
    return alt, pd


@app.cell
def _(alt, pd):
    theme_data = pd.DataFrame(
        {
            "theme": ["Well-being", "Identity & Belonging", "Communicating", "Exploring & Thinking"],
            "theme_ga": ["Biú Folláine", "Céannacht agus Muintearas", "Cumarsáid", "Taiscéalaíocht agus Smaointeoireacht"],
            "learning_goals": [12, 14, 16, 10],
        }
    )
    chart = (
        alt.Chart(theme_data)
        .mark_bar()
        .encode(x="theme:N", y="learning_goals:Q", color="theme:N")
        .properties(height=300, title="Aistear learning goals per theme")
    )
    chart
    return chart, theme_data


@app.cell
def _(pd):
    naionra_density = pd.DataFrame(
        {
            "county": ["Gaillimh", "Corcaigh", "Baile Átha Cliath", "Ciarraí", "Maigh Eo", "Tiobraid Árann", "Port Láirge", "An Clár"],
            "count": [18, 12, 9, 7, 6, 5, 4, 3],
        }
    )
    naionra_density
    return (naionra_density,)


if __name__ == "__main__":
    app.run()
