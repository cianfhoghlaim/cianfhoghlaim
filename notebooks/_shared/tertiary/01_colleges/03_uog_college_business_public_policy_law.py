"""UoG College of Business, Public Policy, and Law — 6-tab marimo notebook."""
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
        # College of Business, Public Policy, and Law

        3 schools (Law + Business + 1 other).

        Notable: Irish Centre for Human Rights (Law school) + J.E.
        Cairnes School of Business + Economics.
        """
    )
    return


@app.cell
def __(mo):
    mo.ui.tabs({
        "Schools": "Schools (3)",
        "Programmes": "Programmes",
        "Modules": "Modules",
        "Handbooks": "Module handbooks",
        "Past Papers": "Past papers",
        "Research": "Research (ICHR + AIR)",
    })
    return


if __name__ == "__main__":
    app.run()
