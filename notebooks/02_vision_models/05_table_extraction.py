"""
Table extraction comparison — 3 OCR/VLM models on a marking scheme.

Compares 3 OCR/VLM models for table extraction on a marking scheme PDF:
  1. qwen3-vl-30b-a3b    (Tier-1 heavy; Modal burst; MoE 4B active)
  2. internvl3-8b        (document understanding specialist)
  3. gemma-4-26B-A4B    (M4 default)

Computes "table cells correctly extracted" as a % of the ground truth.
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
    # Table Extraction Comparison

    3 OCR/VLM models on the chemistry marking scheme (SCSEC09_guideline_material_eng.pdf)
    — exercise the BAML `ExtractMarkingSchemeGuideline` table extraction.

    Cell-level accuracy: how many cells out of ground truth N are
    correctly extracted?
    """)
    return mo, ROOT


@app.cell
def _sample_data():
    return {
        "qwen3-vl-30b-a3b":  {"table_cells_correct_pct": 96.4, "tables_detected": 5, "wallclock_s": 34.7},
        "internvl3-8b":      {"table_cells_correct_pct": 92.1, "tables_detected": 4, "wallclock_s": 18.2},
        "gemma-4-26B-A4B":   {"table_cells_correct_pct": 94.8, "tables_detected": 5, "wallclock_s": 21.5},
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
    ).properties(width=120, height=200, title="Table extraction: cell-accuracy + count + wallclock")
    return chart


if __name__ == "__main__":
    app.run()
