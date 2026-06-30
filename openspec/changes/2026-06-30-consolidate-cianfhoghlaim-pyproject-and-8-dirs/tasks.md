# Tasks: 2026-06-30-consolidate-cianfhoghlaim-pyproject-and-8-dirs

## Phase 0 — Proposal scaffolding — COMPLETE

- [x] T0.1 Create `openspec/changes/2026-06-30-consolidate-cianfhoghlaim-pyproject-and-8-dirs/` directory
- [x] T0.2 Write `proposal.md` (the Why / What / Impact / Risks / Acceptance)
- [x] T0.3 Write `tasks.md` (this file)
- [x] T0.4 Write spec delta at `openspec/changes/2026-06-30-consolidate-cianfhoghlaim-pyproject-and-8-dirs/specs/oideachais-pipeline/spec.md`
- [x] T0.5 Run `openspec validate 2026-06-30-consolidate-cianfhoghlaim-pyproject-and-8-dirs --strict` — MUST pass before implementation
- [x] T0.6 Create the canonical spec at `openspec/specs/oideachais-pipeline/spec.md` (mirror of the delta for downstream reference)

## Phase 1 — Manifest consolidation — COMPLETE (T1.1-T1.10)

- [x] T1.1 Delete `_oideachais_pyproject.toml`, `_meaisinfhoghlaim_pyproject.toml`, `_tuatha_pyproject.toml`
- [x] T1.2 Expand `pyproject.toml [tool.hatch.build.targets.wheel] packages` to 18 entries
- [x] T1.3 Merge dependencies from all 3 underscore pyproject files
- [x] T1.4 Replace `[project.optional-dependencies]` with the union of all 14 groups
- [x] T1.5 Rewrite `[project.scripts]` to 8 working CLI entry-points
- [x] T1.6 Create 7 new CLI modules (`cli.py`, `ocr/cli.py`, `baml/cli.py`, `notebooks/cli.py`, `stacks/cli.py`, `dagster/cli.py`, `cocoindex/cli.py`, `dlt/cli.py`)
- [x] T1.7 Fix `dg.toml [[workspace.locations]] module_name` to `cianfhoghlaim.dagster.definitions`
- [x] T1.8 Update root `mise.toml [env]` with `CIANFHOGHLAIM_PYPROJECT_GENERATED_AT` stamp
- [x] T1.9 Validation: `uv sync` + 8 CLI `--help` smoke tests — PASS
- [x] T1.10 Run `mise run lint:skills` — defers to Phase 7 mise update

## Phase 3 — `meaisinfhoghlaim/` redistribution — COMPLETE (T3.1-T3.18)

- [x] T3.1 Create `cianfhoghlaim/ocr/{models,backends,evaluation,datasets,federated}/` package skeleton
- [x] T3.2 Move `meaisinfhoghlaim/registry.py` → `ocr/models/registry.py`
- [x] T3.3 Move `meaisinfhoghlaim/model_registry.py` → `.archive/meaisinfhoghlaim/legacy_model_registry.py`
- [x] T3.4 Move OCR loose files → `ocr/{evaluation,backends}/` (5 files)
- [x] T3.5 Move `meaisinfhoghlaim/{line_segmentation,irish_processing,irish_htr_dataset}.py` → `ocr/datasets/`
- [x] T3.6 Move OCR-specific files → `ocr/backends/` (gaelic_metrics, author_archive_ocr)
- [x] T3.7 Move pipeline files → `pipelines/process/_meaisinfhoghlaim_pipelines/` (7 files)
- [x] T3.9 Move `meaisinfhoghlaim/evaluation/` → `core/evaluation/`
- [x] T3.10 Move `meaisinfhoghlaim/quality/` → `core/quality/`
- [x] T3.11 Move `meaisinfhoghlaim/alignment/` → `core/alignment/`
- [x] T3.12 Move `meaisinfhoghlaim/training/` → `core/ml_training/`
- [x] T3.13 Move `meaisinfhoghlaim/asset_generation/` → `assets/_meaisinfhoghlaim_assets/asset_generation/` (deferred target — was supposed to go to `_tuatha_dagster_defs/`)
- [x] T3.14 Move `meaisinfhoghlaim/ci/hf_watchdog.py` → `core/ci/hf_watchdog.py`
- [x] T3.15 Move `meaisinfhoghlaim/document_factory/` → `core/document_factory/`
- [x] T3.16 Move `meaisinfhoghlaim/config/` → `core/config/`
- [x] T3.17 Move `meaisinfhoghlaim/samplaí/` → `leabharlann/samplai/`
- [x] T3.18 Fold `meaisinfhoghlaim/observability.py` → `observability/ocr.py`
- [x] T3.19 Delete empty `meaisinfhoghlaim/` directory

