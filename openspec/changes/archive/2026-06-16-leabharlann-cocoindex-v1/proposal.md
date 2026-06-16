# Leabharlann Lakehouse + CocoIndex v1 Migration

> **Supersedes** [`author-archive-gemini-and-uos-ingestion`](../author-archive-gemini-and-uos-ingestion/proposal.md). The previous change is preserved as a historical record; its functionality is replaced by this change's `leabharlann-ingestion` + `cocoindex-v1-migration` specs.

## Why

Three forces are converging on the `oideachais/` data platform:

1. **Directory relocation.** The user has reorganised the personal archives. The old paths under `author_cian_deacy_lyons_mac_an_déisigh_uí_liatháin/{university_of_galway,gemini_deep_research}/` no longer exist; the new home is `leabharlann/`. The previous `author-archive-gemini-and-uos-ingestion` change's `DEFAULT_UOG_PATH` / `DEFAULT_GEMINI_PATH` constants point at deleted directories, and a v0-cocoindex dependency now blocks every existing flow from loading.

2. **New content types.** The new `leabharlann/` tree includes:
   - `ollscoil_na_gaillimhe/` (2.2 GB, the renamed university archive)
   - `gemini_deep_research/` (79 MB, the renamed Gemini archive)
   - `zotero/` (**117 PDFs in real Zotero storage format** — arXiv IDs, `__dup0` duplicate markers, `_.pdf` empty placeholder; many HTR / Irish-LM / OCR papers)
   - `gaeilge/` (40 PDFs + 2 MDs + 37 PNGs in `previews/`)
   - `aigne/` (7 psychology / mental-health books)
   - `stedding/Takeout/` (**sample googletakeout: 64 .docx + 1 .csv** under `Drive/`, no `<account>/` prefix)

3. **CocoIndex v0 is dead.** The venv has `cocoindex==1.0.9` (v1 API). All 8 modules in `oideachais/cocoindex_flows/` use the removed v0 DSL (`@cocoindex.flow_def`, `FlowBuilder`, `DataScope`, `cocoindex.sources.DuckDB`, `cocoindex.targets.lancedb`, `cocoindex.functions.SplitRecursively`, `cocoindex.functions.SentenceTransformerEmbed`). The `.agents/skills/cocoindex/SKILL.md` and the canonical `docs/cocoindex/` examples are all v1. The v0 code is broken at import time.

## What Changes

### 1. CocoIndex v0 → v1 migration (`oideachais/cocoindex_flows/`)

- **Migrate** the 8 v0 files to v1 idioms, following the canonical patterns from `docs/cocoindex/{pdf_embedding,code_embedding_lancedb,paper_metadata,multi_format_indexing,live_updates}/main.py`:
  - `curriculum_embedding.py` (v1) — `@coco.fn` + `@coco.lifespan` + `localfs.walk_dir` + `RecursiveSplitter` + `LanceDB` target
  - `curriculum_translation.py` (v1) — BAML via `instructor.from_litellm(acompletion, mode=instructor.Mode.JSON)` (mirrors `paper_metadata/main.py:122`)
  - `geospatial_indexing.py` (v1) — GeoParquet target via fsspec
  - `learning_outcome_graph.py` (v1) — SurrealDB / Neo4j target stub
  - `ocr_embedding.py` (v1) — Pylaia back-end + VLM rerank
  - `research_embedding.py` (v1) — live filesystem source for `leabharlann/`
  - `author_archive_embedding.py` (v1) — refactor of the v0 module just added
- **Add** 3 new v1 Apps:
  - `leabharlann_books_embedding.py` — books source (PDF + DOCX + EPUB + MD)
  - `leabharlann_zotero_embedding.py` — Zotero PDFs with BAML metadata extraction
  - `leabharlann_takeout_embedding.py` — Takeout filesystem (Phase 1)
