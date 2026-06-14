---
title: 'oideachais - Unified Celtic Education Platform'
domain: 'architecture'
status: 'stable'
description: 'The post-restructure oideachais data lakehouse quadrant. DLT sources for Ireland, NI, EN, SCT, WLS, IOM, JEY, GGY across 4 domains (education, medicine, law, statistics).'
read_when:
  - working in oideachais/
  - adding a new DLT source or Dagster asset
  - querying the unified lakehouse
updated: '2026-06-13'
supersedes:
  - docs/OIDEACHAIS_PIPELINE.md
  - docs/02-architecture/OIDEACHAIS_PIPELINE.md (prior version)
truth: sole
ccc_query_hints:
  - oideachais data lakehouse
  - dlt dagster education ireland uk
---

# oideachais - Unified Celtic Education Platform

> For the project identity + quadrant map, see
> [`docs/00-core/CLAUDE.md`](../../00-core/CLAUDE.md). This file is
> the **authoritative architecture doc for `oideachais/`** — the data
> lakehouse quadrant.

## What this is

A unified data platform for Celtic language education, covering **8 nations**
(Ireland, Northern Ireland, England, Scotland, Wales, Isle of Man, Jersey,
Guernsey) across **4 domains** (education, medicine, law, statistics) plus
a `site_analysis` sidecar for firecrawl/browserbase MCP page fingerprinting.

| Feature | Detail |
|---|---|
| Data assets | 30+ Dagster `@dlt_assets` + 7 per-subject Leaving Cert assets |
| DLT sources | 43 sources registered in `oideachais/sources.yaml` across 8 nations × 4 domains |
| Asset key contract | `{nation}.{domain}.{entity}` (e.g. `ie.education.ncca`) |
| Storage writes | DuckLake on Garage S3 (`oideachais.dlt_utils.destinations`) |
| Storage reads | MotherDuck (`md:oideachais`) via marimo / SPA / agents |
| Vector search | LanceDB (1024-dim BAAI/bge-m3 multilingual) |
| Knowledge graph | Cognee (1 dataset per domain + `oideachais_cross_nation`) |
| Embedding | CocoIndex (1 source.yaml-driven flow per domain) |
| Cross-namespace | 0 absolute `oideachais.data_platform.*` imports (CI-enforced) |

## Topology (5 quadrants + 8 workspace members)

This is **one** of the 5 quadrants. For the full picture, see
[`docs/00-core/CLAUDE.md`](../../00-core/CLAUDE.md).

```
oideachais/                                   ← this quadrant
├── dlt_sources/
│   ├── domains/                              ← canonical (Phase 5+)
│   │   ├── education/{ie,ni,en,sct,wls,iom,jey,ggy}/
│   │   ├── medicine/{ie,ni,en,sct,wls}/
│   │   ├── law/{ie,ni,en,sct,wls}/            ← statutory only
│   │   ├── statistics/                         ← future
│   │   └── site_analysis.py
│   ├── ireland/, uk/, crown_dependencies/    ← legacy re-export shims
│   ├── common/                                ← firecrawl_source, http_factories, shared.utils shim
│   └── celtic/, geospatial/, teanga/         ← vendor-copied + extracted
├── dagster_defs/
│   ├── definitions.py
│   ├── assets/
│   │   ├── ie/education/                      ← domain-first path
│   │   │   └── leaving_cert/
│   │   ├── ni/, en/, sct/, wls/, iom/, jey/, ggy/
│   │   └── site_analysis/                     ← Phase 8
│   ├── sensors/, schedules/, resources.py
│   ├── partitions_v2.py
│   └── asset_checks.py
├── dlt_utils/
│   ├── source_factory.py                      ← 7-method SourceFactory
│   ├── destinations.py                        ← DuckLake/R2 factory
│   └── ...
├── cocoindex_flows/                           ← BAAI/bge-m3 flows
├── cognee_integration/                        ← cognify assets
├── agents/                                    ← ADK + AGNO + BAML
├── ocr/                                       ← 10 OCR/HTR models
├── site_analysis/                             ← firecrawl + browserbase MCP
│   ├── extractor.py
│   ├── _stubs/                                ← USE_LOCAL_SCRAPES=true mode
│   └── baml_src/site_analysis.baml            ← BAML schema
├── baml_src/                                  ← type-safe LLM extraction
├── sources.yaml                               ← canonical source registry
└── tests/                                     ← 30 passing pytests
```

## How the 4 layers compose

For every source in `sources.yaml`:

1. **DLT ingestion** (`oideachais/dlt_sources/domains/{domain}/{nation}/{entity}.py`)
   — pulls from the public endpoint, yields page/record dicts, applies
   `merge` write disposition on `{url|id}`.
2. **DuckLake destination** (`oideachais/dlt_utils/destinations.py`)
   — Parquet on Garage S3, Postgres catalog; one schema per
   `oideachais.{domain}.{nation}`.
3. **LanceDB embedding** (`oideachais/cocoindex_flows/`)
   — `bge-m3` 1024-dim; ≥100-text batches; `bge-m3` 1024-dim per
   `oideachais/cocoindex_flows/{domain}_embedding.py`.
4. **Cognee cognify** (`oideachais/cognee_integration/`)
   — 1 dataset per domain; cross-nation edges in
   `oideachais_cross_nation`.

## Where the canonical docs live

- Data architecture: [`docs/02-data-platform/data-architecture.md`](../../02-data-platform/data-architecture.md)
- DLT pipeline patterns: [`docs/02-data-platform/dlt-pipelines.md`](../../02-data-platform/dlt-pipelines.md)
- Dagster orchestration: [`docs/02-data-platform/dagster-orchestration.md`](../../02-data-platform/dagster-orchestration.md)
- Cross-domain asset-key contract: [`docs/02-data-platform/cross-domain-registry.md`](../../02-data-platform/cross-domain-registry.md)
- Storage mental model: [`docs/02-data-platform/storage-mental-model.md`](../../02-data-platform/storage-mental-model.md)

## OpenSpec change record

| Change | Status |
|---|---|
| `lateralise-british-isles-domains` | scaffold (Phase 5+ shipped; pending archive) |
| `leaving-cert-2026` | scaffold (per-subject assets + LC SPA live) |
| `cianfhoghlaim-oideachais-baml-first` | scaffold (BAML pipeline integration) |
| `consolidate-external-libs-into-tuatha` | implemented (post-monorepo-restructure-v2) |
| `monorepo-restructure-v2` | implemented (the 5-quadrant topology you see now) |
| `docs-restructuring` | implemented (the 7-domain canonical tree) |

## See also

- [`oideachais/README.md`](../../../oideachais/README.md) — runtime README
- [`oideachais/PIPELINE_OPERATIONS.md`](../../../oideachais/PIPELINE_OPERATIONS.md) — operational runbook
- [`oideachais/CHANGELOG.md`](../../../oideachais/CHANGELOG.md) — release notes
