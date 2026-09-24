"""UoG BSc Computer Science (GZ01) — 4-tab marimo notebook (per-programme deep dive)."""
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
        # BSc Computer Science (GZ01)

        10 modules: CS101 + CS102 + CS201 + CS202 + CS203 + CS204 +
        CS301 + CS302 + CS401 + CS402.

        Phase 1 has full handbooks + reading lists + past papers for
        CS203 (Data Structures).
        """
    )
    return


@app.cell
def __(mo):
    mo.ui.tabs({
        "Modules": "10 modules",
        "Handbooks": "Module handbooks (PDF)",
        "Reading Lists": "Reading lists",
        "Past Papers": "Past papers (regexam)",
    })
    return


if __name__ == "__main__":
    app.run()
