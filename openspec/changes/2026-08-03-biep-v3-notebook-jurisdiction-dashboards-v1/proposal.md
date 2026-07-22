# 2026-08-03-biep-v3-notebook-jurisdiction-dashboards-v1

## Why

The BIEP v3 batch shipped 5 generic jurisdiction pipelines covering
~1,560 cohorts across 8 British Isles jurisdictions, but the
marimo notebook surface is incomplete:

- 0 of 5 jurisdiction dashboard notebooks exist
  (`notebooks/19..23_*.py`)
- 57 of 99 top-level notebooks still reference `oideachais.*`
  (the Phase 0 rename sweep was incomplete for notebooks)

This is the B5 change. It lives in the **cianfhoghlaim repo** (the
notebooks are at `notebooks/`).

## What changes

### 1. Create the 5 missing jurisdiction dashboard notebooks

- `notebooks/19_ireland_pipeline_dashboard.py` (new) — 544 Ireland
  cohorts table + 4 sub-tabs (LC / JC / short / CBA)
- `notebooks/20_england_pipeline_dashboard.py` (new) — 276 England
  cohorts (3 boards × 92 subjects matrix)
- `notebooks/21_sct_wls_ni_pipeline_dashboard.py` (new) — 380
  SCT/WLS/NI cohorts split
- `notebooks/22_crown_dependencies_dashboard.py` (new) — 360 Crown
  cohorts split Jersey / Guernsey / Isle of Man
- `notebooks/23_8_jurisdiction_overview.py` (new) — all 1,560
  cohorts side-by-side

### 2. Rename sweep across 57 notebooks

- `find notebooks -name "*.py" ! -name "__init__.py" ! -path "*__pycache__*"`
  + `sed -i '' 's/oideachais\./cianfhoghlaim\./g'`

## Dependencies

```yaml
Blocked by: 2026-08-01-biep-v3-dlt-jurisdiction-pipeline-bugfix-v1
Affected repos: cianfhoghlaim (single-repo change)
```

## Acceptance gates

- `marimo run notebooks/19_ireland_pipeline_dashboard.py --headless`
  renders the 544-row cohort table
- `marimo edit notebooks/23_8_jurisdiction_overview.py` opens all 8
  jurisdiction tabs
- `grep -r "oideachais\." notebooks/*.py | grep -v "__pycache__"`
  returns 0 matches
- `openspec validate 2026-08-03-biep-v3-notebook-jurisdiction-dashboards-v1 --strict` passes

## Cross-references

- `notebooks/18_cianfhoghlaim_subject_registry.py` (the Phase 1 companion notebook)
- `notebooks/40_leaving_cert_subject_panel.py` (the 2026-07-25 grouped LC panel)
- `dlt/british_isles/_cross/registry_api.py` (the registry)
- `.agents/skills/marimo/SKILL.md` — the marimo conventions