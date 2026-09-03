# Agent 135 — Marimo for Analysis (5 Starter Analysis Notebooks, 2026-06-29)

**Date:** 2026-06-29
**Scope:** 5 analysis notebooks that go deeper than the 11 existing
dashboards — they read from **all 5 stages** + the leabharlann corpus
and surface cross-corpus insights. Drop-in peers to the dlthub starter
notebooks at `.agents/skills/dlthub/notebooks/starter_*.py`.
**Prior art:** the 5-stage dashboards at
`cianfhoghlaim/notebooks/_oideachais/dashboards/{aistear,primary,junior_cycle,senior_cycle,tertiary}.py`.

## 1. TL;DR

The 11 existing dashboards at `oideachais/notebooks/_oideachais/dashboards/`
are **per-stage single-corpus views**. The 5 new analysis notebooks
answer **cross-corpus questions** that no single dashboard answers today: (1) what topics dominate the leabharlann? (2) how accurate is OCR across the 6 backends? (3) how complete is the BAML coverage of Senior Cycle outcomes? (4) is the DLT pipeline healthy? (5) is the Dagster code-location healthy?

Every notebook is `uv run`-able, uses `mo.ui.dropdown` for **interactive filtering** (re-runs the heavy cell automatically via marimo's reactive DAG), and writes its summary back to `lakehouse.analysis.<notebook_name>` for the `oideachais-web` dashboard.

## 2. The 5 starter analysis notebooks

### 2.1 `01_leabharlann_topic_distribution.py`
| Field | Value |
|:--|:--|
| **Purpose** | Visualise topic distribution across the 6 leabharlann sub-corpora (`aigne`, `gaeilge`, `gemini_deep_research`, `mata`, `ollscoil_na_gaillimhe`, `zotero`) using BGE-M3 + UMAP |
| **Marimo features** | `mo.ui.multiselect` (corpus), `mo.ui.slider` (n_neighbors), `mo.ui.altair_chart` (scatter), `mo.ui.dataframe` (top topics) |
| **Data source** | `lancedb_data/leabharlann.lance` (BGE-M3 + BGE-large-en-v1.5 hybrid) |
| **Expected output** | 2-D UMAP scatter by cluster + sidebar table of top-10 docs per cluster |
| **Write-back** | `INSERT INTO lakehouse.analysis.leabharlann_topics SELECT cluster_id, COUNT(*) FROM ...` |

| Field | Value |
|:--|:--|
| **Purpose** | Compare the 6 OCR backends (Pylaia, TrOCR, PaddleOCR, Tesseract, dots.ocr, VLM) on the 50-page gold corpus from `meaisinfhoghlaim/ocr/tests/gold/` |
| **Marimo features** | `mo.ui.dropdown` (page), `mo.ui.tabs` (one per backend), `mo.ui.dataframe` (per-line confidence), `mo.md` (CER summary), `mo.ui.altair_chart` (CER bar) |
| **Data source** | `lakehouse.meaisinfhoghlaim.ocr_runs` (the per-page CER + WER + runtime) |
| **Expected output** | A 6-tab view: each tab shows the page image + 6 candidate transcriptions + the gold text + per-backend CER. A summary bar chart at the top. |
| **Write-back** | `INSERT INTO lakehouse.analysis.ocr_accuracy SELECT model, AVG(cer) FROM ...` |

### 2.3 `03_outcome_coverage.py`
| Field | Value |
|:--|:--|
| **Purpose** | For each Senior Cycle subject, show % of NCCA outcomes with matching BAML row, broken down by material_type |
| **Marimo features** | `mo.ui.multiselect` (subjects), `mo.ui.slider` (year), `mo.ui.dataframe` (%), `mo.ui.altair_chart` (stacked bar), `mo.md` (action items) |
| **Data source** | `learning_outcomes` ⨝ `baml_extractions` |
| **Expected output** | Coverage matrix 24 subjects × 4 material types; click → drill-down of missing outcomes |
| **Write-back** | `INSERT INTO lakehouse.analysis.outcome_coverage ...` |

### 2.4 `04_dlt_pipeline_health.py`
| Field | Value |
|:--|:--|
| **Purpose** | Monitor the 8 DLT pipelines (`examinations_ie`, `curriculum_online_ie`, `ncca_ie`, `ccea_org_uk`, `wjec_co_uk`, `sqa_org_uk`, `leabharlann_*.zotero`, `leabharlann.gemini_research`) for load failures, row counts, last-success |
| **Marimo features** | `mo.ui.dropdown` (pipeline), `mo.ui.table` (last 20 runs), `mo.ui.altair_chart` (row count trend), `mo.md` (alert banner) |
| **Data source** | `dlt_loads` ⨝ `dlt_load_details` |
| **Expected output** | 8-row "fleet health" with green/yellow/red; click → row-count trend + run log |
| **Write-back** | None (read-only) |

### 2.5 `05_dagster_health.py`
| Field | Value |
|:--|:--|
| **Purpose** | Monitor 4 Dagster code-locations (`oideachais`, `tuatha`, `croilar`, `meaisinfhoghlaim`) for asset failures, sensor skips, duration outliers |
| **Marimo features** | `mo.ui.dropdown` (location), `mo.ui.tabs` (Assets / Sensors / Runs), `mo.ui.dataframe` (failures), `mo.ui.altair_chart` (duration histogram) |
| **Data source** | Dagster GraphQL `runs` + `assets` + `sensors` |
| **Expected output** | 3-tab: (1) Assets — last materialisation red/yellow/green; (2) Sensors — last 5 evals with skip reason; (3) Runs — duration histogram + outlier table |
| **Write-back** | None (read-only) |

## 3. Common pattern (the shared prologue)

All 5 notebooks start with the same 4-cell prologue:

```python
# /// script
# requires-python = ">=3.12"
# dependencies = ["marimo", "polars", "duckdb", "lancedb", "pyarrow", "altair"]
# ///
import marimo
app = marimo.App(width="full", layout_file="grid.json")

@app.cell
def _():
    import marimo as mo
    import polars as pl
    from cianfhoghlaim.core.motherduck import get_motherduck_connection
    return get_motherduck_connection, mo, pl

@app.cell
def _(get_motherduck_connection):
    conn = get_motherduck_connection(read_only=True)
    return (conn,)

@app.cell
def _(mo):
    mo.md("# <Notebook Title> — Cianfhoghlaim Analysis")
    return
```

This prologue is the same one used in
`meaisinfhoghlaim/marimo/01_leabharlann_descriptive.py` and `02_dpre_lag_analysis.py`.

## 4. Anti-patterns (do not violate)

1. **Don't use `print()`** — use `mo.md()` or `mo.ui.dataframe`.
2. **Don't use `pandas`** — every notebook imports `polars` (10× faster, native MotherDuck interop).
3. **Don't `conn.execute(...).arrow()` then re-convert** — use `mo.sql(engine=conn)`.
4. **Don't commit `.ipynb`** — these are pure-Python modules; commit only the `.py` file.
5. **Don't skip `@app.cell(column=N)`** if > 4 cells — multi-column layout keeps the dashboard compact.

## 5. Cross-references

- `openspec/specs/oideachais-marimo-dashboards/spec.md`
- `133-marimo-latest-features.md`
- `134-marimo-for-implementation.md`
- `136-marimo-for-demos.md`
- `.agents/skills/dlthub/notebooks/starter_runs_notebook.py` (template)
