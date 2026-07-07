# Tasks: 2026-07-04-dev-env-setup-latest-packages-and-wire-25-notebooks

## Phase 1 — Fix pyproject.toml broken references (5 min)

- [x] 1.1 Update [project.scripts] cianfhoghlaim-dagster → cianfhoghlaim.orchestration.cli:main
- [x] 1.2 Update [tool.dg] registry_modules → cianfhoghlaim.orchestration.components
- [x] 1.3 Update [tool.hatch.build.targets.wheel].packages to only 6 dirs with __init__.py (agents, cocoindex, observability, orchestration, storage, meaisinfhoghlaim)
- [x] 1.4 Simplify mlx + mlx-omni-server: remove ; sys_platform markers
- [x] 1.5 Commit + verify Python imports work

## Phase 2 — Bump 91 package pins to >=latest (45-90 min)

- [x] 2.1 Find latest version of each of 97 pinned packages via PyPI API
- [x] 2.2 Update pyproject.toml to set >=X.Y.Z on all main + optional deps
- [x] 2.3 Drop upper bounds on fastapi (<0.140), uvicorn (<0.35.0) per user "no upper bounds"
- [x] 2.4 Drop [tool.hatch.build.targets.wheel] packages core, sources, dagster (rename to orchestration); add meaisinfhoghlaim
- [x] 2.5 `uv lock --upgrade` — 601 packages resolved
- [x] 2.6 `uv pip install ".[all]"` from cianfhoghlaim/ — 574 packages installed
- [x] 2.7 Verify critical 14 packages import (dagster, dlt, cognee, falkordb, mlflow, easyocr, docling, llama_cpp, graphiti_core, letta, huggingface_hub, marimo, baml_py, [paddleocr requires paddlepaddle])
- [x] 2.8 Commit + push

## Phase 3 — Wire 25 dev notebooks to live DLT data (45-90 min)

- [x] 3.1 Wire 4 LC5 per-subject notebooks (02-05) with subject filter
- [x] 3.2 Wire 5 LC5 cross-subject notebooks (06-10) with all 72 rows
- [x] 3.3 Wire 5 LC5 model benchmark notebooks (11-15) with model_key column
- [x] 3.4 Wire LC5 16_runtime_comparison with status @app.cell
- [x] 3.5 Wire 5 Gemini per-corpus notebooks (01_*.py in each corpus)
- [x] 3.6 Wire 3 Gemini cross-corpus notebooks (02-04)
- [x] 3.7 Fix ROOT path bug in Gemini notebooks (3 levels → 2 levels up)
- [x] 3.8 Verify all 27/27 notebooks parse
- [x] 3.9 Commit + push

## Phase 4 — Final 5-step smoke test (5-10 min)

- [x] 4.1 Verify 14 critical packages + 22 VISION_MODELS + 5 KCG Components import
- [x] 4.2 Verify LC5 (72 rows) + Gemini (224 rows) DLT sources
- [x] 4.3 Run `dagster definitions validate -m cianfhoghlaim.orchestration.definitions` (partial — pre-existing source_factory fallback)
- [x] 4.4 Verify 6/8 priority stacks healthy (graphiti+llama-swap not deployed)
- [x] 4.5 Verify all 27 marimo notebooks parse

## Phase 5 — Openspec change files + HEALTH_REPORT Session 11

- [x] 5.1 Create openspec/changes/2026-07-04-dev-env-setup-latest-packages-and-wire-25-notebooks/{proposal,tasks}.md
- [ ] 5.2 Add 2 spec deltas (dagster-5-layer-component-architecture + oideachais-pipeline)
- [ ] 5.3 Add Session 11 entry to HEALTH_REPORT.md
- [ ] 5.4 Commit + push

## Phase 6 — Final commit + push

- [ ] 6.1 Verify all 27 notebooks parse + 14 packages import
- [ ] 6.2 Final commit with all files
- [ ] 6.3 Push to origin/main
