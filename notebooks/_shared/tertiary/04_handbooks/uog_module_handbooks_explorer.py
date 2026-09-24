"""UoG Module Handbooks Explorer — 4-tab marimo notebook."""
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
        # UoG Module Handbooks Explorer

        The BIEP v2 4-path OCR ensemble (BAML/Docling + Unstract +
        qwen3-vl-8b + gemma-4-26B-A4B) + RAGAS voting per the
        centralised-registry spec.

        Phase 1 ships 3 handbooks (CS203, MA101, GA101).
        """
    )
    return


@app.cell
def __(mo):
    mo.ui.tabs({
        "Handbooks": "Per-module handbooks",
        "Reading Lists": "Reading lists",
        "Learning Outcomes": "Learning outcomes",
        "Assessment Breakdown": "Assessment breakdown",
    })
    return


if __name__ == "__main__":
    app.run()