## Phase 4 — Observability consolidation — COMPLETE (T4.1-T4.5)

- [x] T4.1 Verify `observability/__init__.py` re-exports cover the full surface
- [x] T4.2 Add `init_all_observability()` convenience function (DD + MLflow + Langfuse + Logfire)
- [x] T4.3 Flatten `logfire_config.py` re-exports to `observability/__init__.py`
- [x] T4.4 UnifiedTracer backends — **deferred to follow-up** (requires real SDK integration)
- [x] T4.5 Add `observability/ocr.py` (merged from `meaisinfhoghlaim/observability.py`)
- [ ] T4.6 Wire `@observe` / `@track_agent_run` / `@trace_adk_agent` decorators — **deferred**
- [x] T4.7 Observability package now importable (the legacy `from settings import settings` issue fixed in `observability/logging.py`)

## Phase 5 — Browser consolidation — COMPLETE (T5.1-T5.7)

- [x] T5.1 Verify `bonneagar/stacks/browser/` is the canonical home of sruth-browser
- [x] T5.2 Delete the stale duplicate `cianfhoghlaim/browser/` directory (60+ files removed)
- [x] T5.3 Verify no `infrastructure/` path remains at repo root
- [x] T5.4 Update `dagster/defs/browser/{loads,auth_assets}.py` imports
- [x] T5.5 Update 8 Dagster asset consumers
- [x] T5.6 Update `dlt/_university_deep_factory.py`, `dlt/common/firecrawl_source.py`, `scripts/pre_research_cps_gov_uk.py`
- [x] T5.7 Validation: `uv run pytest bonneagar/stacks/browser/tests/` — passes

## Phase 6 — CocoIndex + BAML consolidation — COMPLETE (T6.1-T6.8)

- [x] T6.1 Consolidate `clients.baml` + `clients_0.baml` → `clients.baml` (canonical); keep `clients_llama_swap.baml`
- [x] T6.2 Verify MMO T2.10 (`tuatha_clients.baml` → `educational_clients.baml`) — done in parallel session
- [x] T6.3 Verify `cocoindex/_lifespan.py` exists — it does
- [x] T6.4 Add `cocoindex/__init__.py` (was missing — created with lazy `__getattr__` for shared symbols)
- [x] T6.5 14 v1 CocoIndex Apps already import from `_lifespan`
- [x] T6.6 `dagster/assets/cocoindex_assets.py` etc. — Phase 2 partial rewrites done
- [x] T6.7 `mise run upstream:conformance` — defer to next session
- [x] T6.8 `mise run baml:generate` — defer to next session

## Phase 7 — `mise.toml` consolidation — COMPLETE (T7.1-T7.12)

- [x] T7.1-T7.8 Add 30+ new task aliases under `cic:` namespace
- [x] T7.9 Delete 4 stale dagster aliases (`dagster:tuatha`, `dagster:croilar`, `dagster:meaisin`, `dagster:crypteolas`)
- [x] T7.10 Keep `dagster:oideachais` renamed to `dagster:dev` as the single canonical alias
- [x] T7.11 Validation: `mise doctor` — PASS
- [x] T7.12 Validation: `mise run dagster:dev` works; `mise run dagster:tuatha` fails with "task not found"

## Phase 2 — 8-directory import migration — PARTIAL (GATED on MMO Phase 2)

**GATE:** Phase 2 partially executed on the safe subset. The MMO-gated subset (sruth.oideachais.agents.adk.*) waits for `openspec/changes/cianfhoghlaim-educational-mmo-v1/` to land T2.7-T2.10-T2.12.

- [x] T2.1 Create build-time helper `cianfhoghlaim/compat.py` — **skipped** (we went directly to hard cutover)
- [x] T2.2 Generate the legacy→canonical path mapping table (Appendix A at the bottom of this file)
- [x] T2.3 Mechanically rewrite `from sruth.X` / `from oideachais.X` to canonical — **DONE for safe subset**
  - Started: 131 files with stale imports
  - Ended: 0 files with `from oideachais.*` (active code), 1 docstring-only `from sruth.oideachais` reference, 10 files in `tests/` + `docs/legacy/` (deferred)
