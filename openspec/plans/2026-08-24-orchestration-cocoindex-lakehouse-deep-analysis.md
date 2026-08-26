# Orchestration + CocoIndex + Lakehouse Deep Analysis (2026-08-24)

> Read-only research subagent deliverable. Working directory:
> `/Users/cianmacandeisigh/dev/kings_college_galway`. Date: 2026-08-24.
>
> **TL;DR.** The platform is *partially* on the modern Dagster
> Components (dg) architecture (1.13+ `dg.load_defs()`) but the
> conversion is **incomplete and inconsistent**: the L3 model-lifecycle
> layer is fully componentised (96 `defs.yaml` instances +
> `CelticModelLifecycleComponent`), but L1 ingestion still uses the
> hand-rolled `@asset` + `safe_dlt_run` pattern from the v4 era, L2
> is half hand-rolled (33 per-jurisdiction `_assets.py` files) and half
> Componentised (BIEP v3), L4 only has 2 asset files, L5 is on its own
> ad-hoc modules. CocoIndex is on v1 (no Live mode yet, no
> `coco.auto_refresh`, no `LiveComponent`). The lakehouse is
> DuckLake 1.0 with Postgres catalog + Garage S3 + Iceberg REST
> (Lakekeeper). Observability is OTel-native with a fan-out collector.

---

## A) Dagster orchestration inventory

### A.1 Top-level inventory

| Path | LOC | What it is |
|---|--:|---|
| `orchestration/__init__.py` | 24 | Package marker |
| `orchestration/_defs_walker.py` | 131 | **FALLBACK** walker for Dagster <1.13; bypasses Python 3.13 tokenizer bug for digit-leading identifiers (`2_m`,`3_model_lifecycle`). Uses `importlib.util.spec_from_file_location`. |
| `orchestration/definitions.py` | 348 | **PRIMARY** code-location entry point. `dg.load_defs(defs_root=_defs_pkg)` → falls back to `_defs_walker.load_defs_via_walker()`. Plus 4 explicit merges: `sync_schedules`, `DagsterDltResource`, UoG exam/official-docs/NUI/personal-archive modules. |
| `orchestration/cli.py` | 69 | Stub CLI; not on the agent hot path. |
| `orchestration/components/__init__.py` | 109 | Re-exports all 5 KCG Components + 5 jurisdiction/topic-scoped Components (BIEP, England boards, Junior Cycle, KCG cognify, OCR ensemble, Federated OCR). |
| `orchestration/components/layer1_ingestion.py` | 324 | `CelticIngestionComponent` + `CelticFederatedOcrComponent`. StateBackedComponent support + `defs_state` resolution. |
| `orchestration/components/layer2_materials.py` | 255 | `CelticMaterialsComponent` — wraps BAML extraction as partitioned `@asset` + `@asset_check`. |
| `orchestration/components/layer3_model_lifecycle.py` | 648 | `CelticModelLifecycleComponent` — emits `is_virtual=True` `@asset` per CocoIndex App. R1-R4 conformance check at execute time. |
| `orchestration/components/layer4_asset_generation.py` | 145 | `CelticAssetGenerationComponent` — wraps marimo/TanStack/oRPC/Hono dashboards. |
| `orchestration/components/layer5_agent_ops.py` | 340 | `CelticAgentOpsComponent` — emits 5 assets per agent (health, routing, memory, event, trace). |
| `orchestration/components/biep_subject_component.py` | 152 | BIEP v3 jurisdiction-scoped Component. |
| `orchestration/components/biiep_ocr_ensemble_component.py` | 267 | 4-path OCR ensemble Component. |
| `orchestration/components/england_board_subject_component.py` | 122 | England board (AQA/OCR/Edexcel) Component. |
| `orchestration/components/england_cross_board_comparator_component.py` | 78 | England cross-board comparator. |
| `orchestration/components/junior_cycle_subject_component.py` | 204 | JC CBA/ShortCourse/Subject Component. |
| `orchestration/components/kcg_cognify_component.py` | 374 | KCGCognifyComponent + CognifyIngestSensorsComponent + KCGSubjectPilotFactoryComponent. |
| `orchestration/resources.py` | 868 | **22 `ConfigurableResource` subclasses**: DuckDB / LanceDB / IcebergCatalog / LanceNamespace / GeoParquet / Memgraph / Neo4j / FalkorDB / TemporalGraph / CogneeMemory / DuckLake / Firecrawl / Browserbase / AgenticCrawler / OCRModelRegistry / GaelicMetrics / UnslothTraining / BAMLGeneration / ImageGeneration / Translation / Terminology / ProgressTracker / LiteLLM. |
| `orchestration/partitions.py` | 551 | **Legacy** partition definitions (208 / 780 partition schemes — DEPRECATED per the v2 comment). |
| `orchestration/partitions_v2.py` | 326 | **Canonical** partitions: `ireland_curriculum_partitions` (4) + `biiep_v3_scope_year_partition` (2-axis scope×year). |
| `orchestration/storage/ducklake_client.py` | 178 | **DEPRECATED** — kept only for backwards compat. Canonical impl is `dlt_sources.common.destinations_cianfhoghlaim`. |
| `orchestration/dbt_translator.py` | 91 | dbt → DuckLake bridge for BIEP v3. |
| `orchestration/verification.py` | 212 | Store-backed asset-check helpers. THE RULE: "An asset check queries the destination. It never asserts against the upstream asset's return value." Returns `None` on failure → check must fail. |
| `orchestration/defs.yaml` | 28 | Root `DefsFolderComponent`. |
| `orchestration/automation/sync_schedules.py` | 90 | 3 cron schedules: `sync_health_every_4h` / `dagster_sync_health_every_4h` / `baml_sync_health_every_4h`. |
| `orchestration/automation/biiep_daily_automation.py` | 68 | BIEP daily automations. |
| `orchestration/automation/biiep_scheduling.py` | 187 | BIEP cron wiring. |
| `orchestration/automation/subject_backfill.py` | 27 | Backfill helper. |
| `orchestration/sensors/__init__.py` + 14 sensors | 1,488 | 11 hand-written sensors: NCCA/CCEA/SQA/WJEC/Guernsey/IoM/Jersey/JCQ registry sensors, OCR completion sensor, garage PDF arrival, upstream breaking change, meaisin education ops, cognee health check. |
| `orchestration/defs/sensors/england_change_detection_sensor.py` | 193 | England change-detection. |
| `orchestration/defs/sensors/examinations_paper_sensor.py` | 170 | Examinations.ie paper-arrival sensor. |
| **Total orchestration .py** | **127 files / ~5,000 LOC core + 19,464 total** |

### A.2 The 5 layers — `orchestration/defs/<layer>/`

| Layer | Path | Asset count | Style | Notes |
|---|---|--:|---|---|
| **1_ingestion** | `defs/1_ingestion/` | 2 dirs (apple_photos, cognee_health, curriculum, law, _layer) | **Hybrid** — dirs exist but mostly empty | The hand-rolled `@asset` files from `_base/` are intentionally disabled (see `definitions.py:189`); the BIEP sources live in `2_materials/` instead. |
| **2_materials** | `defs/2_materials/` | 41 dirs (`_base/`, `baml_extraction/`, `biiep_v3/`, `crown_dependencies_education/`, `endpoint_health/`, `england_education/`, `eu_multilingual/`, `filesystem_pipelines/`, `grading/`, `guernsey_education/`, `heritage_pipelines/`, `ie_law/`, `ireland_education/`, `isle_of_man_education/`, `jersey_education/`, `junior_cycle/`, `language_pipelines/`, `lc_extraction/`, `meaisin_*/`, `northern_ireland_education/`, `official_media/`, `pdf_processing/`, `portal_eval/`, `root_pdf_assets.py`, `scotland_education/`, `sct_wls_ni_education/`, `tg4_foghlaim/`, `wales_education/`) | **Mixed** — BIEP uses Components via `defs.yaml`; the 33 per-subject/per-jurisdiction Python `@asset` modules are still hand-rolled (the legacy v4 path). |
| **3_model_lifecycle** | `defs/3_model_lifecycle/` | 5 dirs (`cocoindex_v1/`, `cognify/`, `cross_archive/`, `federated_ocr/`, `lc_cognify/`, `legal_research/`) + `defs.yaml` | **Modern Components** — 96 `cocoindex_v1/<name>/defs.yaml` files, each backed by `CelticModelLifecycleComponent`. The `_schedules/defs.yaml.planned` is intentionally disabled (it tried to use `dagster.schedule` which is NOT a Component). |
| **4_asset_generation** | `defs/4_asset_generation/` | 5 dirs (`_layer/`, `education_asset_assets.py`, `marimo_dashboards/`, `orpc_routes/`, `secrets/`, `tanstack_pages/`) | **Hybrid** — the marimo_dashboards uses Components (`CelticAssetGenerationComponent`) but the rest is hand-rolled. |
| **4_budget** | `defs/4_budget/` | 1 file `firecrawl_budget_asset.py` | **Hand-rolled** — Firecrawl budget tracking asset. |
| **4_memory** | `defs/4_memory/` | 1 file `docs_index_memory_job.py` | **Hand-rolled** — docs_index memory job. |
| **5_agent_ops** | `defs/5_agent_ops/` | 5 dirs (`_layer/`, `adk/`, `agno/`, `custom/`, `meaisinfhoghlaim/`, `credential_assets.py`, `heritage_assets.py`) | **Hand-rolled** — the 12-agent fleet surfaces via individual assets + checks, NOT via `CelticAgentOpsComponent` YAML defs. |

