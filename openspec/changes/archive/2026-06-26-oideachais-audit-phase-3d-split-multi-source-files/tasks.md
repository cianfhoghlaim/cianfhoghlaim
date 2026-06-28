# Tasks — Round 11 Phase 3D

## 1. Create openspec change

- [x] Create `openspec/changes/oideachais-audit-phase-3d-split-multi-source-files/`
- [x] Write `proposal.md`
- [x] Write `tasks.md`
- [ ] Write spec delta at `specs/oideachais-pipeline/spec.md`
- [ ] `openspec validate oideachais-audit-phase-3d-split-multi-source-files --strict`

## 2. Build a Python splitter utility

The splitter reads each multi-source file, identifies `@dlt.source` function blocks, extracts shared helpers (non-`@dlt.source` functions + module constants), and writes:
- One file per `@dlt.source` function (with its nested `@dlt.resource` functions)
- A `_helpers.py` file with shared helpers (if any)

## 3. Split IE multi-source files

- [ ] `ireland/oide.py` → 4 files in `ie/education/` + `_oide_helpers.py`
- [ ] `ireland/examinations.py` → 6 files in `ie/education/` + `_examinations_helpers.py`
- [ ] `ireland/local_documents.py` → 2 files in `ie/culture/`
- [ ] `ireland/agentic_discovery.py` → 2 files in `ie/education/`
- [ ] `ireland/pdf_downloader.py` → 2 files in `ie/education/`

## 4. Split UK multi-source files

- [ ] `uk/england/national_curriculum.py` → 5 files in `en/education/`
- [ ] `uk/northern_ireland/ccea_curriculum.py` → 3 files in `ni/education/`
- [ ] `uk/scotland/curriculum_for_excellence.py` → 3 files in `sct/education/`
- [ ] `uk/wales/curriculum_for_wales.py` → 3 files in `wls/education/`

## 5. Split Celtic multi-source files

- [ ] `celtic/canuint.py` → 5 files in `ie/culture/canuint/`
- [ ] `celtic/duchas_images.py` → 2 files in `ie/culture/`
- [ ] `celtic/gaois.py` → 4 files in `ie/culture/`

## 6. Split geospatial multi-source files

- [ ] `geospatial/met_office.py` → 2 files in `ie/statistics/`
- [ ] `geospatial/cso_small_areas.py` → 3 files in `ie/statistics/`
- [ ] `geospatial/geohive.py` → 2 files in `ie/statistics/`

## 7. Split bunchloch multi-source files

- [ ] `bunchloch/filesystem_source.py` → 2 files in `cross/bunchloch/`

## 8. Update all importers

- [ ] Update `from dlt_sources.ireland.{oide,examinations,local_documents,agentic_discovery,pdf_downloader}` → canonical paths
- [ ] Update `from dlt_sources.uk.{england/national_curriculum,northern_ireland/ccea_curriculum,scotland/curriculum_for_excellence,wales/curriculum_for_wales}` → canonical paths
- [ ] Update `from dlt_sources.celtic.{canuint,duchas_images,gaois}` → canonical paths
- [ ] Update `from dlt_sources.geospatial.{met_office,cso_small_areas,geohive}` → canonical paths
- [ ] Update `from dlt_sources.bunchloch.filesystem_source` → `from dlt_sources.cross.bunchloch.filesystem`

## 9. Delete legacy multi-source files

- [ ] `git rm dlt_sources/ireland/{oide,examinations,local_documents,agentic_discovery,pdf_downloader}.py`
- [ ] `git rm dlt_sources/uk/england/national_curriculum.py` etc.
- [ ] `git rm dlt_sources/celtic/{canuint,duchas_images,gaois}.py`
- [ ] `git rm dlt_sources/geospatial/{met_office,cso_small_areas,geohive}.py`
- [ ] `git rm dlt_sources/bunchloch/filesystem_source.py`

## 10. Validate

- [ ] `python3 -m compileall` all new files: OK
- [ ] `mise run lint:skills`: 123/123 PASS
- [ ] All `@dlt.source` functions importable from canonical paths
- [ ] No remaining imports of legacy multi-source modules (excluding 3E-deferred files in `ireland/`, `uk/`, `celtic/`, `geospatial/`, `bunchloch/`)

## 11. Commit + push

- [ ] `git add -A` (excluding pre-existing modifications)
- [ ] `git commit` with detailed message
- [ ] `git push`

## 12. Archive openspec

- [ ] `openspec archive oideachais-audit-phase-3d-split-multi-source-files --yes`
- [ ] Update `REFACTORING.md` with Phase 3D entry
- [ ] Commit + push docs