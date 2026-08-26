# Data-Plane Surface Map for meaisinfhoghlaim

Read-only snapshot post-trilogy (`689143bb3`, `a7f25919e`, `b3535ba36`,
`b553d10e8`). All file paths are repo-relative. **Facts only; no
recommendations.**

---

## 1. dlt + Dagster surface touching meaisinfhoghlaim

### 1.1 dlt sources that use the v4 OCR registry (`select_ocr_backend()` / `VISION_MODELS`)

| File path | Source name(s) | Destination table(s) | `destinations_cianfhoghlaim` factory? | `DltRunObserver`? |
|:--|:--|:--|:--|:--|
| `dlt_sources/filesystem/leaving_cert_source.py` | LC6 (chemistry/computer_science/english/gaeilge/geography/mathematics × en/ga) | `lc_<subject>_papers / lc_<subject>_syllabus / lc_<subject>_marking` (per docstring L14-L29) | NO — uses `dlt_sources` import but no `destinations_cianfhoghlaim` call; uses bare `dlt.resource` (`dlt_sources` package-style import at L42) | NO |
| `dlt_sources/filesystem/pdf_download_source.py` | LC PDF downloads | `pdf_downloads` (per L115 comment) | NO — local-file write path | NO |
| `dlt_sources/filesystem/gemini_corpus_source.py` | Gemini corpus | (per L16) | NO | NO |
| `dlt_sources/british_isles/_cross/jurisdiction_pipeline_base.py` | BIEP v3 jurisdiction base class for 8 jurisdictions | `cianfhoghlaim.education.<jurisdiction>.<stage>` (via subclass) | **YES** — `from dlt_sources.common.destinations_cianfhoghlaim import get_dlt_destination` (L18); called at L78 `get_dlt_destination(use_ducklake=use_md)` | NO |
| `dlt_sources/british_isles/<jurisdiction>/education/<jurisdiction>_jurisdiction_pipeline.py` (× 8: ireland / england / scotland / wales / northern_ireland / jersey / guernsey / isle_of_man) | BIEP v3 jurisdiction pipeline | inherits base | **YES** — subclass of `JurisdictionPipelineBase`; same factory | NO |
| `dlt_sources/api_sources/{soundcloud_scraper.py, spotify_source.py, researchgate.py, linkedin.py}` | API sources | per-source | NO (`from dlt_utils import get_dlt_destination` — different legacy `dlt_utils` path) | NO |
| `dlt_sources/common/named_destinations.py` (`_warehouse_destination`) | NCCA warehouse | `cianfhoghlaim.leaving_cert` | **NO** — hardcodes `md:oideachais?motherduck_token=` (L94) — **deprecated alias** | NO |