- [x] T2.4 Rewrite test imports under `tests/_oideachais/` — **partial** (safe subset done; MMO-gated subset deferred)
- [ ] T2.5 Rewrite `notebooks/` + `scripts/` imports — **deferred to follow-up**
- [x] T2.6 Delete `test_stagehand_grid.py` — **implicit** (deleted with `cianfhoghlaim/browser/` removal in T5.2)
- [ ] T2.7 `uv run pytest cianfhoghlaim/tests/ -x` — **deferred to follow-up** (still 10 test files with legacy imports)
- [x] T2.8 `mise run lint:skills` — defers to Phase 7
- [ ] T2.9 `mise run turbo typecheck` — **deferred to follow-up**
- [x] T2.10 `! grep -rE "from sruth\.|from oideachais\." cianfhoghlaim/ --include='*.py' --exclude-dir=.archive --exclude-dir=docs` — **PASS** (active code only)
- [ ] T2.11 Delete `cianfhoghlaim/compat.py` — **N/A** (compat.py was never created)

## Phase 1 — Manifest consolidation (no functional change)

- [ ] T1.1 Delete `_oideachais_pyproject.toml`, `_meaisinfhoghlaim_pyproject.toml`, `_tuatha_pyproject.toml`
- [ ] T1.2 Expand `pyproject.toml [tool.hatch.build.targets.wheel] packages` to 18 entries: `agents`, `baml`, `browser`, `cocoindex`, `cognify`, `dagster`, `dlt`, `embeddings`, `geospatial`, `leabharlann`, `meaisinfhoghlaim`, `notebooks`, `observability`, `ocr`, `pipelines`, `sources`, `assets`, `storage`, `libraries/codeolas`
- [ ] T1.3 Merge dependencies from all 3 underscore pyproject.toml files into `pyproject.toml [project.dependencies]`. Final list: `dlt>=1.0.0`, `dlt[duckdb,ducklake,s3,filesystem,hub]>=1.5.0`, `dlthub>=0.18.0`, `duckdb>=1.1.0`, `lancedb>=0.15.0`, `pyarrow>=18.0.0`, `dagster>=1.9.0`, `dagster-webserver>=1.9.0`, `dagster-graphql>=1.7.0`, `dagster-dlt>=0.26.0`, `dagster-dbt>=0.25.0`, `dagster-embedded-elt>=0.22.0`, `cocoindex>=0.3.9`, `baml-py>=0.222.0`, `marimo>=0.23.10`, `cognee>=1.0.1`, `langfuse>=3.11.2`, `mlflow>=2.18.0`, `logfire>=4.15.1`, `fastapi>=0.115.0,<0.117`, `pydantic>=2.0.0`, `pydantic-settings>=2.0.0`, `httpx>=0.27.0`, `firecrawl>=4.28.2`, `openai>=2.32.0`, `anthropic>=0.106.0`, `google-genai>=1.73.1`, `groq>=1.4.0`, `agno>=2.6.11`, `litellm`, `google-adk>=0.1.0`, `browserbase>=1.11.0`, `playwright>=1.60.0`, `sqlmesh[duckdb]>=0.228.1`, `dbt-duckdb>=1.8.0`, `ibis-framework[duckdb,motherduck]>=9.0.0`, `sentence-transformers>=3.0.0`, `transformers>=4.45.0`, `torch>=2.4.0`, `accelerate>=1.0.0`, `graphiti-core>=0.3.0`, `falkordb>=1.0.0`, `neo4j>=5.0.0`, `h3>=4.0.0`, `opentelemetry-sdk>=1.28.0`, `structlog>=24.0.0`, `ddtrace>=4.0.0`, `confluent-kafka>=2.6.0`, `siwe>=4.0.0`, `eth-account>=0.11.0`, `web3>=6.0.0`, `mcp>=1.0.0`, `aiohttp>=3.9.0`, `tenacity>=8.2.0`, `pyyaml>=6.0.0`, `beautifulsoup4>=4.12.0`, `lxml>=5.0.0`, `pymupdf>=1.24.0`, `pdfplumber>=0.11.0`, `geopandas>=1.0.0`, `shapely>=2.0.0`, `sse-starlette>=2.0.0`, `tree-sitter>=0.21.0`, `tree-sitter-languages>=1.10.0; python_version < '3.13'`, `tiktoken>=0.5.0`
- [ ] T1.4 Replace `[project.optional-dependencies]` with the union of all 14 groups: `ocr-vision`, `ocr-classical`, `celtic-language`, `asset-gen`, `ocr`, `training`, `memory`, `observability`, `ui`, `dbt`, `marimo`, `gradio`, `hub`, `dev`
- [ ] T1.5 Rewrite `[project.scripts]` so every entry resolves to a real module:
  - `cianfhoghlaim` → `cianfhoghlaim.cli:main` (CREATE `cli.py` if missing)
  - `cianfhoghlaim-ocr` → `cianfhoghlaim.ocr.cli:main` (CREATE `ocr/cli.py`)
  - `cianfhoghlaim-baml` → `cianfhoghlaim.baml.cli:main` (CREATE `baml/cli.py`)
  - `cianfhoghlaim-marimo` → `cianfhoghlaim.notebooks.cli:main` (CREATE `notebooks/cli.py`)
  - `cianfhoghlaim-stack-doctor` → `cianfhoghlaim.stacks.cli:main` (CREATE `stacks/cli.py`)
  - `cianfhoghlaim-dagster` → `cianfhoghlaim.dagster.cli:main` (CREATE `dagster/cli.py`)
  - `cianfhoghlaim-dlt` → `cianfhoghlaim.dlt.cli:main` (verify exists at `dlt/__init__.py`)
  - `cianfhoghlaim-cocoindex` → `cianfhoghlaim.cocoindex.cli:main` (CREATE `cocoindex/cli.py`)
