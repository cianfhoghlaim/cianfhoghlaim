## ADDED Requirements

### Requirement: 4-stage plane extension

The system SHALL extend the centralized registry surface (per
`2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1`)
to cover the 4-stage plane (Leaving Cycle + Junior Cycle + A-Level
+ GCSE) across all 5 packages (BAML + CocoIndex + Google ADK +
CopilotKit + Marimo).

The extension includes:
- `MODEL_REGISTRY` covers the 4 stages (each stage has its own
  text_llm / ocr_vision / embedder defaults)
- `notebooks/_shared/schema.py` exposes 4 new helpers:
  `list_stage_templates()`, `list_stage_agents()`,
  `list_stage_cocoindex_apps()`, `list_stage_marimo_notebooks()`
- `notebooks/00_control_panel.py` expands from 5 tabs to 7 tabs
  (Models / Pipelines / Datasets / Stacks / Agents / Notebooks / Registry)
- `deployment-choice.yaml` covers all 4 stages

#### Scenario: Each stage has the same canonical surface

- **GIVEN** the 4 stages (Leaving Cycle + Junior Cycle + A-Level + GCSE)
- **WHEN** the operator runs
  `python -c "from notebooks._shared.schema import list_stage_templates; print(list_stage_templates())"`
- **THEN** the output is a dict of 4 stages × 5 packages = 20
  canonical surfaces

### Requirement: BAML stage template list

The system SHALL expose the 5 BAML stage templates
(`lc_extraction_template.baml`, `junior_cycle_template.baml`,
`alevel_extraction_template.baml`, `gcse_extraction_template.baml`,
`qpack_template.baml`) via the `list_stage_templates()` helper.

#### Scenario: All 5 templates are listed

- **GIVEN** the 5 BAML stage templates under `baml_src/british_isles/_shared/`
- **WHEN** the operator runs `list_stage_templates()`
- **THEN** the output lists 5 templates with their stage, path,
  and subjects covered