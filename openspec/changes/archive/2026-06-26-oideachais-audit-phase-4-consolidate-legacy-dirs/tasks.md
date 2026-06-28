# Phase 4 tasks

## 1. Specs

- [x] 1.1 Update `openspec/specs/oideachais-pipeline/spec.md` with the
      "Legacy Flat Files Consolidated at Canonical Paths" Requirement
      (4 Scenarios: tearma split, utility modules moved to common/,
      dlthub_projects moved to dlt_utils/, importers rewired)

## 2. tearma split (per Phase 3D pattern)

- [ ] 2.1 Read full `dlt_sources/tearma.py` to identify the exact
      function bodies of `tearma_source`, `tearma_search_source`, and
      all shared helpers
- [ ] 2.2 Create `dlt_sources/ie/culture/tearma.py` (exports
      `tearma_source`)
- [ ] 2.3 Create `dlt_sources/ie/culture/tearma_search.py` (exports
      `tearma_search_source`)
- [ ] 2.4 Create `dlt_sources/ie/culture/_tearma_helpers.py` (shared
      private state + module constants + `_get_tearma_factory` +
      `_parse_tearma_tsv` + `_download_tearma_export` +
      `_search_tearma_api` + `_load_tearma_terms` + `TerminologyLinker`)
- [ ] 2.5 Update `dlt_sources/ie/culture/__init__.py` to re-export
      `tearma_source` + `tearma_search_source` from the new locations
- [ ] 2.6 Verify `from dlt_sources.ie.culture.tearma import tearma_source` works
- [ ] 2.7 Verify `from dlt_sources.ie.culture.tearma_search import tearma_search_source` works

## 3. Utility files → `common/`

- [ ] 3.1 `git mv dlt_sources/crawl_utils.py dlt_sources/common/crawl_utils.py`
- [ ] 3.2 `git mv dlt_sources/http_client.py dlt_sources/common/http_client.py`
- [ ] 3.3 `git mv dlt_sources/pagination.py dlt_sources/common/pagination.py`
- [ ] 3.4 Verify all 3 modules import correctly from `dlt_sources.common.{name}`

## 4. Pipeline config → `dlt_utils/`

- [ ] 4.1 `git mv dlt_sources/dlthub_projects.py dlt_utils/dlthub_projects.py`
- [ ] 4.2 Update `dlt_utils/__init__.py` to re-export `apply_dlthub_wrappers`
- [ ] 4.3 Verify `from dlt_utils.dlthub_projects import apply_dlthub_wrappers` works

## 5. Importer rewires

- [ ] 5.1 Update `dlt_sources/ie/education/curriculum.py:600`
      `from dlt_sources.dlthub_projects import apply_dlthub_wrappers`
      → `from dlt_utils.dlthub_projects import apply_dlthub_wrappers`
- [ ] 5.2 Update `dlt_sources/ie/education/curriculum_source.py:600`
      → `from dlt_utils.dlthub_projects import apply_dlthub_wrappers`
- [ ] 5.3 Update `dlt_sources/ie/education/exam_source_update.py:2`
      → `from dlt_utils.dlthub_projects import apply_dlthub_wrappers`
- [ ] 5.4 Update `dlt_sources/dagster_defs/factories.py:325`
      `source_module="data_platform.dlt_sources.tearma"`
      → `source_module="data_platform.dlt_sources.ie.culture.tearma"`
- [ ] 5.5 Update `dlt_sources/tests/dlt_sources/test_integration.py`
      (6 imports: lines 100, 111, 123, 135, 148, 168)
      `from oideachais.dlt_sources.crawl_utils import …`
      → `from dlt_sources.common.crawl_utils import …`
      (Note: also fixes the absolute-namespace violation as a side
      benefit, but the test file's brokenness is out-of-scope)

## 6. Validation

- [ ] 6.1 `openspec validate oideachais-audit-phase-4-consolidate-legacy-dirs --strict` MUST pass
- [ ] 6.2 All 31 canonical imports verified (25 Phase 3D + 3 Phase 3E + 3 Phase 4)
- [ ] 6.3 `mise run lint:skills` → 138/138 pass
- [ ] 6.4 Pre-existing test failures in
      `tests/dlt_sources/domains/uk/test_crown_deps.py` (medicine + law
      asset modules) — still skipped (out of scope)

## 7. REFACTORING.md + commit + push + archive

- [ ] 7.1 Add Phase 4 entry to `sruth/oideachais/REFACTORING.md`
- [ ] 7.2 Stage ONLY the Phase 4 files (carefully avoid in-flight
      modifications: `.agents/skills/*.md`, `.infisical.env`,
      `infrastructure/AGENTS.md`, `pyproject.toml`,
      `sruth/oideachais/notebooks/dashboards/education/all_nations.py`,
      `sruth/oideachais/celtic/duchas.py`,
      `sruth/oideachais/subjects/subjects/*`)
- [ ] 7.3 Single atomic commit + push
- [ ] 7.4 `openspec archive oideachais-audit-phase-4-consolidate-legacy-dirs --yes`
- [ ] 7.5 Commit + push the spec delta auto-applied by the archive step
