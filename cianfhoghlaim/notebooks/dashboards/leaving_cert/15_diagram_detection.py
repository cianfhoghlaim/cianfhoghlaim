"""
Diagram detection comparison — 3 OCR/VLM models for figure pointing.

Compares 3 OCR/VLM models that specialise in figure / diagram detection:
  1. molmo2-8b    (Transformers; **top workhorse for syllabus diagram pointing**)
  2. qwen3-vl-8b  (workhorse; ALSO has DIAGRAM capability)
  3. glm-4.6v-flash (MLX; diagram-aware per the v4 registry)

Used by the BAML `ExtractSyllabusDiagram` workflow on chemistry formulas
+ geography maps. Compares pointing accuracy (IoU > 0.5 on bounding box).
"""

import marimo

__generated_with__ = "0.13.0"
app = marimo.App(width="medium")


@app.cell
def _setup():
    import marimo as mo
    mo.md("""
    # Diagram Detection Comparison

    3 OCR/VLM models for **diagram pointing** on chemistry + geography diagrams.

    Note: `molmo2-8b` (allenai/molmo2 arch; base=Qwen3-8B; TRANSFORMERS
    backend) is advertised as the "top workhorse for syllabus diagram
    pointing" in the v4 registry. `qwen3-vl-8b` is the workhorse fallback.
    `glm-4.6v-flash` is multilingual (Irish-friendly) and also has DIAGRAM.

    Metric: **pointing IoU > 0.5** (% of expert-marked regions hit).
    """)
    return mo


@app.cell
def _sample_data():
    return {
        "molmo2-8b":      {"pointing_iou_pct": 91.4, "diagrams_detected": 17, "wallclock_s": 26.3},
        "qwen3-vl-8b":    {"pointing_iou_pct": 84.7, "diagrams_detected": 15, "wallclock_s": 19.8},
        "glm-4.6v-flash": {"pointing_iou_pct": 82.3, "diagrams_detected": 14, "wallclock_s": 14.5},
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
    ).properties(width=120, height=200, title="Diagram pointing: IoU + count + wallclock")
    return chart


if __name__ == "__main__":
    app.run()
