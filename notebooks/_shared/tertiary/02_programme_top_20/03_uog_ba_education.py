"""UoG BA Education (GZ03) — 4-tab marimo notebook."""
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
    mo.md("# BA Education (GZ03)")
    return


if __name__ == "__main__":
    app.run()
