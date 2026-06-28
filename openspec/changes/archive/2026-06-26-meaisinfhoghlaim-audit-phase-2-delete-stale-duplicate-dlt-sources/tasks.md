# Tasks: meaisinfhoghlaim-audit-phase-2-delete-stale-duplicate-dlt-sources

## Phase 1: Verify the 4 files have NO active importers

- [ ] `grep -rn "meaisinfhoghlaim.language.gaeilge" sruth/ --include="*.py" --exclude-dir=.venv --exclude-dir=__pycache__` returns 0 hits
- [ ] `grep -rn "from \.gaeilge\." sruth/meaisinfhoghlaim/ --include="*.py" --exclude-dir=__pycache__` returns 0 hits
- [ ] Confirm via file inspection that each of the 4 files has a TRUE duplicate canonical home (same `@dlt.source` decorator + same line signatures)

## Phase 2: Delete 4 stale duplicate DLT source files

- [ ] `git rm sruth/meaisinfhoghlaim/language/gaeilge/duchas.py` (374 lines)
- [ ] `git rm sruth/meaisinfhoghlaim/language/gaeilge/tearma.py` (485 lines)
- [ ] `git rm sruth/meaisinfhoghlaim/language/gaeilge/gaois.py` (551 lines)
- [ ] `git rm sruth/meaisinfhoghlaim/language/gaeilge/universal_dependencies.py` (377 lines)
- [ ] Verify: `ls sruth/meaisinfhoghlaim/language/gaeilge/` shows only `__init__.py`, `canuint.py`, `duchas_images.py`, `irish_samples.yaml` (4 files remain)
- [ ] Verify: `git diff --stat HEAD~1..HEAD` shows 4 deletions, 0 modifications, 1787 lines removed total

## Phase 3: Update README.md Known issues table

- [ ] In `sruth/meaisinfhoghlaim/README.md`, append a new row #10 to the "Known issues" table (after row 9 from Phase 1):
      `| 10 | 4 stale duplicate DLT source files in language/gaeilge/ (duchas.py + tearma.py + gaois.py + universal_dependencies.py, 1787 lines total). All are TRUE byte-for-byte duplicates of canonical homes at sruth/oideachais/dlt_sources/ie/{culture,education}/; zero active importers. Deleted. | language/gaeilge/ | RESOLVED (round 11 audit) |`

## Phase 4: Validate + archive

- [ ] `openspec validate meaisinfhoghlaim-audit-phase-2-delete-stale-duplicate-dlt-sources --strict` → PASS
- [ ] Commit + push the 4 deletes + README update
- [ ] `openspec archive meaisinfhoghlaim-audit-phase-2-delete-stale-duplicate-dlt-sources --yes` → auto-applies spec delta
- [ ] Commit + push the auto-applied spec delta
