# Author Archive — Gemini Deep Research + University of Galway Ingestion

> **Superseded by** [`leabharlann-cocoindex-v1`](../leabharlann-cocoindex-v1/proposal.md). This change is preserved as a historical record of the v0 attempt. The functionality is replaced by the new change's `leabharlann-ingestion` + `cocoindex-v1-migration` specs. The previous paths under `author_cian_deacy_lyons_mac_an_déisigh_uí_liatháin/{university_of_galway,gemini_deep_research}/` no longer exist; the new home is `leabharlann/`.

## Why

Two rich personal archives sit on the workstation and are not yet wired into the existing `oideachais/` data platform:

1. **`author_cian_deacy_lyons_mac_an_déisigh_uí_liatháin/gemini_deep_research/`** — 78 MB, ~110 PDF reports across 7 domains (culture, law, medical, politics, technology, other, plus a duplicated `damages_estimates_tax_plannings.pdf`). All produced by Gemini's Deep Research feature (`README.md:1-24`) via agentic multi-step prompting. Rich in inline citations and topical clusters (royal family, Irish identity, dual citizenship, British–Irish relations, medical access, disability rights).

2. **`author_cian_deacy_lyons_mac_an_déisigh_uí_liatháin/university_of_galway/`** — 2.2 GB across 5 sub-directories (`education`, `irish`, `mata`, `past`, `software_development`). Mix of `.pdf`, `.docx`, `.pages`, `.pptx`, `.xlsx`, `.doc`. Course-code-bearing files match the regex `([A-Z]{2,3})(\d{3,4})` already used by `oideachais/dlt_sources/bunchloch/filesystem_source.py:62`. Many handwritten math equations in the `mata/` and `past/` folders and several Apple `.pages` files.

A third source will be needed in the near future: **Google Takeout archives** from one or more Gemini-Google accounts. The user will provide the Takeout `.zip`s later, so this change ships the filesystem-only Phase 1 of the takeout source; Phase 2 (OAuth + Drive API + Gmail export) is documented as out of scope and added as a follow-up.

The existing `croilar-cv-extraction` capability spec (`openspec/specs/croilar-cv-extraction/spec.md:1`) covers `achievement/`, `teaching/`, `identity/`, and `vetting/` from the same `author_cian_deacy_lyons…` tree but **does not** cover `gemini_deep_research/`, `university_of_galway/`, or `google_takeout/`. The `croilar-data-engineering` capability (`openspec/specs/croilar-data-engineering/spec.md:1`) provides the architectural pattern (Dagster + DLT + CocoIndex + BAML) but the implementation has not reached these three directories.

The existing oideachais data platform has all the building blocks: `bunchloch_source` for filesystem ingestion, `local_documents.py` for hash-based incremental + extraction, `research_embedding.py` for CocoIndex embeddings, `dagster_defs/assets/research_assets.py` for the Dagster asset group, and `oideachais/ocr/` for the handwritten content pipeline. **What is missing is the new `author_archive` namespace that ties them together for these three specific archive types.**

## What Changes

### 1. New dlt source package

- **Add** `oideachais/dlt_sources/author_archive/` with:
  - `_scanner.py` — refactor of the bunchloch scanner into a generic, path-parameterised, multi-account module. Re-uses the existing `FileHashTracker` from `oideachais/dlt_sources/ireland/local_documents.py:420` (hoisted into the new package as `oideachais.dlt_sources.author_archive._scanner.FileHashTracker`; the old import path continues to work via a re-export shim).
  - `_takeout_paths.py` — `TakeoutAccountConfig` dataclass (per-account label + takeout root + default domain), `TakeoutAccounts` loader that reads `author_archive_accounts.yaml` from the repo root or `os.environ["AUTHOR_ARCHIVE_ACCOUNTS_PATH"]`.
  - `_citation_extractor.py` — PyMuPDF-based inline-citation scraper for Gemini's deep-research PDFs; yields `(text, cited_url)` tuples; tolerant of PDFs without citations.
  - `university_of_galway.py` — `@dlt.source name="author_archive_uog"`.
  - `gemini_deep_research.py` — `@dlt.source name="author_archive_gemini"`.
  - `google_takeout.py` — `@dlt.source name="author_archive_takeout"` (Phase 1: filesystem only; Phase 2 stub).
