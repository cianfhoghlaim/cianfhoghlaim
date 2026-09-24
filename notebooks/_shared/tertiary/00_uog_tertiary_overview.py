"""UoG Tertiary Overview — 6-tab marimo notebook.

Per openspec/changes/2026-09-23-consolidate-uog-tertiary-pipeline-v1/.
The umbrella overview across the 14 DLT sources + 8 BAML files +
10 CocoIndex flows + 2 ADK agents + the per-user authenticated portal.

Run with:
    marimo edit notebooks/_shared/tertiary/00_uog_tertiary_overview.py

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo>=0.10.0",
#     "duckdb>=1.0.0",
#     "pandas>=2.0.0",
#     "pyyaml>=6.0.0",
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
        # UoG Tertiary Pipeline — Overview

        14 DLT sources + 8 BAML files + 10 CocoIndex flows + 2 ADK agents
        in the canonical `dlt_sources/british_isles/ireland/tertiary/uog/`
        namespace.

        - **Colleges** (4): science-engineering + arts-social-sciences-celtic-studies +
          business-public-policy-law + medicine-nursing-health-sciences
        - **Schools** (~10): per college
        - **Programmes** (~200): degree + masters + micro-credentials
        - **Modules** (~1,500): per programme, with module handbooks (PDF),
          reading lists, past papers

        Authenticated surfaces (per-user M365 OAuth + AppProxy cookies):
        - regexam.nuigalway.ie (past exam papers)
        - canvas.universityofgalway.ie (course materials)
        """
    )
    return


@app.cell
def __(mo):
    tabs = mo.ui.tabs({
        "Health": "Health — pipeline status",
        "Colleges": "Colleges — 4 UoG colleges",
        "Schools": "Schools — ~10 UoG schools (per college)",
        "Programmes": "Programmes — ~200 UoG programmes",
        "Modules": "Modules — ~1,500 UoG modules",
        "Authenticated": "Authenticated — regexam.nuigalway.ie + Canvas",
    })
    tabs
    return (tabs,)


@app.cell
def __(tabs):
    tabs.value
    return


if __name__ == "__main__":
    app.run()
