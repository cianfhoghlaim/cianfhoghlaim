"""UoG College of Arts, Social Sciences, and Celtic Studies — 6-tab marimo notebook."""
# /// script
# requires-python = ">=3.11"
# dependencies = ["marimo>=0.10.0", "duckdb>=1.0.0", "pandas>=2.0.0"]
# ///
import marimo

__generated_with = "0.10.0"
app = marimo.App(width="medium")


@app.cell
def __():
    import marimo as mo
    return (mo,)


@app.cell
def __(mo):
    mo.md(
        """
        # College of Arts, Social Sciences, and Celtic Studies

        4 schools (Education + Acadamh na hOllscolaíochta Gaeilge +
        2 others).

        Gaeilge-medium modules are 50% of the cohort.

        **Note**: this college is bilingual (EN/GA). Per the BIEP v3
        lc_subject_pattern, the per-language CocoIndex factory emits 2
        Apps per module (en + ga).
        """
    )
    return


@app.cell
def __(mo):
    mo.ui.tabs({
        "Schools": "Schools (4)",
        "Programmes": "Programmes",
        "Modules (EN)": "Modules (English)",
        "Modules (GA)": "Modules (Irish)",
        "Handbooks": "Module handbooks",
        "Past Papers": "Past papers",
    })
    return


if __name__ == "__main__":
    app.run()
