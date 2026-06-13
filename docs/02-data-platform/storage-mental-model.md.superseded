---
title: 'Storage Mental Model'
domain: 'data_platform'
status: 'stable'
description: 'One-liner: writes go to DuckLake, reads go to MotherDuck, Iceberg is the long-tail catalogue. The full lakehouse architecture is in data-architecture.md.'
read_when:
  - debugging a write/read mismatch
  - deciding where a new asset reads from
  - onboarding a new analyst
truth: sole
updated: '2026-06-13'
ccc_query_hints:
  - storage mental model ducklake motherduck iceberg
---

# Storage Mental Model

> **One line:**
> - **Writes** → **DuckLake** (Parquet on Garage S3, Postgres catalog)
> - **Reads** (marimo, SPA, public) → **MotherDuck** (`md:oideachais`)
> - **Long-tail catalogue** → **Apache Iceberg** via Lakekeeper (not written to today; exists for future parity)
> - **Change watching** → **ChangeDetection.io** at `infrastructure/stacks/tools/changedetection` and on `arm1-oci`

The full architecture is in [`docs/02-data-platform/data-architecture.md`](data-architecture.md).
The constraint list is in [`docs/00-core/CONSTRAINTS.md`](../00-core/CONSTRAINTS.md).
The pattern reference is in [`docs/02-data-platform/STORAGE.md`](STORAGE.md).

## Three layers

### 1. DuckLake (write substrate)

- **What**: SQL table format on Parquet files; ACID on object storage
  via a Postgres catalog.
- **Where it lives in this monorepo**:
  - `s3://ducklake/oideachais/{domain}/{nation}/{table}/*.parquet`
  - Catalog: Postgres at `localhost:5433` (local) or PlanetScale (prod)
  - Concrete code: `oideachais/dlt_utils/destinations.py:get_dlt_destination()`
- **Who writes**:
  - `oideachais/dagster_defs/assets/*` (the unified asset graph)
  - `oideachais/dlt_sources/domains/*` (the 43 registered sources)
  - `tuatha/dagster_assets/*` (tuath's curriculum-in-game assets)
- **Schema convention**: `oideachais.{domain}.{nation}` — e.g.
  `oideachais.education.ie.ncca_pages`. Each DLT run auto-creates
  the schema on first write.

### 2. MotherDuck (read substrate)

- **What**: Managed DuckDB-compatible service; attaches a remote
  catalog over HTTPS. Used for analyst-facing reads.
- **Where it lives**:
  - `md:oideachais` (the canonical public database)
  - Concrete code: `oideachais/api/ducklake_reader.py` (the API reader)
- **Who reads**:
  - `oideachais/notebooks/dashboards/*` (marimo dashboards)
  - `oideachais/api/` (the SPA backend)
  - agents (ADK / AGNO via the motherduck MCP at `opencode.json`)
- **Why a separate read path**:
  - MotherDuck handles many concurrent readers (no single-threaded
    segfault risk on the read side).
  - Public analyst queries don't touch the local Postgres catalog.

### 3. Apache Iceberg via Lakekeeper (long-tail catalogue)

- **What**: Open-source Iceberg REST catalog. Stays in the stack
  on port 8181 (Lakekeeper) + 8182 (Lance Namespace sidecar).
- **Why we don't write to it today**:
  - DuckLake is sufficient for the current data volume.
  - Iceberg's value is cross-engine compatibility (Spark, Trino,
    Athena). We don't run those.
- **When it gets used** (future):
  - If we need a second query engine (e.g. Athena for public
    analytics).
  - If we need cross-region replication at the catalog level.
- **Concrete code**: `infrastructure/stacks/storage/lakehouse/` —
  the Lakekeeper + Lance Namespace sidecar running at 8181/8182.

### 4. ChangeDetection.io (change-watching)

- **What**: Stand-alone service that watches sitemaps and detects
  changes on public sources.
- **Where**:
  - Compose: `infrastructure/stacks/tools/changedetection/compose.yaml`
  - Deployed on: `arm1-oci` (the control-plane host)
  - Local checkout: `/Users/cianmacandeisigh/dev/kings_college_galway/infrastructure/stacks/tools/changedetection`
- **Why we use it** (vs firecrawl's `changeTracking`):
  - ChangeDetection.io is the canonical change-watcher for
    `oideachais/sources.yaml` — it has a UI, history, and webhooks.
  - It is one of the 88 stacks; it's already paid for in our
    infrastructure budget.
  - firecrawl's `changeTracking` is a single-shot endpoint; we
    don't get history without re-running.

## How the three layers interact

```
                  ┌──────────────┐
   DLT sources ───▶│   DuckLake   │──┐
                  │  (writes)    │  │
                  └──────────────┘  │  ┌────────────┐
                                     ├─▶│ MotherDuck │
                  ┌──────────────┐  │  │  (reads)   │
   Sitemap sensors ┤ Lakehouse ┤──┘  └────────────┘
   ───▶ 8181/8182  │  (Iceberg) │
                  └──────────────┘
                          ▲
                          │ long-tail catalogue
                          │ (future)

   ChangeDetection.io ────▶ sitemap sensors
       (deployed on arm1-oci)
```

## See also

- [`docs/02-data-platform/data-architecture.md`](data-architecture.md) — full architecture
- [`docs/02-data-platform/STORAGE.md`](STORAGE.md) — pattern reference
- [`docs/02-data-platform/cross-domain-registry.md`](cross-domain-registry.md) — asset-key contract
- [`docs/01-platform-architecture/infrastructure-stacks.md`](../01-platform-architecture/infrastructure-stacks.md) — stack index
- [`docs/03-agents/change-detection.md`](../03-agents/change-detection.md) — sensor patterns
