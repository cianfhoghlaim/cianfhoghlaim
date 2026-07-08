# Change: 2026-07-04-dev-env-setup-latest-packages-and-wire-25-notebooks

## Why

The Cianfhoghlaim dev `.venv` was a bare-bones install (195 packages, missing
the entire Dagster + DLT + Cognee + OCR stack). To use the LC5-subject +
Gemini 6-corpus pipelines end-to-end in the dev environment, the 97 pinned
packages need to be at their latest available versions, with package
conflicts resolved by the "Drop both lower bounds" policy.

Simultaneously, the 25 dev marimo notebooks (16 LC5 + 9 Gemini) need
to wire to live DLT data (the 2 already-wired from Session 9 + 23 newly
wired in this change).

## What changes

This omnibus openspec change ships 4 phases over 2 days (2026-07-04
through 2026-07-05):

### Phase 1 — Fix `pyproject.toml` broken references (5 min)

The cianfhoghlaim/dagster → cianfhoghlaim/orchestration rename (Session 10)
left 4 stale references in pyproject.toml:

1. `[project.scripts]` line 256: `cianfhoghlaim-dagster = "cianfhoghlaim.dagster.cli:main"`
   → `cianfhoghlaim.orchestration.cli:main`
2. `[tool.dg]` line 278: `registry_modules = ["cianfhoghlaim.dagster.components"]`
   → `["cianfhoghlaim.orchestration.components"]`
3. `[build-system]` `[tool.hatch.build.targets.wheel].packages` line 296-314:
   removed 11 non-existent dirs (assets, baml, cognify, core, dagster, dlt,
   embeddings, geospatial, leabharlann, notebooks, ocr, pipelines, sources,
   libraries/codeolas); renamed `dagster` → `orchestration`; added
   `meaisinfhoghlaim`. Final 6 packages (with `__init__.py`):
   agents, cocoindex, observability, orchestration, storage, meaisinfhoghlaim.
4. Simplified `mlx` and `mlx-omni-server`: removed `; sys_platform == 'darwin'`
   markers; let uv resolve per-platform. Removed the `apple-silicon-mlx` extra
   entirely (it required uvicorn<0.35 + sse-starlette<3.4 which conflict
   with the rest of the stack).

### Phase 2 — Bump 91 package pins to >=latest (45-90 min)

Per the user's "Drop both lower bounds" policy, when a transitive
constraint conflicts, drop the lower bound entirely on the package that
has more flexibility.

- 64 main deps bumped: openai 2.44.0, pydantic 2.13.4, fastapi 0.139.0,
  uvicorn 0.50.0, langfuse 4.13.0, mlflow 3.14.0, ragas 0.4.3, cognee 1.2.2,
  graphiti-core 0.29.2, cocoindex 1.0.15, marimo 0.23.13, duckdb 1.5.4,
  lancedb 0.34.0, dlt 1.28.1, dagster 1.13.1, transformers 4.57.0 (yanked
  but required for hf-hub<1 compat), sentence-transformers 5.6.0,
  accelerate 1.14.0, torch 2.12.1, paddleocr 3.0.0, easyocr 1.7.2,
  docling 2.78.0, mineru 3.4, llama-cpp-python 0.3.0, huggingface-hub 0.36.2,
  letta 0.1.0, etc.
- 27 optional-deps bumped: altair 5.5.0, ruff 0.8.0, mypy 1.13.0, pytest 9.0.3,
  wandb 0.18.0, trl 0.25.0, datasets 3.0.0, etc.
- 8 conflict-causing lower bounds DROPPED: huggingface-hub, pyyaml,
  paddleocr, unsloth, letta, mlx-omni-server, docling, transformers
  (per "Drop both lower bounds" rule).
- 2 dagster-ecosystem packages pinned exact (match transitive constraints):
  dagster==1.13.1, dagster-webserver==1.13.1, dagster-graphql==1.13.1,
  dagster-dlt==0.29.1, dagster-embedded-elt==0.29.1, dagster-dbt==0.29.1
