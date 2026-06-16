# Tasks — Author Archive Gemini + University of Galway Ingestion

## Phase 0 — OpenSpec and capability registration (week 0)

- [ ] 1. Create `openspec/changes/author-archive-gemini-and-uos-ingestion/{proposal.md, tasks.md, specs/}` with the 5 spec deltas.
- [ ] 2. Add the new capability `author-archive-filesystem` to the `Personal Portfolio (croilar)` section of `openspec/AGENTS.md` and `openspec/project.md`.
- [ ] 3. Add the new capability `google-takeout-ingestion` to the `Personal Portfolio (croilar)` section of `openspec/AGENTS.md` and `openspec/project.md`.
- [ ] 4. Add the new capability `author-archive-baml-extraction` to the `Education Platform` section of `openspec/AGENTS.md` and `openspec/project.md`.
- [ ] 5. Add the new capability `author-archive-ocr-htr` to the `Education Platform` section of `openspec/AGENTS.md` and `openspec/project.md`.
- [ ] 6. Validate the change: `openspec validate author-archive-gemini-and-uos-ingestion --strict`.

## Phase 1 — BAML schema (week 1)

- [ ] 7. Create `baml_src/author_archive.baml` with `GeminiDeepResearchReport`, `UniversityOfGalwayArtifact`, `HandwrittenEquation`, `CitedUrl`, the 5 enums (`GeminiDomain`, `UoGArtifactKind`, `UoGStage`, `UoGLanguage`, `EquationConfidence`), and the 3 functions (`ExtractGeminiReport`, `ExtractUoGArtifact`, `ExtractHandwrittenEquations`).
- [ ] 8. Extend `baml_src/generators.baml` to register the `extract_en` client alias (English-only, points at `litellm/gemini-2.0-flash`).
- [ ] 9. Extend `baml_src/clients.baml` to declare the `extract_en` client and a `extract_en_strong` fallback (e.g. `litellm/anthropic/claude-sonnet-4-20250514`).
- [ ] 10. Run `mise run baml:generate` (or `uv run baml-cli generate`) to regenerate the Python and TypeScript clients under `baml_client/`.
- [ ] 11. Add BAML tests in `baml_src/author_archive.baml` (`test ExtractGeminiReportTest`, `test ExtractUoGArtifactTest`, `test ExtractHandwrittenEquationsTest`).
- [ ] 12. Run `mise run baml:test` (or `uv run baml-cli test`); ensure existing tests still pass.

## Phase 2 — dlt source package (week 1-2)

- [ ] 13. Create `oideachais/dlt_sources/author_archive/__init__.py` exporting the public API.
- [ ] 14. Create `oideachais/dlt_sources/author_archive/_scanner.py` — refactor of `bunchloch/filesystem_source.py:1` and `ireland/local_documents.py:1` into a generic scanner. Functions: `compute_file_hash`, `get_file_type`, `extract_course_code`, `detect_subject` (parameterised by `path_grammar`), `should_skip_file`, `get_document_metadata`, `scan_directory`, `FileHashTracker` (hoisted from `local_documents.py:420` with a re-export shim at the old path).
- [ ] 15. Add the re-export shim in `oideachais/dlt_sources/ireland/local_documents.py` (top-of-file `from oideachais.dlt_sources.author_archive._scanner import FileHashTracker  # noqa: F401`) so the existing call-sites keep working.
- [ ] 16. Create `oideachais/dlt_sources/author_archive/_takeout_paths.py` — `TakeoutAccountConfig` dataclass, `load_takeout_accounts(path: str | Path | None = None) -> list[TakeoutAccountConfig]` that reads YAML.
- [ ] 17. Create `oideachais/dlt_sources/author_archive/_citation_extractor.py` — `extract_citations(pdf_path: Path) -> list[CitedUrl]` using PyMuPDF link annotations + first-page header regex (`/^#\s+(.+)/m`).
- [ ] 18. Create `oideachais/dlt_sources/author_archive/university_of_galway.py` — `@dlt.source name="author_archive_uog"` with the 6 resources, partition columns `account` (constant `"university_of_galway"`), `domain` (top-level subdir), and `course_code` when extractable.
- [ ] 19. Create `oideachais/dlt_sources/author_archive/gemini_deep_research.py` — `@dlt.source name="author_archive_gemini"` with the 6 resources, partition columns `account` (constant `"gemini_deep_research"`), `domain` (one of `culture | law | medical | politics | technology | other | identity`), and a `gemini_citations` column for the scraped inline-citation list.
- [ ] 20. Create `oideachais/dlt_sources/author_archive/google_takeout.py` — `@dlt.source name="author_archive_takeout"` with `takeout_index` + `takeout_documents` resources (filesystem-only Phase 1). Phase 2 hooks (`_oauth.py`, `_download.py`) stubbed with `NotImplementedError` and TODO comments.
- [ ] 21. Add an `author_archive_accounts.yaml` template at `oideachais/dlt_sources/author_archive/config.example.yaml` (gitignored; lives at repo root when populated).

