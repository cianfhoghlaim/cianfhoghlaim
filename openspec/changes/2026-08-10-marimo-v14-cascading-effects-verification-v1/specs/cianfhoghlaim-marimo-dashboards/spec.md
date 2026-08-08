## ADDED Requirements

### Requirement: v14 helper modules are the canonical notebook surface (R1 + R2)

The system SHALL provide 3 canonical helper modules that collapse the
14-line `try/except ImportError` header (R1) + the open-coded 8-cell
BIEP v3 operator console (R2) into reusable functions:

- `notebooks/_shared/marimo_patterns.py` (706 LOC, 22 public symbols) —
  `setup_biep_registry_header()`, `tabbed_biep_operator_console()`,
  `progress_bar_with_eta()`, `form_gated_run_button()`,
  `llm_chat_with_prompts()`, `three_column_grid_app()`,
  `ragas_gauge_widget()`, `cli_argparser_biep()`, `cli_payload_to_output()`,
  `cli_main_if_argv()`, plus `LITELLM_BASE_URL` constant
- `notebooks/_shared/area_shims/biiep_v3_dashboard.py` (623 LOC, 26
  symbols) — `build_biep_v3_dashboard(jurisdiction, milestone, deferred)`
- `notebooks/_shared/ragas_gauge.py` (229 LOC) — `RAGASGaugeWidget`
  anywidget

Per the 2026-08-10-marimo-v14-ireland-england-dashboards-refactor-v1
OpenSpec change + the 2026-08-10-marimo-v14-cascading-effects-verification-v1
verification change.

#### Scenario: operator opens the Ireland dashboard via the canonical helpers

- **GIVEN** the operator runs `marimo edit notebooks/19_ireland_pipeline_dashboard.py`
- **WHEN** the notebook loads
- **THEN** the `_intro` cell calls `_ctx = setup_biep_registry_header()`
  (R1 — the 14-line try/except ImportError block is collapsed)
- **AND** the `_dashboard` cell calls `build_biep_v3_dashboard(jurisdiction="ireland", milestone="M1")`
  (R2 — the 8-cell operator console is collapsed)

#### Scenario: operator imports the helpers from the notebooks package

- **WHEN** the operator runs `python3 -c "from notebooks import build_biep_v3_dashboard, setup_biep_registry_header"`
- **THEN** the import succeeds
- **AND** the notebooks package re-exports both helpers via
  `notebooks/__init__.py`

### Requirement: Marimo v14 PEP 723 dependency standard

The system SHALL ship every active marimo notebook with the canonical
PEP 723 inline dependency block:

```python
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "marimo>=0.13", "ibis-framework[duckdb]>=9.0", "pandas>=2.2", "altair>=5.0", "pyarrow>=15",
#   "anywidget>=0.9", "traitlets>=5.14",
# ]
# ///
```

Per the 2026-08-10-marimo-v14-cascading-effects-verification-v1 change.

#### Scenario: operator runs a notebook with `uv run`

- **WHEN** the operator runs `uv run notebooks/19_ireland_pipeline_dashboard.py`
- **THEN** `uv` resolves the dependencies from the inline PEP 723 block
- **AND** `anywidget>=0.9` + `traitlets>=5.14` are installed (per the v14
  standard)

#### Scenario: CI lints every notebook's PEP 723 block

- **WHEN** the CI runs `mise run biep:v3:marimo:all`
- **THEN** every active marimo notebook passes `marimo check`
- **AND** every notebook has the v14 PEP 723 block + the v14 `__generated_with = "0.14.10"`

### Requirement: legacy CLI + helpers are @deprecated back-compat shims

The system SHALL keep `notebooks/cli.py` + `notebooks/nb_utils.py` as
deprecated back-compat shims (per user decision — do NOT delete them).

The system SHALL emit `DeprecationWarning` on import.

Per the 2026-08-10-marimo-v14-cascading-effects-verification-v1 change.

#### Scenario: developer imports nb_utils

- **WHEN** the developer runs `from notebooks.nb_utils import connect_biep_lakehouse`
- **THEN** a `DeprecationWarning` is emitted pointing to
  `notebooks._shared.db.connect_md`
- **AND** the import still works (back-compat preserved)

### Requirement: sync_health.py is the canonical 11-sync-layer dashboard

The system SHALL provide `notebooks/sync_health.py` as the single
canonical 11-sync-layer health dashboard (consolidating the 10
legacy sub-dashboards `14_dev_env_tools_*.py` + `15_observability_*.py`
+ `25_dagster_sync_dashboard.py` + `26_baml_sync_dashboard.py` +
`27_stacks_sync_dashboard.py` + `28_dlt_sync_dashboard.py` +
`29_agents_sync_dashboard.py` + `30_notebooks_sync_dashboard.py`).

The 11 sync layers are: paths, ccc, cognee, skills, mcp, dagster, baml,
stacks, agents, notebooks, drift-docs.

The 5 sync-loop skills (`agents-sync`, `notebooks-sync`, `stacks-sync`,
`dagster-asset-sync`, `baml-schema-sync`) SHALL reference
`sync_health.py` instead of the deprecated sub-dashboards.

Per the 2026-08-10-marimo-v14-sync-health-dashboard-consolidation-v1
change + the 2026-08-10-marimo-v14-cascading-effects-verification-v1
verification change.

#### Scenario: operator opens the canonical sync health dashboard

- **WHEN** the operator runs `marimo edit notebooks/sync_health.py`
- **THEN** the 11-tab grouped marimo notebook renders (Overview + 10
  per-layer tabs)
- **AND** the Overview tab shows the latest `stedding/sync-reports/all-<date>.md`
  parsed status grid

#### Scenario: developer reads the agents-sync skill

- **WHEN** the developer reads `.agents/skills/agents-sync/SKILL.md`
- **THEN** the skill references `notebooks/sync_health.py` Agents tab
  (NOT the deprecated `notebooks/29_agents_sync_dashboard.py`)

### Requirement: CI gate runs `marimo check` on every PR that touches notebooks/

The system SHALL provide a CI gate that runs `mise run biep:v3:marimo:all`
+ `mise run biep:v3:lint` on every PR that touches `notebooks/`,
`notebooks/_shared/`, `notebooks/_shared/area_shims/`, `mise.toml`,
or `scripts/`.

Per the 2026-08-10-marimo-v14-cascading-effects-verification-v1 change.

#### Scenario: PR adds a new BIEP dashboard

- **WHEN** a developer opens a PR that adds `notebooks/99_new_dashboard.py`
- **THEN** the CI runs `mise run biep:v3:marimo:all`
- **AND** the CI fails if the new dashboard doesn't parse
- **AND** the CI fails if any existing dashboard regresses