- Each source yields six resources: `all_documents`, `pdf_documents`, `word_documents`, `code_documents`, `handwritten_pages`, `extraction_metadata`. The `extraction_metadata` resource is memoised by `(file_hash, baml_function_name)`.
- All write to DuckLake via `oideachais/dlt_utils/destinations.py:118` (`get_dlt_destination()`). Partition columns: `account`, `domain`. `primary_key=["file_hash"]`, `write_disposition="merge"`.

### 2. New BAML schema

- **Add** `baml_src/author_archive.baml` with 4 classes and 3 functions:
  - `GeminiDeepResearchReport` (topic, domain enum, summary, key_findings, cited_urls, gemini_account, research_date) + `ExtractGeminiReport(pdf_text: string, file_name: string) -> GeminiDeepResearchReport`.
  - `UniversityOfGalwayArtifact` (artifact_kind enum, course_code, module_title, stage enum, language enum, key_topics, requires_handwriting_ocr) + `ExtractUoGArtifact(pdf_text: string, file_name: string, file_type: string) -> UniversityOfGalwayArtifact`.
  - `HandwrittenEquation` (latex, verbatim, context, confidence) + `ExtractHandwrittenEquations(ocr_text: string, file_name: string) -> HandwrittenEquation[]`.
- **Wire** the new functions into `baml_src/generators.baml` under the `extract_en` client alias (English-only).
- **Regenerate** the client: `mise run baml:generate` (or `uv run baml-cli generate`).

### 3. New CocoIndex flow

- **Add** `oideachais/cocoindex_flows/author_archive_embedding.py` mirroring `oideachais/cocoindex_flows/research_embedding.py:125`:
  - Embedding model: `BAAI/bge-large-en-v1.5` (English-tuned, 1024-d, same dimension as BGE-M3 for LanceDB HNSW parity).
  - 4 source collectors: `author_archive_gemini`, `author_archive_uog_documents`, `author_archive_uog_code` (CodeBERT), `author_archive_equations`.
  - 4 LanceDB tables, all with IVF_HNSW + FTS indexes, written to `LANCEDB_URI` from `research_embedding.py:31`.
  - 1 `@query_handler` named `search_author_archive(query, account=None, domain=None, artifact_kind=None, course_code=None, limit=10)`.
- **Export** the new symbols from `oideachais/cocoindex_flows/__init__.py`.

### 4. New Dagster asset group

- **Add** `oideachais/dagster_defs/assets/author_archive_assets.py` with 7 `@asset`s, group `author_archive_ingestion`:
  - `author_archive_university_of_galway_raw` (Dagster `DynamicPartitionsDefinition(name="author_archive_uog_subdirs")`).
  - `author_archive_gemini_deep_research_raw` (DynamicPartitions `author_archive_gemini_domains`).
  - `author_archive_takeout_raw` (DynamicPartitions `author_archive_accounts`).
  - `author_archive_handwriting_ocr` (depends on the three raw assets; runs the OCR chain from `oideachais/ocr/author_archive_ocr.py`).
  - `author_archive_baml_extraction` (depends on the three raw assets; calls BAML functions).
  - `author_archive_documents_embeddings` (depends on the five above; runs the CocoIndex flow).
  - `author_archive_equations_index` (depends on `author_archive_handwriting_ocr`; indexes equations).
- **Add** `oideachais/dagster_defs/sensors/author_archive_sensors.py` — directory-watcher sensor that emits `RunRequest`s on mtime change.
- **Register** the new assets in `oideachais/dagster_defs/definitions.py`.

### 5. New OCR module

- **Add** `oideachais/ocr/author_archive_ocr.py` with `AuthorArchiveOCRConfig`, `AuthorArchiveOCRRunner` and `run_ocr_for_page(path, page_index) -> dict` that selects the back-end (Pylaia for Irish HTR, TrOCR for Latin handwriting, VLM for equations) based on the file's path grammar. Re-uses `oideachais/ocr/pylaia_comparison.py` and `oideachais/ocr/irish_processing.py`.

### 6. Specs & secrets

- New openspec change `author-archive-gemini-and-uos-ingestion` with 5 capability spec deltas (this PR):
  - `author-archive-filesystem` (filesystem ingestion for UoG + Gemini directories).
  - `google-takeout-ingestion` (Phase 1 filesystem only; Phase 2 out of scope).
  - `author-archive-baml-extraction` (the 4 BAML schemas + 3 functions).
  - `author-archive-ocr-htr` (the handwriting pipeline).
  - `semantic-search` (MODIFIED — adding the new query handler).
