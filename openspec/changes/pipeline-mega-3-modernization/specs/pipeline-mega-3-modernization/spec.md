# pipeline-mega-3-modernization Specification

## ADDED Requirements

### Requirement: Cross-batch Mega-3 milestone contract

The system SHALL ship the Mega-3 4-stage plane modernization as ONE
milestone composed of 5 sequenced sub-changes (Roadmap + Fast-Follow
+ 3a + 3b + 3c). No sub-change may archive independently — the
BAML stage templates, CocoIndex stage factories, ADK agent fleet,
Marimo stage dashboards, and integration helpers all depend on
each other and must be tested as one stack.

#### Scenario: Mega-3 milestone ships as one batch

- **WHEN** the 3 dated changes (`2026-08-18-mega-3-roadmap-v1`,
  `2026-08-18-mega-3-fast-follow-v1`,
  `2026-08-26-mega-3a-baml-and-adk-v1`) complete
- **THEN** this umbrella archives with `openspec archive
  pipeline-mega-3-modernization --yes`
- **AND** the net LOC across all 5 packages drops by approximately
  25,799 lines (per the Mega-3 target)
- **AND** every Leaving Certificate + Junior Certificate + A-Level +
  GCSE subject reuses one of the 4 stage templates (not per-subject
  hand-written code)

### Requirement: 5 integration helpers

The system SHALL provide 5 reusable integration helpers (one per
sub-package boundary) that the 3 sequenced Mega-3 batches wire into:

  1. `BAMLFunctionTool` — wrap any BAML function as an ADK FunctionTool
  2. `marimo_baml` — marimo cell that calls a BAML function with progress UI
  3. `agent_ui_bridge` — bridge agent output to marimo cell reactive state
  4. `marimo_to_copilotkit` — marimo cell → CopilotKit action
  5. `cocoindex_query_api` — typed query API over CocoIndex App

#### Scenario: Every Mega-3 batch uses the 5 helpers

- **WHEN** a BAML function is exposed to a marimo notebook
- **THEN** it MUST go through `marimo_baml` (not raw `baml_client.sync_client`)
- **AND** the marimo cell MUST be reactive (per marimo v14 patterns
  established in `pipeline-marimo-dashboards-v14`)

### Requirement: BAML 0.223.0 feature adoption

The system SHALL adopt the BAML 0.223.0 features (`spawn`,
`host.callable`, `catch`, `render_null_as`, multimodal, intersection
bounds) in the 4 stage templates + the 5 integration helpers.

#### Scenario: stage templates use the new BAML features

- **WHEN** a subject is added via the LC/JC/A-Level/GCSE stage
  template
- **THEN** the template MUST use `render_null_as` for every optional
  field (so missing data renders as the documented default, not as
  a hard error)
- **AND** the template MUST use `catch` for every cross-system call
  (BAML → Marimo, BAML → ADK, BAML → CocoIndex)
