# Tasks: Round 11 Phase 5 — Delete pre-split `canuint.py` + `duchas_images.py` duplicates from meaisínfhoghlaim

## Pre-flight

- [x] Confirmed `sruth/meaisinfhoghlaim/language/gaeilge/canuint.py` (1,041 lines) contains all 5 canuint source functions (`canuint_source` + `canuint_search_source` + `canuint_audio_source` + `canuint_dialect_summary_source` + `canuint_word_alignment_source`) — pre-split duplicate of canonical split (1,095 lines across 5 files)
- [x] Confirmed `sruth/meaisinfhoghlaim/language/gaeilge/duchas_images.py` (787 lines) contains both `duchas_images_source` + `hidden_heritages_source` — pre-split duplicate of canonical split (445 lines across 2 files)
- [x] Confirmed byte-level near-identity of all 7 source functions: total 278-byte diff (0.6%) across 45,274 bytes; differences are decorator-only (`@dlt.source(name="canuint_pronunciation")` on top-level function)
- [x] Confirmed 0 active importers of either file across `sruth/` (verified via `grep -rn "language\.gaeilge\.canuint\|language\.gaeilge\.duchas_images" sruth/ --include="*.py"`)
- [x] Confirmed `sruth/meaisinfhoghlaim/quality/canuint_validator.py` does NOT depend on `language/gaeilge/canuint.py` (only imports `get_logger` from `sruth.oideachais.observability.logging`)
- [x] Confirmed canonical split files all import cleanly via `PYTHONPATH=./sruth python3 -c "from ... import ..."` for all 7 source functions
- [x] Confirmed `sruth/meaisinfhoghlaim/language/gaeilge/__init__.py` is empty (0 bytes) — no re-exports to update
- [x] Confirmed `irish_samples.yaml` (the 3rd file in `language/gaeilge/`) is NOT a duplicate (real Irish-language reference data, 7,795 bytes)

## Implementation

- [ ] Create openspec change directory `openspec/changes/meaisinfhoghlaim-audit-phase-5-delete-pre-split-canuint-and-duchas-images-duplicates/`
- [ ] Write `proposal.md` (done)
- [ ] Write `tasks.md` (this file)
- [ ] Write `specs/meaisinfhoghlaim-platform/spec.md` delta with 1 ADDED Requirement (no-pre-split-multisource-duplicates-in-meaisínfhoghlaim)
- [ ] Run `openspec validate meaisinfhoghlaim-audit-phase-5-delete-pre-split-canuint-and-duchas-images-duplicates --strict` (must pass before commit)
- [ ] Move (git mv) `sruth/meaisinfhoghlaim/language/gaeilge/canuint.py` to archive directory `openspec/changes/meaisinfhoghlaim-audit-phase-5-delete-pre-split-canuint-and-duchas-images-duplicates/archive/sruth/meaisinfhoghlaim/language/gaeilge/canuint.py`
- [ ] Move (git mv) `sruth/meaisinfhoghlaim/language/gaeilge/duchas_images.py` to archive directory `openspec/changes/meaisinfhoghlaim-audit-phase-5-delete-pre-split-canuint-and-duchas-images-duplicates/archive/sruth/meaisinfhoghlaim/language/gaeilge/duchas_images.py`
- [ ] Update `sruth/meaisinfhoghlaim/README.md` "Known issues" table — add 1 RESOLVED row: pre-split canuint.py + duchas_images.py duplicates (1828 lines)
- [ ] Verify post-state: `ls sruth/meaisinfhoghlaim/language/gaeilge/` returns `__init__.py` + `irish_samples.yaml` only
- [ ] Verify post-state: `PYTHONPATH=./sruth ./.venv/bin/python -c "from sruth.oideachais.dlt_sources.ie.culture.canuint import canuint_source"` returns OK (canonical still works)
- [ ] Verify post-state: `PYTHONPATH=./sruth ./.venv/bin/python -c "from sruth.oideachais.dlt_sources.ie.culture.duchas_images import duchas_images_source"` returns OK
- [ ] Run `mise run lint:skills` (123/123 pass)

## Commit + push

- [ ] Stage only files for this phase: 2 archive moves (git mv) + 1 README.md update
- [ ] **Do NOT stage**: pre-existing in-flight work in `.agents/skills/`, `.infisical.env`, `infrastructure/AGENTS.md`, ROOT `pyproject.toml`, `sruth/oideachais/notebooks/dashboards/education/all_nations.py`, `sruth/oideachais/celtic/duchas.py`, `sruth/oideachais/subjects/subjects/*`, `spaces/data-engineering`, `infrastructure/komodo/*`, `infrastructure/stacks/monitoring/*`, `openspec/changes/add-open{chamber,claw}-*`, `infrastructure/stacks/open{chamber,claw}/`
- [ ] Commit 1: `refactor(meaisinfhoghlaim): round 11 phase 5 — delete pre-split canuint + duchas_images duplicates`
- [ ] Push to `q3-2026-oideachais-consolidation`
- [ ] Run `openspec archive meaisinfhoghlaim-audit-phase-5-delete-pre-split-canuint-and-duchas-images-duplicates --yes`
- [ ] Commit 2: `docs(openspec): apply Phase 5 spec delta to meaisinfhoghlaim-platform`
- [ ] Push to `q3-2026-oideachais-consolidation`
- [ ] Verify `git status` shows "up to date with origin"

## Post-archive

- [ ] Verify `openspec/specs/meaisinfhoghlaim-platform/spec.md` contains 1 new ADDED Requirement (no-pre-split-multisource-duplicates)
- [ ] Verify `openspec/changes/meaisinfhoghlaim-audit-phase-5-delete-pre-split-canuint-and-duchas-images-duplicates/` no longer in `openspec list` output
- [ ] Round 11 status: 15 openspec changes archived (10 oideachais + 5 meaisinfhoghlaim)
