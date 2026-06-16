# Leabharlann Stack Overview — End-to-End Diagram

**Last updated:** 2026-06-16

This document is the canonical end-to-end diagram of how a leabharlann PDF (or a Google Takeout docx, or a Zotero arXiv paper) flows through the full Cianfhoghlaim stack — from file system, through the lakehouse, through BAML extraction, through CocoIndex v1 embedding, through Cognee cognify, to a queryable LanceDB / FalkorDB / DuckLake dataset.

> For the canonical data architecture, see `docs/02-data-platform/DATA_ARCHITECTURE.md`. For the data-platform canonical docs index, see `docs/02-data-platform/README.md`. For the DAG-level agent architecture, see `docs/00-core/PROJECT_SPEC.md`.

---

## Stack layer diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                       SOURCE TREES                                        │
│  leabharlann/ollscoil_na_gaillimhe/  leabharlann/zotero/  leabharlann/gaeilge/          │
│  leabharlann/aigne/                  stedding/Takeout/      (EPUB, DOCX, PDF, MD)        │
└────────────────────────────────────────┬────────────────────────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              LAYER 1: CONTROL PLANE                                         │
│                                                                                            │
│   ┌──────────────┐    ┌────────────────┐    ┌──────────────────┐    ┌──────────────┐    │
│   │  Komodo      │    │  Infisical     │    │  Locket          │    │  Pocket ID   │    │
│   │  (GitOps)    │───▶│  (secret vault)│───▶│  (sidecar inj.)  │    │  (OIDC SSO)  │    │
│   │  port 9120   │    │  dev-baile env  │    │  per stack       │    │  port 1411   │    │
│   └──────┬───────┘    └────────────────┘    └──────┬───────────┘    └──────────────┘    │
│          │                                       │                                       │
│          ▼                                       ▼                                       │
│   ┌────────────────────────────────────────────────────────────────────────────┐         │
│   │  Pangolin (Traefik v3.4.0 reverse proxy + WireGuard VPN + TinyAuth)            │         │
│   │  crowdsec + HTTPS + TinyAuth forward auth → routes to oideachais.cianfhoghlaim.ie   │         │
│   └────────────────────────────────────────────────────────────────────────────┘         │
│                                                                                            │
└────────────────────────────────────────┬────────────────────────────────────────────────────┘
                                         │  sync secrets
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              LAYER 2: DAGSTER + BAML + COCOINDEX                            │
│                                                                                            │
│   ┌────────────────────────────────────────────────────────────────────────────┐         │
│   │  Dagster unified (port 3335)                                                   │         │
│   │  /opt/dagster/ in container, dg workspace at `oideachais/workspace.yaml`         │         │
│   │                                                                                    │         │
│   │  Assets (registered in `oideachais/dagster_defs/definitions.py`):                │         │
│   │  • 21 asset modules, 7 groups (multi_nation_curriculum, uk_education, etc.)         │         │
│   │  • 7 leabharlann assets (books / zotero / takeout / baml / 3 cocoindex)              │         │
│   │  • 7 author-archive assets (UoG / Gemini / Takeout / BAML / 3 OCR+embedding)           │         │
│   └────────────────────────────────────────────────────────────────────────────┘         │
│                                                                                            │
│   ┌──────────────────────────────┐         ┌────────────────────────────────────┐        │
│   │  DLT (ingestion)             │         │  BAML (structured extraction)     │        │
│   │  /oideachais/dlt_sources/    │  ───▶   │  /baml_src/                       │        │
│   │  author_archive/ (6 sources) │         │  • aistear.baml, primary.baml,     │        │
│   │  ireland/ (18 sources)       │         │    junior_cycle.baml,              │        │
│   │  uk/ (16 sources)            │         │    tertiary.baml, ui_components,  │        │
│   │  crown_dependencies/         │         │    curriculum_extraction.baml,    │        │
│   │                              │         │    author_archive.baml (12 cls),  │        │
│   │  Hash-based incremental via  │         │    image_generation.baml           │        │
│   │  SHA-256 + FileHashTracker   │         │                                   │        │
│   └──────────────┬───────────────┘         └─────────────┬─────────────────────┘        │
│                  │                                       │                              │
│                  ▼                                       ▼                              │
│   ┌────────────────────────────────────────────────────────────────────────────┐         │
│   │  CocoIndex v1 (incremental embedding)                                           │         │
│   │  /oideachais/cocoindex_flows/                                                   │         │
│   │  • 11 flows total (1 v1 working + 10 v0 broken — see STATUS.md § 3)                │         │
│   │  • `leabharlann_embedding.py` (v1) — 3 Apps + 3 search handlers (BGE-large-en)     │         │
│   │  • `author_archive_embedding.py` (v0, broken) — UoG + Gemini + Takeout              │         │
│   └────────────────────────────────────────────────────────────────────────────┘         │
│                                                                                            │
└────────────────────────────────────────┬────────────────────────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                          LAYER 3: LAKEHOUSE STORAGE (Garage + Iceberg + DuckLake)             │
│                                                                                            │
│   ┌────────────────────┐   ┌────────────────────┐   ┌────────────────────────────┐       │
│   │  Garage S3         │   │  Lakekeeper        │   │  Lance Namespace sidecar    │       │
│   │  port 3900-3904    │◀─▶│  Iceberg REST       │◀─▶│  port 8182                   │       │
│   │  /iceberg/         │   │  port 8181          │   │  registers LanceDB tables   │       │
│   │  /lance/           │   │  (REST catalog)     │   │  as Iceberg tables           │       │
│   │  /ducklake/        │   │                     │   │                              │       │
│   └────────────────────┘   └────────────────────┘   └────────────────────────────┘       │
│              ▲                                                                     ▲        │
│              │                                                                     │        │
│   ┌──────────┴──────────────────────────────────────────────────────────────┐          │
│   │  Postgres (local dev) or PlanetScale (prod) — Lakekeeper catalog metadata         │          │
│   └─────────────────────────────────────────────────────────────────────────────────┘          │
│                                                                                            │
└────────────────────────────────────────┬────────────────────────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                  LAYER 4: ML / GRAPH / VECTOR STORAGE (Cognee + FalkorDB + Graphiti +       │
│                                       LanceDB)                                            │
│                                                                                            │
│   ┌────────────────────┐   ┌────────────────────┐   ┌────────────────────────────┐       │
│   │  LanceDB REST      │   │  Cognee             │   │  FalkorDB                  │       │
│   │  port 8081 viewer  │   │  port 8000          │   │  port 6379, 3000           │       │
│   │  rest://lance-api  │   │  knowledge graph    │   │  Redis-based graph         │       │
│   │  .cianfhoghlaim.ie │   │  (Neo4j / Memgraph)  │   │  cache + queries            │       │
│   └────────────────────┘   └────────────────────┘   └────────────────────────────┘       │
│              ▲                         ▲                          ▲                    │
│              │                         │                          │                    │
│   ┌──────────┴────────────────────────────────────────────────────────────────┐          │
│   │  Graphiti (port 8080) — bi-temporal knowledge graph (Neo4j OR FalkorDB profile)        │          │
│   └─────────────────────────────────────────────────────────────────────────────────┘          │
│                                                                                            │
└────────────────────────────────────────┬────────────────────────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                       LAYER 5: USER-FACING (Web + Marimo + API)                              │
│                                                                                            │
│   ┌──────────────────┐   ┌────────────────────┐   ┌────────────────────────────┐       │
│   │  TanStack Start   │   │  Marimo notebooks   │   │  FastAPI (AG-UI / oRPC)   │       │
│   │  port 3000        │   │  /dashboards/*       │   │  port 8000                 │       │
│   │  (oideachais/web/)│   │  (oideachais/        │   │  (oideachais/api/)         │       │
│   │  bilingual EN/GA  │   │   notebooks/)        │   │  AG-UI streaming          │       │
│   │  CopilotKit AG-UI │   │                      │   │  oRPC procedures           │       │
│   └──────────────────┘   └────────────────────┘   └────────────────────────────┘       │
│                                                                                            │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## How a leabharlann PDF flows through the stack (5 stages)

### Stage 1 — Secret injection (Komodo + Infisical + Locket)

When the Dagster container starts on `bunchloch` (MacBook M4) or in production (OCI ARM1), the Locket sidecar reads the stack's `secrets.env` and hydrates `infisical://dev-baile/...` references. The Dagster asset materialisation runs with the resolved secrets in its environment (no plaintext on disk).

### Stage 2 — DLT filesystem scan with SHA-256 dedup

`oideachais/dagster_defs/assets/leabharlann_assets.py:leabharlann_books_raw` materialises → `dlt_sources.author_archive.leabharlann_books_source()` walks `leabharlann/{gaeilge,aigne}/`, hashes every file with SHA-256, yields one row per file with metadata + preview_path. `FileHashTracker` memoises the file-hash ledger. The dlt primary key (`file_hash`) prevents re-loads on incremental re-runs. Output goes to DuckLake (`oideachais.author_archive_uog.documents` or similar).

Similarly `leabharlann_zotero_raw` (117 PDFs in real Zotero storage format with `__dup0` markers, arXiv IDs) and `leabharlann_takeout_v1_raw` (sample googletakeout at `stedding/Takeout/`).

### Stage 3 — BAML structured extraction

`leabharlann_paper_metadata` materialises → for each Zotero PDF, calls `b.ExtractZoteroMetadata(pdf_text, file_name, arxiv_id)` which returns a `ZoteroPaper` with `paper_kind`, `arxiv_id`, `doi`, `title`, `authors`, `year`, `abstract`, `venue`, `irish_relevant`, `htr_relevant`, `confidence`. Memoised by `(file_hash, baml_function_name)` in the `author_archive.extraction_metadata` DuckDB table.

The BAML client (`ExtractEn`) routes through the LiteLLM gateway → `litellm/gemini-2.5-flash` (or `litellm/anthropic/claude-sonnet-4` via the `ExtractEnStrong` fallback).

### Stage 4 — CocoIndex v1 incremental embedding

`leabharlann_cocoindex_zotero_update` materialises → invokes `subprocess.run(["cocoindex", "update", "oideachais.cocoindex_flows.leabharlann_embedding:LeabharlannZoteroEmbedding"])`.

The v1 App:
- Sources: `localfs.walk_dir(sourcedir, recursive=True, path_matcher=PatternFilePathMatcher(included_patterns=["**/*.pdf"], excluded_patterns=["**/.DS_Store", "**/_.pdf"]), live=True)`.
- Per file: `process_zotero_file` extracts text, chunks via `RecursiveSplitter(chunk_size=2000, chunk_overlap=500, language="markdown")`, embeds each chunk via `SentenceTransformerEmbedder("BAAI/bge-large-en-v1.5")` in 100+ batches, declares one row per chunk in LanceDB.
- Stable IDs: `IdGenerator()` + `await id_gen.next_id(chunk.text)`.
- Memoised: `@coco.fn(memo=True)` on the file-level processor.
- Output: `rest://lance-api.cianfhoghlaim.ie:8181/leabharlann_zotero` (vector + FTS indexes).

