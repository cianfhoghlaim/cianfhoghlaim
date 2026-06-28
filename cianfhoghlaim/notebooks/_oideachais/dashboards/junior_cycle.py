"""Junior Cycle dashboard — Cianfhoghlaim Oideachais."""
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
        # Junior Cycle (Iar-Bhunscoil) — Cianfhoghlaim Oideachais
        ## *Iar-Bhunscoil*

        18 core subjects + 16 short courses, 2 CBAs each, 4 Achievement Levels.
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
    jc_data = pd.DataFrame(
        {
            "subject": ["Gaeilge", "English", "Maths", "Science", "Business", "Geography", "History",
                        "French", "German", "Spanish", "Italian", "Art", "Music", "Home Ec",
                        "Engineering", "Technology", "Graphics", "Classics"],
            "outcomes": [40, 38, 48, 56, 32, 30, 30, 26, 26, 26, 26, 24, 24, 28, 32, 32, 28, 24],
        }
    )
    chart = (
        alt.Chart(jc_data)
        .mark_bar()
        .encode(x="subject:N", y="outcomes:Q", color="subject:N")
        .properties(height=300, title="JC learning outcomes per subject (18 core)")
    )
    chart
    return chart, jc_data


if __name__ == "__main__":
    app.run()
