# Tasks — Round 11 Phase 3C

## 1. Inventory

- [x] Inventory legacy flat-tree files
- [x] Classify single-source vs multi-source
- [x] Map single-source files to canonical paths

## 2. Create openspec change

- [x] Create `openspec/changes/oideachais-audit-phase-3c-migrate-legacy-single-sources/`
- [x] Write `proposal.md`
- [x] Write `tasks.md`
- [ ] Write spec delta at `specs/oideachais-pipeline/spec.md`
- [ ] `openspec validate oideachais-audit-phase-3c-migrate-legacy-single-sources --strict`

## 3. Move IE education single-source files

- [ ] `git mv dlt_sources/ireland/aistear.py dlt_sources/ie/education/aistear.py`
- [ ] `git mv dlt_sources/ireland/curriculum_source.py dlt_sources/ie/education/curriculum_source.py`
- [ ] `git mv dlt_sources/ireland/junior_cycle.py dlt_sources/ie/education/junior_cycle.py`
- [ ] `git mv dlt_sources/ireland/leaving_cert.py dlt_sources/ie/education/leaving_cert.py`
- [ ] `git mv dlt_sources/ireland/ncca.py dlt_sources/ie/education/ncca.py`
- [ ] `git mv dlt_sources/ireland/primary.py dlt_sources/ie/education/primary.py`
- [ ] `git mv dlt_sources/ireland/senior_cycle.py dlt_sources/ie/education/senior_cycle.py`
- [ ] `git mv dlt_sources/ireland/tertiary.py dlt_sources/ie/education/tertiary.py`
- [ ] `git mv dlt_sources/ireland/sec_aural_transcripts.py dlt_sources/ie/education/sec_aural_transcripts.py`
- [ ] `git mv dlt_sources/ireland/edcolearning.py dlt_sources/ie/education/edcolearning.py`

## 4. Move UK education single-source files

- [ ] `git mv dlt_sources/uk/england/ofsted.py dlt_sources/en/education/ofsted.py`
- [ ] `git mv dlt_sources/uk/england/school_info.py dlt_sources/en/education/school_info.py`
- [ ] `git mv dlt_sources/uk/northern_ireland/education_ni.py dlt_sources/ni/education/education_ni.py`
- [ ] `git mv dlt_sources/uk/northern_ireland/etini.py dlt_sources/ni/education/etini.py`
- [ ] `git mv dlt_sources/uk/scotland/insight_benchmarking.py dlt_sources/sct/education/insight_benchmarking.py`

## 5. Move UK statistics single-source files

- [ ] `git mv dlt_sources/uk/england/dfe_explore_statistics.py dlt_sources/en/statistics/dfe_explore_statistics.py`
- [ ] `git mv dlt_sources/uk/northern_ireland/nisra.py dlt_sources/ni/statistics/nisra.py`
- [ ] `git mv dlt_sources/uk/scotland/gov_scot_statistics.py dlt_sources/sct/statistics/gov_scot_statistics.py`
- [ ] `git mv dlt_sources/uk/scotland/simd.py dlt_sources/sct/statistics/simd.py`
- [ ] `git mv dlt_sources/uk/wales/statswales.py dlt_sources/wls/statistics/statswales.py`
- [ ] `git mv dlt_sources/uk/wales/estyn.py dlt_sources/wls/education/estyn.py`

## 6. Move Celtic single-source files

- [ ] `git mv dlt_sources/celtic/duchas.py dlt_sources/ie/culture/duchas.py`
- [ ] `git mv dlt_sources/celtic/universal_dependencies.py dlt_sources/ie/education/universal_dependencies.py`

## 7. Move shared utilities to dlt_sources/common/

- [ ] `git mv dlt_sources/ireland/source_adapters.py dlt_sources/common/source_adapters.py`
- [ ] `git mv dlt_sources/ireland/curriculum_registry.py dlt_sources/common/curriculum_registry.py`
- [ ] `git mv dlt_sources/ireland/content_deduplication.py dlt_sources/common/content_deduplication.py`
- [ ] `git mv dlt_sources/ireland/json_seed.py dlt_sources/ie/education/json_seed.py`
- [ ] `git mv dlt_sources/ireland/parallel_corpus.py dlt_sources/ie/education/parallel_corpus.py`
- [ ] `git mv dlt_sources/ireland/exam_source_update.py dlt_sources/ie/education/exam_source_update.py`

## 8. Move Ireland subjects/ sub-package

- [ ] `git mv dlt_sources/ireland/subjects/ dlt_sources/ie/education/subjects/`

## 9. Update all importers

- [ ] Update intra-legacy-tree imports in remaining `dlt_sources/ireland/*.py` files (e.g. `curriculum_registry.py` imports `source_adapters.py` from same dir → update to `dlt_sources.common.source_adapters`)
- [ ] Update `dlt_sources/ireland/__init__.py` re-exports
- [ ] Update Dagster asset imports in `dagster_defs/assets/{ie,en,ni,sct,wls}/education/`
- [ ] Update test imports in `tests/dlt_sources/`, `tests/test_*.py`
- [ ] Update `dlt_utils/source_factory.py`
- [ ] Update any other importers

## 10. Validate

- [ ] `python3 -m compileall` all moved .py files: all OK
- [ ] `mise run lint:skills`: 123/123 pass
- [ ] 8-router spot-check: imports succeed
- [ ] No remaining `from .ireland.X`, `from .uk.X`, or `from .celtic.X` references in moved-or-updated files

## 11. Commit + push

- [ ] `git add -A`
- [ ] `git commit` with detailed message
- [ ] `git push`

## 12. Archive openspec

- [ ] `openspec archive oideachais-audit-phase-3c-migrate-legacy-single-sources --yes`
- [ ] Update `REFACTORING.md` with Phase 3C entry
- [ ] Update `STATUS.md` if any references moved
- [ ] Commit + push docs