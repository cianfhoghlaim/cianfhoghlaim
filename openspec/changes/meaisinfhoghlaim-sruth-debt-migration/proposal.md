# Change: meaisinfhoghlaim-sruth-debt-migration

## Why

Round 8 of the multi-quadrant refactor plan. Per the
`meaisinfhoghlaim/` subagent's deep-dive report (2026-06-24):

- **13 source files** import from the `sruth.*` namespace (the
  predecessor `bonneagar` project's Python package, deleted from
  the filesystem). Every import raises `ModuleNotFoundError` on
  startup.
- The 13 files are: `evaluation/run_evaluation.py`,
  `pipelines/llm_router.py`, `alignment/{irish_g2p,canuint_exporter,
  character_interpolator}.py`, `pipelines/canuint_audio_slicer.py`,
  `quality/canuint_validator.py`, `language/gaeilge/{duchas,tearma,
  gaois,duchas_images,canuint}.py`, `agents/bunchloch_research_agent.py`,
  `agents/api/main_simple.py`, `ocr/config/base.py`
- `ocr/config/base.py` (381 lines) is an **entire-file copy-paste
  of `sruth`'s `FlowSettings` base**; the docstring even says
  "Base Configuration for sruth data pipelines"
- `oideachais/agents/{adk,agno}/` near-duplicate the model-layer
  agents in `meaisinfhoghlaim/agents/` (25 files vs. 17; the
  post-Phase-5 thin-shim treatment was only applied to the 4
  tuatha agents)
- `oideachais/ocr/` (13 files) near-duplicates `meaisinfhoghlaim/ocr/`
  (12 files; identical filenames)
- `meaisinfhoghlaim-ocr-htr/spec.md` says **10 models** but the
  code (`meaisinfhoghlaim/ocr/model_registry.py:OCR_MODELS`) has
  **9**. The spec also says the backends are "Pylaia, TrOCR,
  PaddleOCR, Tesseract, dots.ocr, VLM" but the `ModelBackend` enum
  has "LITELLM, MLX, TRANSFORMERS, OLLAMA, OPENAI, ANTHROPIC" —
  the two lists are disjoint
- 3 new skills are landing: `celtic-ocr-evaluation`,
  `irish-speech-pipeline`, `agent-fleet-orchestration`

The change codifies the v0→v1 migration of the 13 sruth imports
+ the 2 thin-shim reductions (oideachais/agents/ + oideachais/ocr/)
+ the OCR spec count reconciliation.

## What Changes

### 1. `meaisinfhoghlaim-platform` spec (MODIFIED + ADDED)

1 MODIFIED Requirement ("no sruth imports") + 1 ADDED
Requirement ("agent + ocr thin-shim canonicalisation") that
codify the v0→v1 migration + the thin-shim pattern.

### 2. `meaisinfhoghlaim-ocr-htr` spec (MODIFIED + ADDED)

1 MODIFIED Requirement ("OCR model count + backend list") that
reconciles the spec's 10-model / 6-backend list with the code's
9-model / 6-backend registry. 1 ADDED Requirement for the 10th
model placeholder.

### 3. Refactor: 13 sruth.* imports → canonical homes

The 13 affected files get their `sruth.*` imports replaced with
the canonical home:

- `from sruth.oideachais.observability.logging import get_logger`
  → `from oideachais.observability.logging import get_logger`
  (the new home in `oideachais/observability/logging.py`, to be
  created in this round)
- `from sruth.oideachais.evaluation.ragas_pipeline import ...`
  → `from meaisinfhoghlaim.evaluation.ragas_pipeline import ...`
  (the local sibling, NOT the sruth one)
- `from sruth.oideachais.dlt_sources.celtic.duchas import duchas_source`
  → `from oideachais.dlt_sources.celtic.duchas import duchas_source`
  (the canonical home per the cross-domain-registry skill)
- `from sruth.shared.embeddings import ...` →
  `from oideachais.embeddings.batch import ...`
- `from sruth.shared.graph import ...` →
  `from oideachais.graph.client import ...`
- `ocr/config/base.py` (entire file, 381 lines) → DELETE; the
  re-imports come from `meaisinfhoghlaim/observability/config.py`
  (a 50-line shim)

