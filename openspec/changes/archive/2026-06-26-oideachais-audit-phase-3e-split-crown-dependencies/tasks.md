# Phase 3E Tasks

## 1. Write the openspec change docs
- [x] `proposal.md` — written
- [ ] `tasks.md` — this file
- [ ] `specs/oideachais-pipeline/spec.md` — spec delta

## 2. Split `crown_dependencies/channel_islands.py`
- [ ] Read full `crown_dependencies/channel_islands.py` to extract `jersey_source` + `guernsey_source` + shared helpers
- [ ] Create `jey/education/channel_islands.py` with `jersey_source`
- [ ] Create `ggy/education/channel_islands.py` with `guernsey_source`
- [ ] Create `jey/education/_channel_islands_helpers.py` with shared helpers (`_crawl_jersey_education` if shared)
- [ ] Create `ggy/education/_channel_islands_helpers.py` (or symlink via import) with shared helpers (`_crawl_guernsey_education` if shared)
- [ ] Update both new files to import helpers from sibling `_channel_islands_helpers.py`

## 3. Move `crown_dependencies/isle_of_man.py` → `iom/education/isle_of_man.py`
- [ ] Read full `crown_dependencies/isle_of_man.py` to extract `isle_of_man_source`
- [ ] Create `iom/education/isle_of_man.py` with `isle_of_man_source`
- [ ] Update file header docstring to reference new canonical path

## 4. Break the circular import in 3 per-nation shims
- [ ] Update `iom/education/__init__.py` to `from dlt_sources.iom.education.isle_of_man import isle_of_man_source`
- [ ] Update `jey/education/__init__.py` to `from dlt_sources.jey.education.channel_islands import jersey_source`
- [ ] Update `ggy/education/__init__.py` to `from dlt_sources.ggy.education.channel_islands import guernsey_source`

## 5. Rewire consumers
- [ ] Find all consumers of `dlt_sources.crown_dependencies` and rewrite to canonical paths
- [ ] Update `dagster_defs/assets/uk_education_assets.py` (the only known production consumer)
- [ ] Update `tests/dlt_sources/domains/uk/test_crown_deps.py` if it imports from the legacy path

## 6. Delete the umbrella
- [ ] `git rm` `dlt_sources/crown_dependencies/__init__.py`
- [ ] `git rm` `dlt_sources/crown_dependencies/channel_islands.py`
- [ ] `git rm` `dlt_sources/crown_dependencies/isle_of_man.py`
- [ ] `git rm -rf` `dlt_sources/crown_dependencies/__pycache__/` (untracked cache)

## 7. Validation
- [ ] `openspec validate oideachais-audit-phase-3e-split-crown-dependencies --strict` PASS
- [ ] All 3 new per-nation imports succeed: `from oideachais.dlt_sources.{iom,jey,ggy}/education.{isle_of_man,channel_islands} import {isle_of_man,jersey,guernsey}_source`
- [ ] All 3 per-nation `__init__.py` shims work without circular import: `from dlt_sources.{iom,jey,ggy}.education import {isle_of_man,jersey,guernsey}_source`
- [ ] No remaining references to `crown_dependencies` in production code (grep)
- [ ] `python3 -m compileall` all new + modified .py files: OK
- [ ] Run `tests/dlt_sources/domains/uk/test_crown_deps.py`: PASS

## 8. Documentation + commit + push + archive
- [ ] Add Phase 3E entry to `sruth/oideachais/REFACTORING.md`
- [ ] Commit + push
- [ ] `openspec archive oideachais-audit-phase-3e-split-crown-dependencies --yes`