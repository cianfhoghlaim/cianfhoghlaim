#!/usr/bin/env python3
"""Performance benchmark of the PDF processing pipeline.

Per R7.4: PDF processing benchmark.
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
    """Benchmark the 5 OCR converters + the BAML extraction pipeline on a 10-PDF sample."""
    from cianfhoghlaim.meaisinfhoghlaim.evaluation.compare import compare_runtime
    return compare_runtime,


if __name__ == "__main__":
    app.run()