`Observability.DltRunObserver` (defined at `dlt_sources/common/observability.py:39`) is **only instantiated** in `dlt_sources/common/destinations_cianfhoghlaim.py:349-351` (an internal helper inside the factory's `_build_local_destination`); **no** meaisinfhoghlaim-touching dlt source wraps its `@dlt.resource` / `@dlt.source` with a `DltRunObserver` context manager.

### 1.2 Dagster assets that import meaisinfhoghlaim

| File path | Asset key(s) | Schedule / automation | Emits OTEL? |
|:--|:--|:--|:--|
| `orchestration/defs/2_materials/meaisin_ocr_htr/ocr_model_assets.py` | `ocr_model_<key>_ingested` / `…_extractions` / `…_embeddings` (× 24 models: deepseek-ocr-2, docling-serve, dots-ocr, gemma-3-4b, glm-4.6v-flash, internvl3-8b, llama-3.2-vision-11b, molmo2-4b, molmo2-8b, olmocr-2-7b-1025, paddleocr-vl-1.6, qwen3-vl-30b-a3b, qwen3-vl-4b, qwen3-vl-8b, qwen3.6-27b-mtp, uccix-llama-3.1-8b, uccix-llama2-13b, uccix-mistral-24b, unstract-api + 5 extra) | `make_weekly_smoke_test_automation()` (ingested + embeddings) / `make_nightly_audit_automation()` (extractions) — `orchestration/automation/biiep_scheduling.py:114-130` | NO |
| `orchestration/defs/2_materials/meaisin_document_factory/converter_assets.py` | `converter_<name>_ingested / _extractions / _embeddings` (× 7: docling / marker / unstructured / deepseekocr / pymupdf4llm / curriculum_document / pdf_factory) | `make_monthly_circulars_automation()` / `make_nightly_audit_automation()` | NO |
| `orchestration/defs/2_materials/ocr_comparison/ensemble_comparison/biiep_ocr_ensemble.py` | `biiep_ocr_ensemble` + `biiep_ocr_ensemble_ragas_check` | (legacy `0 5 * * *` cron retired per file docstring L118-L130; now yearly + event-driven) | NO (asset itself) |
| `orchestration/defs/2_materials/meaisin_agents/agent_assets.py` | meaisín agents | (refers to `meaisinfhoghlaim/agents/`) | NO |
| `orchestration/defs/2_materials/biiep_v3/m0_foundation_assets.py` | BIEP v3 M0 foundation | `make_weekly_smoke_test_automation()` (L42, L93, L154, L202, L256) | NO |
| `orchestration/defs/2_materials/ireland_education/generic_ireland_assets.py` | Ireland generics | (per BIEP v3) | NO |
| `orchestration/defs/2_materials/england_education/generic_england_assets.py` | England generics | `make_nightly_audit_automation()` (L49) | NO |
| `orchestration/defs/2_materials/scotland_education/scotland_assets.py` | Scotland | (per base file) | NO |
| `orchestration/defs/2_materials/language_pipelines/generic_language_assets.py` | language pipelines | `make_monthly_circulars_automation()` + `make_nightly_audit_automation()` (L45-46, L90, L147) | NO |
| `orchestration/defs/3_model_lifecycle/federated_ocr/defs.yaml` | `irish_ocr_federated_smoke` | cron `*/30 * * * *` (every 30 min) | NO |
| `orchestration/defs/4_asset_generation/marimo_dashboards/uog_math_coursework/defs.yaml` | uog math coursework | (depends on `5_agent_ops/meaisinfhoghlaim/academic_history_agent`) | NO |
| `orchestration/defs/5_agent_ops/meaisinfhoghlaim/academic_history_agent/defs.yaml` | `agent_health / agent_routing / agent_memory / agent_event / agent_trace` (per L5 L5 CelticAgentOpsComponent contract) | (managed by `CelticAgentOpsComponent`) | NO (no `langfuse_otel` wiring in defs.yaml) |

**Assets NOT registered that reference meaisinfhoghlaim by name string**:
- `orchestration/defs/2_materials/meaisin_ocr_htr/` has only `ocr_model_assets.py` — no `defs.yaml`.
- `orchestration/defs/2_materials/meaisin_document_factory/` has only `converter_assets.py` — no `defs.yaml`.

`england_change_detection_sensor.py` (in `orchestration/defs/sensors/`) is not meaisinfhoghlaim-related.

---

## 2. CocoIndex surface touching meaisinfhoghlaim

### 2.1 CocoIndex v1 Apps that reference meaisinfhoghlaim OCR models

| File path | App name | Embedder model | Target table |
|:--|:--|:--|:--|
| `cocoindex_flows/british_isles/england/ocr_education_embedding.py` | `england_ocr_education_embedding` | inherits from `cocoindex_flows._shared._lifespan.EMBEDDER` (= `BAAI/bge-m3`) | `lancedb.mount_table_target(LANCE_DB, "cianfhoghlaim.england.ocr.{subject}.{qualification_level}")` (L49) |
| `cocoindex_flows/biep_parity/england_gcse_apps.py` (factory for 129 Apps = 43 GCSE subjects × 3 boards AQA/OCR/Edexcel) | `england_gcse_<board>_<subject>` × 129 | shared (`EMBEDDER` from `_lifespan`) = BAAI/bge-m3 | `lancedb.mount_table_target(LANCE_DB, "cianhoghlaim.england.gcse.<board>.<subject>_gcse_chunks")` (per docstring L13-L19) |
| `cocoindex_flows/biep_parity/england_a_level_apps.py` (factory for 147 Apps = 49 A-Level × 3 boards) | `england_a_level_<board>_<subject>` × 147 | shared BAAI/bge-m3 | `lancedb.mount_table_target(LANCE_DB, "cianhoghlaim.england.a_level.<board>.<subject>_a_level_chunks")` |
| `cocoindex_flows/biep_parity/ireland_jc_apps.py` | (Ireland JC factory) | shared BAAI/bge-m3 | `lancedb.mount_table_target(LANCE_DB, "cianhoghlaim.ireland.jc.<subject>_jc_chunks")` (per L141-L145) |
| `cocoindex_flows/biep_parity/ireland_lc_*` (4 files: gaeilge / mathematics / computer_science + `_education_embedding.py`) | Ireland LC | shared BAAI/bge-m3 | `cianhoghlaim.ireland.lc.<subject>` |
| `cocoindex_flows/biep_parity/{en,wls,sct,ni,je,gg,im}_education_embedding.py` (7 jurisdictions) | per-jurisdiction App | shared BAAI/bge-m3 | `cianhoghlaim.<jurisdiction>.education_chunks` |
| `cocoindex_flows/media/ocr_aware_flow.py` | `ireland_syllabus_chunks` (legacy v0-style + references `OCR_VISION_REGISTRY` + `CLASSICAL_OCR_REGISTRY`) | documented BGE-M3 | `ireland_syllabus_chunks` (L31) |
| `cocoindex_flows/knowledge_graph/youtube_kg_embedding.py` | `youtube_kg_embedding_app` | `Annotated[list[float], "BAAI/bge-m3"]` (L101, L118, L134) — **hardcoded** | `cianfhoghlaim.youtube.youtube_videos` (L79) |
| `cocoindex_flows/_shared/repo_embedding.py:124-125, 244` | `repo_embedding` | `SentenceTransformerEmbed(model="BAAI/bge-m3")` — **hardcoded** | (canonical cross-cutting infrastructure index) |
| `cocoindex_flows/corpus/unified_embedding.py:103` | `unified_embedding_app` | `os.getenv("UNIFIED_EMBED_MODEL", "BAAI/bge-m3")` — non-canonical env var | per-corpus |
| `cocoindex_flows/infrastructure/api_indexing.py:79` | `api_indexing_app` | `os.getenv("API_EMBED_MODEL", "BAAI/bge-m3")` — non-canonical | per-stack |
| `cocoindex_flows/infrastructure/filesystem_indexing.py:72` | `filesystem_indexing_app` | `os.getenv("FS_EMBED_MODEL", "BAAI/bge-m3")` — non-canonical | per-stack |
| `cocoindex_flows/infrastructure/codebase_indexing.py:93` | `codebase_app` | `os.getenv("CODEBASE_EMBED_MODEL", "BAAI/bge-m3")` — non-canonical | code |
| `cocoindex_flows/infrastructure/docs_skills_consolidation.py:84` | `docs_skills_app` | `os.getenv("DOCS_SKILLS_EMBED_MODEL", "BAAI/bge-m3")` — non-canonical | docs |
| `cocoindex_flows/infrastructure/storage_indexing.py:97, 17` | `storage_indexing_app` | `os.getenv("STORAGE_EMBED_MODEL", "BAAI/bge-m3")` — **non-canonical**; also refs `ATTACH 'md:oideachais'` (deprecated) | per-lake |
| `cocoindex_flows/infrastructure/config_indexing.py:88` | `config_indexing_app` | `os.getenv("CONFIG_EMBED_MODEL", "BAAI/bge-m3")` — non-canonical | config |

### 2.2 The shared `_lifespan.py` embedder

`cocoindex_flows/_shared/_lifespan.py:107` reads `os.getenv("CIANFHOGHLAIM_EMBED_MODEL", "BAAI/bge-m3")` — canonical. But **7+ CocoIndex Apps bypass the shared lifespan and hardcode their own embedder env knob** (see 2.1 table column 3 rows marked *non-canonical*).

### 2.3 Direct hardcoded `BAAI/bge-m3` strings (not reading env)

- `cocoindex_flows/british_isles/england/aqa_education_embedding.py:15` (docstring)
- `cocoindex_flows/british_isles/england/edexcel_education_embedding.py` (docstring)
- `cocoindex_flows/british_isles/ireland/ie_law_{court_rules,courts,judgements,legal_aid,piab}.py` (5 files, docstrings)
- `cocoindex_flows/british_isles/ireland/canuint_embedding.py`
- `cocoindex_flows/british_isles/ireland/ireland_legal_embedding.py:137` (runtime call to `SentenceTransformerEmbedder(EMBED_MODEL)` where `EMBED_MODEL` resolves from the shared `_lifespan`)
- `cocoindex_flows/celtic/{gaeilge_embedding,mythology_embedding}.py` — `cocoindex.functions.SentenceTransformerEmbed(model="BAAI/bge-m3")` (L37 of mythology)
- `cocoindex_flows/knowledge_graph/youtube_kg_embedding.py:101, 118, 134` (3x) — `Annotated[list[float], "BAAI/bge-m3"]`
- `cocoindex_flows/corpus/{government_circulars_embedding,university_embedding,leabharlann_flow,duchas_embedding,local_documents_embedding}.py` (docstrings)
- `cocoindex_flows/subjects/{junior_cycle_embedding,lc_subject_embedding}.py` (docstrings)
- `cocoindex_flows/american_nations/united_states/california_education_embedding.py:7`
- `cocoindex_flows/commonwealth/canada/provinces/quebec/montreal_education_embedding.py:6`
- `cocoindex_flows/commonwealth/nigeria/education_embedding.py:5`
- `cocoindex_flows/commonwealth_cross/education_embedding.py:7`
- `cocoindex_flows/european_nations_cross/{law_embedding,education_embedding,medicine_embedding}.py`

`cocoindex_flows/knowledge_graph/youtube_kg_embedding.py:393` does `from cianfhoghlaim.meaisinfhoghlaim.ocr.models.registry import ...` — uses the **legacy** (deprecated) `meaisinfhoghlaim.ocr.models.registry` shim, not `meaisinfhoghlaim.models.registry`.

---

## 3. BAML surface touching meaisinfhoghlaim OCR

| File path | Function name | Input type | Output type | Wraps OCR router / hardcodes backend URL? |
|:--|:--|:--|:--|:--|
| `baml_src/processing/ocr_extraction.baml:119` | `ExtractHiddenHeritagesTale` | `tale_id, source_url, source_collection` | `HiddenHeritagesTale` | `client ExtractEn` (canonical text client → `minimax-m3`) |
| `baml_src/processing/ocr_extraction.baml:151` | `ExtractTalesListing` | page-url list | `TalesListingPage` | `client ExtractEn` |
| `baml_src/processing/ocr_validation.baml:272` | `ValidateOCRResult` | ocr-result + meta | `OCRValidationResult` | `client ExtractEn` |
| `baml_src/processing/ocr_validation.baml:281` | `ValidateIrishContent` | extracted text | `IrishContentQuality` | `client ExtractEn` |
| `baml_src/processing/ocr_validation.baml:288` | `ExtractDocumentStructure` | doc text | `DocumentStructure` | `client ExtractEn` |
| `baml_src/processing/ocr_validation.baml:296` | `CompareOCRModels` | multi-model output | `ModelComparisonResult` | `client ExtractEn` |
| `baml_src/processing/ocr_registry_test.baml:8` | `GetOptimalForM4` | none | `OCRModelV4` | `client ExtractEn` |
| `baml_src/processing/ocr_registry_test.baml:13` | `SelectOCRBackend` | `pdf_path: string` | `OCRBackendV4` | `client ExtractEn` |
| `baml_src/british_isles/england/education/ensembled_extraction.baml:56` | `ExtractEnglandEnsembleConsensus` | `pdf_text, baml_output, unstract_json, qwen3_vl_response, gemma4_response, subject` | `EnsembleConsensus` | `client ExtractEn` (does NOT use `Docling` or `Unstract` — these are wired in `clients_ocr_ensemble.baml`) |
| `baml_src/clients_ocr_ensemble.baml:22` (named client `Docling`) | n/a — client def | n/a | n/a | `base_url env.DOCLING_URL` (default `http://localhost:5001/v1`); `api_key env.DOCLING_API_KEY` (default `"docling"`); `model "docling"` |
| `baml_src/clients_ocr_ensemble.baml:34` (named client `Unstract`) | n/a — client def | n/a | n/a | `base_url env.UNSTRACT_API_URL` (default `http://localhost:8000/api/v1/deployment`); `model env.UNSTRACT_DEPLOYMENT_ID` (workflow ID) |
| `baml_src/clients_llama_swap.baml` (`LlamaSwapClient`, `LlamaSwapOCRClient`→qwen3-vl-8b, `LlamaSwapExtractionClient`→gemma-4-12B, `LlamaSwapReasoningClient`→qwen3.6-27b-mtp) | n/a — client defs | n/a | n/a | `base_url env.LLAMASWAP_BASE_URL`; `api_key env.LLAMASWAP_API_KEY`; **hardcoded** model strings `qwen3-vl-8b`, `gemma-4-12B`, `qwen3.6-27b-mtp` (L20, L38, L46, L54) |
| `baml_src/clients.baml` (`LocalVisionGemma4` L37, `LocalVisionQwen3vl` L48, `LocalVision` L100, `VisionExtractor` L136, `BIEPV3Vision` L189) | n/a — client defs | n/a | n/a | All use `env.LITELLM_BASE_URL` + `env.LITELLM_API_KEY`; **hardcoded** `model "local/vision/gemma-4-26B-A4B"` and `"local/vision/qwen3-vl-8b"` (despite next-line `MODEL_REGISTRY: family=ocr_vision, role=qwen3_vl_default → qwen3-vl-8b` annotations) |
| `baml_src/clients.baml` (`Default`/`LitellmClient`/`ExtractEn`/`ExtractEnStrong`/`BIEPV3Extract`/`BIEPV3ExtractStrong` + ~14 generic aliases at L123-L138) | n/a — client defs | n/a | n/a | `env.MINIMAX_BASE_URL` + `env.MINIMAX_API_KEY`; **hardcoded** `model "minimax-m3"` for all |

Result: the model **strings** are hardcoded in `.baml` files but are annotated with `MODEL_REGISTRY` comments; the **endpoints/keys** are routed through env vars (`DOCLING_URL`, `LLAMASWAP_BASE_URL`, `MINIMAX_BASE_URL`, `LITELLM_BASE_URL`).

`baml_src/processing/_shared/video_kg.baml:25` and `baml_src/processing/named_entities.baml:6-12` reference `ocianfhoghlaim.meaisinfhoghlaim.ocr.models.registry.VISION_MODELS` in docstrings only.

---

## 4. marimo notebooks that consume meaisinfhoghlaim OCR

| File path | OCR backend it queries | Table it reads from | Goes through `notebooks/_shared/db.py`? |
|:--|:--|:--|:--|
| `notebooks/08_ocr_ensemble_audit.py` (L99) | The 4 ensemble paths (BAML + Unstract + qwen3-vl + gemma-4-26B-A4B) | `cianfhoghlaim.education.british_isles.*._all_docling`, `cianfhoghlaim.education.british_isles.*._all_qwen3_vl`, `cianfhoghlaim.education.british_isles.*._all_gemma4`, `cianfhoghlaim.education.british_isles.*._all_unstract_json` (per `conn.sql` L131, L171) | **NO** — `ibis.duckdb.connect("md:cianfhoghlaim")` directly (L99) — bypasses `notebooks/_shared/db.py:connect_md` |
| `notebooks/05_england_aqa_ocr_edexcel.py` (L81) | England OCR + AQA + Edexcel | `md:cianfhoghlaim` | **NO** — `ibis.duckdb.connect("md:cianfhoghlaim")` directly (L81) |
| `notebooks/06_celtic_languages_06_local_documents_subject_viewer.py` (L65, L67) | qwen3-vl-8b (LlamaSwap), molmo2-8b | `md:cianfhoghlaim` or `/tmp/cianfhoghlaim.duckdb` | **NO** — direct `ibis.duckdb.connect(...)` |
| `notebooks/10_biep_pipeline_lakehouse_07_subject_full_pipeline.py` | gemma-4-E2B (Stage 1, L100) | `cianfhoghlaim.education.<jurisdiction>.…` | (reads via the pipeline; no direct `connect_md` import found in head) |
| `notebooks/10_biep_pipeline_lakehouse_03_dlt_pipeline_overview.py` | n/a (overview) | `md:cianfhoghlaim` | (mentions no raw `duckdb.connect`; docstring L17 asserts `no raw ibis.duckdb.connect()` but actual usage not yet inspected) |
| `notebooks/19_ireland_pipeline_dashboard.py`, `notebooks/20_england_pipeline_dashboard.py` | ChangeDetection.io OCR (`jcq_registry_sensor` for AQA+OCR+Edexcel) | per-jurisdiction | (separate dashboards) |
| `notebooks/06_celtic_languages_02_duchas_folklore_with_bboxes.py` | bbox OCR + Dúchas | n/a | n/a |

Other notebooks that *touch* OCR/MODEL_REGISTRY but not OCR data paths:
- `notebooks/14_dev_env_tools_07_model_registry.py` (model registry UI)
- `notebooks/06_celtic_languages_01_gaois_terminology_explorer.py` (gemma-4-26B-A4B English)
- `notebooks/06_celtic_languages_07_celtic_curriculum_browser.py` (Welsh/Scottish/Breton/Manx/Cornish → gemma-4-26B-A4B)
- `notebooks/01_overview_setup.py:205` (gemma-4-26B-A4B vs qwen3-vl-8b side-by-side)
- `notebooks/03_education_pdf_vision_pipeline.py` (refers to gemma-4-26B-A4B vs qwen3-vl-8b)

The 3 notebooks that **bypass** `notebooks/_shared/db.py` and call `ibis.duckdb.connect("md:cianfhoghlaim")` directly: `08_ocr_ensemble_audit.py:99`, `05_england_aqa_ocr_edexcel.py:81`, `06_celtic_languages_06_local_documents_subject_viewer.py:65,67`. (`notebooks/_shared/db.py` exports `connect_md` / `connect_local_lakehouse` / `connect_lance` / `connect_local` / `LAKEHOUSE_URI_DEFAULT = "md:cianfhoghlaim"`.)

Notebooks that use `notebooks/_shared/db.py:connect_md`: `22_crown_dependencies_dashboard.py:66-67`, `21_sct_wls_ni_pipeline_dashboard.py:68-69`, `23_8_jurisdiction_overview.py:70-71`, plus `12_corpus_overview__shared.py:16`.

---

## 5. MotherDuck federated-layer integration across meaisinfhoghlaim

### 5.1 `md:` alias references in `meaisinfhoghlaim/` + `meaisinfhoghlaim/ocr/`

| File | Alias used | Notes |
|:--|:--|:--|
| `meaisinfhoghlaim/ocr/ensemble/ensembled_extractor.py:277` | **reference only** — `dlt.common.destinations_oideachais.with_namespace('oideachais')` mentioned in docstring | Legacy path — does not exist at this version (`dlt_sources/common/destinations_cianfhoghlaim.py` is the canonical home) |
| `meaisinfhoghlaim/process/irish_document_scanner.py:539` | `os.getenv("MOTHERDUCK_TOKEN")` (no `md:` ref) | OK |

**No runtime code in `meaisinfhoghlaim/` references `md:oideachais` or `md:cianfhoghlaim` directly.**

### 5.2 `md:` alias references in `dlt_sources/`

| File | Line | Alias used | Notes |
|:--|:--|:--|:--|
| `dlt_sources/common/destinations_cianfhoghlaim.py:49` | `LAKEHOUSE_DUCKDB: str = "md:cianfhoghlaim"` | `md:cianfhoghlaim` | **Canonical** |
| `dlt_sources/common/ducklake_pool.py:24` | `acquire(self, uri: str = "md:cianfhoghlaim")` | `md:cianfhoghlaim` | Canonical |
| `dlt_sources/british_isles/_cross/registry_loader.py:401, 725` | `os.getenv("BIEP_REGISTRY_URI", "md:cianfhoghlaim")` | `md:cianfhoghlaim` | Canonical (env-overridable) |
| `dlt_sources/british_isles/_cross/registry_api.py:116, 152, 172, 195, 215, 261` (× 6) | `os.getenv("BIEP_REGISTRY_URI", "md:cianfhoghlaim")` | `md:cianfhoghlaim` | Canonical |
| `dlt_sources/README.md:58, 73` | (docs) | `md:cianfhoghlaim` | Canonical |
| `dlt_sources/common/named_destinations.py:54, 94` | `md:oideachais?motherduck_token=…` | **`md:oideachais` (DEPRECATED)** | Still active code path — `warehouse` named destination |
| `dlt_sources/filesystem/pdf_download_source.py:59, 115` | `GARAGE_BUCKET = "s3://garage/oideachais"`; docstring references `destinations_oideachais.py:_build_local_destination` | **`oideachais` legacy bucket name + module path** | Reference only |
| `dlt_sources/common/destinations_cianfhoghlaim.py:366-368, 427` | (comments) `tuatha/dlt_utils/destinations.py: from cianfhoghlaim.dlt.destinations_oideachais import with_namespace` | (legacy reference) | Comments only |
| `dlt_sources/common/destinations_tuatha.py:9, 33` | (legacy ref) `destinations_oideachais` | Legacy path in docstring + import | The function attempts `from dlt_sources.destinations_oideachais import with_namespace` (legacy module path; fallback would be `destinations_cianfhoghlaim`) |

**Net**: 1 active code path still uses **`md:oideachais`** (`dlt_sources/common/named_destinations.py:94` inside `_warehouse_destination`); the rest of the surface uses `md:cianfhoghlaim`.

---

## 6. OCR_WEBHOOK_URL convention integration with meaisinfhoghlaim

| Location | Reads/Emits `OCR_WEBHOOK_URL`? |
|:--|:--|
| `orchestration/sensors/ocr_completion_sensor.py:134` | **YES (consumer)** — `os.environ.get("OCR_WEBHOOK_URL", "").strip()`; gracefully SKIPPED if unset |
| `bonneagar/stacks/ocr-router/secrets.env:16` | **YES (emit side — secrets contract)** — `OCR_WEBHOOK_URL=infisical://dev-baile/ocr-router/webhook_url` |
| `bonneagar/stacks/ocr-router/compose.yaml:18, 45` | **YES (emit side)** — comment + env-block |
| `bonneagar/stacks/ocr-router/README.md:31, 42, 85` | (docs) |
| `meaisinfhoghlaim/` (whole tree) | **NO** — grep returns 0 hits |
| `meaisinfhoghlaim/ocr/` (whole subpackage) | **NO** |
| `dlt_sources/` | **NO** |
| `baml_src/` | **NO** |
| `cocoindex/` | **NO** |
| `notebooks/` | **NO** |
| `orchestration/defs/` | **NO** (only `orchestration/sensors/ocr_completion_sensor.py` reads it; this lives in `orchestration/sensors/` not `orchestration/defs/sensors/`) |

The OTel span for the sensor emission: `orchestration/sensors/ocr_completion_sensor.py:184-186` only emits log lines; the spec-required OpenTelemetry span emission with `dagster.sensor=ocr_completion, dagster.document_id=<doc-abc>` tags is documented in the docstring (L16-L19) but not implemented in code (only `run tags` are set on `RunRequest` at L116).

---

## 7. meaisinfhoghlaim env-var contract: canonical 48 vs. observed

### 7.1 Env vars consumed by `meaisinfhoghlaim/` + `meaisinfhoghlaim/ocr/` and their canonical-contract status

| Env var | In 48-var contract? | Where consumed |
|:--|:--|:--|
| `FALKORDB_HOST` | NO | `meaisinfhoghlaim/config/base.py:123, 307` |
| `FALKORDB_PORT` | NO | `meaisinfhoghlaim/config/base.py:128, 312` |
| `FALKORDB_PASSWORD` | NO | `meaisinfhoghlaim/config/base.py:133, 317` |
| `CONFLUENT_API_KEY` | NO | `meaisinfhoghlaim/process/irish_document_scanner.py:589` |
| `CONFLUENT_API_SECRET` | NO | `meaisinfhoghlaim/process/irish_document_scanner.py:590` |
| `CONFLUENT_BOOTSTRAP_SERVERS` | NO | `meaisinfhoghlaim/process/irish_document_scanner.py:586` |
| `DOCLING_URL` | NO | `meaisinfhoghlaim/backends/adapters.py:64` (default `http://localhost:5001`) |
| `DOTS_OCR_URL` | NO | `meaisinfhoghlaim/backends/adapters.py:69` (default `http://localhost:8001`) |
| `PADDLEOCR_URL` | NO | `meaisinfhoghlaim/backends/adapters.py:59` (default `http://localhost:8000`) |
| `UNSTRACT_URL` | NO | `meaisinfhoghlaim/backends/adapters.py:74` (default `http://localhost:8002`) |
| `HF_TOKEN` | NO | `meaisinfhoghlaim/process/llm_router.py:142`, `meaisinfhoghlaim/training/modal_finetune/finetune_irish.py:296` |
| `LANCEDB_URI` | **YES (Group 8)** | `meaisinfhoghlaim/process/irish_document_scanner.py:511`, `meaisinfhoghlaim/datasets/irish_htr_dataset.py:680` |
| `LANCEDB_API_KEY` | **YES (Group 8)** | `meaisinfhoghlaim/training/modal_finetune/embed_batch.py:258` |
| `LANGFUSE_HOST` | **YES (Group 1)** | `meaisinfhoghlaim/training/training/langfuse_callbacks.py:47` |
| `LANGFUSE_PUBLIC_KEY` | **YES (Group 1)** | `meaisinfhoghlaim/training/training/langfuse_callbacks.py:45` |
| `LANGFUSE_SECRET_KEY` | **YES (Group 1)** | `meaisinfhoghlaim/training/training/langfuse_callbacks.py:46` |
| `MLFLOW_TRACKING_URI` | **YES (Group 2)** | `meaisinfhoghlaim/training/modal_finetune/{finetune_irish.py:132, embed_batch.py:219}` |
| `MOTHERDUCK_TOKEN` | **YES (Group 7)** | `meaisinfhoghlaim/process/irish_document_scanner.py:539` |
| `SLACK_WEBHOOK_URL` | NO | `meaisinfhoghlaim/models/ci/hf_watchdog.py:158` |
| `OCR_WEBHOOK_URL` | **NO** (not in 48; should be Group 5 per trilogy spec) | (not consumed in meaisinfhoghlaim — see §6) |
| `minimax_BASE_URL` | NO (LLM-provider scope; TODO per env-var-contract.md L228-L232) | (consumed via BAML clients, not directly in `meaisinfhoghlaim/`) |
| `minimax_API_KEY` | NO | (consumed via BAML clients) |
| `LITELLM_BASE_URL` / `LITELLM_API_KEY` | NO (LLM-provider scope) | (BAML clients) |
| `LLAMASWAP_BASE_URL` / `LLAMASWAP_API_KEY` | NO (LLM-provider scope) | (BAML clients) |
| `DOCLING_API_KEY` | NO | (BAML client `Docling`) |
| `UNSTRACT_API_URL` / `UNSTRACT_API_KEY` / `UNSTRACT_DEPLOYMENT_ID` | NO | (BAML client `Unstract`) |
| `OPENCODE_GO_MODEL` etc. (M3 chokepoint env-vars) | NO | (per `_text_llm_entries` `_env_var` annotations in MODEL_REGISTRY) |

### 7.2 Gaps (env vars NOT in the 48-var contract)

14 env vars read by `meaisinfhoghlaim/` are absent from `docs/observability/env-var-contract.md`:

1. `FALKORDB_HOST`, `FALKORDB_PORT`, `FALKORDB_PASSWORD` — graph-DB cluster identity
2. `CONFLUENT_*` (3 vars) — Kafka backend for the RisingWave layer
3. `DOCLING_URL`, `DOTS_OCR_URL`, `PADDLEOCR_URL`, `UNSTRACT_URL` (4 vars) — OCR backend endpoints
4. `HF_TOKEN` — HuggingFace download token (used during finetune)
5. `SLACK_WEBHOOK_URL` — CI watchdog alert channel
6. `OCR_WEBHOOK_URL` — Dagster→ocr-router callback URL (the trilogy's new convention)

`OCR_WEBHOOK_URL` is the only gap that overlaps with the trilogy; the rest are data-plane gaps.

---

## 8. MODEL_REGISTRY coverage (52 entries / 7 families)

### 8.1 Source file

`meaisinfhoghlaim/models/model_registry.py` (1019 lines). Re-exports from `meaisinfhoghlaim/models/registry.py` (752+ lines for `VISION_MODELS`, `CLASSICAL_OCR`, `TEXT_MODELS`). The merged canonical `MODEL_REGISTRY = _ModelRegistry()` instance lives at L973 with `model_for(...)` / `filter_models(...)` helpers.

### 8.2 Entry counts by family

| Family | Count (file headers) | Source |
|:--|:--|:--|
| `ocr_vision` | 22 (per L10, L126 — projected from `VISION_MODELS` dict) | `meaisinfhoghlaim/models/registry.py:VISION_MODELS` (`gemma-4-E2B`, `gemma-4-E4B`, `gemma-4-12B`, `gemma-4-26B-A4B`, `glm-4.6v-flash`, `qwen3-vl-4b`, `qwen3-vl-8b`, `qwen3-vl-30b-a3b`, `qwen3.6-27b-mtp`, `deepseek-ocr-2`, `olmocr-2-7b-1025`, `granite-docling-258M`, `uccix-mistral-24b`, `uccix-llama-3.1-8b`, `uccix-llama2-13b`, `dots-ocr`, `paddleocr-vl-1.6`, `molmo2-4b`, `molmo2-8b`, `internvl3-8b`, `llama-3.2-vision-11b`, `gemma-3-4b`, `unstract-api`, `docling-serve` = 24 unique keys; `gemma-4-E2B` is split between MLX + LLAMASWAP) | `model_registry.py:125` |
| `text_llm` | 18 | `_text_llm_entries()` (L169) — `kimi-k2.6`, `glm-5.1`, `minimax-m2.5`, `mimo-v2.5`, `deepseek-v4-flash`, `minimax-m3`, `qwen3.6-27b-mtp`, `uccix-mistral-24b`, `uccix-llama-3.1-8b`, `uccix-llama2-13b` (DEPRECATED), `claude-sonnet-4-20250514`, `gpt-4o-mini`, `gemini-2.5-pro`, `email_triage_gemini_2_5_pro`, `unsloth/gemma-3-4b-it-GGUF`, `unsloth/gemma-4-26B-A4B-it-GGUF`, `Qwen/Qwen2.5-7B-Instruct`, `meta-llama/Llama-3.1-8B-Instruct`, `google/gemma-2-9b-it` = 19 |
| `embedder` | 3 | `BAAI/bge-m3`, `BAAI/bge-large-en-v1.5`, `all-MiniLM-L6-v2` |
| `rerank` | 3 | `jina-reranker-v2-base-multilingual`, `rerank-v3.5`, `gte-rerank-v2` |
| `image_gen` | 5 | `local/image/flux2-dev`, `local/image/z-image-turbo`, `local/image/qwen-image`, `local/image/sdxl`, `local/image/fibo` |
| `voice` | 5 | `whisper-large`, `wav2vec2-irish`, `chatterbox`, `aba-tts`, `ResembleAI/chatterbox` (DEPRECATED) |
| `translation` | 3 | `opus-mt`, `m2m100`, `nllb` |
| **Total** | **59 model_registry entries** (≈52 after collapsing the deprecated `uccix-llama2-13b` + `ResembleAI/chatterbox` twins) | |

Plus the 6-entry `CLASSICAL_OCR` Docker registry (separate `dict[str, dict[str, Any]]` at `model_registry.py:762` — `docling-serve` (port 5001), `paddleocr` (port 8888), `tesseract` (port 8889), `tesseract-shadow` (port 8890), `unstract` (port 8002), `dots-ocr` (port 8001) — 6 stacks).

Plus the 3-entry `TEXT_MODELS` dict for the agent fleet (`qwen3.6-27b-mtp` + `uccix-mistral-24b` + `uccix-llama-3.1-8b` at `registry.py:811`).

### 8.3 Consumers of `MODEL_REGISTRY` (runtime)

- `meaisinfhoghlaim/models/__init__.py:54-94` — single canonical re-export (`from meaisinfhoghlaim.models.model_registry import (MODEL_REGISTRY, model_for, filter_models, ModelFamily, ModelRegistryEntry)`).
- `meaisinfhoghlaim/models/README.md` — documentation references only.
- No runtime call sites in `meaisinfhoghlaim/`, `dlt_sources/`, `cocoindex/`, or `orchestration/` directly invoke `MODEL_REGISTRY.resolve(...)` / `model_for(...)` / `MODEL_REGISTRY.filter(...)`.

### 8.4 Models used by meaisinfhoghlaim code that are NOT in the canonical registry

None — the 22-entry `VISION_MODELS` + 6-stack `CLASSICAL_OCR` + 3-entry `TEXT_MODELS` are all surfaced through `MODEL_REGISTRY`. Hardcoded model strings inside `meaisinfhoghlaim/`:

- `qwen3-vl-8b` (e.g., `dlt_sources/filesystem/leaving_cert_source.py:62` — `LC_PDF_KIND_REGISTRY` regex map)
- `gemma-4-26B-A4B` (L72)
- `molmo2-8b` (L75)
- `glm-4.6v-flash` (L83)
- `deepseek-ocr-2`, `dots-ocr`, `paddleocr-vl-1.6`, `internvl3-8b`, `qwen3-vl-30b-a3b`, `qwen3-vl-4b`, `molmo2-4b`, `gemma-3-4b`, `granite-docling-258M`, `unstract-api`, `docling-serve` — all appear in `meaisinfhoghlaim/ocr/ensemble/ensembled_extractor.py` docstring + `meaisinfhoghlaim/models/registry.py`

All are in the canonical registry.

---

## 9. BAML + CocoIndex + Dagster coverage of the 10 OCR models per `meaisinfhoghlaim-ocr-htr`

`orchestration/defs/2_materials/meaisin_ocr_htr/ocr_model_assets.py:39-58` declares `OCR_MODELS` as 19 keys (not 10 — the user-mentioned spec likely refers to a subset or an older list). For completeness, the 19 are covered:

| Model | dlt source | BAML function | CocoIndex App | Dagster asset |
|:--|:--|:--|:--|:--|
| `deepseek-ocr-2` | `dlt_sources/filesystem/leaving_cert_source.py` docstring L25-31 (select_ocr_backend reference); `dlt_sources/filesystem/leaving_cert_source.py:62` regex map default fallback | `baml_src/clients_llama_swap.baml` docstring L51 (transformers-only, no llama-swap) | n/a | `ocr_model_deepseek_ocr_2_*` (3 assets + 3 checks) |
| `docling-serve` | `dlt_sources/filesystem/leaving_cert_source.py:64` (not in `LC_PDF_KIND_REGISTRY`; routed via fallback) | `baml_src/clients_ocr_ensemble.baml:22` named `Docling` client (Path 1 ensemble) | n/a | `ocr_model_docling_serve_*` |
| `dots-ocr` | `dlt_sources/filesystem/leaving_cert_source.py:75` (not directly, but via CLASSICAL_OCR stack `dots-ocr`) | n/a (no BAML function) | `cocoindex_flows/corpus/duchas_embedding.py:19` (referenced in docstring) | `ocr_model_dots_ocr_*` |
| `gemma-3-4b` | `dlt_sources/filesystem/leaving_cert_source.py` not in L62-L83 map; routed via `select_ocr_backend()` | `baml_src/clients_ocr_ensemble.baml` docstring + Path 4 spec | `orchestration/defs/3_model_lifecycle/federated_ocr/defs.yaml` uses `model_name: gemma-3-4b` (L11) | `ocr_model_gemma_3_4b_*` |
| `glm-4.6v-flash` | `dlt_sources/filesystem/leaving_cert_source.py:83` (`GAEILGE_MODEL_KEY`) | n/a | n/a | `ocr_model_glm_4_6v_flash_*` |
| `internvl3-8b` | `dlt_sources/filesystem/leaving_cert_source.py` not in L62-L83 map | n/a | n/a | `ocr_model_internvl3_8b_*` |
| `llama-3.2-vision-11b` | `dlt_sources/filesystem/leaving_cert_source.py` not in L62-L83 map | n/a | n/a | `ocr_model_llama_3_2_vision_11b_*` |
| `molmo2-4b` | `dlt_sources/filesystem/leaving_cert_source.py` not in L62-L83 map | n/a | n/a | `ocr_model_molmo2_4b_*` |
| `molmo2-8b` | `dlt_sources/filesystem/leaving_cert_source.py:75` (marking-scheme regex) | n/a (transformers-only per `clients_llama_swap.baml` docstring L48) | `cocoindex_flows/knowledge_graph/youtube_kg_embedding.py:201, 388, 406` (per-frame diagram pointing) | `ocr_model_molmo2_8b_*` |
| `olmocr-2-7b-1025` | `dlt_sources/filesystem/leaving_cert_source.py` not in L62-L83 map | n/a | n/a (referenced in `cocoindex_flows/media/ocr_aware_flow.py:11` docstring) | `ocr_model_olmocr_2_7b_1025_*` |
| `paddleocr-vl-1.6` | `dlt_sources/filesystem/leaving_cert_source.py` not in L62-L83 map | n/a | n/a | `ocr_model_paddleocr_vl_1_6_*` |
| `qwen3-vl-30b-a3b` | `dlt_sources/filesystem/leaving_cert_source.py` not in L62-L83 map | n/a | n/a | `ocr_model_qwen3_vl_30b_a3b_*` |
| `qwen3-vl-4b` | `dlt_sources/filesystem/leaving_cert_source.py` not in L62-L83 map | n/a | n/a | `ocr_model_qwen3_vl_4b_*` |
| `qwen3-vl-8b` | `dlt_sources/filesystem/leaving_cert_source.py:67, 83` (LC exam-paper regex + default fallback) | `baml_src/clients_llama_swap.baml:15, 38` (`LlamaSwapClient`, `LlamaSwapOCRClient`); `baml_src/clients.baml:48, 100, 189` (`LocalVisionQwen3vl`, `LocalVision`, `BIEPV3Vision`, `VisionExtractor`) | `notebooks/06_celtic_languages_06_local_documents_subject_viewer.py:52` (LlamaSwap routing); `notebooks/01_overview_setup.py:205`, `notebooks/03_education_pdf_vision_pipeline.py` (side-by-side); `notebooks/08_ocr_ensemble_audit.py:27` (Path 3 ensemble) | `ocr_model_qwen3_vl_8b_*` |
| `qwen3.6-27b-mtp` | `dlt_sources/filesystem/leaving_cert_source.py` not in L62-L83 map | `baml_src/clients_llama_swap.baml:52` (`LlamaSwapReasoningClient`) | n/a | `ocr_model_qwen3.6_27b_mtp_*` |
| `uccix-llama-3.1-8b` | n/a | n/a | n/a | `ocr_model_uccix_llama_3_1_8b_*` |
| `uccix-llama2-13b` | n/a (DEPRECATED 2026-08-15, `available=False`) | n/a | n/a | `ocr_model_uccix_llama2_13b_*` |
| `uccix-mistral-24b` | n/a | n/a | n/a | `ocr_model_uccix_mistral_24b_*` |
| `unstract-api` | `dlt_sources/filesystem/leaving_cert_source.py` not in L62-L83 map | `baml_src/clients_ocr_ensemble.baml:34` (`Unstract` client, Path 2 ensemble) | `notebooks/08_ocr_ensemble_audit.py:22` (Path 2 ensemble output) | `ocr_model_unstract_api_*` |

**Ensemble participation** (per `meaisinfhoghlaim/ocr/ensemble/ensembled_extractor.py:1-L102`):

- Path 1 (BAML) — *no specific model*, uses default BAML Path = `client ExtractEn` (minimax-m3 text path) via the function-specific client. Function `ExtractEnglandEnsembleConsensus` is the canonical entry.
- Path 2 (Unstract) — `unstract-api` (via `clients_ocr_ensemble.baml:34`)
- Path 3 (qwen3-vl) — `qwen3-vl-8b` (via `clients.baml:53, 109`)
- Path 4 (gemma-4) — `gemma-4-26B-A4B` (via `clients.baml:43`)

**Dagster asset `biiep_ocr_ensemble`** (`orchestration/defs/2_materials/ocr_comparison/ensemble_comparison/biiep_ocr_ensemble.py:55`) is the umbrella asset that drives the 4-path ensemble + the per-jurisdiction RAGAS vote.

**OCR_WEBHOOK_URL** (§6) is the modern inbound trigger for per-document `ocr_extraction/<document_id>` materialisation; **not** consumed by `meaisinfhoghlaim/`.
