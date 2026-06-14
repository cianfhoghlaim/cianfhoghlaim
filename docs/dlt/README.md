# dlt (Data Load Tool) Reference Library

dlt is an open-source Python library for declarative data loading and ELT pipelines. The `docs/dlt/` library is consolidated from 25 root .md + 3 example subdirs.

Last consolidated: 2026-06-14

---

## Core reference

| Document | Description |
|----------|-------------|
| [dlt-comprehensive.md](dlt-comprehensive.md) | 6,960-line merged doc — dltHub expert skill, deployment patterns, tool integrations (synthesis of 23 source files) |
| [DLT_COMPLETE_GUIDE.md](DLT_COMPLETE_GUIDE.md) | Alternative complete guide |
| [dlthub.md](dlthub.md) | dltHub codebase analysis |
| [dlthub-codebase-analysis.md](dlthub-codebase-analysis.md) | dltHub code-level analysis |
| [dlt-baml-orpc-mcp-typesafe-pipeline-analysis.md](dlt-baml-orpc-mcp-typesafe-pipeline-analysis.md) | Type-safe end-to-end pipeline (BAML + orpc + MCP) |

## Topic-specific

| Document | Topic |
|----------|-------|
| [dlt - SQLMesh.md](dlt%20-%20SQLMesh.md) / [(1)](dlt%20-%20SQLMesh(1).md) | SQLMesh integration |
| [Transformations _ dlt Docs.md](Transformations%20_%20dlt%20Docs.md) / [(1)](Transformations%20_%20dlt%20Docs(1).md) | Transform patterns (two scrapes, kept for context) |
| [crawl4ai-dlt.md](crawl4ai-dlt.md) | crawl4ai → dlt pipeline |
| [baml-dlt-integration.md](baml-dlt-integration.md) | BAML structured extraction feeding dlt |

## Deployment (Google Cloud)

| Document | Topic |
|----------|-------|
| [Deploy GCP Cloud Function as a webhook _ dlt Docs.md](Deploy%20GCP%20Cloud%20Function%20as%20a%20webhook%20_%20dlt%20Docs.md) | Webhook pattern |
| [Deploy with Google Cloud Functions _ dlt Docs.md](Deploy%20with%20Google%20Cloud%20Functions%20_%20dlt%20Docs.md) | Cloud Functions pattern |
| [Deploy with Google Cloud Run _ dlt Docs.md](Deploy%20with%20Google%20Cloud%20Run%20_%20dlt%20Docs.md) | Cloud Run pattern |

## Reference scripts (large .py)

| Script | Description |
|--------|-------------|
| `dlt_optimisation.py` | Performance optimization reference |
| `dlt_OpenAPI_Generator.py` | OpenAPI source generator |
| `dlt_lance.py` | LanceDB destination reference |
| `dlt_cognee_memgraph.py` | Cognee + Memgraph destination |
| `dlt_dagster_jaffle.py` | Dagster + dlt + jaffle-shop example |
| `cognee_taxi_dataset demo.py` | Cognee ingestion example |

## Examples (3 subdirs in `examples/`)

- `examples/dlt_modal/` — Modal deployment
- `examples/github_api_init/` — GitHub API ingestion (init script + 7 research .md)
- `examples/small-data-sf-2025/` — Small Data SF 2025 workshop (Elvis)

## Note on duplicates

`dlt (dagster-dlt) _ Dagster Docs.md` was a byte-identical dupe of the same file in `dagster/`; kept in `dagster/` (it documents the Dagster integration) and removed here. Similarly, `github_api_init/AGENT.md` and `CLAUDE.md` were byte-identical — kept `AGENT.md` per consolidation policy.
