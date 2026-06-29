# Agent 134 — Marimo for Implementation (10 Notebook Plan, 2026-06-29)

**Date:** 2026-06-29
**Scope:** Spec the 10 marimo implementation notebooks that pair 1:1 with the
Cianfhoghlaim code components. Each notebook is a **reproducible
executable spec** of a component — runnable end-to-end with
`uv run <name>.py` thanks to PEP 723 inline dep blocks.
**Prior art:** the 11 existing dashboards at
`cianfhoghlaim/notebooks/_oideachais/` (see
`openspec/specs/oideachais-marimo-dashboards/spec.md`).

## 1. TL;DR

Cianfhoghlaim's 11 existing notebooks at `oideachais/notebooks/` are **analysis/dashboard** surfaces (read-side). The **implementation-side** is currently scattered across Python modules in `cianfhoghlaim/core/`, `agents/`, `web/`. The 10 new notebooks proposed here each encode a **complete vertical slice** of one platform component — import the real code, execute it on a 1-row fixture, display inputs/outputs/BAML extractions/Cognee adds, and assert the contract. They serve as:

1. **Living documentation** (runnable, not stale)
2. **PR review aids** (the diff in a notebook PR is the explanation)
3. **Onboarding** (new contributors `uv run` to see what `dlt_sources/ireland/...` does)
4. **CI smoke tests** (the marimo cell that does `assert result["n_pages"] > 0` IS the smoke test)

All 10 are PEP 723 + marimo 0.23.11 + `mo.ui.dropdown` + `mo.md` + `polars`. `curriculum_educator.py` is the canonical template.

## 2. The 10 implementation notebooks

| # | Path (under `cianfhoghlaim/notebooks/_implementation/`) | Component | Marimo features used | Code integration |
|:-:|:--|:--|:--|:--|
| 1 | `01_ireland_dlt_source.py` | Ireland DLT source | `@app.setup` + `mo.ui.dropdown` + dlt + `mo.ui.table` + `mo.md` | `from cianfhoghlaim.ingest.dlt_sources.ireland.examinations import examinations_source` |
| 2 | `02_baml_extraction.py` | BAML `ExtractEn` + `ExtractEnStrong` | `mo.ui.dropdown` (model) + `mo.ui.text_area` + `mo.ui.code` + `mo.md` | `from cianfhoghlaim.core.baml import b`; `b.ExtractLearningOutcome(...)` |
| 3 | `03_cocoindex_leabharlann.py` | Leabharlann CocoIndex v1 App | `@app.setup` + `mo.ui.button` + `mo.ui.table` + `mo.status.spinner` | `from cianfhoghlaim.assets.cocoindex.leabharlann import leabharlann_app` |
| 4 | `04_lancedb_hybrid_search.py` | LanceDB BGE-M3 + RRFReranker | `mo.ui.text` + `mo.ui.slider` + `mo.ui.table` + `mo.ui.altair_chart` | `oideachais_table.search(q, query_type="hybrid").rerank(RRFReranker())` |
| 5 | `05_cognee_official_media.py` | Cognee cognify + 4-lookup | `mo.ui.text_area` + `mo.ui.button` + `mo.ui.dataframe` + `mo.md` | `await cognify_official_media_post(url)` |
| 6 | `06_dagster_oideachais_assets.py` | Dagster `oideachais` code-location | `mo.ui.multiselect` + `mo.ui.table` + `mo.ui.code` (SQL) | `defs.get_asset_graph().get(...)` |
| 7 | `07_ocr_ensemble.py` | 6-backend OCR ensemble | `mo.ui.file` + `mo.ui.dropdown` + `mo.ui.dataframe` + `mo.md` | `run_ensemble(pdf, strategy="majority_vote")` |
| 8 | `08_motherduck_dive.py` | MotherDuck Dive authoring | `mo.ui.dropdown` + `mo.ui.code_editor` (SQL) + `mo.ui.table` + `mo.md` | `get_dive(database, sql).publish()` |
| 9 | `09_unsloth_finetune.py` | Unsloth `FastModel` + Studio API | `mo.ui.dropdown` + `mo.ui.slider` + `mo.ui.button` + `mo.status.progress_bar` | `FastModel.from_pretrained(model).get_peft_model(r=r)` |
| 10 | `10_browserbase_research.py` | Browserbase `agent_experience` audit | `mo.ui.text` + `mo.ui.text_area` + `mo.ui.code` + `mo.md` (DX report) | `browse.agent_experience(url=url, task=task)` |

