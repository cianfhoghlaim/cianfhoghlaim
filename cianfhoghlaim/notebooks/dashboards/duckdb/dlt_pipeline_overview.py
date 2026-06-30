#!/usr/bin/env python3
"""Show the 8-nation dlt pipeline overview.

Per R7.7: DLT pipeline overview.
"""
import marimo

__generated_with_marimo = True
app = marimo.App(width="medium")


@app.cell
def __():
    import marimo as mo
    return mo,


@app.cell
def __():
    """Show the 8 British Isles nations × 4 domains = 32 dlt sources + 2 special (filesystem, api, language, official_media, portfolio)."""
    from cianfhoghlaim.dlt import __init__ as dlt_init
    return dlt_init,


if __name__ == "__main__":
    app.run()
