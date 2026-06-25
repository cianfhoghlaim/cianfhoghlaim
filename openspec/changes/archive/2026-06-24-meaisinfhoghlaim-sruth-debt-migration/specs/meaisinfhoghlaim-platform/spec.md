# Spec Delta: meaisinfhoghlaim-platform

## MODIFIED Requirements

### Requirement: 10 sub-packages

The system SHALL NOT import from the `sruth.*` namespace. The
`sruth` package is the predecessor `bonneagar` project's Python
package and has been deleted from the filesystem. The 13
remaining `sruth.*` imports in the meaisinfhoghlaim source tree
unblock the following:

- The 5 `language/gaeilge/{duchas,tearma,gaois,duchas_images,canuint}.py`
  DLT sources
- The 4 `alignment/*.py` G2P / character-interpolation modules
- The `pipelines/llm_router.py` (the entire LLM routing layer)
- The `pipelines/canuint_audio_slicer.py` audio pipeline
- The `quality/canuint_validator.py` audio quality scorer
- The `evaluation/run_evaluation.py` RAGAS runner
- The `agents/bunchloch_research_agent.py` research agent
- The `agents/api/main_simple.py` FastAPI alternate entry-point
- The `ocr/config/base.py` (entire file is a sruth copy)

Every affected file SHALL be migrated to import from the
canonical home in `oideachais.*` or `meaisinfhoghlaim.*`. The
canonical observability logger is at
`oideachais.observability.logging.get_logger`.

#### Scenario: A developer runs the test suite

- **GIVEN** the 13 source files have been migrated
- **WHEN** `uv run pytest sruth/meaisinfhoghlaim/tests/` runs
- **THEN** no `ModuleNotFoundError: No module named 'sruth'`
  exception is raised
- **AND** all 22 tests pass (the 3 test files: test_ensemble_gradio,
  test_hf_hub_push, test_marimo_notebooks)

## ADDED Requirements

### Requirement: Agent + OCR thin-shim canonicalisation

The system SHALL canonicalise the `sruth/oideachais/agents/{adk,agno}/`
and `sruth/oideachais/ocr/` directories as **thin re-exports** of the
model-layer agents + OCR modules in `sruth/meaisinfhoghlaim/agents/` +
`sruth/meaisinfhoghlaim/ocr/`. The 12 ADK agents (root_agent,
curriculum_agent, translation_agent, corpus_agent,
research_agent, education_research_agent,
bunchloch_research_agent, geospatial_agent,
statistics_agent, curriculum_comparison_agent,
agui_curriculum_agent, mcp_curriculum_agent) and the 12 OCR
modules (adapters, comparison_runner, gaelic_metrics,
irish_htr_dataset, irish_processing, line_segmentation,
model_registry, observability, pylaia_comparison,
vision_comparison, vlm_finetune_comparison, gaelscribhneoir)
SHALL be re-exported, not duplicated.

The system SHALL keep the 5 tuatha-specific agents
(celtic_tutor_agent, mythology_narrator_agent,
quest_guide_agent, research_assistant_agent, tuatha_root_agent)
and the 1 leabharlann-specific OCR file
(`sruth/oideachais/ocr/author_archive_ocr.py`) as real code (they
are domain-specific, not duplicates).

#### Scenario: A consumer imports the same agent via both paths

- **GIVEN** the canonical agent lives at
  `sruth/meaisinfhoghlaim/agents/curriculum_agent.py`
- **AND** the thin-shim re-exports it at
  `sruth/oideachais/agents/adk/curriculum_agent.py`
- **WHEN** a consumer does
  `from oideachais.agents.adk.curriculum_agent import curriculum_agent`
- **THEN** the imported `curriculum_agent` is the **same object**
  as `meaisinfhoghlaim.agents.curriculum_agent.curriculum_agent`
  (verified via `is` comparison)

## REMOVED Requirements

(None.)
