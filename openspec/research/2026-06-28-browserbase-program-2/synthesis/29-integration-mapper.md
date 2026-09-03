# Agent 29 — Integration Mapper (Wave 3 Synthesis)

**Date:** 2026-06-28 · **Wave:** 3 of 7 · **Role:** cross-package mapper
**Inputs:** 25 wave-1 agent outputs + `SHARED_DISCOVERY_LOG.md` (503 lines, 11 cross-agent deps, 4 conflicts).
**Output:** this file (≤ 400 lines) — system diagram + data-flow matrix + 10 integration anti-patterns + handoffs + migration paths.

## 1. TL;DR — top 3 integration insights

1. **The platform is a 3-tier sealed system with one leaky seam at the LLM gateway.** User → Cloudflare edge → Pangolin/Newt (EE) → Komodo orchestrator → 70+ Docker Compose stacks. The cross-cutting backbone is **Infisical → Locket → every container** (130+ secret URIs in `.infisical.env`). Every LLM call funnels through a single LiteLLM gateway on `:4000` that aliases 9 BAML clients, 4 MLX routes, 2 GGUF routes, 1 Dives target, and the `minimax` de-risking path. The single leaky seam is **BAML inline `client "anthropic/claude-sonnet-4-..."` calls** at `_oideachais_src/curriculum_extraction.baml:164-1086` (8 occurrences) that bypass the gateway entirely — no fallback, no Langfuse trace, no `minimax` derisking.
2. **The "Lakehouse" stack is actually 4 sibling storage layers on one Garage S3 bucket** — not one system. `infrastructure/stacks/lakehouse/` runs **Garage S3** (object storage, 2-3 versions stale), **Postgres** (DuckLake + Lakekeeper catalog), **Iceberg REST catalog via Lakekeeper** (`:8181`), and **LanceDB namespace** (`:8182`). DuckLake writes `s3://garage/ducklake/`, LanceDB writes `s3://garage/lance/`, MotherDuck attaches via `md:` prefix (BYOB), Iceberg catalog metadata lives in Postgres. The agents documented at least **4 path/config drifts** (MotherDuck pricing, dlt 1.28.0 breaking changes, LanceDB v0.33 HNSW vocabulary, DuckLake 1.0 pin).
3. **The "agent memory" stack has 4 overlapping systems with no clear boundary contract** — Cognee (KG cognition), Graphiti (temporal episodic), FalkorDB (vector+graph Redis module), Memgraph (legacy crypteolas). Cognee has **two separate configs** (Postgres-unified in compose.yaml:42-59 vs Memgraph+LanceDB in `core/memory/memory/cognee_config.py:66-94`). FalkorDB ships without `--loadmodule vector.so` (P1B-07 spec drift → production silently broken). Graphiti has a 16-param `add_episode` API but the KCG client only forwards 5. The whole subsystem is the highest-drift surface in the platform.

## 2. Mermaid system diagram

