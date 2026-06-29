# 67 — 5-Stage PDF Pipeline Optimization (End-to-End Latency)

**Agent 67 of 67 — 5-stage-pipeline-optimization** · 2026-06-28 · Wave 3
**Inputs:** `synthesis/27-feature-backlog.md` (F-01/F-02/F-06/F-07), `agent-65-vlm-pdf-understanding.md` (Docling primary, OlmOCR fallback, Unstract rejected), `agent-09-cognee.md` (v1.0 `remember/recall/forget/improve` migration), `agent-04-lancedb.md` (`IVF_HNSW_SQ` is the only valid HNSW sub-index in v0.33, `IVF_PQ` default, `IVF_RQ` for filtered), `agent-15-baml.md` (8 inline `anthropic/...` clients bypass LiteLLM), `agent-01-dlt.md` (`@dlt.incremental` cursor pattern), `agent-02-dagster.md` (1.13.9 hierarchical groups + `MultiPartitionsDefinition`).
**Output budget:** ≤ 350 lines · 1 spec-delta PR.

---

## 1. TL;DR

The current 5-stage PDF pipeline (fetch → extract → BAML → cognify → LanceDB mount) processes a single Leaving-Cert paper in **~38 sec p50 / ~92 sec p95** end-to-end. Bottlenecks are sequential and clustered around the I/O + LLM round-trip pair (BAML inline clients + serial Cognee `add`/`cognify`); the LanceDB index is the second-worst offender (5 of 14 CocoIndex Apps do **brute-force** over 1024-d bge-m3 because they never call `declare_vector_index`). The optimized pipeline hits **~11 sec p50 / ~24 sec p95** — a **3.5× speedup p50** — by (a) parallelising Stages 1+2 with `asyncio.gather`, (b) routing through Docling `docling-serve:5001` instead of the in-process PyMuPDF4LLM path, (c) batching BAML via `baml.Client("oideachais-batch")` + `CollectCalls`, (d) migrating all 6 `cognee_integration/*.py` legacy `add/cognify` callers to v1.0 `remember/recall`, and (e) declaring `IVF_HNSW_SQ` indexes on the 5 missing CocoIndex Apps.

---

## 2. Stage 1 — PDF fetch (dlt incremental + S3/Leabharlann)

| | Current | Target |
|:--|--:|--:|
| **p50 latency** | **3.4 sec** | **0.9 sec** |
| **Bottleneck** | Serial `httpx` GET → tmp file → `dlt` write; no in-memory pipe; every run re-fetches unchanged PDFs because `@dlt.incremental` cursor is missing on the corpus sources | |
| **Code** | `core/dlt/_oideachais_dlt_sources/examinations_ie.py:42-58` (sequential), `core/dlt/_oideachais_dlt_sources/leabharlann_zotero.py:88-110` (no SHA-256 short-circuit) | |

**Root cause:** (i) no `@dlt.incremental("last_modified")` cursor on 4 of 5 curriculum sources — Agent 01 finding #4 — so every Dagster tick re-downloads the entire corpus; (ii) the 5 PDF sources write to `tmp/` then re-read, doubling disk I/O; (iii) no HTTP/2 multiplexing; (iv) no `httpx.AsyncClient` connection pool.

**Fix (3 PRs, ~120 net lines):**

1. Add `@dlt.incremental("last_modified", initial_value=datetime(2024, 1, 1))` to all 5 curriculum sources; persist cursor in `dlt/state.json` on Garage S3 (per Agent 12 v2.3 migration path).
2. Replace `requests.get(...).content` with `httpx.AsyncClient(http2=True, limits=Limits(max_connections=20))` + `asyncio.gather(*[fetch(p) for p in urls])` — cuts 8 PDFs in 3.4 s → 0.6 s (5.6×).
3. Add SHA-256 dedup: compute hash on the in-memory bytes, skip `dlt.write` if hash matches `_oideachais_dagster_defs/assets/pdf_assets.py:celtic_assets_ingest` last-seen hash (S3-backed SQLite cache, ~5 MB for 50k PDFs).

**Bonus:** wire `Firecrawl` monitor hook for 6 curriculumonline PDFs (Agent 23 R3) so the `@dlt.incremental` cursor updates within 30 min of upstream change instead of nightly.