- Each v1 App exposes: `query_once` and `query` async helpers for ad-hoc semantic search (mirrors `docs/cocoindex/pdf_embedding/main.py:162`).
- Each embedder is a `coco.ContextKey[SentenceTransformerEmbedder]("embedder", detect_change=True)` so a model swap auto-re-embeds.
- Each source uses `localfs.walk_dir(sourcedir, recursive=True, path_matcher=PatternFilePathMatcher(...), live=True)`.
- Each target uses `await lancedb.mount_table_target(LANCE_DB, table_name=..., table_schema=lancedb.TableSchema.from_class(MyRecord, primary_key=["id"]))`.
- IDs use `IdGenerator()` + `await id_gen.next_id(chunk.text)` for stability across re-runs.
- The expensive file-level processing function is `@coco.fn(memo=True)` so unchanged files are skipped.
- **One shared LMDB state path** (`storage/cocoindex/oideachais.ldb`) configured via `COCOINDEX_DB` env var, per your answer 8.

### 2. New dlt sources (`oideachais/dlt_sources/author_archive/`)

- **Add** `leabharlann_books.py` — `@dlt.source name="leabharlann_books"`, one source with subject partition key (`gaeilge` | `aigne` | `epub` | `md`).
- **Add** `zotero.py` — `@dlt.source name="leabharlann_zotero"`, scans `leabharlann/zotero/`, dedupes via SHA-256 (handles `__dup0` and `_(N)` duplicate suffixes), regex-extracts arXiv IDs / authors / year from filenames.
- **Add** `takeout_v1.py` — `@dlt.source name="leabharlann_takeout"` (filesystem Phase 1), auto-discovers:
  - `stedding/Takeout/` (no account prefix → `account_label_fallback = "stedding_takeout"`)
  - `stedding/Takeout/<account>/` (multi-account, per the existing `google_takeout.py` pattern)
  - `~/Downloads/takeout-*.zip` (new zips; not extracted — just registered for unzip+ingest follow-up)
- **Add** `_epub_extractor.py` — `ebooklib`-based chapter-by-chapter text extraction. The library is added to `oideachais/pyproject.toml` as an optional dep with graceful degradation.
- **Add** `previews.py` — small pure-function helper that pairs `<book>.pdf` with `<book>_preview.png` in a sibling `previews/` directory and returns the matched preview path (per your answer 2, the PNG is recorded as a column, not indexed as a separate document).
- **Update** the 3 existing sources' `DEFAULT_*_PATH` constants to point at `leabharlann/` (preserving the existing source factories for back-compat).
- **Update** `_scanner.PathGrammar` to add `.epub` to `file_type_extensions["epub"]` and add a `EPUB_HANDLING = "optional"` knob (so `_epub_extractor` is a try-import).

### 3. BAML schema extension (`baml_src/author_archive.baml`)

- **Add** `ZoteroPaper` (paper_kind, arxiv_id, doi, title, authors, year, abstract, venue, irish_relevant, htr_relevant, confidence) + `Author` + `PaperKind` enum.
- **Add** `ExtractZoteroMetadata(pdf_text, file_name, arxiv_id) -> ZoteroPaper` (English-only via the existing `ExtractEn` client).
- **Skip** TSV parser per your answer 1 (the `*.tsv` in `leabharlann/zotero/` is not parsed — metadata comes from BAML + filename regex).
- **Regenerate** the BAML client with `baml-cli generate`.

### 4. Dagster asset group (`oideachais/dagster_defs/assets/leabharlann_assets.py`)

7 new assets, `group_name="leabharlann_ingestion"`:

| Asset | Partition def | Compute kind | Deps |
|:--|:--|:--|:--|
| `leabharlann_books_raw` | `leabharlann_books_subjects` (DynamicPartitions) | dlt | — |
| `leabharlann_zotero_raw` | `leabharlann_zotero_batches` (StaticPartitions × 5, ~24 papers each) | dlt | — |
| `leabharlann_takeout_v1_raw` | `leabharlann_takeout_accounts` (DynamicPartitions) | dlt | — |
| `leabharlann_paper_metadata` | none | baml | `leabharlann_zotero_raw` |
| `leabharlann_cocoindex_books_update` | none | embedding | `leabharlann_books_raw`, `leabharlann_paper_metadata` |
| `leabharlann_cocoindex_zotero_update` | none | embedding | `leabharlann_zotero_raw`, `leabharlann_paper_metadata` |
| `leabharlann_cocoindex_takeout_update` | none | embedding | `leabharlann_takeout_v1_raw` |

