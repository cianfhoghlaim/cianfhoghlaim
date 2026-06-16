# Data Engineering Documentation and Refactor Roadmap

## Why

The `oideachais/` data platform has reached a size where the existing documentation no longer matches the actual state of the code:

1. **British Isles education coverage is uneven.** `oideachais/dlt_sources/uk/` has 16 dlt source files across 4 nations (England, Scotland, Wales, Northern Ireland) plus `oideachais/dlt_sources/crown_dependencies/` for the Channel Islands and the Isle of Man, and `oideachais/dlt_sources/domains/education/{ie,en,ggy,jey,iom,ni,sct,wls}/` for 8 domains × nations. **There is no top-level README explaining what's covered, what's missing per nation × per cycle, and which BAML schema backs which dlt source.** A new contributor (or an agent) cannot answer "does the system have Key Stage 4 BAML extraction backed by a dlt source?" without reading every file.

2. **BAML-without-dlt gap.** `baml_src/primary.baml` and `baml_src/junior_cycle.baml` define 4 BAML functions (`ExtractPrimaryFramework`, `ExtractJCSpec`, `ExtractCBADescriptor`, `ExtractAistearFramework`) but **no matching dlt source backs them in `oideachais/dlt_sources/ireland/`** (only `aistear.py` and `senior_cycle.py` exist). The BAML extraction is unreachable.

3. **CocoIndex v0 vs v1 inconsistency.** The recent `leabharlann-cocoindex-v1` change migrated `oideachais/cocoindex_flows/leabharlann_embedding.py` to v1, but 10 of the 11 modules in `oideachais/cocoindex_flows/` are still v0 (`curriculum_embedding.py`, `ocr_embedding.py`, `geospatial_indexing.py`, `learning_outcome_graph.py`, `curriculum_translation.py`, `research_embedding.py`, etc.). The `oideachais/cocoindex_flows/__init__.py` paper-over this with a try/except import of the new module.

4. **Stack features under-used.** The `lancedb` compose stack has an `rclone` FUSE mount profile for S3-backed LanceDB blob storage (`infrastructure/stacks/machine_learning/lancedb/compose.yaml:44-75`). Nothing in `oideachais/` uses it. The `falkordb` compose stack exists (`infrastructure/stacks/machine_learning/falkordb/compose.yaml`) and the client exists (`oideachais/graph/falkordb_client.py`) but the cognify result is not persisted to it. The `graphiti` compose stack exists with both `neo4j` and `falkordb` profiles; `oideachais/graph/temporal.py` reimplements Graphiti in pure Python without ever connecting to the Graphiti service.

5. **No single source of truth for pipeline status.** The 21 Dagster asset modules, 11 CocoIndex flows, 8 BAML files, 6 leabharlann assets, 4 author-archive assets, and 70+ Leaving Cert assets are scattered across many directories. A user asking "is the primary curriculum pipeline end-to-end working today?" has to read every file.

## What Changes

### 1. `oideachais/STATUS.md` (new)

A single source of truth listing:

- Each BAML schema file → which dlt source backs it → which Dagster asset materialises it → which CocoIndex v1 (or v0) flow embeds it → which Cognee cognify pass enriches it.
- Each CocoIndex flow → API version (v0 or v1) → status (`working`, `broken_on_v1`, `unwired`).
- Each Dagster asset → group name → compute kind → partitions.
- Each dlt source → working directory path → partition keys.
- Per-nation × per-cycle coverage matrix for British Isles education (Ireland Aistear/Primary/JC/SC, England KS1-5, Scotland CfE, Wales CfW, NI KS1-5, Crown Dependencies).
- A "Refactor Roadmap" section linking to `oideachais/REFACTORING.md`.

### 2. `oideachais/REFACTORING.md` (new)

A backlog of refactoring + redundancy findings with explicit `Status` (`done` | `in_progress` | `backlog`) per item. Top items:

- 5 BAML functions (`ExtractHandwrittenEquations`, `ExtractZoteroMetadata`, `ExtractPrimaryFramework`, `ExtractJCSpec`, `ExtractCBADescriptor`) defined but not invoked from any dlt `extraction_metadata` resource.
- 10 v0 CocoIndex flows in `oideachais/cocoindex_flows/` that need migration to v1 (the package `__init__.py` paper-overs the broken imports with a try/except).
- 3 document extraction utilities (`_scanner._extract_text_from_{pdf,word,code}` + `document_factory/pdf_converter.py` + `cocoindex_flows/pdf_embedding.py:PDFEmbeddingPipeline`) that re-implement pymupdf + python-docx with slightly different error handling.
- 2 parallel graph stacks (`oideachais/cognee_integration/` + `oideachais/graph/{memgraph_client,falkordb_client,temporal}.py`).
- `oideachais/graph/temporal.py` re-implements Graphiti in pure Python without ever connecting to the Graphiti compose stack.

### 3. Per-area READMEs (new or rewritten)

