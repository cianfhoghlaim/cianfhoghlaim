# Delta: meaisinfhoghlaim-platform

## ADDED Requirements

### Requirement: meaisinfhoghlaim_platform Python asset module

The `meaisinfhoghlaim_platform` asset group SHALL be declared as a
Python asset module at
`cianfhoghlaim/assets/_oideachais_dagster_defs/defs/meaisinfhoghlaim_platform/assets.py`,
mounted via a `defs.yaml` at the same directory.

The module SHALL export exactly 6 assets, one per meaisinfhoghlaim
AI/ML pipeline:

1. `canuint_audio_slicer_asset` — Canuint audio recording slicer
2. `dialect_classifier_asset` — Irish dialect classifier
3. `irish_document_scanner_asset` — Irish PDF OCR scanner
4. `llm_router_asset` — LiteLLM-based LLM router
5. `transcript_aligner_asset` — Audio-transcript aligner
6. `ensemble_gradio_asset` — Gradio ensemble UI launcher

All 6 assets SHALL be tagged with `group_name: meaisinfhoghlaim_platform`
and the `compute_kind` SHALL be `python` (5 assets) or `gradio`
(1 asset: `ensemble_gradio_asset`).

#### Scenario: a Dagster user runs the AI/ML pipelines

- **GIVEN** the `dagster dev` webserver is running on port 3335
- **WHEN** the user materialises the `meaisinfhoghlaim_platform` group
- **THEN** all 6 AI/ML pipelines materialise (each one calls the
  underlying Python implementation in
  `cianfhoghlaim/pipelines/process/_meaisinfhoghlaim_pipelines/`)
