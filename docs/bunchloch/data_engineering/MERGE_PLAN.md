# Data Engineering Subdirectory Flattening — MERGE_PLAN.md

**Date:** 2026-06-06  
**Phase:** 1 — Merge Planning  
**Total subdirs:** 29  
**Total .md files:** ~726  
**Target merged files:** 12  

---

## Merge Group 1: dagster-comprehensive.md

| Attribute | Detail |
|-----------|--------|
| **Subdirs** | `dagster/` |
| **File count** | 62 |
| **Key content** | Dagster expert skill (487 lines), API quick reference, design patterns research, DuckLake integration, Iceberg integration, DSPy components, Dagster integration research (dlt, datadog, duckdb), GCP/K8s deployment guides, orchestration for CocoIndex/Graphiti |
| **Firecrawl context** | `docs.dagster.io` — Asset-based orchestration, declarative programming model, integrated lineage/observability, Dagster Plus managed offering |
| **Output** | `docs/data_engineering/dagster-comprehensive.md` |
| **Merge strategy** | Consolidate dagster.md (skill), dagster-api-quick-reference.md, dagster-design-patterns-research.md, and dagster-research.md into one guide. Preserve dagster-dspy, dagster-iceberg, dagster-ducklake, dagster-modal, dagster-sqlmesh, dagster-evidence as subsection appendices with their own READMEs inlined. Keep deployment guides as a dedicated section. |

---

## Merge Group 2: dlt-comprehensive.md

| Attribute | Detail |
|-----------|--------|
| **Subdirs** | `dlt/` |
| **File count** | 23 |
| **Key content** | dltHub expert skill (501 lines), GitHub API init research, Modal deployment, small-data-sf-2025 patterns, BAML/ORPC/MCP typesafe pipeline analysis, Kafka integration, SQLMesh integration, marimo exploration, GCP Cloud Function deployment |
| **Firecrawl context** | `dlthub.com/docs` — Open-source Python library, REST API sources, SQL sources, filesystem sources, schema inference/data normalization, incremental loading, schema evolution/contracts, 8,000+ managed sources, agent-native workflow |
| **Output** | `docs/data_engineering/dlt-comprehensive.md` |
| **Merge strategy** | Core dlthub.md skill as main body. Append github_api_init research as `## GitHub API Source Pattern`. Inline deployment guides (GCP Cloud Function/Run), small-data-sf-2025 patterns, and tool integration notes (Kafka, SQLMesh, marimo) as appendices. |

---

## Merge Group 3: duckdb-reference.md

| Attribute | Detail |
|-----------|--------|
| **Subdirs** | `duckdb/` |
| **File count** | 9 |
| **Key content** | DuckDB expert skill (483 lines), comprehensive research, spatial extension, SQLMesh integration, MotherDuck/PlanetScale integration, pg_duckdb extensions, geospatial analysis |
| **Firecrawl context** | `duckdb.org/docs` — Columnar storage, client APIs (Python/JS/Java/Rust/R/Go/C/C++/WASM), SQL dialect, data types (Array/Map/Struct/Union/Geometry/JSON/Variant), extensions (Iceberg/Delta/Lance/Spatial/Postgres/MySQL), DuckLake core extension, Quack remote protocol, Lakehouse formats, partitioning (Hive), performance tuning, guides for Python/Jupyter/marimo/Ibis/Polars |
| **Output** | `docs/data_engineering/duckdb-reference.md` |
| **Merge strategy** | Core duckdb.md skill with API examples. Append comprehensive research as `## Reference`, spatial as `## Geospatial`, MotherDuck as `## Cloud: MotherDuck`. Firecrawl context provides the authoritative extension catalog and SQL dialect overview to structure the reference section. |

---

## Merge Group 4: lancedb-reference.md

| Attribute | Detail |
|-----------|--------|
| **Subdirs** | `lance/` |
| **File count** | 30 |
| **Key content** | LanceDB research report (1009 lines — comprehensive), KCG summary, Lance namespace interface, Lance + Ray distributed indexing, 15+ example READMEs (RAG LOTR, ColPali, hybrid search, multimodal search, multilingual RAG, time-travel RAG, geospatial recommendation, chunking analysis, cognee-RAG), Iceberg integration, Ibis+LanceDB integration |
| **Firecrawl context** | `lancedb.github.io/lancedb` — SDK Reference with Python/JS/Java/Rust APIs, links to full docs at docs.lancedb.com |
| **Output** | `docs/data_engineering/lancedb-reference.md` |
| **Merge strategy** | lancedb-research-report.md as core body (covers architecture, use cases, API, performance). KCG_SUMMARY.md as executive summary. Lance+Ray docs as `## Distributed Indexing`. Group example READMEs into `## Patterns & Recipes` with subsections: RAG patterns, multimodal, temporal, geospatial, hybrid search. DuckDB Lance extension note from Firecrawl. |