### 4. Refactor: `oideachais/agents/{adk,agno}/` → thin re-exports

The 25-file `oideachais/agents/adk/` directory reduces to:
- `__init__.py` (50 lines) that re-exports the 12 model-layer
  agents from `meaisinfhoghlaim/agents/`
- 5 tuatha-specific agents (the 4 from Phase 5 + the 1 tuatha_root_agent)
  stay as real code
- The 19 other ADK files (root_agent, curriculum_agent,
  translation_agent, etc.) become 12-line shims

The 1-file `oideachais/agents/agno/` directory stays as a re-export
shim (or gets removed if the Agno team lives entirely in
`meaisinfhoghlaim/agents/agno/`).

### 5. Refactor: `oideachais/ocr/` → thin re-exports

The 13-file `oideachais/ocr/` directory reduces to:
- `__init__.py` that re-exports the 12 model-layer modules from
  `meaisinfhoghlaim/ocr/`
- 1 leabharlann-specific file (`author_archive_ocr.py`) stays as
  real code (because the leabharlann pipeline lives in oideachais)

### 6. Refactor: OCR spec ↔ registry reconciliation

`meaisinfhoghlaim-ocr-htr/spec.md` says 10 models. The code has 9.
Either:
- (a) Update the spec to match the code (9 models, not 10)
- (b) Add the 10th model (suggested: `gemma-3-vision` per the
  llama-swap config)

This change goes with (b): add `gemma-3-vision` to the registry
+ the spec, bringing both to 10.

For the 6 backends, the spec's 6 backends are a misnomer (they
list 6 OCR engines, not 6 model-serving backends). Update the
spec to use the correct 6: `litellm`, `mlx`, `transformers`,
`ollama`, `openai`, `anthropic`.

### 7. 3 new skills land

- `.agents/skills/celtic-ocr-evaluation/SKILL.md` (220 lines)
- `.agents/skills/irish-speech-pipeline/SKILL.md` (180 lines)
- `.agents/skills/agent-fleet-orchestration/SKILL.md` (250 lines)

### 8. 3 doc updates (1-line diffs each)

- `meaisinfhoghlaim/AGENTS.md` — add `marimo/` row + `sruth migration` row
- `meaisinfhoghlaim/README.md` — drop Known-Issues #2; add `sruth.*` import debt as the new highest priority; add §11 "v0→v1 migration backlog"
- `meaisinfhoghlaim/pyproject.toml` — add `[tool.uv.sources]` block for `oideachais` + `codeolas`

## Impact

- Affected specs: `meaisinfhoghlaim-platform` (1 MODIFIED + 1 ADDED) + `meaisinfhoghlaim-ocr-htr` (1 MODIFIED + 1 ADDED)
- Affected skills: 3 new (celtic-ocr-evaluation, irish-speech-pipeline, agent-fleet-orchestration)
- Affected code:
  - 13 sruth.* imports migrated
  - 1 file (`ocr/config/base.py`) deleted
  - 1 new file (`oideachais/observability/logging.py`) added
  - 25 ADK files reduced to 12-line shims
  - 13 OCR files reduced to 12-line shims
- 1 commit + 1 archive commit per the established pattern

## Success criteria

- `from sruth.X` raises no `ModuleNotFoundError` in the test suite
- `oideachais/agents/adk/curriculum_agent` is the same object as
  `meaisinfhoghlaim/agents/curriculum_agent` (the thin-shim re-export)
- `oideachais/ocr/adapters` is the same module as
  `meaisinfhoghlaim/ocr/adapters` (the thin-shim re-export)
- `meaisinfhoghlaim/ocr/model_registry.py:OCR_MODELS` has 10 entries
- `meaisinfhoghlaim-ocr-htr/spec.md` documents 10 models + 6
  backends (litellm, mlx, transformers, ollama, openai, anthropic)
- 3 new skills exist with valid frontmatter
- `openspec validate meaisinfhoghlaim-sruth-debt-migration --strict` passes
- 1 commit + 1 archive commit land on `q3-2026-oideachais-consolidation`