The 3 CocoIndex-update assets invoke each v1 App as `subprocess.run(["cocoindex", "update", "..."], ...)` (the canonical v1 invocation pattern, matching `docs/cocoindex/AGENTS.md`) **or** import + call `app.update_blocking(live=True)` if cocoindex is importable in the worker.

### 5. Sensor (`oideachais/dagster_defs/sensors/leabharlann_sensors.py`)

- `leabharlann_directory_sensor` polls every 60 s for new/modified files in:
  - `leabharlann/{gaeilge,aigne}/` (any subdir)
  - `leabharlann/zotero/` (top level)
  - `stedding/Takeout/` and `stedding/Takeout/<account>/` (any subdir)
  - `~/Downloads/takeout-*.zip` (new zips)

### 6. Tests (`oideachais/tests/test_leabharlann_pipeline.py`)

~15 new tests covering:
- Each new dlt source (filesystem scan against the real `leabharlann/` directories)
- `_epub_extractor` graceful degradation when `ebooklib` is not installed
- `takeout_v1` auto-discovery with and without account prefix
- BAML `ZoteroPaper` schema imports + arxiv_id extraction
- CocoIndex v1 App loadability (each App's `app_main` is callable)
- The 7 Dagster assets (import + group_name)
- The sensor (60s poll emits a RunRequest on mtime change)

### 7. `oideachais/pyproject.toml`

- Add `ebooklib` as an optional dep (graceful when missing).
- Confirm `cocoindex>=1.0.0` is the version pin (already true in the venv).

### 8. OpenSpec housekeeping

- Add the previous change's "Supersedes" note at the top of this `proposal.md` (already done).
- Add a "Superseded by" note to the previous change's `proposal.md` (in a separate edit, no file deletion).

## Impact

| Surface | Before | After |
|:--|:--|:--|
| `oideachais/cocoindex_flows/` modules | 8 (all v0, broken on import) | 11 (all v1, working) |
| CocoIndex App count | 0 (no `@coco.App` anywhere) | 11 (one per module) |
| `oideachais/dlt_sources/author_archive/` modules | 7 | 11 (+ `leabharlann_books`, `zotero`, `takeout_v1`, `_epub_extractor`, `previews`) |
| BAML functions | 33 | 34 (+ `ExtractZoteroMetadata`) |
| Dagster asset groups | 15 | 16 (+ `leabharlann_ingestion`) |
| Dagster assets | 7 (author-archive) + others | 7 (author-archive) + 7 (leabharlann) |
| Test files | 25 | 26 (+ `test_leabharlann_pipeline.py`) |
| BAML `.baml` files | 9 | 9 (same file, appended) |
| PyPI package name | `cianfhoghlaim-oideachais` (unchanged) | (unchanged) |

## Out of scope

- Phase 2 of the takeout source (OAuth / Drive API / Gmail export) — still deferred.
- `croilar/cocoindex_flows/{cv_embedding,artwork_embedding}.py` v0→v1 migration — same package family but separate `dg.toml` code location. Becomes a follow-up change.
- Bilingual BAML (`*_ga` fields) — still English-only.
- Public web exposure.
- The previous `author-archive-gemini-and-uos-ingestion` change stays in `openspec/changes/` (not deleted) as a historical record.

## Cross-references

- CocoIndex v1 patterns: `docs/cocoindex/{pdf_embedding,code_embedding_lancedb,paper_metadata,multi_format_indexing,live_updates}/main.py`
- CocoIndex v1 skill: `.agents/skills/cocoindex/SKILL.md`
- Lakehouse destination: `oideachais/dlt_utils/destinations.py:118`
- Existing author-archive dlt source: `oideachais/dlt_sources/author_archive/{_scanner,gemini_deep_research,university_of_galway,google_takeout}.py`
- Existing author-archive BAML: `baml_src/author_archive.baml`
- Previous change (superseded): `openspec/changes/author-archive-gemini-and-uos-ingestion/`
- Related capability spec: `openspec/specs/author-archive-filesystem/spec.md` (will be MODIFIED to point at the new paths)
