# meaisinfhoghlaim v3 Operator Surface Capability

## Purpose

`meaisin-v3-operator-surface` is the umbrella capability for the
meaisinfhoghlaim v5 operator surface. It brings the same level of
reproducibility, cross-connection, and documentation to the OCR/HTR
quadrant that the BIEP v3 umbrella brings to the 8 British Isles
jurisdictions.

The 7-phase plan per the `meaisin-v3-systematic-download.md` doc:

1. **Phase 1**: Canonical operator entrypoints (`meaisin:v3:setup` + `meaisin:v3:status`)
2. **Phase 2**: 24 OCR/VLM models wired into the BIEP v3 MotherDuck Dive + Dagster asset surface
3. **Phase 3**: 7 document converters wired into the BIEP v3 MotherDuck Dive + Dagster asset surface
4. **Phase 4**: 7 canonical newcomer docs (this file + 6 more)
5. **Phase 5**: BAML Test blocks for the 4-path OCR ensemble + RAGAS BIEP ensemble + 24-model v4 registry
6. **Phase 6**: 12 agents wired into the BIEP v3 MotherDuck Dive + Dagster asset surface
7. **Phase 7**: 2 new openspec specs (this file + `meaisin-24-ocr-models`)

## Background

The meaisinfoghhlaim quadrant has 11 sub-packages, 72 Python files, and
23,914 lines of code. Prior to the meaisin v5 operator surface, the
24 OCR/VLM models + 7 document converters + 12 agents were INVISIBLE to
the operator surface — no notebooks, no mise tasks, no MotherDuck Dives,
no canonical docs.

The meaisin v5 operator surface fixes this by bringing the same
level of reproducibility, cross-connection, and documentation to the
OCR/HTR quadrant that the BIEP v3 umbrella brings to the 8 British
Isles jurisdictions.

## Requirements

### Requirement: meaisin v3 canonical operator entrypoints

The system SHALL provide the canonical 2 operator entrypoints:

- `mise run meaisin:v3:setup` — the "first 30 minutes" setup script
- `mise run meaisin:v3:status` — the canonical status script

Both are implemented at `scripts/meaisin_v3_setup.py` and
`scripts/meaisin_v3_status.py` (per the meaisin v5 umbrella spec).

#### Scenario: `meaisin:v3:setup` runs all 7 steps

- **WHEN** the operator runs `mise run meaisin:v3:setup`
- **THEN** the script runs 7 steps:
  1. Python version check (>= 3.12)
  2. CUDA availability check (optional)
  3. Registry audit (24 OCR/VLM models × 4 backends)
  4. HF watchdog check
  5. OCR evaluation harness
  6. Validate 4 active meaisinfhoghlaim openspec changes
  7. Run lint:skills (53/53 pass)

### Requirement: Per-component mise task entrypoints

The system SHALL provide the canonical per-component entrypoints:

- 24 per-model entrypoints: `meaisin:ocr:test:<model_key>` (24 OCR/VLM models)
- 7 per-converter entrypoints: `meaisin:converter:test:<name>` (7 converters)
- 12 per-agent entrypoints: `meaisin:agent:test:<name>` (12 agents)

Each entrypoint is implemented at `scripts/meaisin_ocr_htr_tests/`.

#### Scenario: Per-model entrypoint runs the 4-path ensemble

- **WHEN** the operator runs `mise run meaisin:ocr:test:deepseek-ocr-2`
- **THEN** the script runs 3 steps:
  1. Run the 4-path OCR ensemble for the model
  2. Run the OCR evaluation harness
  3. Run the 24-model registry audit

### Requirement: 4-cadence meaisinfhoghlaim scheduling policy

The system SHALL implement the 4-cadence meaisinfhoghlaim scheduling
policy:

- **Weekly** (cron `0 6 * * 1`) for the M0 foundation + registry audit + HF watchdog
- **Nightly** (cron `0 0 * * *`) for the RAGAS BIEP ensemble + 4-path OCR ensemble evaluations
- **Monthly** (cron `0 0 1 * *`) for the 7 document converter pipeline
- **Event-driven** (eager) for the HuggingFace watchdog + DriftMonitor

#### Scenario: 4-cadence policy implemented

- **WHEN** the operator runs `mise run meaisin:v3:status`
- **THEN** the status script shows the 4-cadence policy in section 7

### Requirement: Canonical MotherDuck Dives

The system SHALL provide 12 MotherDuck Dives:

- 4 OCR/VLM Dives: `meaisin_ocr_registry_dive`, `meaisin_ensemble_audit_dive`, `meaisin_evaluation_summary_dive`, + 1 more
- 3 document converter Dives: `meaisin_converter_coverage_dive`, `meaisin_converter_performance_dive`, `meaisin_converter_quality_dive`
- 3 agent Dives: `meaisin_agent_registry_dive`, `meaisin_agent_memory_dive`, `meaisin_agent_observability_dive`
- 2 more agent Dives (total 12)

#### Scenario: 12 canonical Dives

- **WHEN** the operator opens the MotherDuck UI
- **THEN** the 12 canonical meaisinfhoghlaim Dives are visible with the canonical names

### Requirement: Canonical 7 newcomer docs

The system SHALL provide 7 canonical newcomer docs:

- `docs/agents/meaisin-v3-systematic-download.md` — the 7-phase plan
- `docs/agents/meaisin-v3-quickstart.md` — the "first 30 minutes" guide
- `docs/agents/meaisin-v3-faq.md` — the canonical FAQ
- `docs/agents/meaisin-v3-ocr-vlm-client.md` — how to invoke the 24 OCR/VLM models
- `docs/agents/meaisin-v3-storage-layout.md` — the canonical meaisinfhoghlaim storage layout
- `docs/agents/meaisin-v3-cron-schedule.md` — the 4-cadence meaisinfhoghlaim schedule
- `docs/agents/meaisin-v3-mieaisin-7-packages.md` — the 11 sub-packages overview

#### Scenario: 7 canonical docs

- **WHEN** the operator reads `meaisin-v3-systematic-download.md`
- **THEN** they see the 7-phase plan + the 24 OCR/VLM models + the 7 converters + the 12 agents + the 4-cadence schedule

## Cross-references

- `meaisin-24-ocr-models` — the per-OCR/VLM model contract
- `meaisinfhoghlaim-platform` — the umbrella platform spec
- `meaisinfhoghlaim-ocr-htr` — the OCR + HTR capability
- `meaisinfhoghlaim-agent-frameworks` — the 12-agent framework spec
- `multimodal-code-and-media-intel` — the multimodal capability
- `openspec/changes/2026-07-17-fix-phantom-agents-and-ocr-backend-list-v1/` — the v5 fix
- `openspec/changes/2026-07-17-restore-ocr-python-package-v1/` — the v5 restore
- `openspec/changes/2026-07-21-biep-v2-england-aqa-ocr-baml-pipeline-v1/` — the v5 England AQA
- `openspec/changes/2026-07-22-biep-v2-ocr-vlm-pipeline-convergence-v1/` — the v5 ensemble
- `scripts/meaisin_v3_setup.py` — the 7-step setup script
- `scripts/meaisin_v3_status.py` — the 7-section status script
- `scripts/meaisin_ocr_htr_tests/` — the 43 entrypoint scripts
- `docs/agents/meaisin-v3-*.md` — the 7 canonical newcomer docs