### Per-notebook spec (one worked example — #2 BAML)

```python
# /// script
# requires-python = ">=3.12"
# dependencies = ["marimo", "polars", "duckdb", "baml-py>=0.223"]
# ///
import marimo
app = marimo.App(width="wide")

@app.cell
def _():
    import marimo as mo
    from cianfhoghlaim.core.baml import b
    return b, mo

@app.cell
def _(mo):
    sample = mo.ui.text_area(value="Solve quadratic equations by formula, square, factorisation.",
                             label="Paste a learning outcome")
    model = mo.ui.dropdown(options=["extract-en", "extract-en-strong", "minimax"],
                           value="extract-en", label="BAML client")
    mo.vstack([sample, model])
    return model, sample

@app.cell
def _(b, model, sample):
    result = b.ExtractLearningOutcome(learning_outcome=sample.value, client=model.value)
    return (result,)

@app.cell
def _(mo, result):
    mo.ui.code(repr(result), language="json")
    return

if __name__ == "__main__":
    app.run()
```

## 3. Migration plan for the 11 existing notebooks at `oideachais/notebooks/`

The 11 existing notebooks were written **before** marimo 0.23.x and
**before** the `2026-06-28-consolidate-sruth-into-cianfhoghlaim-v4`
change. They need 5 mechanical updates before they are "v4-clean":

| # | Notebook | Path | Migration step |
|:-:|:--|:--|:--|
| 1 | `curriculum_educator.py` | `_oideachais/curriculum_educator.py:1-431` | (a) PEP 723; (b) bump `__generated_with = "0.23.8"` → `0.23.11` |
| 2 | `ducklake_explorer.py` | `_oideachais/ducklake_explorer.py` | (a) PEP 723; (b) `mo.sql(engine=conn)` instead of `conn.execute` + `pl.from_arrow` |
| 3 | `mission_control.py` | `_oideachais/mission_control.py` | (a) PEP 723; (b) `@app.cell(column=N)` + `layout_file` |
| 4 | `pipeline_e2e_test.py` | `_oideachais/pipeline_e2e_test.py` | (a) PEP 723; (b) `mo.status.progress_bar` |
| 5 | `syllabus_visualizer.py` | `_oideachais/syllabus_visualizer.py` | (a) PEP 723; (b) `mo.ui.altair_chart` for outcomes tree |
| 6 | `sources_load.py` | `_oideachais/sources_load.py` | (a) PEP 723; (b) `mo.ui.table` for source diffs |
| 7 | `pdf_download_dashboard.py` | `_oideachais/pdf_download_dashboard.py` | (a) PEP 723; (b) `mo.ui.file` for upload fallback |
| 8–12 | `dashboards/{aistear,primary,junior_cycle,senior_cycle,tertiary}.py` | `_oideachais/dashboards/` | (a) PEP 723; (b) `mo.ui.table.Display` (new 0.23.11) |
| 13 | `dashboards/cross_domain.py` | `_oideachais/dashboards/cross_domain.py` | (a) PEP 723; (b) `mo.ui.tabs` for stage switching |
| 14 | `dashboards/leabharlann_full_stack_demo.py` | `_oideachais/dashboards/leabharlann_full_stack_demo.py` | (a) PEP 723; (b) 6th "Demo run" with `mo.status.progress_bar` |

**Migration order (one PR per batch of 3):** PR1: #1–#3, PR2: #4–#7, PR3: #8–#12, PR4: #13–#14.

**Migration risks:** PEP 723 block must be the **first** non-docstring lines; `mo.ui.table.Display` (0.23.11) is **not available** in 0.23.8 — PRs must bump `__generated_with`.

## 4. Cross-references

- `openspec/specs/oideachais-marimo-dashboards/spec.md`
- `openspec/specs/official-media-marimo/spec.md`
- `133-marimo-latest-features.md` (the 12-new-features table)
- `136-marimo-for-demos.md` (WASM-export + embed strategy)