## Phase 3 — CocoIndex flow (week 2)

- [ ] 22. Create `oideachais/cocoindex_flows/author_archive_embedding.py` mirroring `research_embedding.py:125`. Constants: `EN_MODEL = "BAAI/bge-large-en-v1.5"`, `EMBEDDING_DIM = 1024`, `GEMINI_TABLE = "author_archive_gemini"`, `UOG_TABLE = "author_archive_uog_documents"`, `UOG_CODE_TABLE = "author_archive_uog_code"`, `UOG_EQN_TABLE = "author_archive_equations"`. Four `@cocoindex.flow(name=…)` definitions; one `@query_handler` named `search_author_archive`.
- [ ] 23. Update `oideachais/cocoindex_flows/__init__.py` to re-export the new flow + handler.
- [ ] 24. Run a one-shot `uv run cocoindex update author_archive_embedding` (against DuckDB fallback) to verify the flow compiles.

## Phase 4 — OCR module (week 2-3)

- [ ] 25. Create `oideachais/ocr/author_archive_ocr.py` with `AuthorArchiveOCRConfig` (per-language back-end selection), `AuthorArchiveOCRRunner` (Pylaia for `ga`/mixed; TrOCR for `en`/printed; VLM for equations), and `run_ocr_for_page(path, page_index) -> dict` returning `{text, latex, confidence}`.
- [ ] 26. Wire a no-op fallback when the back-end model isn't on the workstation (graceful degradation: `text = ""` and `requires_ocr = true`).

## Phase 5 — Dagster assets + sensor (week 3)

- [ ] 27. Create `oideachais/dagster_defs/assets/author_archive_assets.py` with the 7 assets. Define `author_archive_uog_subdirs`, `author_archive_gemini_domains`, `author_archive_accounts` as `DynamicPartitionsDefinition`.
- [ ] 28. Create `oideachais/dagster_defs/sensors/author_archive_sensors.py` with `author_archive_directory_sensor` that scans the three target roots every 60 s and emits a `RunRequest` for the affected partition when mtime changes.
- [ ] 29. Register the new assets and sensor in `oideachais/dagster_defs/definitions.py` (extend the existing `assets` and `sensors` lists).

## Phase 6 — Test + archive (week 3-4)

- [ ] 30. Create `oideachais/tests/test_author_archive_pipeline.py` with the 4 scenarios from the spec deltas (filesystem scan, BAML extraction, OCR chain, CocoIndex embed).
- [ ] 31. Run `uv run pytest oideachais/tests/test_author_archive_pipeline.py -q` from the repo root; all tests pass.
- [ ] 32. Run `uv run dagster dev -m dagster_defs.definitions` locally and verify the 7 new assets appear in the asset catalog.
- [ ] 33. Re-validate the change: `openspec validate author-archive-gemini-and-uos-ingestion --strict`.
- [ ] 34. Git: `git pull --rebase`, `git add -A`, `git commit -m "feat(author-archive): gemini deep research + UoG ingestion pipeline"`, `git push`, verify `git status` shows "up to date with origin".
- [ ] 35. Run `openspec archive author-archive-gemini-and-uos-ingestion --yes` to move the change to `archive/`.

## Total: 35 tasks, 4 weeks
