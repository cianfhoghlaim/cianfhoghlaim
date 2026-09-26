# Change: 2026-10-04-fibo-asset-pipeline-v1

## Why

The `celtic-asset-generation` spec describes FIBO 2D diagram generation
from NCCA syllabus PDFs but the actual code only exists as 5 .pyc
files in `tuatha/asset_generation/fibo/__pycache__/` (the source `.py`
files are missing). The `ExtractSyllabusDiagram` BAML function is
referenced in the spec but doesn't exist. The dagster assets under
`orchestration/defs/4_asset_generation/` don't include FIBO.

Without this change, the Tuatha MMO realms (mathematics + applied_mathematics
+ chemistry + geography + history + english + gaeilge + computer_science)
can't be built — each one needs the canonical FIBO window chrome +
sprite atlases that this pipeline produces.

This is Plan 4 of the convergence saga
(`openspec/plans/2026-10-01-convergence-saga-v1.md`).

## What Changes

### Code — new (5 source files + 1 main)
- `tuatha/asset_generation/fibo/__init__.py` — the public package surface
- `tuatha/asset_generation/fibo/schemas.py` — the dataclasses (VisualRequirement + LearningOutcome + SyllabusPage + CurriculumConcept + GeneratedAsset + FiboConfig)
- `tuatha/asset_generation/fibo/education_fibo.py` — the 8 bilingual (EN + GA) NCCA subject prompt templates (per the Brown Ajah theming)
- `tuatha/asset_generation/fibo/resources.py` — FiboResource (litellm image gen) + ValidationResource (VLM scorer via the openai/gpt-4o-mini litellm route)
- `tuatha/asset_generation/fibo/assets.py` — the 3 Dagster assets: `fibo_json_configs` + `generated_images` + `fibo_configs_from_syllabus_diagrams`

### New BAML classes (in `baml_src/media/extract_design_pattern.baml` — already exists per Plan 3)
- Reuses `RetroGameplayPattern` + `GameGenre` + `GameplayPowerEvent` + `GameplayVisualGrammar` + `GameplayPalette`
- The Plan 3 `ExtractGameplayPattern` is extended to handle SyllabusDiagram extraction (when BAML client is generated)

### Visible demo
- `scripts/fibo_render.py` — CLI: `list-subjects` + `show-prompt` + render-one + `render-all`
- `notebooks/dashboards/fibo_diagram_demo.py` — marimo dashboard

### Spec materialised
- `openspec/specs/fibo-asset-pipeline/spec.md` — 4 Requirements (R1: subject coverage, R2: 5-stage pipeline, R3: VLM validation, R4: docs-informed provenance)

### Reference surfaces
- `baml_src/media/extract_design_pattern.baml` — the existing pattern schema (per Plan 3)
- `openspec/specs/celtic-asset-generation/spec.md` — the existing spec
- `bonneagar/stacks/lakehouse/` — the lakehouse bridge (Plan 5 wires the DOC_INLINING + the DuckLake → LanceDB sync)
- `agents/workflows/_render_assets_node.py` — the shared Pillar 4 node from Plan 2

## What this does NOT ship
- Dagster asset materialisation on the live lakehouse bridge (deferred to Plan 5)
- The BAML ExtractSyllabusDiagram function (the source code is here + the spec documents it; the actual function compiles when baml-cli generate runs)
- The full syllabus_diagrams catalog (the BAML ExtractSyllabusDiagram returns 0 records when baml_client not generated; falls back to 0 docs-informed configs)

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
