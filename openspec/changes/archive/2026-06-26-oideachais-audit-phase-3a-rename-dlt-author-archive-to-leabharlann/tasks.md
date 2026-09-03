# Tasks

## 1. Pre-flight
- [x] Confirm all `from dlt_sources.author_archive` importers are in test files only (no production code imports this path).
- [x] Confirm no Dagster asset key changes needed (asset keys are `oideachais_author_archive` which stays).
- [x] Confirm no doc-breaking changes outside the dlt_sources path.

## 2. Rename
- [ ] `git mv sruth/oideachais/dlt_sources/author_archive sruth/oideachais/dlt_sources/leabharlann`
- [ ] Verify 10 .py files + 1 config.example.yaml + 1 __init__.py moved.

## 3. Update importers
- [ ] `sruth/oideachais/tests/test_leabharlann_pipeline.py` — replace 12 occurrences of `dlt_sources.author_archive` with `dlt_sources.leabharlann`.
- [ ] `sruth/oideachais/tests/test_author_archive_pipeline.py` — replace 2 occurrences of `dlt_sources.author_archive`.
- [ ] Grep verify: 0 remaining `dlt_sources.author_archive` references.

## 4. Update docs
- [ ] `sruth/oideachais/STATUS.md` — update directory references.
- [ ] `sruth/oideachais/cocoindex_flows/README.md` — update directory references.
- [ ] `openspec/specs/oideachais-pipeline/spec.md` — update directory references.

## 5. Validate
- [ ] `openspec validate oideachais-audit-phase-3a-rename-dlt-author-archive-to-leabharlann --strict` passes.
- [ ] `python -c "from dlt_sources.leabharlann import zotero_source, leabharlann_books_source, takeout_v1_source"` succeeds.
- [ ] `mise run lint:skills` still 123/123.

## 6. Commit + push
- [ ] `git add -A openspec/changes/oideachais-audit-phase-3a-rename-dlt-author-archive-to-leabharlann/ sruth/oideachais/dlt_sources/leabharlann/ sruth/oideachais/tests/test_leabharlann_pipeline.py sruth/oideachais/tests/test_author_archive_pipeline.py sruth/oideachais/STATUS.md sruth/oideachais/cocoindex_flows/README.md openspec/specs/oideachais-pipeline/spec.md`
- [ ] `git commit -m "refactor(oideachais): round 11 phase 3a — rename dlt_sources/author_archive → leabharlann"`
- [ ] `git pull --rebase && git push`