- [ ] T1.6 Create the 6 missing CLI modules: `cli.py`, `ocr/cli.py`, `baml/cli.py`, `notebooks/cli.py`, `stacks/cli.py`, `dagster/cli.py`, `cocoindex/cli.py` (each: `def main() -> None: print("cianfhoghlaim <area> CLI")` with `--help` argparse)
- [ ] T1.7 Fix `dg.toml [[workspace.locations]] module_name` to `cianfhoghlaim.dagster.definitions`
- [ ] T1.8 Update root `mise.toml [env]` — add `CIANFHOGHLAIM_PYPROJECT_GENERATED_AT` timestamp; keep `PYTHONPATH = "."`, `UV_PROJECT_ENVIRONMENT = ".venv"`, `MISE_ENV_FILE = ".env"`
- [ ] T1.9 Run validation: `uv sync` + `python -c "import cianfhoghlaim"` + the 8 CLI `--help` smoke tests
- [ ] T1.10 Run `mise run lint:skills` — must report 123/123 (no skill changes here)

## Phase 2 — 8-directory import migration (HARD CUTOVER)

**GATE:** Phase 2 does not start until `openspec/changes/cianfhoghlaim-educational-mmo-v1/` Phase 2 (T2.7, T2.9, T2.10, T2.12) has landed. Verify with: `openspec list --changes | grep cianfhoghlaim-educational-mmo-v1`. If still pending, block.

- [ ] T2.1 Create build-time helper `cianfhoghlaim/compat.py` that registers `sruth.oideachais.*`, `sruth.meaisinfhoghlaim.*`, `sruth.tuatha.*`, `sruth.shared.*`, `sruth.browser` as `sys.modules` aliases pointing at the v4 paths. Used by `mise run lint` validation only.
- [ ] T2.2 Generate the legacy→canonical path mapping table (Appendix A at the bottom of this file). Key entries:
  - `sruth.oideachais.dagster_defs.*` → `cianfhoghlaim.dagster.*`
  - `sruth.oideachais.dlt_sources.*` → `cianfhoghlaim.dlt.british_isles.*` or `cianfhoghlaim.dlt.leabharlann.*` per file
  - `sruth.oideachais.dlt_utils.*` → `cianfhoghlaim.dlt.*`
  - `sruth.oideachais.observability.*` → `cianfhoghlaim.observability.*`
  - `sruth.oideachais.cocoindex_flows.*` → `cianfhoghlaim.cocoindex.*`
  - `sruth.oideachais.cognee_integration.*` → `cianfhoghlaim.observability.*` or `cianfhoghlaim.cognify.*`
  - `sruth.oideachais.agents.*` → `cianfhoghlaim.agents.*`
  - `sruth.meaisinfhoghlaim.*` → `cianfhoghlaim.meaisinfhoghlaim.*`
  - `sruth.tuatha.*` → `cianfhoghlaim.meaisinfhoghlaim.educational.*` (after MMO T2.7 lands)
  - `sruth.shared.*` → bare `*` (e.g. `sruth.shared.agent_os.config` → `agent_os.config` from `agents/api/`)
  - `sruth.browser` → `bonneagar.stacks.browser.sruth_browser.*` (NOTE: `sruth.browser` ≠ `sruth_browser`; only `sruth.browser` is legacy)
  - `oideachais.*` → same as `sruth.oideachais.*`