```mermaid
flowchart TB
    %% ===== Edge layer =====
    U[User browser] --> CF[Cloudflare R2 + Workers + D1<br/>edge cache + secrets bootstrap]
    CF --> PG[Pangolin EE + Newt + Gerbil<br/>Pocket ID OIDC + TinyAuth<br/>Traefik public routes :80/:443]

    %% ===== Orchestration =====
    PG --> KM[Komodo v2.2.0<br/>arm1-oci control plane<br/>90 stack GitOps via resource_sync]

    %% ===== Tier-1 stacks =====
    subgraph T1["Tier-1 — Lakehouse (infrastructure/stacks/lakehouse/)"]
      GAR[Garage S3 v1.0.1<br/>PII-isolated buckets]
      PG2[Postgres 17<br/>DuckLake catalog + Lakekeeper metadata]
      LK[Lakekeeper :8181<br/>Iceberg REST Catalog]
      LNS[lance-namespace :8182<br/>Lance tables]
      MD[MotherDuck BYOB<br/>md: attach + Dives]
    end

    subgraph T2["Tier-1 — LiteLLM gateway :4000"]
      LT[LiteLLM :main-stable<br/>9 BAML aliases + 4 MLX + 2 GGUF + 1 Dives]
      LTPG[litellm-postgres :5432<br/>spend tracking + virtual keys]
    end

    subgraph T3["Tier-1 — Cognee + Graphiti"]
      COG[Cognee v1.0<br/>legacy add/cognify + new remember/recall]
      GR[Graphiti 0.29<br/>16-param add_episode]
      FKDB[(FalkorDB :6379<br/>vector.so NOT loaded)]
      DFL[Dragonfly :6379<br/>episode cache + Dagster queue]
    end

    subgraph T4["Tier-1 — BAML extraction (cianfhoghlaim/core/baml/)"]
      BAML[9 named clients<br/>ExtractEn, ExtractEnStrong, LocalVision, etc.]
      BAML2[8 inline anthropic/<br/>BYPASS LiteLLM]
    end

    subgraph T5["Tier-1 — Dagster :3080 (oideachais code-location)"]
      DAG[Dagster 1.13.11<br/>22 asset_check, 780 partitions]
      DLT[DLT 1.25.0 → 1.28.1<br/>190 sources in pipelines/ingest/]
    end

    KM --> T1
    KM --> T2
    KM --> T3
    KM --> T4
    KM --> T5
    KM --> T6[Litestream + Pocketbase + n8n + Vikunja + 64 other stacks]

    %% ===== Cross-cutting secrets =====
    INF[Infisical dev-baile<br/>130+ secret URIs] --> LOK[Locket sidecar<br/>tmpfs inject at container start]
    LOK --> KM
    LOK --> T1
    LOK --> T2
    LOK --> T3
    LOK --> T4
    LOK --> T5

    %% ===== Observability =====
    LF[Langfuse v3 :3000] -.traces.-> T2
    LF -.traces.-> T4
    MLF[MLflow :5500] -.experiments.-> DAG
    LOGF[Logfire] -.OTEL.-> T2
    COG -.knowledge graph.-> LF

    %% ===== Browser-driven research =====
    BB[BrowserBase + Firecrawl] -.research data.-> T5
    CCC[CCC v1 code search<br/>14 CocoIndex apps] -.indexes.-> T1
    COG -.cognify.-> CCC

    %% ===== Data flow =====
    DLT -->|raw PDFs / scrape| GAR
    DLT -->|DuckLake attach| PG2
    DLT -->|Iceberg writes| LK
    DAG -->|@dlt_assets| DLT
    DAG -->|partitions| GAR
    DAG -->|per-asset checks| LF
    BAML --> LT
    LT -->|extract-en, vision, ocr, math, irish, minimax, image-fibo| BAML
    DAG -->|@asset baml calls| BAML
    DAG -->|Cognee cognify task| COG
    DAG -->|Graphiti episodes| GR
    GR --> FKDB
    GR --> DFL
    COG --> PG2
    COG -.->|LANCE dead config| LNS
    COG --> MD
    MD -->|md: share| GAR
    LNS -->|rest://| GAR
    PG -->|private-resources| T1
    PG -->|private-resources| T2
    PG -->|public-resources oideachais-web, api, dagster, agent-os, adk-agents| KM
```

**Legend:** solid arrows = data/control flow; dashed = observability/research. Stacks shown simplified — 64 of 90 omitted as Tier-2/Tier-3; see `infrastructure/AGENTS.md` for full inventory.

## 3. Data flow table (the 25 packages)

