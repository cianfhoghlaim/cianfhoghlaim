#!/usr/bin/env python3
"""Show all 14+ CocoIndex v1 Apps + their LanceDB tables + embedding counts.

Per R7.8: CocoIndex embedding coverage.
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
    """Show the 14+ v1 Apps (8 subject embeddings + 2 leabharlann + 4 infrastructure) and their LanceDB tables."""
    from cianfhoghlaim.cocoindex import _lifespan
    return _lifespan,


if __name__ == "__main__":
    app.run()
