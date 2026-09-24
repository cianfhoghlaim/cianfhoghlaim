"""UoG College of Medicine, Nursing, and Health Sciences — 6-tab marimo notebook."""
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
        # College of Medicine, Nursing, and Health Sciences

        3 schools (Medicine + 2 others — Nursing + Health Sciences).

        Notable: CÚRAM Centre for Research in Medical Devices (SFI
        Research Centre).
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
        "Research": "Research (CÚRAM + REMEDI)",
    })
    return


if __name__ == "__main__":
    app.run()
