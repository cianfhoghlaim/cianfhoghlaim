"""UoG Past Papers Explorer — 4-tab marimo notebook (regexam.nuigalway.ie)."""
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
        # UoG Past Papers Explorer (regexam.nuigalway.ie)

        Authenticated via the per-user vault at
        `bonneagar/stacks/uo-portal-vault/`.

        Phase 1 ships 5 stub past papers (CS203, MA101, GA101, ED116).
        """
    )
    return


@app.cell
def __(mo):
    mo.ui.tabs({
        "By Module": "By module",
        "By Programme": "By programme",
        "By Year": "By year",
        "Cross-Year Trends": "Cross-year trends",
    })
    return


if __name__ == "__main__":
    app.run()
