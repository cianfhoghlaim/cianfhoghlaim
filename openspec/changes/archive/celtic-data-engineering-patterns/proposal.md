# Celtic Data-Engineering + Gradio Ensemble Patterns

## Why

We have two prior-art Spaces that demonstrate reusable patterns we should
adopt, adapt, defer, or skip:

1. **`spaces/data-engineering/`** — the BigQuery → Delta Lake → DuckDB → dbt
   → Evidence stack orchestrated by Dagster. The Dagster+DLT+dbt patterns are
   1:1 applicable to our `sruth/oideachais/` quadrant (we already have Dagster and
   DLT, missing dbt + marimo-equivalent of Evidence). The Evidence dashboard
   itself is the wrong default for us — marimo is our standard notebook
   surface — but the SQL-fenced-block pattern (` ```sql name `) translates
   cleanly to marimo `mo.sql()` cells.

2. **`spaces/anti-phish/`** — the 6-stage ML progression (extract → classical
   → PyTorch → HF Transformers → Flower FL → Gradio). The Gradio ensemble
   pattern (one `Interface` with one `output` per model + `examples=[...]`)
   is the canonical "compare all my models side by side" UI. The HF Hub
   model publish pattern (`foghlaimeoir/phishing-DistilBERT`) is what we
   already do in `sruth/meaisinfhoghlaim/ocr/`; we just don't have a shared helper.

This change codifies those patterns as **2 new OpenSpec capabilities** and
provides the shared code artefacts + 2 marimo notebooks that absorb them.
No new infrastructure (we already have Dagster, DLT, MotherDuck, marimo, the
HF Hub token in `.infisical.env`).

## What Changes

### 1. dbt-duckdb project at `sruth/oideachais/dbt_project/` (Phase 4 — follow-up commit)

Mirror of `spaces/data-engineering/dbt_project/`. Multi-target `dev` (local
DuckDB) / `prod` (MotherDuck) per pattern A6 from `spaces/README.md` §1.
Models: `weekly_downloads`, `language_distribution`, `ocr_confidence_by_model`
— all 3 read from the existing `oideachais.curriculum_*` tables.

### 2. Custom Dagster dbt translator at `sruth/oideachais/dagster_defs/dbt_translator.py` (Phase 4)

`CelticDagsterDbtTranslator(DagsterDbtTranslator)` that flattens
`dbt_resource_props["name"]` to an `AssetKey` and pins `group_name="prepared"`
(per pattern A4).

### 3. Ensemble Gradio helper at `sruth/meaisinfhoghlaim/pipelines/ensemble_gradio.py` (Phase 4)

`build_ensemble_interface(models: dict[str, Pipeline], examples: list[str],
title: str) -> gr.Interface` — wraps patterns B1+B4 from `spaces/README.md` §1.

### 4. HF Hub push helper at `spaces/_common/hf_hub_push.py` (Phase 4)

`push_model_to_hub(local_dir: Path, repo_id: str, commit_message: str) -> str`
(pattern B6). Uses `huggingface_hub.HfApi.upload_folder` rather than the
manual `pipeline.push_to_hub` so the helper handles OCR checkpoints, sklearn
pickles, and BAML-compiled artefacts uniformly.

### 5. Marimo notebook directory at `sruth/meaisinfhoghlaim/marimo/` (new — this commit)

Two notebooks land in this commit (skeletons with TODO markers for data
binding in the follow-up commit):

- `01_leabharlann_descriptive.py` — descriptive statistics on the
  leabharlann/ corpus (token length, fada-preservation rate, lexical
  diversity, per-language counts). Pattern A6 + A8 marimo adaptation.
- `02_dpre_lag_analysis.py` — time-series of `DynamicPartitionsDefinition`
  materialization lags across the 10 OCR models; correlation heatmap of
  BAML extraction confidence vs OCR WER. Pattern A1 extension.

Both register in `sruth/meaisinfhoghlaim/marimo/__init__.py` and a new `[marimo]`
extra in `sruth/meaisinfhoghlaim/pyproject.toml` is added.

### 6. Spaces README at `spaces/README.md` (new — this commit)

Per Phase 1.1 of the plan. The full pattern catalogue (the matrix from the
plan, with `file:line` citations to the prior-art repos and per-pattern
adopt/adapt/defer/skip decisions).

### 7. Spaces STATUS.md patch (this commit)

3-line cross-link to `spaces/README.md`.

## Out of scope (deferred to follow-up commit)

- dbt project + dagster translator + gradio ensemble helper + hf hub push
  helper (the 4 code artefacts in §1-4 above). These land in the follow-up
  commit that follows the user review of this change.

## Spec Deltas

- ADDED `celtic-data-engineering-pipeline` capability
- ADDED `gradio-ensemble-pattern` capability
- MODIFIED `meaisinfhoghlaim-platform` spec (one new sub-package: `marimo/`)

## Cross-references

- `spaces/README.md` (this commit) — the full pattern catalogue
- `openspec/specs/spaces-cicd-pipeline/spec.md` (the sister change in
  `spaces-cicd-reusable-pipeline`) — the reusable GH Action that publishes
  Spaces built using the `gradio-ensemble-pattern`
- `sruth/meaisinfhoghlaim/AGENTS.md` "Quick routing" table (this commit) — adds
  the `marimo/` row
- `oideachais-marimo-dashboards` (existing spec) — the sister capability
  for the oideachais quadrant's marimo notebooks; this change adds the
  meaisinfhoghlaim counterpart
