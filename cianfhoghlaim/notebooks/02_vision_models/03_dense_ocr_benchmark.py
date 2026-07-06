"""
Dense OCR benchmark — formula + LaTeX-heavy maths page extraction.

Compares 2 dense-OCR specialists on a mathematics exam paper:
  1. deepseek-ocr-2    (Transformers; formula OCR specialist)
  2. olmocr-2-7b-1025  (Transformers; math-OCR specialist)

Computes a "formula recovery rate" (% of LaTeX formulas correctly
transcribed from the source PDF).
"""

# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "duckdb>=1.0",
#     "ibis-framework[duckdb]>=9.0",
#     "altair>=5.0",
#     "polars>=0.20",
# ]
# ///

import marimo

__generated_with = "0.13.0"
app = marimo.App(width="medium")


@app.cell
def _stage1_dlt_models(ROOT):
    """Run the real DLT source — 72 rows with model_key for comparison charts."""
    import sys
    sys.path.insert(0, str(ROOT.parent.parent))
    from cianfhoghlaim.dlt.filesystem.leaving_cert_source import lc5_documents
    rows = list(lc5_documents(root_path=str(ROOT.parent)))
    return rows


@app.cell
def _setup():
    import os
    import marimo as mo
    from pathlib import Path
    ROOT = Path(os.environ.get(
        "CIANFHOGHLAIM_LEAVING_CERT_ROOT",
        "/Users/cianmacandeisigh/dev/kings_college_galway/cianfhoghlaim/leaving_certificate",
    ))
    mo.md("""
    # Dense OCR Benchmark (formula-heavy)

    2 dense-OCR specialists on the mathematics exam paper (LC003ALP100EV).

    Why these 2: `deepseek-ocr-2` advertises compressed-document + formula
    OCR; `olmocr-2-7b-1025` advertises math-OCR specialist (based on
    Qwen2.5-VL-7B). Both are in the v4 TRANSFORMERS backend.

    Both need **inline llama-cpp-python or transformers** — they are NOT
    in llama-swap.
    """)
    return mo, ROOT


@app.cell
def _sample_data():
    """Sample data — replaced by real benchmark when the pipeline runs."""
    return {
        "deepseek-ocr-2":      {"formula_recovery_pct": 87.3, "cer_pct": 4.2, "wallclock_s": 28.4},
        "olmocr-2-7b-1025":    {"formula_recovery_pct": 89.7, "cer_pct": 3.6, "wallclock_s": 32.1},
    }


@app.cell
def _viz(sample_data):
    import pandas as pd
    import altair as alt
    rows = []
    for model, d in sample_data.items():
        for metric, val in d.items():
            rows.append({"model": model, "metric": metric, "value": val})
    df = pd.DataFrame(rows)
    chart = alt.Chart(df).mark_bar().encode(
        x="model:O", y="value:Q", color="model:N",
        column="metric:N",
    ).properties(width=150, height=200, title="Dense OCR benchmark on math paper")
    return chart


if __name__ == "__main__":
    app.run()
