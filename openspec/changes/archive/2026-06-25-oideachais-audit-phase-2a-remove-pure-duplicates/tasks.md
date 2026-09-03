# Tasks: oideachais-audit-phase-2a-remove-pure-duplicates

## 1. Pre-flight verification (importer audit)

- [ ] Run `grep -rn "from sruth.oideachais.routes\b\|from oideachais.routes\b" sruth/ infrastructure/ apps/ web/ tests/ openspec/ --include="*.py" --include="*.md"` and confirm 0 matches outside `sruth/oideachais/routes/` itself
- [ ] Run `grep -rn "from sruth.oideachais.sensors\b\|from oideachais.sensors\b" sruth/ infrastructure/ apps/ web/ tests/ openspec/ --include="*.py" --include="*.md"` and confirm 0 matches outside `sruth/oideachais/sensors/` itself
- [ ] Run `grep -rn "from sruth.oideachais.middleware\b\|from oideachais.middleware\b" sruth/ infrastructure/ apps/ web/ tests/ openspec/ --include="*.py" --include="*.md"` and confirm 0 matches outside `sruth/oideachais/middleware/` itself
- [ ] Run `grep -rn "from sruth.oideachais.storage.serial_executor\|from oideachais.storage.serial_executor" sruth/ infrastructure/ apps/ web/ tests/ openspec/ --include="*.py" --include="*.md"` and confirm EXACTLY 1 match: `sruth/oideachais/tests/conftest.py:244`
- [ ] Run `git log --all --oneline -- sruth/oideachais/routes/ sruth/oideachais/sensors/ sruth/oideachais/middleware/` to confirm all 3 dirs originate from the `137ad7b9a refactor: move meaisinfhoghlaim to sruth/` commit (or earlier sprawl commits)

## 2. Update tests/conftest.py to import from canonical core/storage/

- [ ] Edit `sruth/oideachais/tests/conftest.py:244`: change `from oideachais.storage.serial_executor import SerialDatabaseExecutor` → `from oideachais.core.storage.serial_executor import SerialDatabaseExecutor`
- [ ] Verify no other imports of `oideachais.storage.serial_executor` remain anywhere in the repo (re-run the grep from §1)

## 3. Byte-identity confirmation

- [ ] `shasum -a 256 sruth/oideachais/routes/*.py sruth/oideachais/api/routes/*.py | sort | uniq -c | sort -rn | head` — confirm each `.py` appears at least twice (the duplicate + canonical)
- [ ] `shasum -a 256 sruth/oideachais/sensors/curriculum_freshness.py sruth/oideachais/dagster_defs/sensors/curriculum_freshness.py` — confirm identical
- [ ] `shasum -a 256 sruth/oideachais/sensors/domain_sensors.py sruth/oideachais/dagster_defs/sensors/domain_sensors.py` — confirm identical
- [ ] `shasum -a 256 sruth/oideachais/middleware/*.py sruth/oideachais/api/middleware/*.py | sort | uniq -c | sort -rn | head` — confirm each `.py` appears at least twice

## 4. Execute `git rm` (4 deletions)

- [ ] `git rm -r sruth/oideachais/routes/` (5 .py + README)
- [ ] `git rm -r sruth/oideachais/sensors/` (2 .py + __init__ + README)
- [ ] `git rm -r sruth/oideachais/middleware/` (6 files + README)
- [ ] `git rm sruth/oideachais/storage/serial_executor.py`

## 5. Validation gates

- [ ] `openspec validate oideachais-audit-phase-2a-remove-pure-duplicates --strict` → PASS
- [ ] `python -c "import sruth.oideachais"` → OK
- [ ] `python -c "from sruth.oideachais.api.routes import agent, curriculum, search, geospatial, tts, cross_archive_graph, leaving_cert, official_media; print('all 8 routers importable')"` → OK
- [ ] `python -c "from sruth.oideachais.dagster_defs.sensors import all_sensors; assert len(all_sensors) >= 5, 'canonical should register 5 sensor groups'"` → OK
- [ ] `python -c "from sruth.oideachais.api.middleware import AuthMiddleware; print('AuthMiddleware OK')"` → OK
- [ ] `python -c "from sruth.oideachais.core.storage import SerialDatabaseExecutor, DuckDBClient, LanceDBClient; print('core.storage OK')"` → OK
- [ ] `grep -rn "from sruth.oideachais.routes\b\|from sruth.oideachais.sensors\b\|from sruth.oideachais.middleware\b\|from oideachais.storage.serial_executor" sruth/ infrastructure/ apps/ web/ tests/ openspec/ --include="*.py"` → 0 matches (zero residual references)
- [ ] `mise run lint:skills` → 108/108 PASS
- [ ] (optional) `uv run --package oideachais python -c "from sruth.oideachais.dagster_defs.definitions import defs; print(len(defs.get_asset_graph().get_all_asset_keys()))"` → ≥120 assets registered

## 6. Doc updates

- [ ] `sruth/oideachais/REFACTORING.md` — add "Round 11 Phase 2A — Pure-Duplicate Removal (2026-06-25)" entry
- [ ] `sruth/oideachais/STATUS.md` — strike through any reference to `sruth/oideachais/routes/`, `/sensors/`, `/middleware/` (none expected, but verify)

## 7. Archive + commit + push

- [ ] `openspec archive oideachais-audit-phase-2a-remove-pure-duplicates --yes`
- [ ] `git add -A && git diff --cached --stat | grep -v "openspec/changes/.*proposal.md\|openspec/changes/.*tasks.md\|openspec/changes/.*spec.md" | head -20` to review what is being committed
- [ ] `git commit -m "refactor(oideachais): round 11 phase 2a — remove 4 pure-duplicate dirs (-5527 LOC)"`
- [ ] `git pull --rebase && git push` → branch up to date
- [ ] `git status` → clean (except pre-existing modifications from other in-flight work)
