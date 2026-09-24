"""UoG Authenticated Portal Explorer — 4-tab marimo notebook (regexam + Canvas)."""
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
        # UoG Authenticated Portal Explorer

        Per-user credential vault at
        `bonneagar/stacks/uo-portal-vault/` (the
        `komodo run unlock-uo-portal --user <u> --service {regexam,canvas}`
        procedure).
        """
    )
    return


@app.cell
def __(mo):
    mo.ui.tabs({
        "regexam": "regexam.nuigalway.ie — past papers",
        "Canvas": "canvas.universityofgalway.ie — course materials",
        "Submissions": "Per-user download history",
        "Vault": "Vault status (per-user cookies + tokens)",
    })
    return


if __name__ == "__main__":
    app.run()