The asset materialisation returns a `MaterializeResult` with `cocoindex_app=LeabharlannZoteroEmbedding, returncode=0, lance_table=leabharlann_zotero`.

### Stage 5 — Cognee cognify (cross-archive)

`(queued — see oideachais/REFACTORING.md Feature 2)`. The plan is to add `cognee_cognify_zotero` (and the equivalent for books / takeout) + `cognee_cross_archive_edges` + 1 FastAPI route + 1 daily cron sensor. Cognee `cognify()` builds the knowledge graph and persists to Memgraph + FalkorDB cache. The cross-archive edges asset computes relationships like `GeminiDeepResearchReport -[:CITES]-> ZoteroPaper` (when an arxiv_id matches) and `UoGArtifact -[:TEACHES]-> ZoteroPaper` (when the module title matches a paper title).

---

## How the 6 docker-compose layers integrate

Per `infrastructure/AGENTS.md`:

1. **Control plane** (`stacks/infrastructure/`) — Pangolin (Traefik + WireGuard + Pocket ID + CrowdSec), Komodo (GitOps), PlanetScale (Postgres), MotherDuck (cloud query engine), R2 (Cloudflare blob), Pulumi (cloud IaC), Forgejo (self-hosted Git).
2. **Storage** (`stacks/storage/`) — Garage (S3-compatible object store on `bunchloch`), Lakehouse (Lakekeeper + Lance Namespace + Postgres), LakeFS (git-for-data), Beszel (server/Docker monitoring).
3. **Engineering** (`stacks/engineering/`) — LiteLLM (LLM gateway), Dagster (orchestration), oideachais (the app stack: Dagster + FastAPI + TanStack Start), Convex (realtime backend), Windmill (workflow), n8n (visual workflows), Coder (cloud dev env), DevDocs, MCPJungle.
4. **Machine learning** (`stacks/machine_learning/`) — Cognee (knowledge graph), Graphiti (temporal knowledge graph), Langfuse (LLM observability), MLflow, Qdrant, Memgraph, FalkorDB, LanceDB, olake, lmnr, logfire, nimtable.
5. **Tools** (`stacks/tools/`) — Productivity / media utilities.
6. **Browser** (`stacks/browser/`) — Browser automation.

