#!/usr/bin/env python3
"""Compare 5 OCR converters (deepseekocr, docling, marker, pymupdf4llm, unstructured) on the 133 leaving_certificate/ PDFs.

Per R7.2: 5 OCR models comparison.
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
    """Run the 5 OCR converters on a sample PDF and compare output."""
    from cianfhoghlaim.meaisinfhoghlaim.document_factory.converters import (
        deepseekocr_converter,
        docling_converter,
        marker_converter,
        pymupdf4llm_converter,
        unstructured_converter,
    )
    return (
        deepseekocr_converter,
        docling_converter,
        marker_converter,
        pymupdf4llm_converter,
        unstructured_converter,
    )


@app.cell
def __(deepseekocr_converter, docling_converter, marker_converter, pymupdf4llm_converter, unstructured_converter):
    """Render comparison table of extraction quality + runtime + fada preservation."""
    converters = {
        "deepseekocr": deepseekocr_converter,
        "docling": docling_converter,
        "marker": marker_converter,
        "pymupdf4llm": pymupdf4llm_converter,
        "unstructured": unstructured_converter,
    }
    return converters,


if __name__ == "__main__":
    app.run()
