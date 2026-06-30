#!/usr/bin/env python3
"""Audit all BAML functions vs actual usage in dlt/, dagster/, cocoindex/, agents/.

Per R7.6: BAML drift audit.
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
    """Compare the 250+ BAML functions in baml/education/ + baml/celtic/ + baml/processing/ against actual usages found via ccc search."""
    import ccc
    # Pseudocode: for each BAML function, count callers
    return ccc,


if __name__ == "__main__":
    app.run()