The leabharlann pipeline touches all 6 layers:
- **Control plane** — Komodo deploys the oideachais stack; Locket injects secrets; Pangolin routes `oideachais.cianfhoghlaim.ie`.
- **Storage** — Garage stores NCCA / SEC PDFs and DuckLake Parquet files; Lakekeeper is the Iceberg REST catalog; Lance Namespace registers LanceDB tables as Iceberg tables; Postgres holds Lakekeeper metadata.
- **Engineering** — Dagster orchestrates; LiteLLM routes BAML calls; Convex stores the front-end state; the oideachais compose stack hosts Dagster + FastAPI + TanStack Start.
- **Machine learning** — Cognee + FalkorDB + Graphiti build the knowledge graph; LanceDB serves the vector search; Langfuse traces the BAML calls; MLflow tracks model experiments.
- **Tools** — n8n + Windmill expose the pipeline as a visual workflow; DevDocs hosts the human-facing docs.
- **Browser** — Crawl4AI / Firecrawl scrape NCCA / SEC pages (Phase 2 of the leabharlann takeout source).

---

## The 5 integration points

1. **Komodo + Infisical + Locket** — secret injection at runtime, no plaintext on disk, GitOps workflow.
2. **dlt + DuckLake** — append-only ingestion with hash-based incremental; primary key `file_hash`; partition columns `account` + `domain`.
3. **BAML + Cognee** — typed extraction with schema validation; `cognee.add()` + `cognify()` builds the knowledge graph; cross-archive edges via 8 canonical relationship types.
4. **CocoIndex v1 + LanceDB** — incremental embedding with `@coco.fn(memo=True)`; IVF_HNSW + FTS indexes; v1 `localfs.walk_dir(live=True)` source for continuous monitoring.
5. **FalkorDB + Graphiti** — bi-temporal graph (Graphiti via `graphiti` compose stack or `oideachais/graph/temporal.py` re-implementation); FalkorDB for cache/queries.

---

## Cross-references

- `oideachais/STATUS.md` — single source of truth for pipeline state.
- `oideachais/REFACTORING.md` — refactor backlog (5 features that close the open gaps).
- `oideachais/dlt_sources/uk/README.md` — UK coverage matrix.
- `oideachais/dlt_sources/ireland/README.md` — Ireland coverage matrix.
- `oideachais/cocoindex_flows/README.md` — v0/v1 status per flow.
- `baml_src/README.md` — BAML schema catalogue.
- `infrastructure/AGENTS.md` — control plane + secret management + canonical docker-compose patterns.
- `docs/02-data-platform/DATA_ARCHITECTURE.md` — data architecture (Tripartite data landscape, BAML schema specs, Cognee ontology).
- `openspec/changes/data-engineering-documentation-and-refactor-roadmap/` — this change.
