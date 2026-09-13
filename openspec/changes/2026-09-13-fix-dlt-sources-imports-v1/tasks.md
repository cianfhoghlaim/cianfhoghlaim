# Tasks: Fix 3 broken `import dlt_sources` regressions

## Phase 0 — Identify

- [ ] 0.1. `grep -lE "^import dlt_sources$" /Users/cianmacandeisigh/dev/cianfhoghlaim/orchestration/defs -r | grep -v __pycache__` returns 3 files

## Phase 1 — Fix

- [ ] 1.1. Fix `orchestration/defs/2_materials/eu_multilingual/english_coverage_monitor.py`
- [ ] 1.2. Fix `orchestration/defs/2_materials/eu_multilingual/irish_coverage_monitor.py`
- [ ] 1.3. Fix `orchestration/defs/2_materials/eu_multilingual/language_alignment_mapper.py`

## Phase 2 — Validate

- [ ] 2.1. `grep -lE "^import dlt_sources$" /Users/cianmacandeisigh/dev/cianfhoghlaim/orchestration/defs -r | grep -v __pycache__` returns 0 files
- [ ] 2.2. `uv run python -c "from orchestration.defs.eu_multilingual.english_coverage_monitor import *"` succeeds
- [ ] 2.3. `openspec validate 2026-09-13-fix-dlt-sources-imports-v1 --strict` exits 0

## Phase 3 — Commit + push

- [ ] 3.1. `git add orchestration/defs/2_materials/eu_multilingual/`
- [ ] 3.2. `git commit -m "fix(orchestration): replace 3 stale 'import dlt_sources' with canonical paths"`
- [ ] 3.3. `git push origin main`
