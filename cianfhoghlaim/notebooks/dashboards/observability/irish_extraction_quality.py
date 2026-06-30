#!/usr/bin/env python3
"""Irish-specific quality checks: fada preservation, dialect detection.

Per R7.5: Irish content validation.
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
    """Check fada preservation rate and Munster/Connacht/Ulster dialect coverage."""
    from cianfhoghlaim.meaisinfhoghlaim.quality.content_quality import check_irish_quality
    return check_irish_quality,


if __name__ == "__main__":
    app.run()