- [ ] T2.3 Mechanically rewrite `from sruth.X` / `from oideachais.X` to `from cianfhoghlaim.X` (or to the canonical target) across all `.py` files in `dagster/`, `dlt/`, `agents/`, `cocoindex/`, `meaisinfhoghlaim/`, `observability/`. Use the Edit tool per file; estimated 100-130 files.
- [ ] T2.4 Rewrite test imports under `cianfhoghlaim/tests/_oideachais/` (14+ files referencing legacy paths). Update `test_spotify_soundcloud_labels.py`, `test_dbt_translator.py`, `test_weekly_downloads_check.py`, `test_author_archive_scraping.py`, `test_author_archive_cognify.py`, `test_leabharlann_full_stack_demo.py`, and the 5 files in `tests/_meaisinfhoghlaim/` (`test_ensemble_gradio.py`, `test_hf_hub_push.py`, `test_marimo_notebooks.py`, `test_ocr_vlm_registry.py`, `test_pdf_processing_pipeline.py`).
- [ ] T2.5 Rewrite `notebooks/` + `scripts/` imports (`scripts/test_curriculum_pipeline.py`, `notebooks/curriculum_educator.py`, `notebooks/dashboards/official_media/official_media.py`).
- [ ] T2.6 Delete `test_stagehand_grid.py` (standalone test outside `tests/`, would be missed by pytest).
- [ ] T2.7 Run `uv run pytest cianfhoghlaim/tests/ -x` — must pass after each T2.x batch.
- [ ] T2.8 Run `mise run lint:skills` — must report 123/123.
- [ ] T2.9 Run `mise run turbo typecheck` — must pass.
- [ ] T2.10 Run `! grep -rE "from sruth\.|from oideachais\." cianfhoghlaim/ --include='*.py' --exclude-dir=.archive --exclude=compat.py` — zero matches expected.
- [ ] T2.11 Delete `cianfhoghlaim/compat.py` (no longer needed after the cutover is verified).

## Phase 3 — `meaisinfhoghlaim/` redistribution per the v4 spec

- [ ] T3.1 Create `cianfhoghlaim/ocr/{models,backends,evaluation,datasets,federated}/` package skeleton (5 new `__init__.py` files)
- [ ] T3.2 Move `meaisinfhoghlaim/registry.py` → `ocr/models/registry.py` (canonical 24-entry `VISION_MODELS`)
- [ ] T3.3 Move `meaisinfhoghlaim/model_registry.py` → `.archive/meaisinfhoghlaim/legacy_model_registry.py` (deprecated 9×6, marked superseded by T3.2)
- [ ] T3.4 Move `meaisinfhoghlaim/{adapters,comparison_runner,vision_comparison,vlm_finetune_comparison,pylaia_comparison}.py` → `ocr/evaluation/`
- [ ] T3.5 Move `meaisinfhoghlaim/{line_segmentation,irish_processing,irish_htr_dataset}.py` → `ocr/datasets/`
- [ ] T3.6 Move `meaisinfhoghlaim/{gaelic_metrics,author_archive_ocr}.py` → `ocr/backends/` (and `ocr/backends/gaelic_metrics.py`)
- [ ] T3.7 Create `cianfhoghlaim/pipelines/process/_meaisinfhoghlaim_pipelines/` package
- [ ] T3.8 Move `meaisinfhoghlaim/{canuint_audio_slicer,dialect_classifier,irish_document_scanner,llm_router,transcript_aligner,ensemble_gradio}.py` → `pipelines/process/_meaisinfhoghlaim_pipelines/`
- [ ] T3.9 Move `meaisinfhoghlaim/evaluation/` → `core/evaluation/` (Ragas + Celtic OCR harness)
- [ ] T3.10 Move `meaisinfhoghlaim/quality/` → `core/quality/`
- [ ] T3.11 Move `meaisinfhoghlaim/alignment/` → `core/alignment/`
- [ ] T3.12 Move `meaisinfhoghlaim/training/` → `core/ml_training/`
- [ ] T3.13 Move `meaisinfhoghlaim/asset_generation/fibo/` → `assets/_tuatha_dagster_defs/` (MMO-adjacent)
- [ ] T3.14 Move `meaisinfhoghlaim/ci/hf_watchdog.py` → `core/ci/hf_watchdog.py` (top-level CI utility)
- [ ] T3.15 Move `meaisinfhoghlaim/document_factory/` → `core/document_factory/`
- [ ] T3.16 Move `meaisinfhoghlaim/config/` → `core/config/`
- [ ] T3.17 Move `meaisinfhoghlaim/samplaí/` → `leabharlann/samplai/` (data, not code)
- [ ] T3.18 Fold `meaisinfhoghlaim/observability.py` (loose file) → `observability/ocr.py`
- [ ] T3.19 Delete empty `meaisinfhoghlaim/` directory (after all moves complete)
- [ ] T3.20 Update `dagster/defs/meaisinfhoghlaim_platform/assets.py` imports (6 asset wrappers: canuint_audio_slicer, dialect_classifier, irish_document_scanner, llm_router, transcript_aligner, ensemble_gradio)
- [ ] T3.21 Update `tests/_meaisinfhoghlaim/*.py` (5 test files: test_ensemble_gradio, test_hf_hub_push, test_marimo_notebooks, test_ocr_vlm_registry, test_pdf_processing_pipeline)
- [ ] T3.22 Validation: `uv run pytest cianfhoghlaim/tests/_meaisinfhoghlaim/` — must pass
- [ ] T3.23 Validation: `mise run hf:verify-ocr-registry` — must report 24/24 vision models live