---

## Merge Group 5: marimo-reference.md

| Attribute | Detail |
|-----------|--------|
| **Subdirs** | `marimo/` |
| **File count** | 41 |
| **Key content** | marimo skill (465 lines), KCG summary, Cloudflare deployment, multi-language READMEs, example apps (AI chat/tools, cloud/Modal, frameworks: FastAPI/Flask/FastHTML, layouts, SQL, HuggingFace, MotherDuck embeddings, Sage, testing, markdown, control flow) |
| **Firecrawl context** | `docs.marimo.io` — Reactive Python notebook, batteries-included (replaces Jupyter/Streamlit/jupytext/ipywidgets/papermill), git-friendly .py storage, native SQL, AI-native (Claude Code/Copilot), deterministic execution, WASM export, interactive dataframes, built-in package management, NumFOCUS affiliated |
| **Output** | `docs/data_engineering/marimo-reference.md` |
| **Merge strategy** | Core marimo.md skill as introduction. Append KCG_SUMMARY.md. Create `## Patterns` from example READMEs organized by theme (AI integration, deployment, data, frameworks). Firecrawl context enriches the intro with authoritative feature list. |

---

## Merge Group 6: cocoindex-comprehensive.md

| Attribute | Detail |
|-----------|--------|
| **Subdirs** | `cocoindex/` |
| **File count** | 129 |
| **Key content** | API research (250 lines), code MCP server docs (CLAUDE.md, development guide, architecture: ASTChunking, DB abstraction, embedding, flow, hybrid search, MCP server, RAG architecture, tree-sitter). Also: S3 embedding, knowledge graph construction, old STATE/TODO files. |
| **Firecrawl context** | `cocoindex.io/docs` — State-driven programming, processing components, memoization, incremental processing, `mount_each()` pattern, App definition, `localfs` connector, `declare_file()` target state, `cocoindex update` CLI. Docs cover: Core Concepts, Programming Guide (Apps, Flows, Processing Components, Memoization, Target State), Connectors (localfs, S3, etc.), Getting Started. |
| **Output** | `docs/data_engineering/cocoindex-comprehensive.md` |
| **Merge strategy** | Firecrawl-derived quickstart as introduction. Core concepts from docs/cocoindex/*.md files grouped into `## Architecture: Flows, Components, Memoization` and `## Embedding & Search`. MCP server docs consolidated into `## MCP Server Integration`. Skip old STATE/TODO files and old/ directory (archival). API research as `## Programmatic API`. |

---

## Merge Group 7: semantic-layer-reference.md

| Attribute | Detail |
|-----------|--------|
| **Subdirs** | `semantic_layer/` |
| **File count** | 249 |
| **Key content** | Boring Semantic Layer (BSL) — built on Ibis. Docs cover: getting-started, bucketing, builder-agent, charting, comparison, compose, indexing, MCP integration, nested subtotals, percentage/total, profiling, query-agent (chat/LLM-tool/MCP/skill), query-methods, semantic-table, sessionized queries, windowing, YAML config, full API reference (573 lines). Also ~200 prompt template files for query agents (LangChain and MCP backends). |
| **Firecrawl context** | N/A (BSL is a niche package, no dedicated docs site beyond GitHub) |
| **Output** | `docs/data_engineering/semantic-layer-reference.md` |
| **Merge strategy** | API reference (reference.md) as core body. getting-started.md as introduction. Query agent docs grouped under `## Query Agent` (MCP, LLM Tool, AI Skills). YAML config as `## Configuration`. Charting and advanced features (bucketing, windowing, sessionized) as `## Advanced Patterns`. Prompt templates (200+ files) summarized into a single reference table — do NOT inline all 200 files. |

---

## Merge Group 8: data-versioning.md

| Attribute | Detail |
|-----------|--------|
| **Subdirs** | `lakefs/` (38 files) + `ducklake/` (7 files) |
| **File count** | 45 |
| **Key content** | lakeFS: Git-like data versioning for S3, 20+ standalone examples (Spark medallion, Iceberg, Delta Lake, Trino, WAP, Dagster, Airflow, Databricks CI/CD, Kafka, Flink, Prefect, LangChain/OpenAI, MLflow/PyTorch, Labelbox, ParadeDB, Red Hat OpenShift AI). DuckLake: TPCH demo, SQLMesh tutorial, MotherDuck deployment, MLflow+Kafka integration. |
| **Firecrawl context** | DuckDB docs list DuckLake as a core extension for lakehouse capabilities. DuckDB also has native Iceberg and Delta extensions that complement lakeFS. |
| **Output** | `docs/data_engineering/data-versioning.md` |
| **Merge strategy** | **Part 1 (DuckLake):** README.md + tutorial files → Lakehouse on DuckDB. **Part 2 (lakeFS):** KCG_SUMMARY.md as intro, example READMEs grouped by category (Iceberg/Data Lakehouse, ML/AI, Workflow Orchestration, Standalone Examples). lakeFS-samples READMEs are short (each ~30-80 lines); inline the most significant (Spark medallion, WAP, Dagster, LLM-LangChain) and reference-table the rest. Connect the two via DuckDB's DuckLake/Iceberg/Delta extensions. |

---

## Merge Group 9: geoai-reference.md

| Attribute | Detail |
|-----------|--------|
| **Subdirs** | `geoai/` |
| **File count** | 35 |
| **Key content** | GeoAI package docs (PyPI package by Qiusheng Wu): README (144 lines, comprehensive intro), full API docs (auto, change_detection, classify, detectron2, dinov3, download, extract, geo_agents, geoai, hf, installation, map_tools, map_widgets, moondream, qgis_plugin, sam, segment, segmentation, timm_segment, timm_train, train, utils). Also: geospatial-book, geospatial linguistics, Ibis visualization, particle effects, QGIS plugin README, JOSS paper. |
| **Firecrawl context** | N/A (academic package) |
| **Output** | `docs/data_engineering/geoai-reference.md` |
| **Merge strategy** | README.md as introduction. API docs (docs/*.md) consolidated into a unified `## API Reference` organized by capability: Data Acquisition, Model Training, Inference, Segmentation, Visualization, QGIS Plugin. Geospatial research notes (Ibis visualization, linguistics, particle effects) as `## Research & Patterns`. Paper abstract as closing appendix. |

---

## Merge Group 10: knowledge-systems.md

| Attribute | Detail |
|-----------|--------|
| **Subdirs** | `baml/` (14) + `cognee/` (2) + `graphiti/` (2) + `feast/` (3) |
| **File count** | 21 |
| **Key content** | **BAML:** Structured LLM output (type-safe DSL, Schema-Aligned Parsing), dynamic schemas, multimodal evals, git-worktrees, DLT integration, document processing pipeline, "extract anything" patterns. **Cognee:** AI memory platform (ECL pipeline — Extract/Cognify/Load), knowledge graphs, OpenAPI research. **Graphiti:** Bi-temporal knowledge graphs, episodic memory paradigm, temporal queries, crypto adaptation. **Feast:** Feature store patterns (point-in-time joins, data models, operational patterns, SDK API research, LLM integration). |
| **Firecrawl context** | N/A (specialized tools) |
| **Output** | `docs/data_engineering/knowledge-systems.md` |
| **Merge strategy** | Four-part structure: **Part 1 (BAML):** Structured LLM output — baml.md skill + baml-comprehensive-guide + baml-dlt-integration + document-processing-pipeline. **Part 2 (Cognee):** AI memory — cognee.md skill + OpenAPI research. **Part 3 (Graphiti):** Temporal graphs — temporal-graphs.md + crypto adaptation. **Part 4 (Feast):** Feature stores — patterns & best practices + SDK API research. Connect via the common theme: knowledge representation and retrieval systems for AI agents. |

---

## Merge Group 11: data-architecture.md

| Attribute | Detail |
|-----------|--------|
| **Subdirs** | `data-engineering/` (16) + `education/` (7) |
| **File count** | 23 |
| **Key content** | **Data-engineering:** Stack architecture (BigQuery, Dagster, DuckDB, MotherDuck, dbt, Evidence), Graph tech integration, Olake/Lakekeeper/RisingWave integration, Rust/DuckDB/TanStack/CopilotKit, data sources management, Lance namespace/Ray production patterns, self-hosted stack visualization (Supabase/Pigsty), Cognee/Graphiti visualization. **Education:** Education data insights (data richness, research questions), British Isles parallel data sources, EU/Irish datasets, UK education datasets analysis, Leaving Cert material app, AI syllabus to JSON schema. |
| **Firecrawl context** | N/A (internal architecture docs) |
| **Output** | `docs/data_engineering/data-architecture.md` |
| **Merge strategy** | **Part 1 (Platform Architecture):** data-engineering/README.md + KCG_SUMMARY.md + core integration docs → unified architecture diagram and stack decisions. **Part 2 (Education Data):** education_data_insights_summary.md + dataset analysis → domain-specific data architecture patterns. Connect via the theme of designing data platforms for education use cases. |

---

## Merge Group 12: tool-ecosystem.md

| Attribute | Detail |
|-----------|--------|
| **Subdirs** | `crawl4ai/` (7) + `firecrawl/` (1) + `gemini/` (3) + `gradio/` (2) + `ibis/` (2) + `iceberg/` (1) + `kafka/` (1) + `logfire/` (1) + `memgraph/` (2) + `olake/` (4) + `pydantic/` (3) + `risingwave/` (4) + `evidence/` (2) |
| **File count** | 33 |
| **Key content** | 13 tools in one consolidated reference: **Web extraction** (Crawl4AI — async crawler, CSS+LLM extraction; Firecrawl — extract, agent, monitor), **AI/LLM** (Gemini 3 hackathon, code assist config, quick reference), **UI** (Gradio — ML app framework, OpenAPI research), **Data** (Ibis — portable dataframe, LanceDB integration; Iceberg — browser-based WASM with DuckDB; Kafka — topic mirroring with Bento), **Observability** (Logfire — OpenTelemetry-based), **Graph** (Memgraph — in-memory graph DB, Cypher, real-time analytics), **Replication** (OLake — CDC to Iceberg, Dagster orchestration), **Validation** (Pydantic v2 — models, validation, LLM integration), **Streaming** (RisingWave — streaming SQL, materialized views, CDC pipelines), **BI** (Evidence — SQL-driven dashboards). |
| **Firecrawl context** | N/A (tool-specific docs already in repo) |
| **Output** | `docs/data_engineering/tool-ecosystem.md` |
| **Merge strategy** | Grouped reference by tool category: `## Web Data Acquisition` (Crawl4AI + Firecrawl), `## AI & LLM Infrastructure` (Gemini + Gradio), `## Data Processing & Analysis` (Ibis + Pydantic + Evidence), `## Streaming & Replication` (Kafka + RisingWave + OLake), `## Graph & Geo` (Memgraph + Iceberg), `## Observability` (Logfire). Each tool gets a concise 1-2 page entry with: overview, key API patterns, and integration notes with the KCG stack. |

---

## Summary Table

| # | Output File | Subdirs Merged | .md Files | Firecrawl Sources |
|---|-------------|----------------|-----------|-------------------|
| 1 | `dagster-comprehensive.md` | dagster | 62 | docs.dagster.io |
| 2 | `dlt-comprehensive.md` | dlt | 23 | dlthub.com/docs |
| 3 | `duckdb-reference.md` | duckdb | 9 | duckdb.org/docs |
| 4 | `lancedb-reference.md` | lance | 30 | lancedb.github.io/lancedb |
| 5 | `marimo-reference.md` | marimo | 41 | docs.marimo.io |
| 6 | `cocoindex-comprehensive.md` | cocoindex | 129 | cocoindex.io/docs |
| 7 | `semantic-layer-reference.md` | semantic_layer | 249 | — |
| 8 | `data-versioning.md` | lakefs, ducklake | 45 | duckdb.org/docs (DuckLake ext) |
| 9 | `geoai-reference.md` | geoai | 35 | — |
| 10 | `knowledge-systems.md` | baml, cognee, graphiti, feast | 21 | — |
| 11 | `data-architecture.md` | data-engineering, education | 23 | — |
| 12 | `tool-ecosystem.md` | crawl4ai, firecrawl, gemini, gradio, ibis, iceberg, kafka, logfire, memgraph, olake, pydantic, risingwave, evidence | 33 | — |
| | **TOTAL** | **29 subdirs** | **~700** | **6 sites** |

---

## Execution Notes

1. **Order of execution:** Start with Groups 3, 4, 5 (reference docs — most self-contained), then 1, 2 (comprehensive), then 6, 7 (large merges), then 8-12 (multi-subdir merges).

2. **Skip list** (files excluded from merge):
   - `cocoindex/cocoindex-code-mcp-server/docs/old/*.md` — archival state/todo files
   - `semantic_layer/boring-semantic-layer/docs/md/prompts/` — 200+ prompt templates; summarize as reference table instead of inlining
   - `lakefs/lakeFS-samples/` — READMEs only; skip .ipynb, Docker, JSON/YAML configs, scripts (already removed per KCG_SUMMARY.md)

3. **Quality gates:** After each merge, verify:
   - All critical API signatures preserved
   - Code blocks correctly formatted
   - Internal cross-references updated to new filenames
   - No orphaned links

4. **Post-merge cleanup:** After all 12 merged files are produced and validated:
   - Archive the 29 subdirs into `docs/data_engineering/.archive/`
   - Update `docs/data_engineering/INDEX.md` to point to the 12 new files
   - Run `ccc:index` to refresh the codebase index