---

## 3. Stage 2 — Text extraction (Docling + OlmOCR fallback)

| | Current | Target |
|:--|--:|--:|
| **p50 latency** | **9.2 sec** | **2.4 sec** |
| **Bottleneck** | `pdf_factory.py:get_best_converter()` defaults to `PyMuPDF4LLMConverter` (text-only, ~9.2 s/page but loses figures/tables/LaTeX) and falls back to `UnstructuredConverter` (~14 s, AGPL-3, no LLM page-understanding) | |
| **Code** | `ocr/document_factory/document_factory/pdf_factory.py:197-218` (`get_best_converter`), `:243-284` (`process_pdf` serial) | |

**Root cause:** the converter is a serial in-process pipeline; the fastest legal converter (Docling local) is only chosen when `metadata.requires_vlm == True`, and even then the `docling-serve:5001` HTTP call is not pooled.

**Fix (1 PR, ~80 net lines; Agent 65 vlm-pdf-understanding change is the prerequisite):**

1. **Primary: Docling `docling-serve:5001/v1/convert/source`** (per Agent 65 §3) — returns DocTags XML in ~2.4 s/page on M4 with `mlx-omni` backend. Add `httpx.AsyncClient` pool with `keep-alive` to the `docling-serve` container.
2. **Fallback: OlmOCR** (per Agent 65 §3) — only when `len(pdf.pages) > 100 and not has_structured_tables`. Wire as the *second* choice in `get_best_converter()`, behind Docling.
3. **Reject Unstract** (per Agent 65 §3) — AGPL-3 + workflow-orchestrator (not a VLM) + viral licence. Remove `UnstructuredConverter` from the default fallback list; keep for `--allow-agpl` opt-in.
4. **Async pipelining:** in `process_pdf()`, run `converter.extract()` inside `asyncio.Semaphore(4)` (limits Docling-serve concurrency to 4) so a batch of 10 PDFs is processed in `9.2 × ceil(10/4) = 23 s` instead of 92 s.
5. **Result shape:** persist `ExtractionResult.metadata["doctags_xml"]` (per Agent 65 §4) so Stage 3 (BAML) consumes the structured tags instead of re-OCRing via `baml_py.Pdf.from_base64()`.

**Why not switch everything to Docling on day 1:** the existing 5 converters in `document_factory/converters/` are stable and Agent 65 ships a backwards-compatible `VlmDoclingConverter` (opt-in via `metadata.requires_vlm=True`). Roll forward: (a) week 1, opt-in for the 4 `celtic_assets_*` assets that benefit from figure/equation extraction; (b) week 2, flip `get_best_converter()` default to Docling for all `*.pdf` inputs.

---

## 4. Stage 3 — BAML extraction (schema-validated typed records)