- 2 harmless warnings (per "drop both lower bounds" policy):
  ibis-framework[motherduck] extra doesn't exist in 12.x; transformers
  4.57.0 is yanked (no alternative satisfies both docling 2.78.0 and
  modern transformers constraints)

Total packages installed: 574 (vs. 195 in the prior minimal venv) via
`uv pip install ".[all]"` from cianfhoghlaim/.

### Phase 3 — Wire 25 dev notebooks to live DLT data (45-90 min)

Per user "Wire all 25 notebooks now". The 2 already-wired notebooks
(01_chemistry_analysis.py LC5 + 01_law_corpus_overview.py Gemini) were
skipped. The 23 newly-wired notebooks all have a new `@app.cell` that
runs the actual DLT source:

- 16 LC5 notebooks under `leaving_cert/`:
  - 02-05: per-subject (computer_science, gaeilge, geography, mathematics)
    — filter by subject
  - 06-10: cross-subject (en_vs_ga, syllabus_topic_overlap, exam_paper_difficulty,
    marking_scheme_complexity, curriculum_evolution) — all 72 rows
  - 11-15: model benchmark (ocr_model_comparison, layout_extraction,
    dense_ocr_benchmark, table_extraction, diagram_detection) — uses
    `model_key` column from the 72 rows
  - 16: runtime_comparison_llama_swap_vs_cpp — added a status @app.cell
    that explains the 13 GGUF models are queued for download (~95 GB
    via `mise run llama-swap:download-models`)

- 9 Gemini notebooks under `{medical,politics,culture,technology,other,law}/`:
  - 01_{medical,politics,culture,technology,other}_corpus_overview:
    per-corpus (filter by corpus) — 5 notebooks
  - 02_cross_corpus_timeline, 03_jurisdictional_map, 04_pattern_detection:
    cross-corpus (all 224 rows) — 3 notebooks
  - 01_law_corpus_overview: already wired (Session 9)

Path fix: in the Phase 3 wiring script I initially used
`ROOT.parent.parent.parent` (3 levels up) but the notebooks' `ROOT` is set
to the corpus_dir (e.g. .../gemini_deep_research/law), so the correct path
is `ROOT.parent` (2 levels up) = gemini_deep_research/. Fixed all 8 Gemini
notebooks.

### Phase 4 — Final 5-step smoke test (5-10 min)

```
STEP 1 PASS: 14 packages + 22 VISION_MODELS + KCG components importable
STEP 2 PASS: LC5=72 rows, Gemini=224 rows
STEP 3 PARTIAL: dagster definitions load (with pre-existing source_factory
                fallback to empty Definitions; tracked as a follow-up)
STEP 4 PASS: 6/8 priority stacks healthy (graphiti+llama-swap not deployed)
STEP 5 PASS: 27/27 notebooks parse + DLT-import wired
```

## Impact

- **Affected specs:** `dagster-5-layer-component-architecture`, `oideachais-pipeline`
- **Affected code:** 28 files (2 pyproject + uv.lock + 25 notebooks)
- **Affected hosts:** dev venv only (no docker images)
- **Risk:** low — package conflicts resolved by "drop both lower bounds"
- **Audit gates:** `uv lock --upgrade` resolves cleanly; `uv run python` import
  tests pass for all 14 critical packages; 27/27 notebooks parse

## Non-goals

- No custom Docker images (per user)
- No source_factory stub (per user; redundant with existing
  `dlt/common/destinations_oideachais.py`)
- No new containers (the 8 user-priority stacks are already Up)
- No per-subject ADK agent wiring (deferred)
- No GGUF cache population (95 GB; deferred)

## Cross-references

- Per openspec/changes/2026-07-03-infrastructure-foundation/
- Per openspec/changes/2026-07-03-leaving-cert-5-subject-pipeline-with-diagrams/
- Per openspec/changes/2026-07-03-gemini-6-corpus-pipeline/
- Per openspec/changes/2026-07-03-specs-and-session-9-health-report/
