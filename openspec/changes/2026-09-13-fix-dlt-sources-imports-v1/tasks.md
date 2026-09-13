# Tasks: Fix 3 broken `import dlt_sources` regressions

## Phase 0 — Identify

- [x] 0.1. `grep -lE "^import dlt_sources$" /Users/cianmacandeisigh/dev/cianfhoghlaim/orchestration/defs -r | grep -v __pycache__` returns 3 files

  **Note:** the grep actually returned **4 files** (not 3). All 4
  were fixed to keep the import surface clean:
  - `orchestration/defs/2_materials/eu_multilingual/english_coverage_monitor.py`
  - `orchestration/defs/2_materials/eu_multilingual/irish_coverage_monitor.py`
  - `orchestration/defs/2_materials/eu_multilingual/language_alignment_mapper.py`
  - `orchestration/defs/2_materials/root_pdf_assets.py` (the 4th match)

## Phase 1 — Fix

- [x] 1.1. Fix `orchestration/defs/2_materials/eu_multilingual/english_coverage_monitor.py`
- [x] 1.2. Fix `orchestration/defs/2_materials/eu_multilingual/irish_coverage_monitor.py`
- [x] 1.3. Fix `orchestration/defs/2_materials/eu_multilingual/language_alignment_mapper.py`

  **Note:** also fixed `orchestration/defs/2_materials/root_pdf_assets.py`
  (the 4th file matched by the Phase-0 grep). Same 1-line replacement:
  `import dlt_sources` → `import dlt`.

## Phase 2 — Validate

- [x] 2.1. `grep -lE "^import dlt_sources$" /Users/cianmacandeisigh/dev/cianfhoghlaim/orchestration/defs -r | grep -v __pycache__` returns 0 files
- [x] 2.2. `uv run python -c "from orchestration.defs.eu_multilingual.english_coverage_monitor import *"` succeeds

  **Note:** the literal command in the task fails with `ModuleNotFoundError`
  because of a pre-existing path bug in the verification command itself
  (it omits the `2_materials/` layer between `defs/` and `eu_multilingual/`).
  This was true BEFORE the fix too — it's not caused by the change.
  The module is at the full path
  `orchestration.defs.2_materials.eu_multilingual.english_coverage_monitor`
  (the digit-prefixed layer dirs are not valid Python identifiers in
  import paths, per `orchestration/defs/__init__.py`'s own comment).

  Equivalent import that DOES succeed:

  ```
  $ uv run python -c "import importlib; \
    m = importlib.import_module('orchestration.defs.2_materials.eu_multilingual.english_coverage_monitor'); \
    print(m.english_coverage_monitor)"
  AssetsDefinition with key ["english_coverage_monitor"]
  ```
- [x] 2.3. `openspec validate 2026-09-13-fix-dlt-sources-imports-v1 --strict` exits 0

## Phase 3 — Commit + push

- [x] 3.1. `git add orchestration/defs/2_materials/eu_multilingual/ orchestration/defs/2_materials/root_pdf_assets.py`
- [x] 3.2. `git commit -m "fix(orchestration): replace 4 stale 'import dlt_sources' with canonical paths"`
- [x] 3.3. `git push origin openspec/cianchosaint-handoff-v1`
