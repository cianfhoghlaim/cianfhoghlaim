## ADDED Requirements

### Requirement: 4 stage Marimo dashboards (one per stage)

The system SHALL provide 4 stage Marimo dashboards that mirror the
BAML + CocoIndex + ADK stage planes:

- `notebooks/19_ireland_pipeline_dashboard.py` (Leaving Cycle, existing)
- `notebooks/19_junior_cycle_pipeline_dashboard.py` (Junior Cycle, new)
- `notebooks/20_england_alevel_pipeline_dashboard.py` (A-Level, new)
- `notebooks/20_england_gcse_pipeline_dashboard.py` (GCSE, new)

Each dashboard uses the canonical
`build_biep_v3_dashboard(jurisdiction=..., milestone=...)` helper.

#### Scenario: Each stage dashboard exists and uses the canonical helper

- **WHEN** the operator runs `grep -l "build_biep_v3_dashboard" notebooks/*.py`
- **THEN** the output includes all 4 stage dashboards + the 7 tier dashboards

### Requirement: biiep_v3_dashboard_v2 collapse

The system SHALL collapse the 7 tier dashboards into 1 canonical helper
+ 7 thin wrappers (per Phase 2).

The helper is at `notebooks/_shared/biiep_v3_dashboard_v2.py` and
exposes `build_biep_v3_dashboard(jurisdiction=..., milestone=...)`.

#### Scenario: All 7 tier dashboards use the canonical helper

- **WHEN** `mise run lint:marimo-tier-dashboard-collapse` runs
- **THEN** all 7 tier dashboards MUST use the canonical
  `build_biep_v3_dashboard` helper (no hand-written 8-cell operator
  consoles)

### Requirement: PEP 723 template collapse

The system SHALL collapse the 201 PEP 723 inline metadata blocks
into 1 canonical template + 201 thin imports.

The template is at `notebooks/_shared/_pep723_template.py` and
includes the canonical 9 dependencies.

#### Scenario: All 201 notebooks use the canonical template

- **WHEN** `mise run lint:marimo-pep723-template` runs
- **THEN** all 201 notebooks MUST import from
  `notebooks._shared._pep723_template` (no hand-written PEP 723
  blocks)

### Requirement: Marimo `mo.ui.chat` streaming adoption

The system SHALL adopt `mo.ui.chat(..., streaming=True)` for all 6
BIEP v3 jurisdiction dashboards + the 4 stage dashboards (10 total).

The streaming chat uses the BAML `b.Extract*` functions via
`marimo_baml.py` (per the 2026-08-18-mega-3-fast-follow-v1 change FF.2).

#### Scenario: Every dashboard exposes a streaming chat

- **WHEN** the operator opens any of the 10 BIEP v3 dashboards
- **THEN** the dashboard exposes a `mo.ui.chat(..., streaming=True)`
  cell that streams responses from the BAML extraction functions

### Requirement: Marimo `mo.ui.anywidget` for the RAGAS gauge

The system SHALL use `mo.ui.anywidget(RAGASGaugeWidget(...))` for the
RAGAS gauge widget (per the canonical `notebooks/_shared/ragas_gauge.py`
+ the marimo patterns tour).

The widget is rendered at the top-right corner of every dashboard and
shows the RAGAS ensemble score for the current stage.

#### Scenario: Every dashboard renders a RAGAS gauge

- **WHEN** `grep -l "RAGASGaugeWidget" notebooks/*.py` runs
- **THEN** the output includes all 10 dashboards + the canonical
  `00_marimo_patterns_tour.py`

### Requirement: Marimo `mo.ui.dictionary` for the schema introspection

The system SHALL use `mo.ui.dictionary(...)` to render the schema
introspection results (per `notebooks/_shared/schema.py`) in the
BIEP v3 dashboards.

#### Scenario: The schema dictionary is rendered

- **GIVEN** a BIEP v3 dashboard
- **WHEN** the operator clicks the "Schema" tab
- **THEN** the dashboard renders a `mo.ui.dictionary` with the
  schema introspection results (table names, column names, types)