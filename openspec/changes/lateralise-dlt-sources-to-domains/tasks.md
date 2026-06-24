# Tasks: lateralise-dlt-sources-to-domains

## Phase 1: Pre-migration audit

- [ ] `git grep "from oideachais.dlt_sources.uk\|import oideachais.dlt_sources.uk"` returns all sites
- [ ] `git grep "from oideachais.dlt_sources.ireland\|import oideachais.dlt_sources.ireland"` returns all sites
- [ ] `git grep "from oideachais.dlt_sources.crown_dependencies\|import oideachais.dlt_sources.crown_dependencies"` returns all sites
- [ ] `git grep "from dlt_sources.uk\|from dlt_sources.ireland\|from dlt_sources.crown_dependencies"` (relative imports)

## Phase 2: Update oideachais/AGENTS.md

- [ ] Update the "Quick routing" table (line 42-58) to point to
  `dlt_sources/domains/education/{nation}/` instead of the
  legacy paths
- [ ] Verify the table now references the 8 nation codes
  (`ie`, `en`, `sct`, `wls`, `ni`, `iom`, `jey`, `ggy`)
  instead of the 3 region codes (`uk`, `ie`, `crown_dependencies`)

## Phase 3: Move the dlt source files (git mv)

- [ ] `git mv oideachais/dlt_sources/uk/england/*.py oideachais/dlt_sources/domains/education/en/`
- [ ] `git mv oideachais/dlt_sources/uk/scotland/*.py oideachais/dlt_sources/domains/education/sct/`
- [ ] `git mv oideachais/dlt_sources/uk/wales/*.py oideachais/dlt_sources/domains/education/wls/`
- [ ] `git mv oideachais/dlt_sources/uk/northern_ireland/*.py oideachais/dlt_sources/domains/education/ni/`
- [ ] `git mv oideachais/dlt_sources/ireland/*.py oideachais/dlt_sources/domains/education/ie/`
- [ ] `git mv oideachais/dlt_sources/crown_dependencies/channel_islands.py oideachais/dlt_sources/domains/education/jey/`
- [ ] `git mv oideachais/dlt_sources/crown_dependencies/isle_of_man.py oideachais/dlt_sources/domains/education/iom/`

## Phase 4: Add backward-compat re-exports

- [ ] Update `oideachais/dlt_sources/uk/england/__init__.py` to re-export
- [ ] Update `oideachais/dlt_sources/uk/scotland/__init__.py`
- [ ] Update `oideachais/dlt_sources/uk/wales/__init__.py`
- [ ] Update `oideachais/dlt_sources/uk/northern_ireland/__init__.py`
- [ ] Update `oideachais/dlt_sources/ireland/__init__.py`
- [ ] Update `oideachais/dlt_sources/crown_dependencies/__init__.py`

## Phase 5: Update import sites in dagster_defs/

- [ ] `oideachais/dagster_defs/assets/uk_education_assets.py`
- [ ] `oideachais/dagster_defs/assets/ie/education/*.py` (5 files)
- [ ] `oideachais/dagster_defs/assets/wire_unwired_dlt_sources.py` (C4.1)
- [ ] `oideachais/dagster_defs/assets/author_archive_assets.py` (if any)
- [ ] `oideachais/dagster_defs/definitions.py`
- [ ] `oideachais/dagster_defs/asset_checks.py`
- [ ] `oideachais/dagster_defs/factories.py` (if any)
- [ ] `oideachais/dagster_defs/resources.py` (if any)
- [ ] `oideachais/cognee_integration/author_archive_cognify.py` (if any)

## Phase 6: Update STATUS.md and REFACTORING.md

- [ ] Add a "Layout migration" section to `oideachais/STATUS.md`
- [ ] Add a "Legacy dlt source shim removal" entry to
  `oideachais/REFACTORING.md` (1 release timeline)

## Phase 7: Validation

- [ ] `openspec validate lateralise-dlt-sources-to-domains --strict` passes
- [ ] `uv run --package oideachais python -c "import dagster_defs.definitions"` still loads
- [ ] All 38 dlt source files are accessible from the new canonical location
- [ ] All 6 legacy `__init__.py` shims work for backward compat

## Phase 8: Land the plane

- [ ] Stage the moves + new files + modified docs
- [ ] Commit: `git commit -m "lateralise-dlt-sources-to-domains: move 38 dlt sources to canonical {nation}/{domain} layout"`
- [ ] `git pull --rebase`
- [ ] `git push origin q3-2026-oideachais-consolidation`
