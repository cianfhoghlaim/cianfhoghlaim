## MODIFIED Requirements

### Requirement: 5 jurisdiction dashboard notebooks + 57-notebook rename sweep

The system SHALL provide the 5 jurisdiction dashboard notebooks
(`notebooks/19..23_*.py`) covering the 8 BIEP v3 jurisdictions +
~1,560 cohorts. It SHALL also rename all `oideachais.*` references
across the 99 top-level marimo notebooks to `cianfhoghlaim.*`.

#### Scenario: 5 jurisdiction dashboard notebooks exist

- **WHEN** `ls notebooks/19..23_*.py` runs
- **THEN** exactly 5 files SHALL be listed
  (19_ireland_pipeline_dashboard, 20_england_pipeline_dashboard,
  21_sct_wls_ni_pipeline_dashboard, 22_crown_dependencies_dashboard,
  23_8_jurisdiction_overview)
- **AND** each notebook SHALL render against the live registry

#### Scenario: 57-notebook oideachais → cianfhoghlaim rename sweep

- **WHEN** `grep -r "oideachais\." notebooks/*.py` runs
- **THEN** zero matches SHALL be present
- **AND** all 99 top-level notebooks SHALL use the canonical
  `cianfhoghlaim.education.<jurisdiction>.<stage>[.<board>].<subject>`
  namespace