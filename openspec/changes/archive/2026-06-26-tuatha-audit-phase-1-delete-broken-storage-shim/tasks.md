# Tasks: Round 11 Phase 9 (tuatha Phase 1) — Delete broken `serial_executor.py` shim + rewire `__init__.py`

## Pre-flight

- [x] Confirmed `sruth/tuatha/storage/serial_executor.py:19` imports from deleted `sruth.shared.storage` (commit `8484a6353`)
- [x] Confirmed `sruth/tuatha/storage/__init__.py:8` re-exports from the broken shim, so `sruth.tuatha.storage` is unimportable
- [x] Verified the failure: `PYTHONPATH=./sruth ./.venv/bin/python -c "from sruth.tuatha.storage import SerialDatabaseExecutor"` → `ModuleNotFoundError: No module named 'sruth.shared'`
- [x] Confirmed canonical home `sruth/oideachais/core/storage/serial_executor.py` (5,579 bytes) exists and exports the same 3 names
- [x] Verified canonical works: `PYTHONPATH=./sruth ./.venv/bin/python -c "from sruth.oideachais.core.storage.serial_executor import SerialDatabaseExecutor, get_executor, run_serial"` → OK
- [x] Confirmed 0 active importers of `sruth.tuatha.storage` (verified via `grep -rn "from sruth\.tuatha\.storage\|from sruth\.tuath\.storage" sruth/ openspec/ docs/`)
- [x] Confirmed `sruth/tuatha/storage/` is otherwise a 2-file package: `__init__.py` (320 bytes) + `serial_executor.py` (584 bytes)

## Implementation

- [ ] Create openspec change directory `openspec/changes/tuatha-audit-phase-1-delete-broken-storage-shim/`
- [ ] Write `proposal.md` (done)
- [ ] Write `tasks.md` (this file)
- [ ] Write `specs/tuatha-platform/spec.md` delta with 1 ADDED Requirement (no-broken-cross-quadrant-imports-in-tuatha)
- [ ] Run `openspec validate tuatha-audit-phase-1-delete-broken-storage-shim --strict` (must pass before commit)
- [ ] Move (git mv) `sruth/tuatha/storage/serial_executor.py` to archive directory `openspec/changes/tuatha-audit-phase-1-delete-broken-storage-shim/archive/sruth/tuatha/storage/serial_executor.py`
- [ ] Rewrite `sruth/tuatha/storage/__init__.py` to re-export from canonical `sruth.oideachais.core.storage.serial_executor`
- [ ] Update `sruth/tuatha/README.md` "Known issues" table — add 1 RESOLVED row: broken serial_executor.py shim (32 lines)
- [ ] Verify post-state: `PYTHONPATH=./sruth ./.venv/bin/python -c "from sruth.tuatha.storage import SerialDatabaseExecutor"` returns OK
- [ ] Verify post-state: `ls sruth/tuatha/storage/` returns `__init__.py` only
- [ ] Verify post-state: `PYTHONPATH=./sruth ./.venv/bin/python -c "from sruth.oideachais.core.storage.serial_executor import SerialDatabaseExecutor"` still returns OK (canonical unchanged)
- [ ] Run `mise run lint:skills` (123/123 pass)

## Commit + push

- [ ] Stage only files for this phase: 1 archive move (git mv) + 1 __init__.py rewrite + 1 README.md update
- [ ] **Do NOT stage**: pre-existing in-flight work in `.agents/skills/`, `.infisical.env`, `infrastructure/AGENTS.md`, ROOT `pyproject.toml`, `sruth/oideachais/notebooks/dashboards/education/all_nations.py`, `sruth/oideachais/celtic/duchas.py`, `sruth/oideachais/subjects/subjects/*`, `spaces/data-engineering`, `infrastructure/komodo/*`, `infrastructure/stacks/monitoring/*`, `openspec/changes/add-open{chamber,claw}-*`, `infrastructure/stacks/open{chamber,claw}/`
- [ ] Commit 1: `refactor(tuatha): round 11 phase 9 (tuatha phase 1) — delete broken storage shim`
- [ ] Push to `q3-2026-oideachais-consolidation`
- [ ] Run `openspec archive tuatha-audit-phase-1-delete-broken-storage-shim --yes`
- [ ] Commit 2: `docs(openspec): apply Phase 9 spec delta to tuatha-platform`
- [ ] Push to `q3-2026-oideachais-consolidation`
- [ ] Verify `git status` shows "up to date with origin"

## Post-archive

- [ ] Verify `openspec/changes/tuatha-audit-phase-1-delete-broken-storage-shim/` is now in `archive/` subdirectory
- [ ] Confirm spec delta is now part of `openspec/specs/tuatha-platform/spec.md`
- [ ] Add 1-line summary to `openspec/changes/README.md` Round 11 status table (if it exists)
