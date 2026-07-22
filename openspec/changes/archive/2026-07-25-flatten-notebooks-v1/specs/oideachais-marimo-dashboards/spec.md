## MODIFIED Requirements

### Requirement: notebooks/ directory is flat (no notebook subdirectories)

The system SHALL require the `notebooks/` directory to contain only
top-level `.py` files (no subdirectories of notebooks), with the
**4 named exceptions**:
- `notebooks/_shared/` — the cross-notebook helper package
- `notebooks/legacy/` — the preserved-corpora directory
- `notebooks/analysis_plan/` — 5 markdown reference docs (NOT notebooks)
- `notebooks/subject_study_tools/` — deployment configs (Dockerfile, wrangler.jsonc, deploy.sh) — NOT notebooks

The `notebooks/leaving_cert/03_leaving_cert/` subtree is deleted by
the Change 5 stale purge.

Top-level notebooks SHALL follow the `<area>_<NN>_<topic>.py` naming convention.

#### Scenario: Zero notebook subdirectories in notebooks/ at the top level

- **WHEN** `find notebooks -mindepth 1 -maxdepth 1 -type d ! -name "__pycache__" ! -name "_shared" ! -name "legacy" ! -name "analysis_plan" ! -name "subject_study_tools" ! -name "leaving_cert"` runs after the flatten
- **THEN** zero notebook-subdirs are listed
- **AND** every notebook is a top-level `.py` file

### Requirement: 40_leaving_cert_subject_panel.py renders 7 tabs

The system SHALL require `notebooks/40_leaving_cert_subject_panel.py` to
render 7 marimo `mo.ui.tabs` (Mathematics, Chemistry, Geography, Gaeilge,
English, Computer Science, EN/GA Comparison), each backed by the
per-subject LC LanceDB table `oideachais.lc.<subject>.<level>_<lang>`.

The ibis-first contract SHALL be honoured (no raw `duckdb.connect()`).

#### Scenario: 7 tabs render against the live lakehouse

- **GIVEN** the lakehouse stack is up + the LC LanceDB tables are populated
- **WHEN** the operator runs `marimo run notebooks/40_leaving_cert_subject_panel.py --headless`
- **THEN** the 7 tabs all render against `connect_md()` (no raw `duckdb.connect`)
- **AND** the per-subject queries return the canonical `oideachais.lc.<subject>.<level>_<lang>` rows