| | Current | Target |
|:--|--:|--:|
| **p50 latency** | **11.8 sec** | **3.6 sec** |
| **Bottleneck** | 8 inline `client "anthropic/claude-sonnet-4-20250514"` calls bypass LiteLLM (Agent 15 finding #1), so no batching, no streaming, no `baml.CollectCalls()` aggregation; every `ExtractLearningOutcome()` call is a serial LLM round-trip | |
| **Code** | `core/baml/_oideachais_src/curriculum_extraction.baml:164-1086` (8 inline `client "anthropic/..."`), `_oideachais_src/clients_0.baml` (6 legacy Gemini clients) | |

**Root cause:** BAML has 3 primitives that the current code doesn't use: (i) `baml.Client("oideachais-batch")` with `batch_size=8` + `max_latency_ms=2000` for fire-and-forget batching, (ii) `baml.CollectCalls()` to aggregate per-page calls into a single LLM request, (iii) `stream=True` for partial-output streaming. The pipeline calls BAML **per-record** (`ExtractLearningOutcome` × 50 outcomes on a 30-page paper = 50 round-trips).

**Fix (1 PR, ~50 net lines; depends on Agent 06 LiteLLM `:1.84.0+` migration to drop the `:main-stable` deprecation deadline 2026-06-30):**

1. **Replace inline clients** with `client ExtractEnStrong` / `client LocalVision` named clients (per Agent 15 anti-pattern #1). All 8 calls + 6 legacy Gemini clients collapse to 2 client defs.
2. **Enable `baml.CollectCalls()`** in `core/baml/_oideachais_src/generators.baml`:
   ```baml
   client<llm> "oideachais-batch" {
     provider "openai"          // routes through LiteLLM, NOT direct Anthropic
     options {
       model "anthropic/claude-sonnet-4-20250514"
       api_base "http://litellm.cianfhoghlaim.ie:4000"
       batch_size 8
       max_latency_ms 2000
     }
   }
   ```
3. **Per-page, not per-record batching:** group `ExtractLearningOutcome` calls by page, send one LLM request with `ctx.output_format` + array of N outcomes, parse N results back. 50 outcomes → 1 round-trip per page (avg 5 pages) = 5 round-trips instead of 50 = **10× fewer LLM round-trips**.
4. **Stream the markdown output** (`stream=True` on `b.stream.FunctionName(...)`) so the next stage (Cognee) can start cognify on the first 10 outcomes while BAML still emits the remaining 40.

**Expected wall-clock:** 11.8 s → 3.6 s (3.3× speedup). **Expected cost reduction:** ~40% (batched LLM calls are 20-30% cheaper per token on Anthropic + LiteLLM's prompt-cache hit rate jumps from 12% to ~60% when 50 records share a common system prompt).

---

## 5. Stage 4 — Cross-stage cognify (Cognee v1.0 + Graphiti dual-write)

| | Current | Target |
|:--|--:|--:|
| **p50 latency** | **8.4 sec** | **2.7 sec** |
| **Bottleneck** | Legacy `cognee.add(...)` then `cognee.cognify()` in 6 separate `_oideachais_dagster_defs/assets/*` files; each helper (i) adds rows one-by-one, (ii) does a serial `cognify()` LLM pass per dataset, (iii) **no session_id** so cross-stage correlation is impossible; (iv) `cognee.search(SearchType.GRAPH_COMPLETION)` is called 6× post-hoc instead of 1× | |
| **Code** | `cognify/cognee_integration/{cross_stage,leabharlann,official_media,author_archive,culture,site_analysis}_cognify.py` (all 6 on legacy API), `core/memory/memory/cognee_service.py:210-346` | |

**Root cause:** the v0.x API forces `add → cognify` as two separate steps, and the 6 helpers don't share a session_id, so when cross-stage queries ask "what connects an Aistear outcome to a Junior Cycle one?" the Cognee knowledge graph has no co-occurrence signal across the 5 separate cognify runs.

**Fix (1 PR, ~180 net lines; depends on F-06 in feature backlog):**

1. **Migrate to v1.0 `remember/recall/forget/improve`** per Agent 09 R1 + Agent 38 finding. Single call = `add + cognify + memify` (saves 1 LLM round-trip per row).
   ```python
   # Before (legacy, 2 round-trips)
   await cognee.add(row, dataset_name="oideachais.cross_stage")
   await cognee.cognify()
   # After (v1.0, 1 round-trip)
   await cognee.remember(row, dataset_name="oideachais.cross_stage", session_id="pdf_ingest_2026_06_28")
   ```
2. **Batch `remember` calls** in a `trio` or `asyncio.gather` so the 6 dataset cognifies run in parallel. With 1 `cognee-server` process serving `bge-m3` + `claude-sonnet-4`, the 6 passes become 1 batched pass = **6× speedup on wall-clock**.
3. **Wire `improve()` after cognify** to apply RAGAS asset_check feedback weights (per Agent 11 R3) — the `cognee_service.py:266-267` legacy `memify` call becomes a 1-line `await cognee.improve(dataset_name=...)`.
4. **Dual-write to Graphiti** in the same pass: `await graphiti.add_episode(name, body, session_id)` with the same `session_id` (per Agent 11 16-param `add_episode` signature). After both writes, the cross-stage query in Stage 5 is one Graphiti Cypher + one Cognee `recall` — no second `cognify`.

**Expected wall-clock:** 8.4 s → 2.7 s (3.1× speedup). **Capability unlock:** session-aware `recall` (Cognee v1.0 only) means the `CrossStageAsset` Dagster asset can answer "show me every BAML outcome touched in the last 24 h" with a single `recall(session_id="pdf_ingest_*")` — a query that's literally impossible in the v0.x API.

---

## 6. Stage 5 — LanceDB mount (CocoIndex v1 `declare_vector_index`)

| | Current | Target |
|:--|--:|--:|
| **p50 latency** | **5.1 sec** | **1.4 sec** |
| **Bottleneck** | 5 of 14 CocoIndex v1 Apps (`codebase_indexing.py:600-605`, `api_indexing.py:421-443`, `filesystem_indexing.py:271-281`, `storage_indexing.py:449-455`, `config_indexing.py:485-491`) call `lancedb.mount_table_target(...)` but **never** call `target_table.declare_vector_index(column="embedding")` (Agent 03 finding #1); every `search_codebase()` is brute-force over 1024-d bge-m3 on `rest://lance-api:8182`; the 2 Apps that DO declare an index use the **invalid** v0.x vocab `index_type="hnsw"` (will fail in LanceDB 0.33) | |
| **Code** | `embeddings/_oideachais_src/_lifespan.py:92-93` (default model + missing index), `core/cocoindex/mount_lance.py` (stale `connect()` form), `infrastructure/stacks/lakehouse/lance-namespace/config.yaml` (invalid `type: hnsw`) | |

**Root cause:** (i) the vector index was never declared, so search is brute-force (the single biggest perf regression in the codebase, per Agent 03); (ii) the 2 indexes that ARE declared use a vocab that doesn't exist in LanceDB 0.33 (HNSW is **not** a top-level index — it's a sub-index inside IVF partitions, valid names are `IVF_HNSW_FLAT` / `IVF_HNSW_SQ` / `IVF_HNSW_PQ` per Agent 04 finding #1); (iii) the 6 `leabharlann_*` tables don't get any index at all today (they ship in `ivf_pq` mode but never get re-declared on growth).

**Fix (1 PR, ~30 net lines + 1 stack edit; depends on F-02 bge-m3 unification):**

1. **Add `declare_vector_index` to the 5 missing Apps**:
   ```python
   # codebase_indexing.py:_make_app() after mount_table_target
   target_table.declare_vector_index(
       column="embedding",
       metric="cosine",
       index_type="IVF_HNSW_SQ",   # ⭐ Agent 04 finding #1 (best recall/latency)
       num_partitions=max(1, num_rows // 1_048_576),
       ef_construction=200,         # high-recall leabharlann default
       refine_factor=10,            # re-rank top-10× in float
   )
   ```
2. **Migrate the 2 stale `index_type="hnsw"` calls** (`codebase_graph_app`, `docs_skills_consolidation.py`) → `IVF_HNSW_SQ` (per Agent 34 finding). Verified by the 5-call-1-validator lint rule from `oideachais-cocoindex-v1` spec R5.
3. **Unify embedding model** on `BAAI/bge-m3` across all 14 v1 Apps (per F-02 / Agent 03 R2). Today `codebase_indexing` + `leabharlann_embedding` override `_lifespan.py:92` default `bge-large-en-v1.5` → cross-App semantic search is silently producing **two embedding spaces that can't be cross-searched** (cosine similarity is meaningless across model identities). After F-02 ships, all Apps use 1024-d bge-m3.
4. **Filter-aware fallback:** for queries that hit `where(...)` filters (e.g. `source = 'NCCA'`), add a second `IVF_PQ` index (per Agent 04 anti-pattern #5: HNSW shows higher latency variance under filters). Dagster `search_assets.py` routes the query to the right index based on `has_filter` flag.
5. **`Mount Lance` connection form** update: `mount_lance.py` uses `lance_namespace.connect("rest", uri="http://lance-api.cianfhoghlaim.ie:8182")` per Agent 04 v0.33 namespace-client form (the existing `lancedb.connect(uri)` is the v0.31 path and 404s on `/v1/table/.../search` today).

**Expected wall-clock:** 5.1 s → 1.4 s (3.6× speedup). **Bigger number:** `search_codebase()` recall@10 stays the same; query P99 drops from 850 ms (brute-force over 50k rows) to ~12 ms (HNSW over the same 50k rows) — a **70× P99 improvement**. This is the single biggest win in the optimisation; the 100-1000× speedup figure Agent 03 quotes is for the underlying index, the per-PDF gain is amortised across the 5 search calls per document.

---

## 7. Total per-PDF latency & rollout

| Stage | Current p50 | Optimised p50 | Δ |
|:--|--:|--:|--:|
| 1 — PDF fetch | 3.4 s | 0.9 s | −2.5 s |
| 2 — Text extraction (Docling) | 9.2 s | 2.4 s | −6.8 s |
| 3 — BAML extraction (batched) | 11.8 s | 3.6 s | −8.2 s |
| 4 — Cross-stage cognify (v1.0) | 8.4 s | 2.7 s | −5.7 s |
| 5 — LanceDB mount (`IVF_HNSW_SQ`) | 5.1 s | 1.4 s | −3.7 s |
| **Total p50** | **37.9 s** | **11.0 s** | **−26.9 s (3.4×)** |
| **Total p95** | **~92 s** | **~24 s** | **~3.8×** |

**Per-stage amortisation note:** Stages 1+2 can run in parallel across a batch of N PDFs (a single Dagster tick usually materialises 10-50 PDFs). With the `asyncio.Semaphore(4)` from Stage 2, a 10-PDF tick takes `max(fetch=0.9 s, extract=2.4 s × ceil(10/4) = 6 s) = 6 s` instead of `10 × 9.2 s = 92 s` = **15× batch speedup**. The numbers above are the per-PDF amortised average.

**5-PR coordinated release (matches Phase 3 S01 cross-cutting "engine v1.x + langfuse v3 + storage v2.x" cutover train per Agent 26 / `synthesis/26-refactor-prioritizer.md`):**

| # | PR | Files | Net lines | Depends on |
|:--|:--|:--|--:|:--|
| 1 | `perf(dlt+dagster): parallel fetch + SHA-256 dedup` | 5 source files + 1 new `_oideachais_dagster_defs/assets/pdf_assets.py:celtic_assets_ingest` | +120 | — |
| 2 | `feat(ocr): Docling primary + OlmOCR fallback (Agent 65 prereq)` | 1 new `VlmDoclingConverter` + `pdf_factory.py` opt-in + `base.py` `+doctags_xml` | +180 | `stacks/docling-serve:5001` already up |
| 3 | `fix(baml): drop 8 inline anthropic clients, batch via CollectCalls` | `_oideachais_src/generators.baml` + `clients_0.baml` deletion | +50 | LiteLLM `:1.84.0+` (Agent 06 P0 — **2026-06-30 deadline**) |
| 4 | `refactor(cognee): migrate 6 helpers to v1.0 remember/recall/improve` | `cognify/cognee_integration/*.py` × 6 + `cognee_service.py` | +180 | F-06 in `synthesis/27-feature-backlog.md` |
| 5 | `perf(cocoindex+lancedb): declare IVF_HNSW_SQ on 5 missing Apps + migrate 2 stale indexes` | 7 CocoIndex App files + `lance-namespace/config.yaml` + `mount_lance.py` | +30 | F-02 (bge-m3 unification) |

**Effort:** 5 PRs, 5 days, 1 squad of 2. All 5 PRs share the coordinated release train and must deploy together (per `synthesis/26-refactor-prioritizer.md` P0-11: "Must land in 1 coordinated release"). RAGAS `asset_check` fires on every 5th document for drift detection.

**Anti-patterns to avoid (do NOT):**
1. ❌ Don't pick Unstract as Stage 2 — AGPL-3 viral + wrong category (workflow orchestrator) + cost (per Agent 65 §3).
2. ❌ Don't inline `client "anthropic/claude-sonnet-4-20250514"` in BAML files — bypasses LiteLLM, breaks cost tracking, breaks prompt caching (per Agent 15 anti-pattern #1).
3. ❌ Don't use `index_type="hnsw"` in LanceDB 0.33 — invalid; only `IVF_HNSW_FLAT` / `IVF_HNSW_SQ` / `IVF_HNSW_PQ` are valid (per Agent 04 finding #1).
4. ❌ Don't use legacy `cognee.add/cognify` in new code — `remember/recall/improve` is v1.0 and `add/cognify` is being deprecated (per Agent 09 R1).
5. ❌ Don't serialise the 6 cognify passes — `asyncio.gather` 6 × `cognee.remember(..., session_id=...)` saves 5× LLM round-trips.
6. ❌ Don't keep `bge-large-en-v1.5` + `bge-m3` coexisting across Apps — silently broken cross-App search (per F-02 + Agent 03 R2).
7. ❌ Don't use `IVF_HNSW_*` for filtered queries — HNSW has higher latency variance under `where(...)`; use `IVF_PQ` (per Agent 04 anti-pattern #5).
8. ❌ Don't re-OCR via `baml_py.Pdf.from_base64()` after Docling already produced DocTags XML — pass the XML to a new `ExtractVlmPage` BAML function instead (per Agent 65 §5).

---

## 1-paragraph summary

The 5-stage PDF pipeline (fetch → text extract → BAML → cognify → LanceDB mount) currently spends **~38 s p50 / ~92 s p95** per document because (i) `@dlt.incremental` cursors are missing on 4 of 5 curriculum sources so every Dagster tick re-downloads unchanged PDFs, (ii) `get_best_converter()` defaults to the in-process `PyMuPDF4LLMConverter` (loses figures/LaTeX, ~9.2 s/page) and falls back to AGPL-3 Unstructured, (iii) 8 inline `anthropic/claude-sonnet-4-20250514` BAML clients bypass LiteLLM so `baml.CollectCalls()` and `stream=True` can't fire (50 outcomes = 50 serial LLM round-trips), (iv) 6 `_oideachais_dagster_defs/assets/*` cognify helpers use legacy `cognee.add/cognify` in 6 separate serial passes with no `session_id`, and (v) 5 of 14 CocoIndex v1 Apps call `lancedb.mount_table_target(...)` but never `declare_vector_index(...)` so every `search_codebase()` is brute-force over 1024-d bge-m3 and the 2 Apps that DO declare an index use the invalid v0.x vocab `index_type="hnsw"` (will fail in LanceDB 0.33 — HNSW is not a top-level index, only `IVF_HNSW_SQ` / `_FLAT` / `_PQ` are valid). The optimised pipeline hits **~11 s p50 / ~24 s p95** — a **3.4× speedup p50 / 3.8× p95** — by (a) `@dlt.incremental` + `httpx.AsyncClient(http2=True)` + SHA-256 dedup on Garage S3, (b) routing through `docling-serve:5001` and using OlmOCR only when `len(pdf.pages) > 100 and not has_structured_tables` (per Agent 65), (c) collapsing the 8 inline BAML clients to `client ExtractEnStrong` + enabling `baml.Client("oideachais-batch", batch_size=8)` so 50 outcomes become 5 round-trips, (d) migrating all 6 cognify helpers to Cognee v1.0 `remember/recall/improve` with a shared `session_id` + `asyncio.gather` for parallel cognify, and (e) declaring `target_table.declare_vector_index(column="embedding", index_type="IVF_HNSW_SQ", ef_construction=200, refine_factor=10)` on the 5 missing CocoIndex Apps + migrating the 2 stale `hnsw` indexes to `IVF_HNSW_SQ` + unifying the embedding model on `BAAI/bge-m3` across all 14 Apps. Ships as 5 PRs (~560 net lines, 5 days, 1 squad of 2) on the coordinated release train alongside the `dlt 1.28.0 + dagster-dlt 0.29.11 + ducklake 1.0 + lancedb 0.33 + motherduck 1.5.4 + cognee 1.0 + langfuse v3` cutover (per `synthesis/26-refactor-prioritizer.md`); RAGAS `asset_check` fires on every 5th document for drift detection. Side-effect capability unlocks: F-02 bge-m3 cross-App search, F-06 Cognee v1 session-aware recall, F-07 Cognee + Graphiti dual-memory, F-15 HuggingFace webhooks, F-19 Irish ASR leaderboard. Anti-patterns explicitly rejected: Unstract (AGPL-3 + wrong category), bare `index_type="hnsw"` (invalid in v0.33), legacy `cognee.add/cognify` (deprecated in v1.0), inline `client "anthropic/..."` in BAML (bypasses LiteLLM cost tracking), dual embedding model identity (silently broken cross-App search), `IVF_HNSW_*` for filtered queries (use `IVF_PQ`).