| # | Package | Reads from | Writes to | Triggers | Observed by |
|--:|:--|:--|:--|:--|:--|
| 01 | **dlt 1.25.0** | `steding/ingest_queue/`, Firecrawl, BAML inline | DuckLake (Postgres), Iceberg (Lakekeeper), Lance, MotherDuck | Dagster `@dlt_assets` schedule | Langfuse via LiteLLM |
| 02 | **Dagster 1.13.11** | CCC code index, dlt sources, BAML helpers, Cognee | Materializes lakehouse tables | Upstream-package sensor (motherduck/dlthub/lancedb/cocoindex) | Langfuse `@asset_check` spans |
| 03 | **CocoIndex 1.0.14** | Codebase, leabharlann corpus, oideachais docs | `rest://lance-api:8182` (vector + 5 Apps missing `declare_vector_index`) | Dagster `cocoindex_*` assets | Langfuse + Logfire |
| 04 | **LanceDB 0.33.0** | dlt / CocoIndex / BAML | Lance tables on Garage S3, LanceDB namespace | Dagster partition backfill | Langfuse |
| 05 | **MotherDuck (BYOB)** | dlt / DuckLake | `md:` share → Garage | Dagster `motherduck_sync_asset` (no sensor) | MotherDuck audit logs |
| 06 | **LiteLLM :4000** | BAML 9 clients, MLX :10240, GGUF :8080, OpenCode Go API | litellm-postgres (spend), Langfuse | Dagster `minimax_alias_health` check | Langfuse v3 OTEL |
| 07 | **Lakekeeper :8181** | dlt Iceberg writes, DuckDB ATTACH | Garage S3 (Parquet + Avro manifests) | Iceberg snapshot commit | Lakekeeper metrics :9100 |
| 08 | **DuckLake 1.0** | dlt `ie/law/irish_statute_book`, Dagster exam assets | `ducklake:postgres:...` (catalog) + Garage `s3://garage/ducklake/` | Dagster SEC partition schedule | Langfuse |
| 09 | **Cognee 1.0** | Dagster `cognify` asset, leabharlann PDFs, OpenCode | Postgres (pgvector), Memgraph (legacy), Lance (dead config) | Dagster cron 03:17 UTC | Langfuse + Cognee Studio |
| 10 | **FalkorDB :6379** | Graphiti 0.29 episodes (16 params) | RESP + Bolt dual | Graphiti add_episode call | `vector.so` NOT loaded — broken |
| 11 | **Graphiti 0.29** | FalkorDB / Dragonfly cache, BAML extraction | EntityEdge, EpisodicEdge, CommunityEdge, HasEpisode, NextEpisode | Dagster heartbeat + agent calls | Langfuse |
| 12 | **Garage S3 v1.0.1** | Lakekeeper, Lance, DuckLake, MotherDuck BYOB | Object storage (Parquet/Avro/Lance) | Locket + Komodo `resource_sync` | Garage admin API `/v1/` (will 404 on v2) |
| 13 | **Dragonfly :6379** | Graphiti episode cache, Túatha leaderboard, Dagster run queue | In-memory KV | Locket inject | n/a |
| 14 | **RisingWave 3.0.0** | LiteLLM CDC, Postgres CDC templates | Iceberg sink (premium features gated) | Postgres logical replication | n/a |
| 15 | **BAML 0.74.0** | 73 `.baml` files, 5 client files (1 obsolete), 9 named clients | LiteLLM (8 + 1 inline bypass) | Dagster BAML asset | Langfuse (only gateway-routed) |
| 16 | **Pangolin EE** | All 9 v4 `stacks/*/pangolin.yaml` | Traefik public routes, TinyAuth roles | Locket + Komodo | TinyAuth logs |
| 17 | **Komodo v2.2.0** | `infrastructure/komodo/{servers,stacks,procedures,resource-syncs,sites}/` | arm1-oci + bunchloch Periphery | Git push to `cliste/bonneagar` | Komodo UI |
| 18 | **Infisical** | UI + Universal Auth machine identity | `dev-baile` env (130+ secrets) | `mise` cd-hook, Locket sidecar | Infisical audit log |
| 19 | **Unsloth 3.0+** | 11 OCR models (`unsloth_config.py:166`), llama-swap | GGUF/MLX/Safetensors → HF Hub | Dagster OCR training assets | MLflow (via `report_to=["mlflow"]`) |
| 20 | **MLX-omni :10240** | 3 wired models (granite-docling, olmocr-mlx, fibo) | LiteLLM `local/{ocr,document,image}` aliases | LiteLLM `fallback_chain` | LiteLLM → Langfuse |
| 21 | **HuggingFace** | `hf` CLI (replaces `huggingface-cli`) | 8 aspirational model IDs in P2-23 don't exist | Dagster + Unsloth `push_to_hub_gguf` | HF Hub webhooks |
| 22 | **OpenChamber :3000** | OpenCode wire SDK v2 | bundled-state only (no Postgres/LiteLLM in stack) | User browser → openchamber.cianfhoghlaim.ie | OpenChamber log |
| 23 | **Ireland sites** | curriculumonline.ie, examinations.ie, ncca.ie | dlt sources → BAML extraction | Dagster SEC + NCCA cron | Langfuse + RAGAS |
| 24 | **UK sites** | gov.uk (Fastly), gov.wales (WAF), NI Drupal, Scotland (500) | dlt sources | Dagster | Langfuse + RAGAS |
| 25 | **Crown+Reference** | Jersey CKAN, IoM PDFs, Guernsey, Zotero, arXiv | dlt sources, leabharlann corpus | Dagster + Cognee cognify | Langfuse + RAGAS |