### A.3 The new flat-file additions (post-2026-08-22)

| File | LOC | Purpose | Style |
|---|--:|---|---|
| `orchestration/defs/uog_exam.py` | 96 | UoG exam-papers SSO pipeline (5 assets + nightly schedule) | Hand-rolled `@asset` |
| `orchestration/defs/uog_official_docs.py` | 177 | UoG 5 official-doc assets (Stage 0 audit → DuckLake sink) | Hand-rolled `@asset` |
| `orchestration/defs/uog_personal_archive.py` | 325 | UoG personal-archive (Stage 0 → Stage 6 with typed_join) | Hand-rolled `@asset` |
| `orchestration/defs/uog_personal_archive_figures.py` | 362 | 6 thesis-figure PDFs (matplotlib) | Hand-rolled `@asset` |
| `orchestration/defs/uog_students_union.py` | 75 | 2 Students' Union assets | Hand-rolled `@asset` |
| `orchestration/defs/nui_federation.py` | 93 | NUI 3-asset federation (audit + scrape + archive) | Hand-rolled `@asset` |
| `orchestration/defs/british_isles_tertiary.py` | 111 | QUB/Ulster factory (5 assets, **off-by-default** via `pyproject.toml` opt-in) | Hand-rolled `@asset` |
| `orchestration/defs/media_intel.py` | 809 | **The big one** — 5-layer media-intel spine (5 L1 DLT + 8 official sub-buckets + 5 L2 BAML + 2 L3 CocoIndex + 2 L4 marimo + 1 L5 ADK + 1 asset_check) | Hand-rolled, multi-group |
| `orchestration/defs/sync_assets.py` | 1,092 | The canonical sync_health / dagster_sync_health / baml_sync_health jobs (Layer 6/7) | Hand-rolled + `define_asset_job` |

**Observation:** the 2026-08-23 batch (UoG exam, official-docs, personal-archive, NUI federation, BI tertiary, media-intel) **bypasses the 5-layer Component architecture** in favour of hand-rolled `@asset` per module. This is a regression for consistency — the file format diverges from the rest of the L3.

### A.4 Sensors (16 total)

| Sensor | Purpose | File |
|---|---|---|
| `ncca_registry_sensor.py` | NCCA curriculum change detection | `sensors/` |
| `ccea_registry_sensor.py` | CCEA (NI) change detection | `sensors/` |
| `sqa_registry_sensor.py` | SQA (Scotland) change detection | `sensors/` |
| `wjec_registry_sensor.py` | WJEC (Wales) change detection | `sensors/` |
| `jcq_registry_sensor.py` | JCQ (UK joint) change detection | `sensors/` |
| `jersey_registry_sensor.py` | Jersey change detection | `sensors/` |
| `guernsey_registry_sensor.py` | Guernsey change detection | `sensors/` |
| `isle_of_man_registry_sensor.py` | IoM change detection | `sensors/` |
| `ocr_completion_sensor.py` | OCR ensemble completion | `sensors/` |
| `meaisin_education_ops_sensor.py` | meaisin education ops | `sensors/` |
| `garage_pdf_arrival_sensor.py` | Garage S3 PDF arrival | `sensors/` |
| `upstream_breaking_change_sensor.py` | Upstream breaking-change detection (DLT/Dagster/LanceDB/MotherDuck/CocoIndex) | `sensors/` |
| `cognee_health_check_sensor.py` | Cognee health probe | `sensors/` |
| `jobs.py` | Job helpers | `sensors/` |
| `england_change_detection_sensor.py` | England-specific change detection | `defs/sensors/` |
| `examinations_paper_sensor.py` | Examinations.ie paper-arrival | `defs/sensors/` |

### A.5 Partitions — the explosion vs. the v2 fix

`partitions.py` has **208** NCCA partitions (4 cycles × 26 subjects × 2 languages) and **780** SEC partitions (26 subjects × 10 years × 3 levels) — explicitly **DEPRECATED**.

`partitions_v2.py` collapses them:
- `ireland_curriculum_partitions` — **4** (early_childhood / primary / junior_cycle / senior_cycle) with subject selection at runtime via `CURRICULUM_CONFIG_SCHEMA`.
- `biiep_v3_scope_year_partition` — 2-axis (scope × year). The scope partition is `DynamicPartitionsDefinition(name="cianhoghlaim_scope")` keyed on `<jurisdiction>__<stage>__<subject_slug>__<board>__<qualification_level>__<language>` (note the **typo `cianhoghlaim_scope`** missing the 'a' — pre-existing, documented as a separate migration).

### A.6 The 22 Resources

The `resources.py` file holds 22 `ConfigurableResource` subclasses. The cluster focuses on:

- **Lakehouse stack**: `DuckDBResource` (with spatial extension), `LanceDBResource` (BIEP v3 canonical = `BAAI/bge-m3` 1024-d, legacy = `paraphrase-multilingual-MiniLM-L12-v2` 384-d), `IcebergCatalogResource`, `LanceNamespaceResource`, `GeoParquetResource`, `DuckLakeResource` (uses `dlt_sources.common.destinations_cianfhoghlaim` not the local deprecated `ducklake_client`).
- **Graph backends**: `MemgraphResource`, `Neo4jResource` (legacy), `FalkorDBResource` (primary), `TemporalGraphResource`, `CogneeMemoryResource` (falkordb primary → memgraph fallback).
- **Crawler stack**: `FirecrawlResource`, `BrowserbaseResource`, `AgenticCrawlerResource`.
- **OCR/Training**: `OCRModelRegistry`, `GaelicMetricsResource`, `UnslothTrainingResource`.
- **Generation**: `BAMLGenerationResource`, `ImageGenerationResource`, `TranslationResource`, `TerminologyResource`.
- **Orchestration**: `LiteLLMResource`, `ProgressTrackerResource`.

> **Issue: `all_resources` dict is dead code.** The comment at `definitions.py:259` notes that `all_resources` was never wired into any `Definitions`; only the explicit `defs = dg.Definitions.merge(defs, dg.Definitions(resources={"dlt": DagsterDltResource()}))` line is what actually supplies the `dlt` resource key.

### A.7 The `_defs_walker.py` fallback + Python 3.13 tokenizer bug

`_defs_walker.py` documents the Python 3.13 tokenizer bug for digit-leading identifiers (e.g. `2_materials`, `3_model_lifecycle`). The workaround uses `importlib.util.spec_from_file_location` to bypass `from xorch.X.Y import ...`. The `definitions.py:73-92` block calls `dg.load_defs(defs_root=_defs_pkg)` (Dagster 1.13+ canonical) and only falls back to the walker on `AttributeError`.

The walker is **explicitly retained** because `dg.load_defs()` is the canonical path but the walker covers environments where Dagster <1.13 is installed.

### A.8 4 cross-stack lineage contracts (verified from `definitions.py`)