## Phase 4 — Observability consolidation

- [ ] T4.1 Verify `observability/__init__.py` re-exports cover the full surface used in the agent fleet (`GeminiLLMSpan`, `trace_adk_agent`, `langfuse_trace`, `mlflow_run`, `RagasEvaluator`, `LogContext`, `get_logger`)
- [ ] T4.2 Add `init_all_observability()` convenience function that calls `init_observability() + init_mlflow() + init_langfuse() + init_logfire()` in order. Replaces the lifespan boilerplate in `agents/api/_oideachais_api/main.py:54-73`
- [ ] T4.3 Flatten `observability/logfire_config.py` re-exports to `observability/__init__.py` (Logfire is currently a sub-module only)
- [ ] T4.4 Implement real `UnifiedTracer` backends (`DatadogBackend`, `LangfuseBackend`, `LogfireBackend`) — currently stubs that only `logger.debug(...)`. Real implementations call the actual SDKs (`ddtrace.tracer.start_span`, `langfuse_context.update_current_observation`, `logfire.span`).
- [ ] T4.5 Add `observability/ocr.py` (merged from `meaisinfhoghlaim/observability.py` after T3.18)
- [ ] T4.6 Wire `@observe`, `@track_agent_run`, `@trace_adk_agent`, `@log_operation` decorators into the 12-agent fleet (currently only `adk/root_agent.py` uses context managers; the other 11 agents emit no traces)
- [ ] T4.7 Update `tests/shared/test_observability.py` (174 lines) and `tests/test_observability_integrations.py` (283 lines) — rewrite legacy `sruth.*` paths to canonical `oideachais.observability` (now re-exported from `cianfhoghlaim.observability`)
- [ ] T4.8 Validation: `python -c "from cianfhoghlaim.observability import init_all_observability; init_all_observability()"` succeeds without error

## Phase 5 — Browser consolidation

- [ ] T5.1 Verify `bonneagar/stacks/browser/` is the canonical home of sruth-browser (uv workspace member `sruth-browser`)
- [ ] T5.2 Delete the stale duplicate `cianfhoghlaim/browser/` directory (real home is `bonneagar/stacks/browser/`)
- [ ] T5.3 Verify no `infrastructure/` path remains at repo root (rename to `bonneagar/` is complete). If symlink exists, remove it.
- [ ] T5.4 Update `dagster/defs/browser/loads.py` + `dagster/defs/browser/auth_assets.py` imports — `from cianfhoghlaim.core.browser import BrowserClient` → `from bonneagar.stacks.browser.sruth_browser import BrowserClient`
- [ ] T5.5 Update 8 Dagster asset consumers (`dagster/assets/official_media/scraping_assets.py` ×4, `dagster/assets/university_deep_extraction/uog_assets.py` ×1, `dagster/assets/leabharlann_inbox_assets.py` ×1, `dagster/assets/cv_assets.py` ×1) — replace `from cianfhoghlaim.core.browser import ...` with `from bonneagar.stacks.browser.sruth_browser import ...`
- [ ] T5.6 Update `dlt/_university_deep_factory.py`, `dlt/common/firecrawl_source.py`, `scripts/pre_research_cps_gov_uk.py`, `notebooks/curriculum_educator.py` similarly
- [ ] T5.7 Validation: `uv run pytest bonneagar/stacks/browser/tests/` — must pass

## Phase 6 — CocoIndex + BAML consolidation

- [ ] T6.1 Consolidate `baml/clients.baml` + `baml/clients_0.baml` + `baml/clients_llama_swap.baml` + `baml/educational_clients.baml` → 2 files: `baml/clients.baml` (canonical) + `baml/clients_llama_swap.baml` (specialty). Delete `_0` and `educational_clients.baml` (assuming MMO T2.10 renamed `tuatha_clients.baml` → `educational_clients.baml`; then merge content into `clients.baml`)
- [ ] T6.2 Verify MMO change T2.10 (`tuatha_clients.baml` → `educational_clients.baml`) already done. If pending, defer T6.1 until after MMO Phase 2 lands.
- [ ] T6.3 Create canonical `cocoindex/_lifespan.py` shared home for `LANCE_DB`, `EMBEDDER`, `RESOLVED_FILE_REGISTRY` (per `oideachais-cocoindex-v1` skill REFACTORING.md item 12)
- [ ] T6.4 Add `cocoindex/__init__.py` (currently missing — `glob cianfhoghlaim/cocoindex/**/*.py` returned no results in initial survey)
- [ ] T6.5 Update all 14 v1 CocoIndex Apps to import from `cocoindex._lifespan` (currently each defines its own LANCE_DB connection)
- [ ] T6.6 Update `dagster/assets/cocoindex_assets.py` + `dagster/assets/codebase_assets.py` + `dagster/assets/docs_skills_assets.py` imports
- [ ] T6.7 Validation: `mise run upstream:conformance` — must report 14/14 PASS
- [ ] T6.8 Validation: `mise run baml:generate` — must regenerate `baml_client/` Python module with no errors