## 4. Integration anti-patterns (12 found, ranked by impact)

1. **BAML inline client bypass.** `_oideachais_src/curriculum_extraction.baml:164-1086` contains 8 `client "anthropic/claude-sonnet-4-20250514"` calls that skip the LiteLLM gateway. No fallback chain, no Langfuse trace, no `minimax` de-risking — defeats Phase 0.4. (Agent 15, **HIGH**)
2. **dlt path drift.** P1A-01 docs reference `cianfhoghlaim/dlt_sources/` (404). Real path: `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/` (190 files, 12 subdirs). (Agent 01, **HIGH**)
3. **FalkorDB `vector.so` not loaded.** P1B-07 mandates `--loadmodule /etc/falkordb/vector.so` but `infrastructure/stacks/falkordb/compose.yaml:18-37` omits the `command:` field. Every `db.idx.vector.queryNodes` call silently fails. (Agent 10, **HIGH**)
4. **Garage S3 v1.0.1 → v2.3.0 BREAKING.** Our `replication_mode = "1"` in `garage.toml:5,18` and the 90-line `garage-init` bash script hard-coding `/v1/` endpoints will both fail after v2 upgrade. 18 months stale. (Agent 12, **HIGH**)
5. **Aspirational HF model IDs.** 8 of 11 vision models in P2-23 don't exist on Hub: `unsloth/gemma-4-*`, `unsloth/Qwen3.6-*`, `unsloth/GLM-4.6V-Flash-GGUF` — Gemma 4 and Qwen 3.6 not released. `hf_hub_download()` will 404. (Agent 21, **HIGH**)
6. **LanceDB HNSW vocabulary drift.** Spec uses `index: { type: hnsw, m: 16 }` (invalid in v0.33). Only `IVF_HNSW_FLAT` / `_SQ` / `_PQ` are valid. (Agent 04, **HIGH**)
7. **MotherDuck pricing drift.** P1A-05 said "MotherDuck 0.5" but docs require DuckDB ≥ 1.5.4. `--read-write --allow-switch-databases` MCP flags are explicit anti-pattern. (Agent 05, **MED**)
8. **CocoIndex vector-index gap.** 5 of 14 v1 Apps call `lancedb.mount_table_target` but never `declare_vector_index`. All `search_codebase()` calls brute-force over 1024-d bge-m3. (Agent 03, **MED**)
9. **Two Cognee configs.** `infrastructure/stacks/cognee/compose.yaml` (Postgres-unified) vs `core/memory/memory/cognee_config.py:66-94` (Memgraph+LanceDB). Spec needs explicit split. (Agent 09, **MED**)
10. **Cognee `SearchType.INSIGHTS` doesn't exist.** `core/memory/memory/cognee_service.py:376` references an enum value not in v1.2.2 — `AttributeError` at runtime. (Agent 09, **MED**)
11. **OpenChamber spec fictional.** P2-20 claims `image: openchamber/openchamber:latest`, port 3030, `openchamber-postgres`, `LITELLM_BASE_URL`. Real stack: `ghcr.io/openchamber/openchamber:1.0.0`, port 3000, bundled-mode only, direct provider keys. (Agent 22, **MED**)
12. **MLX-omni spec drift × 5.** Wrong repo (`qifengle` vs `madroidmaq`), wrong CLI name (`mlx-omni` vs `mlx-omni-server`), wrong invocation (no `serve` subcommand), missing Anthropic surface, aspirational "11 vision + 4 text" count. (Agent 20, **MED**)
13. **LiteLLM `main-stable` deprecated 2026-06-30.** Our pin in `stacks/litellm/compose.yaml` must migrate to `:latest` or `:1.84.0+`. **2 days from cutover**. (Agent 06, **MED**)
14. **3 lazy-load TODOs predict 1.27+ break.** `_oideachais_dlt_sources/duchas_images.py:20-23`, `_duchas_images_helpers.py:14-17`, `hidden_heritages.py:18-21` mask `dlt.sources.incremental` import via try/except. (Agent 01, **LOW**)
15. **Komodo `server_id` vs upstream `server`.** Cianfhoghlaim uses `server_id = "bunchloch"` everywhere but upstream v2 docs use `server = "..."`. Silent-drift risk on copy-paste from docs. (Agent 17, **LOW**)
16. **Pangolin blueprint schema collision.** `pangolin.yaml` uses `protocol: http` (deprecated; `mode:` preferred). All 9 v4 stacks + Komodo `sites/` empty subdir could collide with Pangolin's `sites:` blueprint key. (Agent 16+17, **LOW**)

