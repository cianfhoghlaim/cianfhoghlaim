# Tasks — Leabharlann Lakehouse + CocoIndex v1 Migration

## Phase 0 — OpenSpec and capability registration (week 0)

- [ ] 1. Create `openspec/changes/leabharlann-cocoindex-v1/{proposal.md, tasks.md, specs/}` with the 4 spec deltas.
- [ ] 2. Add the new capability `cocoindex-v1-migration` to `openspec/AGENTS.md` and `openspec/project.md` (Education Platform section).
- [ ] 3. Add the new capability `leabharlann-ingestion` to `openspec/AGENTS.md` and `openspec/project.md` (Education Platform section).
- [ ] 4. Annotate `openspec/changes/author-archive-gemini-and-uos-ingestion/proposal.md` with a "Superseded by" header pointing to the new change id.
- [ ] 5. Validate the change: `openspec validate leabharlann-cocoindex-v1 --strict`.

## Phase 1 — CocoIndex v0 → v1 migration of `oideachais/cocoindex_flows/` (week 1-2)

- [ ] 6. Migrate `curriculum_embedding.py` from v0 (`@cocoindex.flow_def`, `FlowBuilder`, `DataScope`) to v1 (`@coco.fn`, `@coco.lifespan`, `coco.App`, `localfs.walk_dir`, `RecursiveSplitter`, `LanceDB` target). Pattern: `docs/cocoindex/pdf_embedding/main.py:1`.
- [ ] 7. Migrate `curriculum_translation.py` to v1. Use `instructor.from_litellm(acompletion, mode=instructor.Mode.JSON)` for BAML calls. Pattern: `docs/cocoindex/paper_metadata/main.py:122`.
- [ ] 8. Migrate `geospatial_indexing.py` to v1. GeoParquet target via fsspec.
- [ ] 9. Migrate `learning_outcome_graph.py` to v1. SurrealDB / Neo4j target stub.
- [ ] 10. Migrate `ocr_embedding.py` to v1. Pylaia back-end + VLM rerank.
- [ ] 11. Migrate `research_embedding.py` to v1. Live filesystem source. Pattern: `docs/cocoindex/code_embedding_lancedb/main.py:1`.
- [ ] 12. Migrate `author_archive_embedding.py` to v1 (refactor of the v0 module just added).
- [ ] 13. Add `leabharlann_books_embedding.py` (v1). Pattern: `pdf_embedding/main.py` + `multi_format_indexing/main.py`.
- [ ] 14. Add `leabharlann_zotero_embedding.py` (v1). BAML `ExtractZoteroMetadata` + abstract chunks. Pattern: `paper_metadata/main.py:1`.
- [ ] 15. Add `leabharlann_takeout_embedding.py` (v1). Filesystem only. Pattern: `pdf_embedding/main.py:1`.
- [ ] 16. Update `oideachais/cocoindex_flows/__init__.py` to re-export the 11 v1 Apps + their `query` helpers.
- [ ] 17. Add `.env.example` (gitignored) documenting `COCOINDEX_DB=storage/cocoindex/oideachais.ldb`, `LANCEDB_URI`, and the `EMBED_MODEL` env var.
- [ ] 18. Run `baml-cli generate` (no schema changes in this phase; confirms client is current).

## Phase 2 — dlt sources for `leabharlann/` (week 2)

- [ ] 19. Update `_scanner.PathGrammar` to add `.epub` to `file_type_extensions["epub"]` and add an `EPUB_HANDLING` knob.
- [ ] 20. Add `_epub_extractor.py` (try-import `ebooklib`, graceful degradation). Re-uses the same pymupdf-style return-shape contract.
- [ ] 21. Add `previews.py` helper that pairs `<book>.pdf` with `<book>_preview.png`.
- [ ] 22. Add `leabharlann_books.py` (one source, subject partition key, 6 resources, EPUB support).
- [ ] 23. Add `zotero.py` (SHA-256 dedup, arxiv-ID regex, `_dup0` and `_(N)` suffix handling).
- [ ] 24. Add `takeout_v1.py` (auto-discovers `stedding/Takeout/`, `stedding/Takeout/<account>/`, `~/Downloads/takeout-*.zip`).
- [ ] 25. Update the 3 existing sources' `DEFAULT_*_PATH` constants to point at `leabharlann/`.
- [ ] 26. Update `oideachais/dlt_sources/author_archive/__init__.py` to re-export the new symbols.
- [ ] 27. Update `oideachais/pyproject.toml` to add `ebooklib` as an optional dep.

## Phase 3 — BAML `ZoteroPaper` schema (week 2-3)

- [ ] 28. Append `ZoteroPaper`, `Author`, `PaperKind` enum, and `ExtractZoteroMetadata` function to `baml_src/author_archive.baml`.
- [ ] 29. Run `baml-cli generate` to regenerate the Python and TypeScript clients.
- [ ] 30. Run `baml-cli check` (zero errors expected).

## Phase 4 — Dagster assets + sensor (week 3)

- [ ] 31. Add `oideachais/dagster_defs/assets/leabharlann_assets.py` with the 7 assets and 3 partition definitions.
- [ ] 32. Add `oideachais/dagster_defs/sensors/leabharlann_sensors.py` with `leabharlann_directory_sensor` (60s poll).
- [ ] 33. Register the new assets and sensor in `oideachais/dagster_defs/definitions.py`.
- [ ] 34. Register the sensor in `oideachais/dagster_defs/sensors/__init__.py`.

## Phase 5 — Test + commit (week 3-4)

- [ ] 35. Create `oideachais/tests/test_leabharlann_pipeline.py` with the 15 tests enumerated in the proposal.
- [ ] 36. Run `uv run pytest oideachais/tests/test_leabharlann_pipeline.py -q` from the repo root; all tests pass.
- [ ] 37. Run `uv run dagster dev -m dagster_defs.definitions` locally and verify the 7 new assets appear in the asset catalog.
- [ ] 38. Re-validate: `openspec validate leabharlann-cocoindex-v1 --strict`.
- [ ] 39. Git: `git pull --rebase`, `git add -A`, `git commit -m "feat(leabharlann): v1 cocoindex + zotero/books/takeout sources"`, `git push`.
- [ ] 40. Run `openspec archive leabharlann-cocoindex-v1 --yes` to move the change to `archive/`.

## Total: 40 tasks, 4 weeks
