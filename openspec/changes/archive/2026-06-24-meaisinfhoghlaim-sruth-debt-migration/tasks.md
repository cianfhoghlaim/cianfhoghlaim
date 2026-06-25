# Tasks: meaisinfhoghlaim-sruth-debt-migration

## 1. 3 new skills

- [x] Create `.agents/skills/celtic-ocr-evaluation/SKILL.md` (220 lines)
- [x] Create `.agents/skills/irish-speech-pipeline/SKILL.md` (180 lines)
- [x] Create `.agents/skills/agent-fleet-orchestration/SKILL.md` (250 lines)

## 2. Openspec changes (2)

- [x] Create `openspec/changes/meaisinfhoghlaim-sruth-debt-migration/proposal.md`
- [x] Create `openspec/changes/meaisinfhoghlaim-sruth-debt-migration/tasks.md`
- [x] Create `openspec/changes/meaisinfhoghlaim-sruth-debt-migration/specs/meaisinfhoghlaim-platform/spec.md`
  (1 MODIFIED + 1 ADDED)
- [x] Create `openspec/changes/meaisinfhoghlaim-sruth-debt-migration/specs/meaisinfhoghlaim-ocr-htr/spec.md`
  (1 MODIFIED + 1 ADDED)
- [x] `openspec validate meaisinfhoghlaim-sruth-debt-migration --strict`
- [x] `openspec archive meaisinfhoghlaim-sruth-debt-migration --yes`

## 3. Refactor: 13 sruth.* imports → canonical homes

- [x] Create `sruth/oideachais/observability/__init__.py` + `sruth/oideachais/observability/logging.py`
  (the canonical home for `get_logger`)
- [x] Migrate `sruth/meaisinfhoghlaim/evaluation/run_evaluation.py:68`:
  `from sruth.oideachais.evaluation.ragas_pipeline import ...`
  → `from meaisinfhoghlaim.evaluation.ragas_pipeline import ...`
- [x] Migrate `sruth/meaisinfhoghlaim/pipelines/llm_router.py:21-23`:
  `from sruth.oideachais.settings import settings` + `from ..core.utils import CircuitBreaker`
  → `from oideachais.settings import settings` + `from oideachais.core.utils import CircuitBreaker`
- [x] Migrate `sruth/meaisinfhoghlaim/alignment/{irish_g2p,canuint_exporter,character_interpolator}.py`:
  `from sruth.oideachais.observability.logging import get_logger`
  → `from oideachais.observability.logging import get_logger`
- [x] Migrate `sruth/meaisinfhoghlaim/pipelines/canuint_audio_slicer.py:21`
- [x] Migrate `sruth/meaisinfhoghlaim/quality/canuint_validator.py:22`
- [x] Migrate `sruth/meaisinfhoghlaim/language/gaeilge/{duchas,tearma,gaois,duchas_images,canuint}.py`
  (5 files): swap `sruth.oideachais.observability.logging` + `sruth.shared.http`
  → `oideachais.observability.logging` + `oideachais.http`
- [x] Migrate `sruth/meaisinfhoghlaim/agents/bunchloch_research_agent.py:94,201`:
  `from sruth.shared.{embeddings,graph} import ...`
  → `from oideachais.embeddings.batch import ...` + `from oideachais.graph.client import ...`
- [x] Migrate `sruth/meaisinfhoghlaim/agents/api/main_simple.py:20`:
  remove the `sruth.shared.storage` import
- [x] Delete `sruth/meaisinfhoghlaim/ocr/config/base.py` (381 lines, the sruth copy)

## 4. Refactor: `sruth/oideachais/agents/{adk,agno}/` → thin re-exports

- [x] Update `sruth/oideachais/agents/adk/__init__.py` to re-export the 12
  model-layer agents from `meaisinfhoghlaim.agents.*`
- [x] Reduce 19 ADK files (root_agent, curriculum_agent,
  translation_agent, corpus_agent, research_agent, education_research_agent,
  bunchloch_research_agent, geospatial_agent, statistics_agent,
  curriculum_comparison_agent, agui_curriculum_agent, mcp_curriculum_agent,
  enhanced_orchestrator, etc.) to 12-line shims
- [x] Keep the 5 tuatha-specific agents (celtic_tutor_agent,
  mythology_narrator_agent, quest_guide_agent,
  research_assistant_agent, tuatha_root_agent) as real code

## 5. Refactor: `sruth/oideachais/ocr/` → thin re-exports

- [x] Update `sruth/oideachais/ocr/__init__.py` to re-export the 12
  model-layer modules from `meaisinfhoghlaim.ocr.*`
- [x] Reduce 12 OCR files to 12-line shims
- [x] Keep `sruth/oideachais/ocr/author_archive_ocr.py` (leabharlann-specific)

## 6. Refactor: OCR spec ↔ registry reconciliation

- [x] Add `gemma-3-vision` to
  `sruth/meaisinfhoghlaim/ocr/model_registry.py:OCR_MODELS`
  (the 10th model)
- [x] Update `sruth/meaisinfhoghlaim/llama-swap-config.yaml` to add
  the GGUF-quantised variant
- [x] Update `meaisinfhoghlaim-ocr-htr/spec.md` to document 10
  models (not 9) and the correct 6 backends (litellm, mlx,
  transformers, ollama, openai, anthropic)

## 7. 3 doc updates (1-line diffs each)

- [x] `sruth/meaisinfhoghlaim/AGENTS.md` — add `marimo/` row + `sruth migration` row
- [x] `sruth/meaisinfhoghlaim/README.md` — drop Known-Issues #2; add
  `sruth.*` import debt as the new highest priority; add §11
  "v0→v1 migration backlog"
- [x] `sruth/meaisinfhoghlaim/pyproject.toml` — add `[tool.uv.sources]`
  block for `oideachais` + `codeolas`

## 8. Commit + push + archive

- [x] `git commit -m "refactor(meaisinfhoghlaim): 3 skills + sruth-debt migration + 2 thin-shims (round 8)"`
- [x] `git push origin q3-2026-oideachais-consolidation`
- [x] `openspec archive meaisinfhoghlaim-sruth-debt-migration --yes`
- [x] `git commit -m "openspec(archive): 2026-06-24-meaisinfhoghlaim-sruth-debt-migration"`
- [x] `git push origin q3-2026-oideachais-consolidation`