## 5. Cross-package handoffs (from SHARED_DISCOVERY_LOG)

| From | To | Handoff | File/line |
|:--|:--|:--|:--|
| 15 BAML | 06 LiteLLM | 9 named clients → 9 model aliases | `_oideachais_src/clients.baml:264` ↔ `litellm/config/config.yaml:34-65` |
| 02 Dagster | 01 dlt | `@dlt_assets` × 7 Leaving Cert + 28+ more via `DltLoadCollectionComponent` | `assets/leaving_cert/dlt_assets.py:50` |
| 02 Dagster | 04 LanceDB | `CelticLancedbHnswComponent` builds HNSW (will fail — see anti-pattern #6) | `components/celtic_lancedb_hnsw.py:24-87` |
| 02 Dagster | 03 CocoIndex | `CelticCocoindexV1Component` wraps 14 v1 Apps | `components/celtic_cocoindex_v1.py:28-129` |
| 02 Dagster | 15 BAML | `@asset` calls BAML functions via `b.ExtractExamPaper` etc. | `assets/*/baml_assets.py` |
| 02 Dagster | 09 Cognee | `cognify` asset triggers cognify with dataset name (drift: dot vs underscore) | `cognify/cognee_integration/cross_stage_cognify.py:131` |
| 02 Dagster | 11 Graphiti | heartbeat + agent calls add_episode (KCG uses 5/16 params) | `graphiti_client.py:158-164` |
| 06 LiteLLM | 20 MLX-omni | `local/ocr/olmocr-mlx`, `local/document/granite-docling`, `local/image/fibo` | `litellm/config/config.yaml:34,37,48,59` |
| 06 LiteLLM | 22 GGUF (llama-swap) | `fallback_chain` for `ocr` alias: MLX → GGUF → gemini-2.5-flash | `config.yaml:575` |
| 10 FalkorDB | 11 Graphiti | `Graphiti(uri="falkordb://...")` with Lite fallback to `/tmp/falkordb_lite` | `graphiti_client.py:111-131` |
| 09 Cognee | 06 LiteLLM | `LLM_BASE_URL=http://litellm:4000/v1` (DeepSeek default, minimax configured) | `compose.yaml:30-41` |
| 09 Cognee | 04 LanceDB | `LANCEDB_URI=rest://lakehouse-lance-namespace:8182` (DEAD — `VECTOR_DB_PROVIDER=pgvector` overrides) | `compose.yaml:60` |
| 08 DuckLake | 05 MotherDuck | Phase 4: catalog in `lakehouse-postgres`, compute moves to MotherDuck | `stacks/lakehouse/examples/DuckLake to MotherDuck_*.md` |
| 01 dlt | 08 DuckLake + 04 LanceDB | dlt 1.28.0 bumped ducklake 1.0 + duckdb 1.5.3 — coordinated pin required | `pyproject.toml:39` |
| 14 RisingWave | 07 Lakekeeper | Iceberg sink + `auto.schema.change` (premium gated) | `init.d/01_init.sql:145-155` |
| 16 Pangolin | 17 Komodo | `pangolin.yaml` referenced as `file_paths` in `[[stack]]` definitions | `stacks/storage-lakehouse.toml:25,54` |
| 18 Infisical | every stack | 130+ `infisical://dev-baile/...` URIs → Locket sidecar → tmpfs | `.infisical.env:50-80` |
| 19 Unsloth | 21 HF | `push_to_hub_gguf` after training (9 refs to deprecated `huggingface-cli`) | `unsloth_trainer.py:409` |
| 19 Unsloth | 18 MLflow | `TrainingArguments.report_to=["mlflow"]` | `unsloth_trainer.py:339` |
| 22 OpenChamber | 06 LiteLLM | **NO handoff** — direct provider keys, intentional | `secrets.env` (deliberately no `LITELLM_BASE_URL`) |
| 23/24/25 Sites | 01 dlt | All sites are dlt sources under `pipelines/ingest/_oideachais_dlt_sources/<jurisdiction>/` | `sources.yaml:278-284` |
| 25 Crown | 09 Cognee | leabharlann cognify consumer of enriched metadata (Zotero + arXiv) | `leabharlann_cross_archive.py` |
| 17 Komodo | 16 Pangolin | `openchamber-arm1-oci.toml` + `deploy-openchamber-arm1-oci.toml` referenced in `proposal.md:82-87` but not on disk | R4 in agent-22 |

**Conflicts surfaced:** (a) Agent 01 dlt path vs Phase 1A-01 spec; (b) Agent 03 CocoIndex embedding model (`bge-m3` vs `bge-large-en-v1.5`); (c) Agent 06 LiteLLM `minimax` vs BAML `minimax` alias; (d) Agent 04 LanceDB `IVF_HNSW_*` vs CocoIndex `hnsw_pq` shorthand; (e) Agent 17 Komodo `server_id` vs upstream `server`; (f) Agent 09 Cognee Postgres-unified vs Memgraph+LanceDB; (g) Agent 10 FalkorDB missing `vector.so` vs P1B-07 spec; (h) Agent 14 RisingWave CDC depends on Agent 06's litellm-postgres schema; (i) Agent 20 MLX-omni P2-24 spec 5 conflicts; (j) Agent 22 OpenChamber P2-20 spec 6 conflicts.

## 6. Migration paths (when X changes, Y must change)

| Change | Cascades to | Severity | Effort |
|:--|:--|:--|:--|
| Bump `dlt>=1.27.0` (per Agent 01) | dagster-dlt (must ≥0.29.11), DuckLake (≥1.0), all 3 lazy-load TODOs, `dlt[hub]` extra for dashboard | HIGH | 1-2 days |
| Bump `dagster-dlt>=0.29.11` | All `@dlt_assets` (no rewrite), but check `DltLoadCollectionComponent.partitions_def` adoption | MED | ½ day |
| Bump `dune-dlt==1.0` (DuckLake) | dlt pin, `pyproject.toml` resolver | MED | ½ day |
| Bump `lancedb>=0.33,<0.34` | All `index: { type: hnsw }` → `IVF_HNSW_SQ`; `connect_namespace("rest", {...})` rewrite; CocoIndex Apps need `index_type="ivf_pq"` or `hnsw_pq` | HIGH | 1 day |
| Bump `garage` v1→v2.3.0 | `replication_mode` removed → fail; `/v1/` → `/v2/` admin API → 90-line `garage-init` rewrite; 8 releases behind | HIGH | 1 day (mandatory before v1 EOL) |
| Cutover `litellm:main-stable` → `:1.84.0+` by **2026-06-30** | BAML client compat (9 named clients), config.yaml model_list, Langfuse v2 callback → v3 OTEL migration | HIGH | ½ day (2 days left) |
| Bump `dagster>=1.13.9` hierarchical groups | ~50 `@dg.asset` decorators (one-time sed) | LOW | 2 hours |
| Bump `cognee>=1.0` (new API) | 6 cognify helpers in `cognee_integration/*.py` + `cognee_service.py:210-346` (legacy `add/cognify/search` → `remember/recall/improve`) | HIGH | 1 week |
| Switch `graphiti-core>=0.29` (16-param `add_episode`) | `graphiti_client.py:158-164` — currently forwards 5/16 params; add `group_id, entity_types, edge_types, edge_type_map` | MED | 1 day |
| Add `--loadmodule /etc/falkordb/vector.so` | `stacks/falkordb/compose.yaml` + Redis 8.0.0+ bump (FalkorDB requirement) | MED | ½ day |
| Bump `cocoindex>=1.0,<2.0,!=1.0.8` | All 14 v1 Apps: add `target_table.declare_vector_index("embedding", index_type="hnsw_pq")` for 5 missing; verify bge-m3 vs bge-large-en-v1.5 embedding model | MED | 1 day |
| Bump `duckdb>=1.5.4` (MotherDuck) | All 50+ `destination="duckdb"` hard-codes → `destinations.py` factory; `motherduck_options.py` BYOB defaults | MED | 1 day |
| Switch `huggingface-cli` → `hf` (rename) | 9 refs in P2-23 + `spaces/build-small-2026-runbook.md`; `infrastructure/ci/spaces-sync.yml:64` (`[cli]` → `[hf]`) | LOW | 1 hour |
| Switch `protocol:` → `mode:` (Pangolin) | 9 v4 `stacks/*/pangolin.yaml` files | LOW | 1 hour |
| Replace 8 aspirational HF model IDs (P2-23) | `unsloth_trainer.py` + `spaces/*` configs + HuggingFace Spaces runbook | MED | ½ day |
| Bump `unsloth>=3.0` (`FastModel` API) | `unsloth_trainer.py:108` still uses `FastVisionModel`; 11 OCR models need unified loader | MED | 1 day |
| Add `train_on_responses_only` | `unsloth_trainer.py:278` (easy +1% accuracy) | LOW | 1 hour |
| Replace `seed=42` → `random_state=3407` | `unsloth_config.py:103` (convention align) | LOW | 5 min |
| Enable MTP speculative decoding | `llama-swap-config.yaml:120` (Qwen3.6 1.4-2.2× speedup) | LOW | 1 hour |
| Add `LMDB` state path | `core/cocoindex/_lifespan.py` (currently `COCOINDEX_DB` not set) | LOW | 30 min |
| Add `wildcard-resources` + `wildcard TLS` + `public-policies` (Pangolin EE features) | 9 v4 `pangolin.yaml` files; cuts 70+ roles[0]: tinyauth@file refs | MED | 1 day |
| Add `sites:` block to Pangolin blueprint | `newt.yaml` (for multi-site HA failover) | MED | ½ day |
| Add `MAINTAINER` for `sites:` Pangolin | `public-resources.maintenance: { enabled, type: forced|automatic }` for 5 public Traefik routes | LOW | ½ day |
| Replace `pangolin apply blueprint --api-key` CLI | `komodo/stacks/pangolin-core-arm1.toml` + `pangolin-tunnels.toml` → one CLI call | MED | ½ day |
| Resolve T&Cs checkbox on examinations.ie | `sec_examinations_browser_source` (`examinations.py:306-399`) — Stagehand `click` on `input[type='checkbox'][name='accept-terms']` BEFORE subject interaction | HIGH (blocks ingestion) | ½ day |
| Add teacher service-account to Infisical | `oideachais/sources/curriculumonline_teacher/{email,password}` (for TCA-gated content) | MED | ½ day |
| Add Zotero API v3 source | `leabharlann/zotero.py:94-124` (currently filesystem-only); `@dlt.incremental` on `Last-Modified-Version` | MED | 1 day |
| Add arXiv OAI-PMH bulk source | `cognify/rules/leabharlann_cross_archive.py` (currently no enrichment) | LOW | ½ day |
| Add Jersey CKAN ingestion (110+ datasets) | `sources.yaml:278-284` currently only `jey.education.govje` | MED | 1 day |
| Add IoM PDF harvester | `iom/law/legislation.py:24-29` (currently HTML only, 750+ Acts PDFs) | MED | 1 day |
| Add Hwb (gov.wales peer) + `cbac.co.uk` peer | `_curriculum_for_wales_helpers.py:14-21` | LOW | ½ day |
| Add Northern Ireland pagination | `_crawl_ni_curriculum` (3-page sitemap `?page=1,2,3`) | LOW | 1 hour |
| Add Dublin Core metadata parser | `ncca.py:149-308` (currently discards `<meta name="DC.*">` tags) | LOW | 1 hour |
| Move OpenChamber from spec fiction to disk | `infrastructure/komodo/stacks/openchamber-arm1-oci.toml` + `procedures/deploy-openchamber-arm1-oci.toml` (per `proposal.md:82-87` but not on disk) | MED | 1 day |
| Resolve sha256:0000...0000 placeholder | `infrastructure/stacks/openchamber/compose.yaml:29` | MED | 5 min |
| Add `mtls` or `policies` block to Komodo sites/ | `infrastructure/komodo/sites/` is empty | LOW | 1 hour |
| Add `policies` block (Pangolin EE) | 9 v4 `pangolin.yaml` files + 70+ blueprint files | MED | 1 day |
| Switch `dagster-dlt` 28+ Celtic sources to `DltLoadCollectionComponent` | Delete `celtic_dlt_source.py:29-97` (100 lines duplicate of upstream) | MED | 1 day |
| Migrate `destinations.py` factory (dlt) | 50+ `destination="duckdb"` hard-codes | MED | 1 day |
| Delete dead DuckLake 352-line class | `stedding/stedding/flows/education/storage/ducklake.py` (dead since `2026-06-27-croilar-audit-phase-2-delete-pipelines-shared-drift`) | LOW | 30 min |
| Delete obsolete Gemini BAML client | `_oideachais_src/clients_0.baml` (39 lines, obsolete) | LOW | 5 min |
| Set `GRAPHITI_TELEMETRY_ENABLED=false` | `stacks/graphiti/secrets.env` (currently unflagged) | LOW | 5 min |

## Summary

The Cianfhoghlaim v4 platform is a **3-tier sealed system** (Cloudflare edge → Pangolin EE → Komodo orchestrator → 90 stacks) with **one cross-cutting Infisical→Locket secrets backbone** (130+ secret URIs) and **one cross-cutting LLM gateway** (LiteLLM `:4000` aliasing 9 BAML + 4 MLX + 2 GGUF + 1 Dives). The highest-impact **integration anti-patterns** are: (1) BAML's 8 inline `anthropic/claude-sonnet-4` calls bypassing LiteLLM, (2) FalkorDB shipping without `--loadmodule vector.so`, (3) Garage S3 pinned 8 releases behind v1 EOL with breaking v2 changes already on the path, (4) 8 aspirational HF model IDs in P2-23 that don't exist on Hub, and (5) dlt path drift between P1A-01 docs (`dlt_sources/`) and v4 reality (`pipelines/ingest/_oideachais_dlt_sources/`). The **highest-cross-cutting migration** is the coordinated `dlt 1.28.0 + dagster-dlt 0.29.11 + ducklake 1.0 + lancedb 0.33 + motherduck 1.5.4` version cluster, plus the OpenSpec change `2026-06-28-pangolin-blueprint-v4-cleanup` that cuts 70+ `roles[0]: tinyauth@file` refs across 9 v4 stacks + Komodo sites + all 64 Tier-2/Tier-3 stacks. The `agent memory` subsystem (Cognee + Graphiti + FalkorDB + Memgraph) is the highest-drift surface and needs a dedicated `openspec/changes/2026-06-28-agent-memory-cleanup/` change to reconcile the 4 overlapping configs.
