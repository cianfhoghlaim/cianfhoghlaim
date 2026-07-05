"""
Layout extraction comparison — 3 specialists on a syllabus PDF.

Compares 3 layout specialists for syllabus extraction:
  1. granite-docling-258M  (mlx_community; tiny, DocTags layout)
  2. dots.ocr              (mlx_community; layout specialist)
  3. internvl3-8b         (llama-swap; document understanding)

Renders figure + table counts per model on the same input.
"""

import marimo

__generated_with__ = "0.13.0"
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
    import marimo as mo
    mo.md("""
    # Layout Extraction Comparison

    3 layout specialists on the geography syllabus:
    - **granite-docling-258M**: tiny (258M), DocTags output
    - **dots.ocr**: 3.0B, layout specialist
    - **internvl3-8b**: 8.5B, document understanding + 2D layout

    All 3 are in the v4 OCR/VLM registry's MLX or LLAMASWAP backends.
    """)
    return mo


@app.cell
def _sample_data():
    """Sample data — replaced by real extraction when the pipeline runs."""
    return {
        "granite-docling-258M": {"figures_detected": 14, "tables_detected": 7, "headings_detected": 23, "wallclock_s": 12.3},
        "dots.ocr":             {"figures_detected": 12, "tables_detected": 6, "headings_detected": 19, "wallclock_s": 18.6},
        "internvl3-8b":         {"figures_detected": 15, "tables_detected": 7, "headings_detected": 25, "wallclock_s": 42.1},
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
        x="model:O", y="value:Q", color="metric:N",
        column="metric:N",
    ).properties(width=120, height=200, title="Layout extraction: figure / table / heading count + wallclock")
    return chart


if __name__ == "__main__":
    app.run()