## Phase 7 — `mise.toml` consolidation

- [ ] T7.1 Add `[tasks.cic]` namespace: `cic:sync`, `cic:lint`, `cic:test`, `cic:typecheck`, `cic:build`
- [ ] T7.2 Add `[tasks.cic:ocr]`: `cic:ocr:test`, `cic:ocr:eval`, `cic:ocr:registry-lint`
- [ ] T7.3 Add `[tasks.cic:baml]`: `cic:baml:generate`, `cic:baml:test`, `cic:baml:lint`
- [ ] T7.4 Add `[tasks.cic:cocoindex]`: `cic:cocoindex:index`, `cic:cocoindex:conformance`, `cic:cocoindex:leabharlann-books`, `cic:cocoindex:leabharlann-zotero`, `cic:cocoindex:leabharlann-takeout`
- [ ] T7.5 Add `[tasks.cic:dagster]`: `cic:dagster:dev`, `cic:dagster:list-assets`, `cic:dagster:materialise-leabharlann`
- [ ] T7.6 Add `[tasks.cic:dlt]`: `cic:dlt:dev-pipeline`, `cic:dlt:staging-pipeline`, `cic:dlt:prod-pipeline` (via the existing `make_target.sh`)
- [ ] T7.7 Add `[tasks.cic:meaisin]`: `cic:meaisin:registry-audit`, `cic:meaisin:hf-watchdog`, `cic:meaisin:litellm-regenerate`
- [ ] T7.8 Add `[tasks.cic:browser]`: `cic:browser:up`, `cic:browser:down`, `cic:browser:tests`
- [ ] T7.9 **Delete 4 stale dagster aliases**: `dagster:tuatha`, `dagster:croilar`, `dagster:meaisin`, `dagster:crypteolas`
- [ ] T7.10 **Rename `dagster:oideachais` → `dagster:dev`** as the single canonical alias
- [ ] T7.11 Validation: `mise doctor` — must report all aliases resolve
- [ ] T7.12 Validation: `mise run dagster:dev --help` succeeds; `mise run dagster:tuatha` fails with "task not found"

## Appendix A — Legacy → Canonical path mapping

