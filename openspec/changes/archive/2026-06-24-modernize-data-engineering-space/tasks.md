# Tasks: modernize-data-engineering-space

## 1. Add the KCG data layer module

- [x] Create `package_analytics/kcg_data_layer/__init__.py`
- [x] Create `package_analytics/kcg_data_layer/pypi_source.py`
      (canonical DLT source for the 5 priority packages)
- [x] Create `package_analytics/kcg_data_layer/motherduck_destination.py`
      (canonical MotherDuck destination with local DuckDB fallback)
- [x] Create `package_analytics/kcg_data_layer/cognee_cognify.py`
      (5-stage Cognee + Graphiti cognify pass)

## 2. Rewrite the README

- [x] Rewrite `README.md` to document the KCG-canonical stack
      (before/after table, 4-tab Evidence dashboard,
      how-to-run with the canonical env vars)

## 3. Spec deltas

- [x] 1 MODIFIED Requirement on `data-engineering-space`:
      "data-engineering Space modernized to the KCG-canonical stack"

## 4. Validate + commit + push + archive

- [x] Commit inside the data-engineering repo
- [x] Commit the monorepo submodule reference change
- [x] Archive the openspec change
- [x] `git push`
