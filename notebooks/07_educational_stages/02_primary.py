"""Primary Curriculum dashboard — Cianfhoghlaim Oideachais."""
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
        # Primary (Bunscoil) — Cianfhoghlaim Oideachais
        ## *Bunscoil*

        NCCA Primary Curriculum Framework — 12 areas, 4 stages.
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
    area_data = pd.DataFrame(
        {
            "area": ["English", "Irish", "Maths", "SESE-Sci", "SESE-Hist", "SESE-Geo", "Art", "Music", "Drama", "PE", "SPHE", "Religion"],
            "outcomes": [48, 48, 56, 36, 28, 28, 24, 18, 16, 20, 24, 20],
        }
    )
    chart = (
        alt.Chart(area_data)
        .mark_bar()
        .encode(x="area:N", y="outcomes:Q", color="area:N")
        .properties(height=300, title="Primary learning outcomes per area")
    )
    chart
    return area_data, chart


if __name__ == "__main__":
    app.run()