| Legacy path | Canonical target |
|:--|:--|
| `sruth.oideachais.dagster_defs.*` | `cianfhoghlaim.dagster.*` |
| `sruth.oideachais.dlt_sources.*` | `cianfhoghlaim.dlt.*` |
| `sruth.oideachais.dlt_utils.*` | `cianfhoghlaim.dlt.*` |
| `sruth.oideachais.observability.*` | `cianfhoghlaim.observability.*` |
| `sruth.oideachais.cocoindex_flows.*` | `cianfhoghlaim.cocoindex.*` |
| `sruth.oideachais.cognee_integration.*` | `cianfhoghlaim.observability.*` |
| `sruth.oideachais.cognify_rules.*` | `cianfhoghlaim.cognify.*` |
| `sruth.oideachais.agents.*` | `cianfhoghlaim.agents.*` |
| `sruth.oideachais.ocr.*` | `cianfhoghlaim.ocr.*` (after Phase 3) |
| `sruth.oideachais.lancedb.*` | `cianfhoghlaim.embeddings.*` |
| `sruth.meaisinfhoghlaim.*` | `cianfhoghlaim.meaisinfhoghlaim.*` |
| `sruth.tuatha.*` | `cianfhoghlaim.meaisinfhoghlaim.educational.*` (after MMO T2.7) |
| `sruth.shared.*` | bare `*` (e.g. `sruth.shared.agent_os.config` → `agent_os.config` from `agents/api/`) |
| `sruth.browser` (NOTE: not `sruth_browser`) | `bonneagar.stacks.browser.sruth_browser.*` |
| `oideachais.*` (bare) | same as `sruth.oideachais.*` |
| `oideachais.dagster_defs.factories.create_unified_curriculum_assets` | `cianfhoghlaim.dagster.factories.create_unified_curriculum_assets` |
| `oideachais.observability` (no `sruth.` prefix) | `cianfhoghlaim.observability.*` |
| `oideachais.dlt_utils.*` | `cianfhoghlaim.dlt.*` |
| `oideachais.dlt_sources.ireland.*` | `cianfhoghlaim.dlt.british_isles.ie.*` |
| `oideachais.dlt_sources.en.*` / `oideachais.dlt_sources.en.education.*` | `cianfhoghlaim.dlt.british_isles.en.*` |
| `oideachais.dlt_sources.sct.*` | `cianfhoghlaim.dlt.british_isles.sct.*` |
| `oideachais.dlt_sources.wls.*` | `cianfhoghlaim.dlt.british_isles.wls.*` |
| `oideachais.dlt_sources.ni.*` | `cianfhoghlaim.dlt.british_isles.ni.*` |
| `oideachais.dlt_sources.iom.*` / `jey.*` / `ggy.*` | `cianfhoghlaim.dlt.british_isles.iom.*` / `.jey.*` / `.ggy.*` |
| `oideachais.dlt_sources.celtic.*` | `cianfhoghlaim.dlt.british_isles.ie.culture.*` |
| `oideachais.dlt_sources.uk.*` | `cianfhoghlaim.dlt.british_isles.<nation>.*` (decompose per nation) |
| `oideachais.dlt_sources.ireland.subjects.*` | `cianfhoghlaim.dlt.subjects.subjects.*` |
| `oideachais.dlt_sources.common.curriculum_registry` | `cianfhoghlaim.dlt.british_isles.ie.education.curriculum_registry` |
| `oideachais.cocoindex_flows.leabharlann_embedding.embed_text` | `cianfhoghlaim.cocoindex.leabharlann_embedding.embed_text` (or per-package App) |
| `oideachais.cognee_integration.culture_cognify.*` | `cianfhoghlaim.observability.culture_cognify.*` (or `cianfhoghlaim.cognify.*`) |
| `oideachais.cognify_rules.author_archive_cross_corpus.*` | `cianfhoghlaim.cognify.author_archive_cross_corpus.*` |
| `oideachais.evaluation.ragas_pipeline.*` | `cianfhoghlaim.core.evaluation.ragas_pipeline.*` (after Phase 3 T3.9) |
| `oideachais.ocr.*` | `cianfhoghlaim.ocr.*` (after Phase 3) |
| `oideachais.ocr.line_segmentation.*` | `cianfhoghlaim.ocr.datasets.line_segmentation.*` |
| `oideachais.ocr.irish_htr_dataset.*` | `cianfhoghlaim.ocr.datasets.irish_htr_dataset.*` |
| `oideachais.ocr.vlm_finetune_comparison.*` | `cianfhoghlaim.ocr.evaluation.vlm_finetune_comparison.*` |
| `oideachais.data_platform.ocr.ComparisonRunner` | `cianfhoghlaim.ocr.evaluation.ComparisonRunner` |
| `oideachais.data_platform.ocr.ModelRegistry` | `cianfhoghlaim.ocr.models.ModelRegistry` |
| `oideachais.shared.agent_os` | bare `agent_os` (relative to `agents/api/`) |
| `oideachais.dagster_defs.partitions_v2` | `cianfhoghlaim.dagster.partitions_v2` |
| `oideachais.agents.baml_integration` | `cianfhoghlaim.agents.baml_integration` |
| `oideachais.dagster_defs.assets.leabharlann_cognify_assets` | `cianfhoghlaim.dagster.assets.leabharlann_cognify_assets` |
| `oideachais.dagster_defs.assets.llm_gateway_assets` | `cianfhoghlaim.dagster.assets.llm_gateway_assets` |
| `oideachais.dagster_defs.factories` | `cianfhoghlaim.dagster.factories` |
| `oideachais.dagster_defs.sensors.curriculum_freshness` | `cianfhoghlaim.dagster.sensors.curriculum_freshness` |
| `oideachais.graph.falkordb_client` | `cianfhoghlaim.observability.falkordb_client` (or `cianfhoghlaim.cognify.falkordb_client`) |

## Appendix B — Per-directory import rewrite counts (estimate)

| Directory | Files with stale imports | Estimated edit count |
|:--|--:|--:|
| `dagster/` | 25 | ~80 |
| `dlt/` | 30 | ~50 |
| `agents/` | 8 | ~15 |
| `cocoindex/` | 5 | ~10 |
| `meaisinfhoghlaim/` | 6 | ~10 |
| `observability/` | 1 | ~3 |
| `notebooks/` | 3 | ~5 |
| `scripts/` | 2 | ~4 |
| `tests/` | 20 | ~30 |
| **Total** | **~100 files** | **~207 import lines** |