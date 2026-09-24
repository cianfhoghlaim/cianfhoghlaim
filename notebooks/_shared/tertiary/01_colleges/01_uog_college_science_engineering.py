"""UoG College of Science and Engineering — 6-tab marimo notebook.

Per openspec/changes/2026-09-23-consolidate-uog-tertiary-pipeline-v1/.
The per-college deep-dive: schools → programmes → modules → handbooks
→ past papers.

Run with:
    marimo edit notebooks/_shared/tertiary/01_colleges/01_uog_college_science_engineering.py

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo>=0.10.0",
#     "duckdb>=1.0.0",
#     "pandas>=2.0.0",
# ]
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
        # College of Science and Engineering

        5 schools (Computer Science + Mathematics/Statistics/Applied
        Mathematics + Physics + Chemistry + Engineering).

        ~70 programmes (BSc + MSc + ME + PhD).
        ~600 modules across those programmes.
        """
    )
    return


@app.cell
def __(mo):
    mo.ui.tabs({
        "Schools": "Schools (5)",
        "Programmes": "Programmes (~70)",
        "Modules": "Modules (~600)",
        "Handbooks": "Module handbooks (PDF)",
        "Past Papers": "Past papers (regexam)",
        "Cohort Matrix": "Cohort × Year matrix",
    })
    return


if __name__ == "__main__":
    app.run()
