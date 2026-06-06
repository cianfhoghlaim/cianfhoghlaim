# Data Engineering — Research Index

Centralized hub for data engineering, pipeline architecture, and AI/ML integration research for the Cianfhoghlaim platform.

---

## Comprehensive Merged Guides

These are the primary reference documents, consolidated from hundreds of scattered files:

| Guide | Source Files | Topics |
|-------|-------------|--------|
| **[DLT_COMPLETE_GUIDE.md](./DLT_COMPLETE_GUIDE.md)** | 22 files from `dlt/` | Resources, sources, incremental loading, REST API, SQLMesh, Kafka, deployment, BAML type-safety |
| **[ARCHITECTURE.md](./ARCHITECTURE.md)** | 19 source documents | Lakehouse, streaming, orchestration, ingestion, transformation, AI/ML integration |

---

## Core Architecture Documents

| File | Topics |
|------|--------|
| `ARCHITECTURE.md` | 6-layer architecture, DuckLake, RisingWave, Dagster, DLT, SQLMesh, Ibis, CocoIndex, LanceDB |
| `data-architecture.md` | Data modeling, schema design, type systems |
| `data-pipeline-architecture.md` | Pipeline patterns, orchestration strategies |
| `data-sources.md` | Source catalog and acquisition strategies |
| `Ontology and Temporal Graphs Research.md` | Knowledge graph ontologies, temporal data modeling |
| `stage-3-production-multi-agent-systems.md` | Multi-agent production patterns |
| `transformers.md` | Transformer architecture and fine-tuning |

---

## Subdirectories by Topic

### Pipeline & Orchestration

| Directory | Content | Files |
|-----------|---------|-------|
| `dlt/` | DLT data load tool → **See [DLT_COMPLETE_GUIDE.md](./DLT_COMPLETE_GUIDE.md)** | 22 |
| `dagster/` | Dagster orchestration patterns | — |
| `sqlmesh-ibis/` | SQLMesh transformations + Ibis portable dataframe | — |

### Storage & Lakehouse

| Directory | Content | Files |
|-----------|---------|-------|
| `duckdb/` | DuckDB analytical database | — |
| `ducklake/` | DuckLake lightweight lakehouse | — |
| `iceberg/` | Apache Iceberg table format | — |
| `lakefs/` | LakeFS version control for data | — |
| `olake/` | OLake CDC replication | — |

### Streaming & Real-Time

| Directory | Content | Files |
|-----------|---------|-------|
| `risingwave/` | RisingWave streaming database | — |
| `kafka/` | Kafka event streaming | — |

### AI/ML & Knowledge

| Directory | Content | Files |
|-----------|---------|-------|
| `cocoindex/` | CocoIndex incremental indexing, LanceDB, BAML extraction | — |
| `cognee/` | Cognee knowledge graph memory | — |
| `graphiti/` | Graphiti temporal knowledge graph | — |
| `memgraph/` | Memgraph graph database | — |
| `lance/` | Lance columnar format | — |
| `feast/` | Feast feature store | — |

### Web & Data Acquisition

| Directory | Content | Files |
|-----------|---------|-------|
| `crawl4ai/` | Crawl4AI web scraping | — |
| `firecrawl/` | Firecrawl scraping platform | — |

### Semantic Layer & Analytics

| Directory | Content | Files |
|-----------|---------|-------|
| `semantic_layer/` | Cube.js, Rill examples | ~400 |
| `evidence/` | Evidence.dev BI dashboards | — |
| `marimo/` | Marimo reactive notebooks | — |
| `ibis/` | Ibis portable dataframe API | — |

### Type Systems & Schema

| Directory | Content | Files |
|-----------|---------|-------|
| `baml/` | BAML schema definitions | — |
| `pydantic/` | Pydantic v2 validation | — |

### Geospatial & Vision

| Directory | Content | Files |
|-----------|---------|-------|
| `geoai/` | Geospatial AI, QGIS plugin, Detectron2, SAM | ~30 |

### Other

| Directory | Content | Files |
|-----------|---------|-------|
| `education/` | Education data sources | — |
| `gemini/` | Google Gemini integration | — |
| `gradio/` | Gradio UI framework | — |
| `logfire/` | Pydantic Logfire observability | — |
| `data-engineering/` | Additional DE research | — |

---

## Related Directories

- **Infrastructure:** `../bonneagar/` — Deployment, networking, secrets
- **Agent skills:** `../../.agents/skills/` — Agent skill definitions
- **Live pipelines:** `../../oideachais/` — Production data platform code
