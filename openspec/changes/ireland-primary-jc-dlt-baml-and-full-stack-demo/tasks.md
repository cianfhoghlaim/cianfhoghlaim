# Tasks — Ireland Primary + JC DLT/BAML Loop & Leabharlann Full-Stack Demo

## Phase 0 — OpenSpec (week 0)

- [ ] 1. Create `openspec/changes/ireland-primary-jc-dlt-baml-and-full-stack-demo/{proposal.md, tasks.md, specs/}` with 3 spec deltas.
- [ ] 2. Add the new capability `ireland-primary-jc-dlt-baml` to `openspec/AGENTS.md` and `openspec/project.md` (Education Platform section).
- [ ] 3. Add the new capability `leabharlann-full-stack-demo` to `openspec/AGENTS.md` and `openspec/project.md`.
- [ ] 4. Validate: `openspec validate ireland-primary-jc-dlt-baml-and-full-stack-demo --strict`.

## Phase 1 — Ireland primary + JC dlt sources (week 1)

- [ ] 5. Create `oideachais/dlt_sources/ireland/primary.py` — 4 dlt resources, hash-based incremental.
- [ ] 6. Create `oideachais/dlt_sources/ireland/junior_cycle.py` — 3 dlt resources, hash-based incremental.
- [ ] 7. Update `oideachais/dlt_sources/ireland/__init__.py` to re-export the new `primary_source()` and `junior_cycle_source()` factories.
- [ ] 8. Add 2 Dagster assets to `oideachais/dagster_defs/assets/ie/education/curriculum_dlt_assets.py` (or new file): `ireland_primary_raw` + `ireland_junior_cycle_raw` with their partition definitions.
- [ ] 9. Register the 2 new assets in `oideachais/dagster_defs/definitions.py`.

## Phase 2 — Wire `b.ExtractZoteroMetadata` into `zotero.py` (week 1-2)

- [ ] 10. Add a 4th resource `arxiv_papers_baml` to `oideachais/dlt_sources/author_archive/zotero.py` that invokes `b.ExtractZoteroMetadata(pdf_text, file_name, arxiv_id)` for each arXiv paper. Graceful degradation when the BAML client is not generated.
- [ ] 11. Verify the existing `leabharlann_paper_metadata` Dagster asset picks up the new resource.

## Phase 3 — Leabharlann full-stack demo (week 2)

- [ ] 12. Create `oideachais/dagster_defs/assets/leabharlann_demo_assets.py` with the `oideachais_cocoindex_leabharlann_full_stack_demo` asset.
- [ ] 13. Add 4 asset checks (`pdf_extraction_status`, `baml_extraction_status`, `cocoindex_chunks_count > 10`, `lance_table_size_bytes > 1000`).
- [ ] 14. Register the new asset + checks in `definitions.py`.
- [ ] 15. Create `oideachais/notebooks/leabharlann_full_stack_demo.py` Marimo notebook with the 5-step pipeline UI.
- [ ] 16. Register the new Marimo app in `oideachais/marimo/__init__.py` (or equivalent).

## Phase 4 — Tests (week 2-3)

- [ ] 17. Add `oideachais/tests/test_ireland_primary_jc_pipeline.py` with tests for:
  - `primary_source()` yields 4 resources with correct primary key.
  - `junior_cycle_source()` yields 3 resources with correct primary key.
  - `ireland_primary_raw` and `ireland_junior_cycle_raw` Dagster assets import with the right group_name.
  - `zotero_source.arxiv_papers_baml` resource is iterable and memoised by `(file_hash, baml_function_name)`.
- [ ] 18. Add `oideachais/tests/test_leabharlann_full_stack_demo.py` with tests for:
  - The demo asset declares its sample PDF paths.
  - The asset checks fire correctly.
  - The Marimo notebook file is parseable.
- [ ] 19. Run `uv run pytest oideachais/tests/test_ireland_primary_jc_pipeline.py oideachais/tests/test_leabharlann_full_stack_demo.py -q`; all tests pass.
- [ ] 20. Re-validate: `openspec validate ireland-primary-jc-dlt-baml-and-full-stack-demo --strict`.

## Phase 5 — Commit + push + archive (week 3)

- [ ] 21. Git: `git pull --rebase`, `git add -A`, `git commit -m "feat(oideachais): primary+JC dlt + BAML + leabharlann full-stack demo"`, `git push`.
- [ ] 22. Run `openspec archive ireland-primary-jc-dlt-baml-and-full-stack-demo --yes` to move the change to `archive/`.

## Total: 22 tasks, ~3 weeks.
