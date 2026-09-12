## 1. Highest priority — silent data-loss bug (do first, independent of everything else)

- [ ] 1.1 Fix `cocoindex_flows/european_nations_cross/law_embedding.py`'s `SOURCE_DIR = pathlib.Path("dlt/european_nations")` to point at the correct post-v7 path (`dlt_sources/european_nations`); verify by confirming the glob under the corrected path returns non-empty results for at least one known-present source file

## 2. Resume any in-flight renames (do not duplicate)

- [ ] 2.1 For each in-flight rename change tracked in `openspec/changes/`, confirm its task list conforms to this change's naming-law spec; resume execution there rather than here

## 3. `official_media/` duplicate-directory cleanup

- [ ] 3.1 For each of the 6 old-flat directories (`sct`, `wls`, `ggy`, `iom`, `jsy`, `companies_house`), grep the codebase for imports of the old path; produce a per-directory "imported: yes/no" table
- [ ] 3.2 Delete each confirmed-dead old directory, or add a dated `LEGACY_ALIASES.md` entry (per Requirement "Deprecation shims declare an expiry date") for each still-imported one; verify `dlt_sources/official_media/` contains no directory present in both old-flat and new-grouped form

## 4. BIEP/BIIEP/BIE spelling unification

- [ ] 4.1 Rename the file containing the literal `biiep_ocr_ensemble` (verify exact path via `rg -l "biiep_ocr_ensemble"`); verify all importers are updated and tests still pass
- [ ] 4.2 Add the lint rule for `\\bbiiep\\b`/`\\bbie-` outside `openspec/changes/archive/`; verify it fails on a deliberately-introduced test occurrence and passes once removed

## 5. Sibling-sprawl nesting (3+ threshold, per this change's spec)

- [ ] 5.1 Nest `crypteolas_*` siblings under `crypteolas/` if 3+ exist; verify import paths updated and tests pass
- [ ] 5.2 Nest `media_*` siblings under `media/` if 3+ exist; verify import paths updated and tests pass
- [ ] 5.3 Resolve `artwork`, `labels`, `portfolio` — nest under `cv/` or a new `portfolio/` parent (decide during execution); verify no remaining references to the retired path

## 6. `pipeline_name=` normalisation

- [ ] 6.1 Locate and rename the pipeline literally named `foo` (`rg -n 'pipeline_name\\s*=\\s*"foo"'`); verify the rename follows the `<domain>_<source>_pipeline` template
- [ ] 6.2 Merge duplicate `pipeline_name=` pairs into one function; verify no remaining reference to the retired name

## 7. Shim expiry policy

- [ ] 7.1 Add `expires: YYYY-MM-DD` to all current shim entries across `dlt_sources/LEGACY_ALIASES.md` and `cocoindex_flows/LEGACY_ALIASES.md`, dated retroactively from each shim's introducing change (+90 days); verify every entry has the field
- [ ] 7.2 Add the `mise run lint:expired-shims` gate; verify it fails against a deliberately-backdated test entry

## 8. Lower priority — scripts/ triage and test renaming (opportunistic)

- [ ] 8.1 Triage the flat `scripts/` directory into `scripts/{sync,lint,ops,cognee,migrations}/`; verify `mise run` tasks referencing script paths still resolve
- [ ] 8.2 Rename `tests/test_phase{2,7,11..22}_*.py` by behaviour instead of session phase, opportunistically when next touching each file; verify test collection still finds the renamed file

## 9. Verification

- [x] 9.1 Run `openspec validate pipeline-naming-taxonomy --strict`; verify it passes (verified 2026-09-12)
- [ ] 9.2 Run `openspec status pipeline-naming-taxonomy`; verify all 4 artifacts report done