# Oideachais (The Engine)

The `oideachais` directory forms the core data engine and lakehouse of the `cianfhoghlaim` stack. It orchestrates the extraction, loading, and transformation (ELT) of all Irish curriculum and examination data.

## The DuckLake Architecture

We utilize an offline-first, highly federated lakehouse architecture rather than expensive cloud data warehouses.

### 1. Extraction (DLT & Firecrawl)
*   **Pipelines**: Located in `data_platform/dlt_sources/ireland/`.
*   **Sources**: `ncca.ie`, `curriculumonline.ie`, and `examinations.ie`.
*   **Offline Fallback (`USE_LOCAL_SCRAPES`)**: To avoid burning Firecrawl API credits and risking rate limits during development, our DLT pipelines automatically intercept network calls and load from `stedding/ingest_queue/`. This queue contains over 7,000 cached structural documents (JSON payloads with base64 PDFs and Markdown).

### 2. Orchestration (Dagster)
*   **Multi-Partitioned Assets**: We track the materialized state of the Irish curriculum dynamically. For example, `ireland/curriculum/junior_cycle` is partitioned by language and subject (e.g., `en|mathematics`).
*   **Centralized Sink**: All pipelines write to a unified DuckDB database (`curriculum_unified.duckdb`) to ensure that syllabi, exam papers, and examiner reports can be seamlessly joined using SQL.

### 3. Storage (DuckDB + Garage S3)
*   The raw binaries (PDFs) are streamed into local S3-compatible object storage (`Garage S3` or `Cloudflare R2`), while the metadata and extracted text are cataloged in DuckDB (managed by `Lakekeeper`).

### 4. Interactive Frontend (TanStack Start)
*   The structured data is surfaced through highly-reactive, SSR-first frontend applications located in `web_app/` and `dashboard/`, utilizing TanStack DB for offline differential data syncs.

## Agent Guidelines
If modifying these pipelines, you MUST assume the `data-engineer` persona.
- Ensure you run `scripts/sync_agent_docs.sh` to update telemetry after altering the DLT pipeline schema.
- **NEVER** use absolute imports originating from the root (e.g., `from oideachais.data_platform...`) inside `data_platform`. Use relative imports to prevent Dagster module resolution crashes.
