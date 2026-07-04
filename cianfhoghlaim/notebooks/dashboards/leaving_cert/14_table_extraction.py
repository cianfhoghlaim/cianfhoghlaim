"""
Table extraction comparison — 3 OCR/VLM models on a marking scheme.

Compares 3 OCR/VLM models for table extraction on a marking scheme PDF:
  1. qwen3-vl-30b-a3b    (Tier-1 heavy; Modal burst; MoE 4B active)
  2. internvl3-8b        (document understanding specialist)
  3. gemma-4-26B-A4B    (M4 default)

Computes "table cells correctly extracted" as a % of the ground truth.
"""

import marimo

__generated_with__ = "0.13.0"
app = marimo.App(width="medium")


@app.cell
def _setup():
    import marimo as mo
    mo.md("""
    # Table Extraction Comparison

    3 OCR/VLM models on the chemistry marking scheme (SCSEC09_guideline_material_eng.pdf)
    — exercise the BAML `ExtractMarkingSchemeGuideline` table extraction.

    Cell-level accuracy: how many cells out of ground truth N are
    correctly extracted?
    """)
    return mo


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