- `oideachais/dlt_sources/uk/README.md` — coverage matrix per nation × cycle, with dlt source filenames, BAML extractors, Dagster assets, Cognee cognify passes.
- `oideachais/dlt_sources/ireland/README.md` — same matrix for Ireland. Highlights the *missing* `primary.py` and `junior_cycle.py` (which `baml_src/primary.baml` and `baml_src/junior_cycle.baml` reference but no dlt source backs).
- `oideachais/cocoindex_flows/README.md` — for each of the 11 flows: v0/v1 status, source, target, embedding model, query handler.
- `oideachais/dagster_defs/assets/README.md` — for each of the 21 asset modules: the asset names, compute kind, dependencies, partition definition.
- `baml_src/README.md` (new, moved from repo root) — for each of the 8 BAML files: schema classes, extraction functions, consumer pipelines, test coverage.
- `oideachais/agents/adk/README.md` + `oideachais/agents/agno/README.md` — the agent surface.

### 4. End-to-end stack overview doc (new)

`docs/06-infrastructure/leabharlann-stack-overview.md` — the end-to-end "how a leabharlann PDF flows through the stack" diagram, with:

- **Left**: `leabharlann/{ollscoil_na_gaillimhe,zotero,gaeilge,aigne}/` and `stedding/Takeout/` (the source trees).
- **Top**: Komodo (GitOps) + Infisical (secret vault) + Locket (runtime injection) + the DAGSTER_UNIFIED webserver + Dagster UI.
- **Centre**: Garage S3 (object store) + Lakekeeper (Iceberg REST catalog) + Lance Namespace (Iceberg adapter) + DuckLake (Postgres-backed catalog) + Lakehouse-OCI (production).
- **Middle**: DLT (ingestion) + BAML (structured extraction) + CocoIndex v1 (incremental embedding).
- **Right**: LanceDB (vector search) + Cognee (knowledge graph) + FalkorDB (graph cache) + Graphiti (bi-temporal graph) + Marimo (notebooks).
- **Bottom**: Pangolin (VPN) + Pocket ID (OIDC) + TinyAuth (auth) + CrowdSec (intrusion detection).

The doc explains how the 6 docker-compose layers (control plane → storage → engineering → machine learning → tools → browser) integrate with the `oideachais/` monorepo, the 5 leabharlann dlt sources, the 7 leabharlann Dagster assets, the 3 leabharlann CocoIndex v1 Apps, the 4 BAML schemas, and the 6 leabharlann search handlers.

## Impact

| Surface | Before | After |
|:--|:--|:--|
| `oideachais/STATUS.md` | (absent) | New single source of truth |
| `oideachais/REFACTORING.md` | (absent) | New refactor backlog with status |
| `oideachais/dlt_sources/uk/README.md` | (absent) | New coverage matrix |
| `oideachais/dlt_sources/ireland/README.md` | (absent) | New coverage matrix |
| `oideachais/cocoindex_flows/README.md` | V0-era, missing v1 modules | Rewritten for v0/v1 status |
| `oideachais/dagster_defs/assets/README.md` | (absent) | New asset catalogue |
| `baml_src/README.md` | (absent) | New BAML schema catalogue |
| `docs/06-infrastructure/leabharlann-stack-overview.md` | (absent) | New end-to-end stack diagram |
| DLT sources | 19 | 19 (no change in this change) |
| Dagster assets | 70+ | 70+ (no change in this change) |
| CocoIndex flows | 11 | 11 (no change in this change) |

## Out of scope (queued for follow-up changes)

- **Feature 1**: Primary + Junior Cycle British Isles dlt + BAML loop (closes the BAML-without-dlt gap). 5 new dlt sources + 5 Dagster assets + 5 BAML extraction functions invoked. Tracked in `oideachais/REFACTORING.md`.
- **Feature 2**: Cognee + FalkorDB cross-archive knowledge graph. 3 cognify assets + 1 cross-archive edges asset + 1 FastAPI route + 1 cron sensor. Tracked in `oideachais/REFACTORING.md`.
- **Feature 3**: LanceDB blob storage via the `lancedb` compose stack + RCLONE FUSE mount. New compose file + Komodo procedure + blob-mode CocoIndex. Tracked in `oideachais/REFACTORING.md`.
- **Feature 4**: Leabharlann full-document processing demo (sample PDFs → BAML → Cognee → FalkorDB → LanceDB blob → Dagster UI). New asset + Marimo notebook. Tracked in `oideachais/REFACTORING.md`.
- Bilingual BAML (`*_ga` fields) — deferred.
- Migrating the 10 v0 CocoIndex flows to v1 — deferred (separate change).
- `oideachais/graph/temporal.py` decision (delete, re-implement, or wire to the Graphiti compose stack) — deferred.

## Cross-references

- Lakehouse compose: `infrastructure/stacks/storage/lakehouse/compose.yaml`
- LanceDB stack with RCLONE FUSE profile: `infrastructure/stacks/machine_learning/lancedb/compose.yaml:44-75`
- FalkorDB stack: `infrastructure/stacks/machine_learning/falkordb/compose.yaml`
- Graphiti stack: `infrastructure/stacks/machine_learning/graphiti/compose.yaml`
- Existing BAML schemas: `baml_src/{aistear,primary,junior_cycle,curriculum_extraction,tertiary,ui_components,author_archive}.baml`
- Existing dlt sources: `oideachais/dlt_sources/{ireland,uk,crown_dependencies,domains,author_archive}/`
- Existing CocoIndex flows: `oideachais/cocoindex_flows/`
- Existing Dagster assets: `oideachais/dagster_defs/assets/`
- Recent leabharlann change: `openspec/changes/archive/2026-06-16-leabharlann-cocoindex-v1/`