- `.infisical.env` gain 3 new optional keys for Phase 2: `GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET`, `GOOGLE_OAUTH_REDIRECT_URI` — written to the vault via `bun run secrets:init`. **Not required for this change; documented as a follow-up.**

### 7. Test

- **Add** `oideachais/tests/test_author_archive_pipeline.py` (pytest) that:
  - runs `_scanner.scan_directory()` against the real `university_of_galway/` and `gemini_deep_research/` paths in `test` mode (DuckDB fallback destination, `max_files=20`);
  - asserts `file_hash` primary key + `account` and `domain` partition columns are populated;
  - calls the BAML extraction with a 3-document subset and asserts a structured dict is returned;
  - runs the CocoIndex flow with a 5-chunk subset and asserts LanceDB row count > 0.

## Impact

| Surface | Before | After |
|:--|:--|:--|
| `oideachais/dlt_sources/author_archive/` | (absent) | 5 modules (`__init__`, `_scanner`, `_takeout_paths`, `_citation_extractor`, `university_of_galway`, `gemini_deep_research`, `google_takeout`) |
| `baml_src/author_archive.baml` | (absent) | 4 classes, 3 functions, 5 enums |
| `oideachais/cocoindex_flows/author_archive_embedding.py` | (absent) | 4 collectors, 1 query handler, IVF_HNSW + FTS indexes |
| `oideachais/dagster_defs/assets/author_archive_assets.py` | (absent) | 7 assets, 3 DynamicPartitions |
| `oideachais/dagster_defs/sensors/author_archive_sensors.py` | (absent) | 1 FsEvent-based sensor |
| `oideachais/ocr/author_archive_ocr.py` | (absent) | Pylaia + TrOCR + VLM back-ends |
| DLT sources (count) | 16 | 19 |
| Dagster asset groups | 14 | 15 (`author_archive_ingestion`) |
| BAML functions | 30+ | 33 |
| CocoIndex flows | 8 | 9 |
| LanceDB tables | 8+ | 12+ |
| Test files | 24+ | 25 |

## Out of scope

- Phase 2 of `google_takeout.py` (OAuth + Drive API + Gmail export) — deferred until the user provides the Takeout zips.
- GPG-at-rest encryption for `identity/`, `vetting/`, `disability/`, `catharnacht/` (the `croilar-cv-extraction` pattern is documented but not extended here; the new `author_archive` source exposes a `gpg_encrypt_paths: list[Path]` config knob for opt-in use).
- Public web exposure (TanStack Start routes, CopilotKit runtime) — `oideachais` stays a back-end data platform; the `oideachais` Dagster UI is the only operator surface.
- Cross-archive knowledge graph (Cognee/Graphiti/Memgraph) — would consume the BAML-extracted `CrossArchiveTheme` later but is a separate change.
- Bilingual BAML output (`*_ga` fields) — user requested English-only for now.
- `oideachais` and `croilar` workspace reorganisation — assets register in the existing `oideachais` code location; no `dg.toml` change.

## Cross-references

- Pattern precedents:
  - `oideachais/dlt_sources/bunchloch/filesystem_source.py:1` (filesystem source)
  - `oideachais/dlt_sources/ireland/local_documents.py:1` (extraction)
  - `oideachais/cocoindex_flows/research_embedding.py:125` (embedding flow)
  - `oideachais/dagster_defs/assets/research_assets.py:1` (asset group)
  - `oideachais/dagster_defs/assets/embedding_assets.py:1` (embedding assets)
  - `oideachais/dlt_utils/destinations.py:118` (DuckLake factory)
  - `oideachais/ocr/pylaia_comparison.py:1` (OCR back-end)
  - `oideachais/agents/baml_integration.py:1` (BAML adapter)
- Related capability specs:
  - `openspec/specs/croilar-cv-extraction/spec.md:1` (closest analogue — also targets `author_cian_deacy_lyons…` tree)
  - `openspec/specs/oideachais-pipeline/spec.md:1` (canonical architecture)
  - `openspec/specs/curriculum-ingestion/spec.md:1` (ingestion pattern)
  - `openspec/specs/semantic-search/spec.md:1` (LanceDB query handlers)
  - `openspec/specs/knowledge-graph/spec.md:1` (future cross-archive KG)