1. **Jurisdiction factory** — `_base/<jurisdiction>_assets.py` is **disabled** (comment block at lines:189-205). The 10 jurisdictions are *intended* to flow through `JurisdictionAssetsBase`, but the broken runtime forces them through `2_materials/<jurisdiction>_education/generic_<jurisdiction>_assets.py` instead. Wave 1 of the KCG roadmap = repair the `_base` factory.
2. **Registry drift alert** — `sync_assets.py` `registry_drift_alert` is auto-discovered by `dg.load_defs()`, so the explicit merge only adds the job + sensor (lines:226-252).
3. **`@dlt_assets` resource wiring** — `definitions.py:267-280` is the only place that actually supplies the `dlt` resource key (`DagsterDltResource()`).
4. **UoG + NUI + BI tertiary merges** — `definitions.py:319-345` is a 5-element loop that dynamically imports each module and merges assets via `__all__`. The pattern is "if it has `__all__` and the names are callable, merge them".

### A.9 Verdict — components vs. legacy

| Aspect | State |
|---|---|
| Components framework | **Dagster 1.13+** `dg.load_defs()` + `DefsFolderComponent` + `[tool.dg]` registry_modules = `["orchestration.components"]`. Confirmed at `pyproject.toml` (per `definitions.py:68`) and `defs.yaml:27`. |
| L1 Ingestion | **Legacy** — `@dlt_assets` + `safe_dlt_run`. The `CelticIngestionComponent` exists but no `1_ingestion/*/defs.yaml` files instantiate it (only `_layer/` shells). |
| L2 Materials | **Mixed** — BIEP v3 uses `BIEPSubjectComponent` via `defs.yaml`. The 33 per-subject Python `@asset` files are hand-rolled. |
| L3 Model Lifecycle | **Modern** — 96 `defs.yaml` files instantiate `CelticModelLifecycleComponent`. |
| L4 Asset Generation | **Mixed** — `marimo_dashboards/` uses Component, the rest is hand-rolled. |
| L4 Budget / Memory | **Legacy** — single hand-rolled files. |
| L5 Agent Ops | **Legacy** — ad-hoc `adk/`, `agno/`, `custom/`, `meaisinfhoghlaim/` modules. The `CelticAgentOpsComponent` exists but is not instantiated from YAML anywhere. |
| Schedules | **Legacy** — `automation/sync_schedules.py` uses `@schedule` decorators (not Components). |
| Sensors | **Legacy** — `sensors/*.py` uses `@sensor` decorators. |

**Conclusion:** Dagster is on the Components path **but only the L3 layer is fully Componentised**. The other layers are partially converted, with significant legacy `@asset` surface remaining. This is consistent with the 2026-08-13 Phase A plan + the 2026-08-14 v8 update that bumped to Dagster 1.13.

---

## B) CocoIndex v0 → v1 migration opportunities

### B.1 Current state — v1, but on the legacy `coco.App` model

The `_lifespan.py` is v1 (`@coco.lifespan`, `ContextKey[SentenceTransformerEmbedder](..., detect_change=True)`, the `coco_lancedb.LanceAsyncConnection`). The PyPI `cocoindex` package is **not installed** (comment at `_lifespan.py:59` — `COCOINDEX_AVAILABLE = False` causes the lifespan to no-op). The repo's own `cocoindex_flows/_shared/` directory shadows the import.

Apps themselves use the v1 pattern but **don't use any v1.0+ Live features**. Every `coco.App(coco.AppConfig(name=...))` is module-scope, with the canonical 14 Apps enumerated in `_lifespan.py:14-29`.

