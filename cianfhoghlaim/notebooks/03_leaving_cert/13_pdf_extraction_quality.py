#!/usr/bin/env python3
"""Ragas evaluation of the PDF extraction pipeline across all 11 subjects.

Per R7.3: PDF extraction quality.
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
    """Run Ragas eval comparing the 5 OCR converters' output against the ground-truth BAML extraction."""
    from cianfhoghlaim.meaisinfhoghlaim.evaluation.ragas_pipeline import run_ragas_eval
    return run_ragas_eval,


if __name__ == "__main__":
    app.run()