The `_lifespan.py` supports v1 (`detect_change=True` on the embedder ContextKey means a model swap auto-re-embeds — that's a v1-only feature).

### B.2 v1 features NOT yet adopted (gap analysis)

| v1 feature | Source | Adopted? | Where it would go |
|---|---|---|---|
| **Live mode** (`app.update_blocking(live=True)`) | cocoindex.io/docs/programming_guide/live_mode/ | ❌ | `lc_subjects/defs.yaml`, `leabharlann_embedding.py`, all 96 cocoindex_v1 Apps |
| **`LocalComponent` protocol** (`process()` + `process_live(operator)`) | cocoindex.io/docs/advanced_topics/live_component/ | ❌ | None — would require rewriting each App's main function as a class |
| **`LiveMapView` / `LiveMapFeed`** | same | ❌ | The `leabharlann` Apps that watch `leabharlann/`, `cognee_health`, `apple_photos` |
| **`coco.auto_refresh(interval=...)`** | same | ❌ | The `upstream_blog_monitor` + `upstream_api_surface` + `apple_photos_metadata` Apps that poll external sources |
| **Target state declarative** (`declare_row(...)`, `declare_file(...)`) | cocoindex.io/docs/programming_guide/target_state/ | ❌ (current pattern uses `mount_table_target` directly) | All target declarations |
| **Schema-evolution handling** (CocoIndex detects schema change → alter in place / drop-and-recreate) | same | ❌ | LC subject schema evolution |
| **`SingleWatcherGuard`** for `watch()` | cocoindex.io/docs/advanced_topics/live_component/#single-subscriber-contract | ❌ | New connectors that add live support |
| **`@coco.fn(memo=True)`** | programming_guide/function | ✅ Partial | Already used in 306 places (per `cocoindex_flows/AGENTS.md:62`) |
| **`Annotated[NDArray, EMBEDDER]`** | skill description | ❌ | Replace hand-rolled embedder columns |
| **`batching=True`, `runner=coco.GPU`, `as_async`, `version`, `deps`, `logic_tracking`** | skill description | ❌ | Performance optimisation |
| **Polars / Pandas DataFrame I/O** (v1 SDK overview) | programming_guide/sdk_overview | ❌ | `unified_embedding.py` could use Polars for transform |

### B.3 Concrete migration opportunities (with target Apps)

1. **`leabharlann_embedding.py`** (38 KB, the biggest) — convert from `mount_table_target` direct + module-scope `app` to a `LocalComponent` class with `process()` (initial scan via `localfs.walk_dir(...).items()`) + `process_live(operator)` (file watcher via `LiveMapView`). Estimated impact: replaces the 3-hr full rescan with second-level incremental updates on `leabharlann/`.

2. **`upstream_blog_monitor.py`** + **`upstream_api_surface.py`** — wrap the polling loop in `coco.auto_refresh(process_fn, interval=datetime.timedelta(hours=6))`. Estimated impact: makes the Apps lazy — currently they block 2-5 min on each `update()`.

3. **`apple_photos_geospatial.py`** (the r4_exempt App) — convert to `LiveComponent` with a `watch()` that subscribes to osxphotos change events. Estimated impact: real-time photo-index updates.

4. **`unified_embedding.py`** (22 KB) — convert to target-state declarative API: `target = lance.mount_table_target(...); target.declare_row(row=ChunkEmbedding(...))` instead of the current imperative flow. Estimated impact: schema-evolution handling + automatic deletion reconciliation.

5. **`code_embedding.py`** + **`codebase_graph.py`** — these watch the codebase (incremental by file mtime). `localfs.walk_dir(sourcedir, live=True).items()` is the canonical pattern. Estimated impact: replaces the `CCC_REINDEX_CRON` with native CocoIndex live mode.

6. **`leabharlann_flow.py`** + **`leabharlann_inbox/`** — same pattern. The Apple-photos geospatial sibling already does this with `localfs` watchfiles; the leabharlann version can use the same `LiveMapView` from `localfs`.

### B.4 Risk / dependency

- The PyPI `cocoindex` package is **not installed** (per `_lifespan.py:59-69`). All existing apps degrade gracefully via `COCOINDEX_AVAILABLE = False`. Before any v1-feature adoption, `uv add cocoindex>=1.0,<2.0,!=1.0.8` must land in `pyproject.toml`.
- The repo's own `cocoindex_flows/` directory shadows the package name. The 88 L3 defs.yaml files use the **wrong module path** (`cianfhoghlaim.cocoindex.<app>` instead of `cocoindex_flows.<subpkg>.<app>`). This is documented at `layer3_model_lifecycle.py:295-303` as a "Wave 0 item in the KCG refactor roadmap".

---

## C) Observability stack analysis

### C.1 Files (13 modules)

| File | LOC | Purpose |
|---|--:|---|
| `observability/__init__.py` | 71 | Re-exports `env_config`, `langfuse_config`, etc. |
| `observability/env_config.py` | 300 | **Canonical `CIANFHOGHLAIM_*` env-var matrix** — 7 vars (LITELLM / LANGFUSE / MLFLOW / FALKORDB / LANCEDB / LOGFIRE / COGNEE_BACKEND). Precedence: `CIANFHOGHLAIM_*` > legacy alias > in-docker DNS default. |
| `observability/agent_tracing.py` | 445 | Agent-specific trace helpers. |
| `observability/fastapi_middleware.py` | 257 | FastAPI OTLP middleware. |
| `observability/langfuse_config.py` | 442 | Langfuse v3 SDK client + `@observe` decorator. Host: `langfuse.cianfhoghlaim.ie` (port-shifted to 3001 on bunchloch to avoid OrbStack). |
| `observability/logfire_config.py` | 464 | Pydantic Logfire SaaS. Uses `OTEL_EXPORTER_OTLP_ENDPOINT` from env_config. |
| `observability/logging.py` | 222 | structlog wiring. |
| `observability/logging_config.py` | 109 | Python `logging` config. |
| `observability/mlflow_config.py` | 426 | MLflow v3 tracking server. |
| `observability/ocr.py` | 423 | OCR-specific telemetry. |
| `observability/platform_tracer.py` | 615 | Platform-level tracer (Datadog LLMObs + Langfuse + Logfire fan-out). |
| `observability/ragas_evaluator.py` | 327 | RAGAS evaluation as a Dagster asset_check. |
| `observability/unified_tracer.py` | 465 | **The umbrella** — `TracingBackend` ABC with `start_span` / `end_span` / `log_event`. Concrete: `DatadogBackend`, plus fallbacks for Langfuse + Logfire. |
| `observability/dashboards/personal_archive.json` | 102 | Grafana dashboard for UoG personal archive. |

### C.2 Env-var contract (canonical at `docs/observability/env-var-contract.md`)

62 canonical vars across 11 groups. The 4 observability groups are the most-critical:

- **Group 1 — Langfuse SDK** (4 vars): `LANGFUSE_HOST` (canonical: `https://langfuse.cianfhoghlaim.ie`), `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_AUTH_HEADER` (base64(PUBLIC:SECRET) for the otelcol exporter).
- **Group 2 — MLflow** (3 vars): `MLFLOW_TRACKING_URI`, `MLFLOW_EXPERIMENT_NAME`, `MLFLOW_S3_ENDPOINT_URL` (Garage at `:3900`).
- **Group 3 — Logfire + OTel fan-out** (7 vars): `OTEL_EXPORTER_OTLP_ENDPOINT` (canonical: `http://logfire-otel:4317`), `OTEL_SERVICE_NAME`, `LOGFIRE_TOKEN`, etc.
- **Group 4 — Shared cluster identity** (3 vars): Infisical machine-identity.

The other 7 groups cover data ingestion (5 vars + DuckLake 9 vars + MotherDuck 6 vars + LanceDB 3 vars + Garage 9 vars + embedder/model 5 vars + OCR backends 6 vars).

### C.3 OTel fan-out architecture (post-2026-08-25)

`docs/observability/lakehouse-otel-fanout.md` documents the architecture:

```
[cognee + graphiti + falkordb + memgraph + lance-namespace + nimtable + olake + memgraph + lakekeeper]
                              |
                              | OTLP/gRPC + OTLP/HTTP
                              v
                +-------------------------------+
                |       otel-collector           |  (profile: `otel`)
                |   (otel/opentelemetry-collector) |
                +-------------------------------+
                              |
              +---------------+---------------+
              |               |               |
              v               v               v
        +-----------+   +-----------+   +-----------+
        | logfire   |   | langfuse  |   | mlflow    |
        | (cloud)   |   | (self)    |   | (local)   |
        +-----------+   +-----------+   +-----------+
```

10 application services emit traces (per `scripts/lakehouse-stack-doctor.sh` Check 9): lakekeeper, lance-namespace, nimtable, olake, cognee, graphiti, falkordb, memgraph. Storage infra (garage + postgres + clickhouse + redis) and read-only UIs (lancedb-viewer + memgraph-lab) are excluded.

The check enforces `OTEL_EXPORTER_OTLP_ENDPOINT` on every application service — fail CI if missing.

### C.4 The 3 backend integrations

1. **Langfuse** — `langfuse.cianfhoghlaim.ie`. v3 SDK + `@observe`. Lazy-import with `_get_langfuse()`. Port :3001 on bunchloch (3000 collides with OrbStack). Has `auth_header` for the otelcol exporter.

2. **MLflow** — `mlflow.cianfhoghlaim.ie`. Tracking + experiment registry + artifact store (Garage S3). Note the `MLFLOW_TRACKING_URI=postgresql://lakekeeper:${POSTGRES_PASSWORD}@postgres:5432/mlflow` for the lakehouse-OTel profile.

3. **Logfire** — Pydantic Logfire SaaS. The collector fans out to logfire cloud + langfuse + mlflow in local mode. Empty `LOGFIRE_TOKEN` = local OTLP.

### C.5 OpenTelemetry semantic conventions applicability

The OTel semantic conventions (1.44.0) define attributes for `db.*`, `messaging.*`, `gen_ai.*` (moved to `semantic-conventions-genai` repo), `object_stores.*`, `http.*`, `rpc.*`. The current platform does **not** strictly enforce these — Langfuse uses its own event schema, MLflow uses its own run/artifact schema, Logfire passes through arbitrary attributes.

**Recommended alignment:**
- `db.system: duckdb` / `db.namespace: cianfhoghlaim` for all DuckDB / DuckLake queries.
- `object_store.system: s3` + `object_store.bucket.name: ducklake` for Garage writes.
- `gen_ai.system: baml` for BAML extraction calls.
- `gen_ai.request.model: BAAI/bge-m3` for CocoIndex embedding calls.

### C.6 Verdict

The observability stack is **mature and well-architected**:
- Single source of truth for env-vars (`observability/env_config.py`).
- 3 complementary backends (Langfuse + MLflow + Logfire) with a fan-out otel-collector.
- Dagster asset-check pattern for RAGAS evaluation (`observability/ragas_evaluator.py`).
- Grafana dashboard at `observability/dashboards/personal_archive.json` for the new UoG personal archive.

**Gaps:**
- No strict OTel semantic-convention enforcement (use the `db.*` / `object_store.*` / `gen_ai.*` namespaces from the upstream specs).
- The `unified_tracer.py` `TracingBackend` ABC has a `DatadogBackend` concrete but Langfuse + Logfire are wired via the platform_tracer / langfuse_config — there's no common abstract for the 3.

---

## D) DuckLake v1.0 best practices for Irish-education data

### D.1 DuckLake v1.0 specification (upstream)

`ducklake.select/docs/stable/specification/introduction` documents the v1.0 stable spec:

> **Building blocks:** catalog database (SQL-92 transactions + primary keys) + Parquet data files in object storage.

The catalog DB can be any SQL-92 compliant database (the platform uses Postgres — `DUCKLAKE_POSTGRES_HOST=lakehouse-postgres`, port 5433). Data is Parquet in object storage (the platform uses Garage S3 at `DUCKLAKE_BUCKET=ducklake`).

### D.2 The platform's DuckLake deployment

Per `docs/lakehouse/deployment-status-2026-07-19.md`:
- ✅ 6/11 services healthy on `bunchloch`
- ✅ 1,990 BIEP v3 subjects seeded
- ✅ 4 jurisdiction pipelines × 8 jurisdictions = 1,990 cohort rows in 5.4 s
- ✅ 7 Lance datasets exported (5,958 rows)
- ⚠️ MotherDuck token NOT wired

Per `orchestration/storage/ducklake_client.py` (DEPRECATED) and `orchestration/resources.py:DuckLakeResource`:
- `DUCKLAKE_BUCKET` defaults to `ducklake` (verified live)
- `DUCKLAKE_POSTGRES_DB` defaults to `ducklake_cianfhoghlaim` (per the v7 namespace)
- `DUCKLAKE_POSTGRES_PORT` = 5433
- The namespace is `cianfhoghlaim` (the v7 canonical alias, not `oideachais`)
- The ATTACH syntax: `ATTACH 'ducklake:postgres:dbname=... host=... port=... user=... password=...' AS <namespace> (DATA_PATH 's3://<bucket>/<namespace>/')`

### D.3 BIEP v3 namespace convention

The LanceDB table naming pattern (from `cocoindex_flows/AGENTS.md:131`):

| Pattern | Example |
|---|---|
| `cianhoghlaim.<jurisdiction>.<stage>.<subject>.<level>_<lang>_chunks` | `cianhoghlaim.ireland.leaving_cycle.mathematics.untiered_en_chunks` |
| `cianhoghlaim.<jurisdiction>.<stage>.<board>.<subject>_<...>_chunks` | `cianhoghlaim.england.a_level.aqa.mathematics_a_level_chunks` |
| `cianhoghlaim.<vertical>.<sub>.<level>_<lang>` | `cianhoghlaim.lc.gaeilge.hl_ga` |
| bare names | `codebase_chunks`, `codebase_graph`, `codebase_graph_edges` |

### D.4 Recommended DuckLake v1.0 best practices for BIEP

1. **Use the Iceberg REST catalog (Lakekeeper)** for cross-engine compatibility — already wired at `bonneagar/stacks/lakehouse/lakekeeper :8181`. The dlt Iceberg connector should be preferred over the raw DuckLake ATTACH pattern for new data sources.
2. **Partition by `subject` + `board` + `language`** (not by year) — `subject` + `board` + `language` are the BIEP v3 group_name axis. Year should be a hidden partition for incremental loads.
3. **Use `data_inlining`** for small tables (e.g. `media_descriptors`, `apple_photos_metadata`) — per the DuckLake v1.0 spec, "Data Inlining" stores small tables entirely in the catalog database. Reduces the Parquet-file churn.
4. **Time-travel queries** for syllabus-version pinning (e.g. `SELECT ... AT (TIMESTAMP => '2025-09-01')` to reproduce the 2025 syllabus corpus). Per the DuckLake spec, time-travel is a first-class query.
5. **Sort expressions** for the LC chunks tables — `ORDER BY (subject, board, year, language)` per `ducklake.select/docs/stable/specification/tables/ducklake_sort_expression`. Improves BGE-M3 vector retrieval by ensuring like-subjects are co-located.
6. **Conflict resolution** via `MERGE INTO` for incremental loads (per `ducklake.select/docs/stable/duckdb/advanced_features/conflict_resolution`). Use for the daily sync of NUI / British Isles tertiary / personal-archive data.
7. **Data change feed** via the per-table `ducklake_table_changes` function (per the spec) — feeds the Cognee cognify pipeline + the daily cron sensor.
8. **Encryption** for the UoG personal-archive namespace — already required by the student-data policy. Per the v1.0 spec, set `encryption.key-id` per-namespace.
9. **Backups** via snapshots — per the v1.0 spec `ducklake.select/docs/stable/duckdb/maintenance/expire_snapshots`, expire snapshots after 30 days (the BIEP daily cron).

### D.5 Migration from DuckDB → DuckLake

The DuckLake docs ship a migration guide at `ducklake.select/docs/stable/duckdb/migrations/duckdb_to_ducklake`. The platform has **5 active namespaces** per `docs/observability/env-var-contract.md`:
- `ducklake_oideachais` (legacy v4)
- `ducklake_crypteolas` (legacy v4)
- `ducklake_croilar` (legacy v4)
- `ducklake_tuath` (legacy v4)
- `ducklake_meaisinfhoghlaim` (legacy v4)
- `ducklake_aleyum` (legacy v4)
- `ducklake_cianfhoghlaim` (post-v7 canonical)

The 6 legacy namespaces are scheduled for consolidation into `ducklake_cianfhoghlaim` per the env-var contract.

---

## E) Cross-stack inconsistencies

### E.1 Naming drift

1. **Namespace string typo**: `biiep_v3_scope_year_partition` defines `DynamicPartitionsDefinition(name="cianhoghlaim_scope")` — missing the **'a'** in Cianfhoghlaim. Documented at `partitions_v2.py:308-309` as a pre-existing typo that requires a LanceDB migration to fix.

2. **Group name slug conventions drift**:
   - L3: `3_model_lifecycle_cocoindex_v1_<app_slug>` (snake-case from CamelCase App name).
   - L4: `4_asset_generation_<kind>_<slug>` (different slugifier).
   - L5: `agent_health_<name>` / `agent_routing_<name>` / etc. (no group_name prefix — bare asset names).
   - UoG: `group_name="uog_personal_archive"` (singular group, not 2-layer).
   - NUI: `group_name="nui_federation"` (same).
   - BI tertiary: `group_name="bitertiary"` (abbreviation inconsistency with `british_isles_tertiary.py`).
   - Media_intel: `group_name="media_intel_l1_ingestion"` (5 separate groups, no shared prefix).

   **Verdict:** the convention documented at `docs/dagster/group-name-underscore-migration.md` is `{layer}_<domain>_<nation>_<...>` (e.g. `1_ingestion_education_ireland_documents`), but the post-2026-08-22 modules use bare names. **Action:** enforce the convention via `dg check yaml` lint.

3. **Pydantic module paths**: 88 L3 defs.yaml files use `cianfhoghlaim.cocoindex.<app>` (the pre-v7 flat layout) — the actual module path is `cocoindex_flows.<subpkg>.<app>`. Documented at `layer3_model_lifecycle.py:295-303` as Wave 0 in the KCG refactor roadmap. **The Components emit `dg.Failure` with "88 of the 95 L3 defs.yaml files still use the pre-refactor flat layout" — these Apps are broken at execute time.**

4. **Bilingual subject slugs**: `celtic_curriculum_embedding.py` uses `celtic_curriculum_embedding` while `biep_parity` uses `gaeilge` / `english` / `mathematics` (the LC subject slugs). The cross-jurisdiction BIEP naming is `cianhoghlaim.<jurisdiction>.<stage>.<subject_slug>` while the cross-cocoindex naming is `cianhoghlaim.<vertical>.<sub>`. **Two parallel namespace conventions.**

### E.2 Layer-boundary drift

| Layer | What it should hold | What's actually there |
|---|---|---|
| **1_ingestion** | DLT sources only | DLT sources + 2 Apple-Photos + 1 cognee_health check + 4 hand-rolled dirs. The `CelticIngestionComponent` is defined but never instantiated. |
| **2_materials** | BAML extractions + dbt + filesystem raw | 33 per-subject Python `@asset` files + 41 dirs of mixed concerns + the `root_pdf_assets.py` (which is a raw-PDF walker, not BAML). |
| **3_model_lifecycle** | CocoIndex v1 Apps + Cognify | 96 cocoindex_v1 defs.yaml (✅) + `cognify/` + `cross_archive/` + `federated_ocr/` + `legal_research/` (hand-rolled). |
| **4_asset_generation** | marimo + TanStack + oRPC | 2 marimo dirs + `education_asset_assets.py` + `secrets/` (which is config, not asset gen) + `orpc_routes/` + `tanstack_pages/` (no defs.yaml in any of these). |
| **4_budget** | budget tracking | 1 file |
| **4_memory** | memory asset | 1 file |
| **5_agent_ops** | agent health/routing/memory/event/trace | 4 dirs (adk, agno, custom, meaisinfhoghlaim) + 2 hand-rolled files (credential_assets, heritage_assets). The `CelticAgentOpsComponent` is defined but never instantiated. |

The split between `4_asset_generation` / `4_budget` / `4_memory` is **arbitrary**. The number `4` is overused (the upstream Dagster Components model has only 5 layers — no budget / memory sub-layers).

### E.3 Version drift across dlt / cocoindex / dagster / ducklake

| Tool | Version | Notes |
|---|---|---|
| **Dagster** | 1.13+ (canonical per `definitions.py:33` and `defs.yaml:1` comment) | The 1.10.9 fallback via `_defs_walker.py` is retained for backwards compat. The `dg scaffold component` workflow (`docs.dagster.io/guides/build/components/creating-new-components`) uses `dg.Component` + `dg.Model` + `dg.Resolvable` — but the platform uses `@dataclass` + `dg.Component` + `dg.Resolvable` instead (the older API still supported). |
| **dlt** | ≥1.4 (per `agent-observability` skill) | The `dlt_sources/common/destinations_cianfhoghlaim.py` is the canonical DuckLake bridge using dlt's first-party `DuckLakeCredentials`. |
| **CocoIndex** | ≥1.0,<2.0 (excluding 1.0.8) — PyPI package not installed | Repo-local `cocoindex_flows/_shared/_lifespan.py` provides the canonical home. |
| **DuckDB** | current | DuckLake v1.0 spec, Postgres 1x catalog. |
| **DuckLake** | 1.0 (stable spec) | Per `ducklake.select/docs/stable/specification/introduction`. |
| **LanceDB** | current | The PyPI package IS installed (per `_lifespan.py:62-64` import path). |
| **Langfuse** | v3 (per `langfuse_config.py`) | Host: `langfuse.cianfhoghlaim.ie`. |
| **MLflow** | v3 (per `mlflow_config.py`) | Backend: Postgres. |
| **Logfire** | Pydantic Logfire SaaS | Token from Infisical. |
| **OpenTelemetry** | collector + SDK (per `lakehouse-otel-fanout.md`) | Fan-out to logfire + langfuse + mlflow. |
| **Postgres** | current (lakehouse-postgres stack) | 5433, owner `lakekeeper`. |
| **Garage S3** | current | 3900, 93.1 GiB capacity. |

**Drift observations:**
1. The CocoIndex `>=1.0,<2.0,!=1.0.8` pin is documented in the `.agents/skills/cocoindex/SKILL.md` but the `pyproject.toml` is not in scope of this read-only subagent — would need to verify whether the pin is enforced.
2. Dagster 1.13+ is canonical, but the platform still imports from `dagster_dlt` (which is in lockstep with dlt, not Dagster). The 1.10.9 → 1.13 transition is documented as "post-2026-08-14 v8 update" — confirmed via the `dagster` component imports working.
3. `LanceDB` is at 1.0+ (per the skill), but `LanceNamespace` (the REST adapter inside the lakehouse stack) is a separate package.

### E.4 Manifest drift

The `orchestration/AGENTS.md` says **199 assets + 31 jobs + 6 schedules + 16 sensors + 22 asset checks**. The actual count (per the file inventory above):
- Assets: 96 cocoindex_v1 + ~30 L2 + ~10 L4 + 8 L5 + 5 UoG + 3 NUI + 5 BI tertiary + ~20 media_intel + ~5 personal-archive + 2 sync_health = **~190** (close)
- Schedules: 3 sync + 1 BIEP daily + 1 BIEP nightly + 1 UoG exam + others = **~8** (slightly over)
- Sensors: 11 + 2 defs/sensors = **13** (under the documented 16)
- Asset checks: 22 (matches)
- Jobs: 31 (matches — includes 1 BIEP + 1 sync_health + 1 dagster_sync_health + 1 baml_sync_health + UoG + others)

**Verdict:** the AGENTS.md count is a 2026-07-29 estimate; the 2026-08-23 batch has added ~30 assets + ~1 job + ~1 schedule without updating AGENTS.md. The `mise run lint:drift-docs` check should catch this — if not, the AGENTS.md is stale.

---

## F) Recommended cascade order

When DLT sources change (e.g. a new jurisdiction factory is added or a source's schema evolves), the changes propagate in this order:

```
   ┌────────────────────────┐
   │ dlt_sources/           │  ← changes originate
   │  • british_isles/...   │     - new source
   │  • european_nations/   │     - schema change
   │  • commonwealth/       │     - new destination
   └───────────┬────────────┘
               │
               ▼
   ┌────────────────────────┐
   │ orchestration/         │  ← L1 re-mount via CelticIngestionComponent
   │  components/           │     (or hand-rolled @asset for legacy)
   │  defs/1_ingestion/     │
   │  + defs/2_materials/   │  ← BAML extraction re-run via CelticMaterialsComponent
   └───────────┬────────────┘
               │
               ▼
   ┌────────────────────────┐
   │ cocoindex_flows/       │  ← L3 cocoindex v1 App re-run (via CelticModelLifecycleComponent)
   │  • _shared/_lifespan.py │     - R1-R4 conformance auto-checks at execute time
   │  • per-jurisdiction Apps│
   │  • corpus/leabharlann   │
   └───────────┬────────────┘
               │
               ▼
   ┌────────────────────────┐
   │ orchestration/         │  ← L4 marimo dashboards re-render
   │  defs/4_asset_generation/│     (the CelticAssetGenerationComponent emits is_virtual=True
   │  + notebooks/         │      Dagster assets that mirror their upstream)
   └───────────┬────────────┘
               │
               ▼
   ┌────────────────────────┐
   │ observability/         │  ← sync_health cron materialises, syncs to Cognee + CCC
   │  + sync:dagster        │
   │  + sync:cognee         │
   │  + sync:ccc            │
   └────────────────────────┘
```

### F.1 The 7-step cascade (per AGENTS.md `mise run sync:all`)

| # | Layer | What gets rebuilt |
|---|---|---|
| 1 | `sync:paths` | The path-mapping docs are regenerated. |
| 2 | `sync:ccc` | CCC (CocoIndex Code) semantic search index is rebuilt. |
| 3 | `sync:cognee` | Cognee knowledge graph re-cognified. |
| 4 | `sync:skills` | 65 skill metadata files validated. |
| 5 | `sync:mcp` | MCP server list synced to the opencode registry. |
| 6 | `sync:dagster` | DAG asset graph validated; ~190 AST-parsed assets. |
| 7 | `sync:drift-docs` | Every AGENTS.md number-claim validated against ground truth. |

### F.2 Concrete cascade rules

1. **Adding a new DLT source** to `dlt_sources/british_isles/<jurisdiction>/`:
   - Add a `CelticIngestionComponent` instance under `orchestration/defs/1_ingestion/<jurisdiction>/defs.yaml` (the **canonical** new pattern).
   - OR — if the source is per-subject — add a hand-rolled `@asset` to `orchestration/defs/2_materials/<jurisdiction>_education/` (the legacy v4 pattern, still acceptable).
   - Run `dg check yaml` to validate. Run `mise run sync:all` to refresh all 7 layers.

2. **Changing the LanceDB table schema**:
   - Update `_lifespan.py` `LANCEDB_URI` (no-op unless the env var changes).
   - Add a new `@coco.fn` to the relevant CocoIndex App module under `cocoindex_flows/<jurisdiction>/`.
   - The R1-R4 conformance check enforces: `from ._lifespan import shared_lifespan` (R1), canonical `ContextKey` import (R2), `coco.App(...)` at module scope (R3), `@coco.fn(...)` decorator present (R4).

3. **Changing the DuckLake namespace**:
   - Update `orchestration/storage/ducklake_client.py` defaults (no-op if env vars take precedence).
   - The dlt-side `dlt_sources.common.destinations_cianfhoghlaim` is the canonical DuckLake bridge — update its `DuckLakeCredentials` config there.
   - Run the lakehouse smoke-test (`docs/lakehouse/smoke-test-2026-08-09.md`) to verify all 5 services healthy.

4. **Adding a new opencode agent or MCP server**:
   - Append to `opencode.json` `agent` and `mcp` sections.
   - Run `mise run lint:skills` (validates the 65 skill metadata files).
   - Run `mise run sync:all` (refreshes `sync:mcp`).

---

## G) Concrete refactor plan

### G.1 Phased approach (4 waves)

#### Wave 0 — Manifest + module-path repair (Week 1, ~3 days)

**Blocker for everything else.** The 88 L3 `defs.yaml` files use the pre-v7 flat module path (`cianfhoghlaim.cocoindex.<app>`); the actual package is `cocoindex_flows/<subpkg>/<app>`. Without this fix, every CocoIndex App fails at execute time with `cocoindex_v1_module_import_failed`.

| Task | Owner | Effort |
|---|---|---|
| Run `dg check yaml` to enumerate the 88 broken paths. | `dagster` subagent | 1 hr |
| Bulk-rewrite `module:` in `orchestration/defs/3_model_lifecycle/cocoindex_v1/<app>/defs.yaml` to use `cocoindex_flows/<subpkg>/<app>`. | `dagster` subagent | 2 hr |
| Install the PyPI `cocoindex` package: `uv add 'cocoindex>=1.0,<2.0,!=1.0.8'`. | `mise` subagent | 30 min |
| Add the `pyproject.toml` entry: `[tool.dg] registry_modules = ["orchestration.components"]`. | `mise` subagent | 15 min |
| Verify `dg list components` shows the 11 KCG Components. | `dagster` subagent | 30 min |

#### Wave 1 — Componentise L1 ingestion (Week 2, ~5 days)

The L1 layer is the most-regressed (still hand-rolled). Replace the 200+ `@dlt_assets` / `@asset` with `CelticIngestionComponent` instances.

| Task | Owner | Effort |
|---|---|---|
| Audit `dlt_sources/common/` for the 928 source factories. | `data-platform` subagent | 1 day |
| Scaffold `defs/1_ingestion/<jurisdiction>/<source_id>/defs.yaml` per source. | `data-platform` subagent | 2 days |
| Wire the `defs_state` cache for the 5 high-churn sources (NCCA, SEC, CCEA, SQA, WJEC). | `data-platform` subagent | 1 day |
| Run `dg check yaml` + smoke-test on `dagster dev`. | `dagster` subagent | 1 day |

#### Wave 2 — Componentise L2 materials (Week 3, ~5 days)

The L2 layer is half-Componentised. Migrate the 33 per-subject Python `@asset` files to `CelticMaterialsComponent` YAML.

| Task | Owner | Effort |
|---|---|---|
| Audit the 33 `_assets.py` files in `defs/2_materials/`. | `data-platform` subagent | 1 day |
| Migrate 10 LC subjects first (mathematics, chemistry, geography, gaeilge, english, computer_science, physics, biology, french, history). | `data-platform` subagent | 2 days |
| Migrate the remaining 23 subjects. | `data-platform` subagent | 1 day |
| Verify partition-key alignment with `partitions_v2.ireland_curriculum_partitions`. | `data-platform` subagent | 1 day |

#### Wave 3 — Componentise L4 + L5 (Week 4, ~3 days)

| Task | Owner | Effort |
|---|---|---|
| Migrate the 4 marimo_dashboards files to `CelticAssetGenerationComponent`. | `notebooks` subagent | 1 day |
| Migrate the 12-agent fleet to `CelticAgentOpsComponent`. | `agent-platform` subagent | 2 days |

#### Wave 4 — Cleanup + naming-drift fix (Week 5, ~3 days)

| Task | Owner | Effort |
|---|---|---|
| Fix the `cianhoghlaim_scope` typo (the LanceDB migration that the doc-comment promises). | `data-platform` subagent | 1 day |
| Standardize group_name convention: `{layer}_{domain}_{nation}_{...}`. Add a `dg check yaml` rule. | `dagster` subagent | 1 day |
| Update `orchestration/AGENTS.md` counts (currently 199 assets, 31 jobs — actually ~190 assets + ~8 schedules). | `plan` subagent | 1 hr |
| Fix the `_base` factory (`defs/2_materials/_base/<jurisdiction>_assets.py`) — the runtime error from `definitions.py:195-202` says it raises `TypeError: 'IrelandJurisdictionPipeline' object is not callable`. | `dagster` subagent | 1 day |

### G.2 CocoIndex v1 → Live migration (post-Wave-0)

The CocoIndex v1 migration is **a separate workstream** that can run in parallel to the Dagster Componentisation. Track:

| Workstream | Owner | Effort | Risk |
|---|---|---|---|
| Convert `leabharlann_embedding.py` to `LocalComponent` with `localfs.walk_dir(live=True).items()` | `baml` / `cocoindex` subagent | 1 week | High — touches the largest CocoIndex App |
| Wrap `upstream_blog_monitor` + `upstream_api_surface` in `coco.auto_refresh(interval=6h)` | `baml` subagent | 3 days | Low |
| Convert `apple_photos_geospatial` to `LiveComponent` with osxphotos watcher | `agents` subagent | 1 week | Medium — depends on osxphotos change-event API |
| Convert `unified_embedding.py` to target-state declarative API | `baml` subagent | 3 days | Medium — schema-evolution behaviour |
| Convert `code_embedding.py` + `codebase_graph.py` to `localfs.LiveMapView` (replaces CCC cron) | `cocoindex` subagent | 3 days | Low |

### G.3 DuckLake v1.0 hardening (post-Wave-0)

| Workstream | Owner | Effort |
|---|---|---|
| Enable `data_inlining` for small tables (`media_descriptors`, `apple_photos_metadata`, `<6 row tables`) | `data-platform` subagent | 1 week |
| Add `sort expressions` to LC chunks tables (`ORDER BY (subject, board, year, language)`) | `data-platform` subagent | 3 days |
| Add `data change feed` consumption for the Cognee cognify pipeline + the daily cron sensor | `data-platform` subagent | 1 week |
| Enable per-namespace encryption for `ducklake_cianfhoghlaim` (UoG student data policy) | `infrastructure` subagent | 3 days |
| Migrate the 6 legacy namespaces (`ducklake_oideachais`, `ducklake_crypteolas`, etc.) into `ducklake_cianfhoghlaim` | `data-platform` subagent | 2 weeks |
| Set up snapshot expiry policy (30 days for BIEP, 7 days for personal-archive) | `data-platform` subagent | 3 days |

### G.4 Observability hardening (parallel workstream)

| Workstream | Owner | Effort |
|---|---|---|
| Add OTel semantic-convention enforcement: `db.system: duckdb` / `gen_ai.system: baml` / `object_store.system: s3` | `agent-platform` subagent | 1 week |
| Standardise the 3 backend integrations behind the `TracingBackend` ABC (currently Datadog is the only concrete) | `agent-platform` subagent | 1 week |
| Add `mise run sync:drift-docs` enforcement that the 192 asset count matches the actual YAML count | `dagster` subagent | 3 days |

### G.5 Component-aligned canonical structure (target)

After all 4 waves complete, the canonical structure should be:

```
orchestration/
├── components/                           # Python class definitions (10 components)
│   ├── layer1_ingestion.py               # CelticIngestionComponent
│   ├── layer2_materials.py               # CelticMaterialsComponent
│   ├── layer3_model_lifecycle.py         # CelticModelLifecycleComponent
│   ├── layer4_asset_generation.py        # CelticAssetGenerationComponent
│   ├── layer5_agent_ops.py               # CelticAgentOpsComponent
│   ├── biiep_subject_component.py        # BIEP v3 (jurisdiction-scoped)
│   ├── biiep_ocr_ensemble_component.py   # 4-path OCR ensemble
│   ├── england_board_subject_component.py
│   ├── england_cross_board_comparator_component.py
│   ├── junior_cycle_subject_component.py
│   ├── kcg_cognify_component.py
│   └── federated_ocr_component.py
├── defs/
│   ├── defs.yaml                          # DefsFolderComponent
│   ├── 1_ingestion/                       # L1: DLT sources via CelticIngestionComponent
│   │   ├── _layer/
│   │   ├── ireland/
│   │   │   ├── education/
│   │   │   │   ├── ncca/defs.yaml
│   │   │   │   ├── sec/defs.yaml
│   │   │   │   └── examinations/defs.yaml
│   │   │   ├── law/
│   │   │   │   └── courts/defs.yaml
│   │   │   └── university/
│   │   │       ├── official_docs/defs.yaml
│   │   │       ├── personal_archive/defs.yaml
│   │   │       └── exam/defs.yaml
│   │   ├── england/
│   │   ├── scotland/
│   │   ├── wales/
│   │   ├── northern_ireland/
│   │   ├── jersey/
│   │   ├── guernsey/
│   │   ├── isle_of_man/
│   │   ├── nui_federation/defs.yaml
│   │   ├── british_isles_tertiary/defs.yaml
│   │   └── media_intel_l1/defs.yaml
│   ├── 2_materials/                       # L2: BAML extraction via CelticMaterialsComponent
│   │   ├── _layer/
│   │   ├── ireland_education/
│   │   │   ├── mathematics/defs.yaml
│   │   │   ├── chemistry/defs.yaml
│   │   │   ├── gaeilge/defs.yaml
│   │   │   └── ... (28 more subjects)
│   │   ├── england_education/
│   │   ├── scotland_education/
│   │   ├── ... (10 jurisdictions)
│   │   ├── baml_extraction/
│   │   ├── biiep_v3/
│   │   └── ... (per-domain)
│   ├── 3_model_lifecycle/
│   │   ├── _layer/
│   │   ├── cocoindex_v1/                   # L3: CocoIndex v1 via CelticModelLifecycleComponent (96 defs.yaml)
│   │   │   ├── lc_subjects/defs.yaml
│   │   │   ├── leabharlann_books/defs.yaml
│   │   │   └── ... (94 more)
│   │   ├── cognify/
│   │   ├── federated_ocr/
│   │   └── cross_archive/
│   ├── 4_asset_generation/
│   │   ├── _layer/
│   │   ├── marimo_dashboards/              # L4: marimo via CelticAssetGenerationComponent
│   │   ├── tanstack_pages/
│   │   ├── orpc_routes/
│   │   └── education_asset_assets.py
│   ├── 5_agent_ops/
│   │   ├── _layer/
│   │   ├── adk/
│   │   ├── agno/
│   │   ├── custom/
│   │   ├── meaisinfhoghlaim/
│   │   └── credential_assets.py
│   ├── sensors/
│   │   ├── england_change_detection_sensor.py
│   │   └── examinations_paper_sensor.py
│   ├── uog_personal_archive_figures.py    # Single thesis-figure asset (no per-asset defs)
│   └── sync_assets.py                     # Layer 6/7 sync_health assets
├── automation/                            # @schedule decorators (legacy; not componentisable in 1.13)
│   ├── sync_schedules.py
│   ├── biiep_daily_automation.py
│   └── biiep_scheduling.py
├── sensors/                               # @sensor decorators (legacy; not componentisable in 1.13)
│   └── ... (11 sensors)
├── definitions.py                         # PRIMARY: dg.load_defs()
├── resources.py                           # 22 ConfigurableResource subclasses
├── partitions.py                          # DEPRECATED (kept for back-compat)
├── partitions_v2.py                       # CANONICAL (4 + 2-axis)
├── verification.py                        # Store-backed asset-check helpers
├── storage/
│   └── ducklake_client.py                 # DEPRECATED (kept for back-compat)
├── dbt_translator.py                      # dbt → DuckLake bridge
└── _defs_walker.py                        # FALLBACK (Dagster <1.13)

cocoindex_flows/
├── _shared/                                # Shared lifespan + utilities
│   ├── _lifespan.py
│   ├── caighdean_standardize.py
│   ├── cli.py
│   ├── cocoindex_query_api.py
│   ├── languages.py
│   ├── repo_embedding.py
│   ├── repo_type_detector.py
│   └── reranker.py
├── biep_parity/                            # 14 + 88 + 147 + 129 = 378 Apps
├── british_isles/
│   ├── england/
│   ├── ireland/                             # 5 ie_law + canuint + ireland_legal
│   └── university/
├── celtic/                                  # 6 Apps (gaeilge, gaois, ud_celtic, mythology, multilingual, curriculum)
├── commonwealth/
├── commonwealth_cross/
├── corpus/                                  # 8 large Apps (leabharlann_embedding 38KB, unified_embedding 22KB, ...)
├── european_nations/
│   ├── _factory.py                          # 40-nation collapse (224 LOC + 40 shims)
│   └── albania/ ... ukraine/                # 40 shims (1-line each)
├── european_nations_cross/
├── european_union/
├── american_nations/
├── infrastructure/                          # Codebase + API + filesystem + storage + config indexes
├── knowledge_graph/
├── media/                                   # Apple Photos + OCR + Artwork + CV
├── media_intel/                             # Reference corpus spine (Class A-E + 8 official)
├── portfolio/
└── subjects/

observability/
├── env_config.py                            # CANONICAL env-var matrix (CIANFHOGHLAIM_*)
├── agent_tracing.py
├── fastapi_middleware.py
├── langfuse_config.py
├── logfire_config.py
├── logging.py
├── logging_config.py
├── mlflow_config.py
├── ocr.py
├── platform_tracer.py                       # 3-backend fan-out (Langfuse + MLflow + Logfire)
├── ragas_evaluator.py
├── unified_tracer.py                        # TracingBackend ABC + Datadog concrete
└── dashboards/
    └── personal_archive.json                 # Grafana dashboard
```

### G.6 Verdict

The platform has **strong bones** — the 5-layer Dagster Component architecture is well-conceived, CocoIndex v1 (sans Live mode) is in production, DuckLake v1.0 is wired with the canonical 3-bucket setup, observability is mature with a fan-out collector.

The **biggest gaps** are:

1. **Module-path shadowing** in L3 — 88 defs.yaml files use the pre-v7 path. Blocks the entire CocoIndex pipeline at execute time. **Wave 0 blocker.**
2. **Layer 1 has zero Component instances** — the entire L1 layer is hand-rolled. The `_base` factory is broken. **Wave 1 priority.**
3. **Naming drift** between layer boundaries — the post-2026-08-23 batch (UoG, NUI, BI tertiary, media_intel) bypasses the convention. **Wave 4 cleanup.**
4. **AGENTS.md drift** — the 199 / 16 / 22 counts are stale. **Wave 4 cleanup.**
5. **CocoIndex v1 Live features not adopted** — the Big Refactor opportunity. **Parallel workstream.**
6. **DuckLake v1.0 best practices partially adopted** — `data_inlining`, `sort expressions`, `data change feed`, `encryption` not yet wired. **Parallel workstream.**
7. **OTel semantic conventions not enforced** — the Langfuse/MLflow/Logfire backends pass through arbitrary attributes. **Parallel workstream.**

---

## H) Cross-references

- `openspec/specs/dagster-5-layer-component-architecture/spec.md` — the 5-layer model this package implements
- `openspec/specs/centralized-model-registry/spec.md` — the 76-entry model registry (post 2026-08-15)
- `openspec/specs/centralized-schema-registry/spec.md` — BAML → Pydantic/Zod codegen
- `openspec/specs/indexing-and-cognition/spec.md` — CCC + Cognee + OpenCode registry
- `openspec/specs/knowledge-sync-loop/spec.md` — the 7-layer sync architecture
- `openspec/specs/agent-memory-systems/spec.md` — Cognee + Graphiti + LanceDB + FalkorDB + Memgraph
- `openspec/specs/agent-observability/spec.md` — Langfuse + MLflow + Logfire + RAGAS
- `openspec/specs/infrastructure-stacks/spec.md` — 94 Docker Compose stacks
- `openspec/specs/british-isles-education-pipeline/spec.md` — the flagship BIEP v3 spec
- `openspec/specs/cianfhoghlaim-personal-archive-typed-modules/spec.md` — the new UoG personal-archive spec
- `.agents/skills/INDEXING_AND_COGNITION.md` — CCC + Cognee + Firecrawl triple-search architecture
- `.agents/skills/dagster/SKILL.md` — Dagster 1.13+ Declarative Automation + KCG Components
- `.agents/skills/cocoindex/SKILL.md` — CocoIndex v1 + R1-R4 conformance
- `.agents/skills/ducklake/SKILL.md` — DuckLake v1.0 reference
- `.agents/skills/lancedb/SKILL.md` — LanceDB HNSW vector store
- `.agents/skills/centralized-registry/SKILL.md` — model + schema registries
- `openspec/changes/2026-08-25-lakehouse-observability-and-cross-stack-integration-v1/` — the OTel fan-out change
- `docs/observability/env-var-contract.md` — the 62 env-var contract
- `docs/observability/lakehouse-otel-fanout.md` — the OTel fan-out architecture
- `docs/lakehouse/deployment-status-2026-07-19.md` — the 1,990-row BIEP v3 deployment
- `docs/lakehouse/smoke-test-2026-08-09.md` — the lakehouse smoke-test
- `docs/dagster/group-name-underscore-migration.md` — the slash-to-underscore migration

---

**Author:** Read-only research subagent.
**Date:** 2026-08-24.
**Working directory:** `/Users/cianmacandeisigh/dev/kings_college_galway`.
**Scope:** `orchestration/` + `cocoindex_flows/` + `observability/` + `docs/{dagster,cocoindex,lakehouse,observability,firecrawl}/`.
**Status:** Analysis complete. Ready for review and openspec change authoring.