---
title: 'oideachas-pipeline (agent skill)'
domain: 'core'
status: 'stable'
description: 'Agent skill description for the oideachas pipeline. Activation hints and project integration.'
read_when: []
updated: '2026-06-13'
truth: sole
ccc_query_hints:
  - oideachas pipeline agent skill
---

# oideachas Pipeline

**Version:** 1.0 | **Last Updated:** 2026-06-13

## Overview

The oideachas (Irish: "education") pipeline processes Celtic education
curriculum content from multiple sources (NCCA, SEC, UK DfE, SQA, CCEA,
WJEC, Estyn, SIMD) and transforms it into searchable, AI-enhanced
learning materials. It lives in the `oideachais/` quadrant.

| Feature | Description |
|---|---|
| DLT ingestion | Multi-source curriculum extraction across 8 nations × 4 domains |
| CocoIndex flows | Embedding generation for semantic search |
| Dagster assets | Orchestrated data transformation; 30+ `@dlt_assets` |
| BAML extraction | Type-safe LLM extraction for curriculum documents |
| Cognee cognify | Knowledge graph memory for the unified dataset |
| LanceDB | Vector search over the embedded curriculum |

## When to use this skill

Activate when users need:

- "Process curriculum documents from NCCA, SEC, DfE, CCEA, SQA, WJEC, Estyn, or SIMD"
- "Generate embeddings for curriculum search"
- "Build the unified knowledge graph (Cognee + DuckLake)"
- "Create a BAML extraction schema for a new source"
- "Add a new country / domain to the unified lakehouse"

## Project integration (post-restructure)

| Component | Path |
|---|---|
| Main package | `oideachais/` |
| DLT sources | `oideachais/dlt_sources/domains/{domain}/{nation}/` (canonical) + `oideachais/dlt_sources/{ireland,uk,crown_dependencies}/` (legacy shim) |
| CocoIndex flows | `oideachais/cocoindex_flows/{domain}_embedding.py` |
| Dagster definitions | `oideachais/dagster_defs/definitions.py` |
| Dagster assets | `oideachais/dagster_defs/assets/{nation}/{domain}/` |
| BAML client | `oideachais/baml_src/` (re-exported via `baml_client/`) |
| Source registry | `oideachais/sources.yaml` |
| SourceFactory | `oideachais/dlt_utils/source_factory.py` |
| Storage layer | DuckLake (writes) + MotherDuck (reads); see `docs/02-data-platform/storage-mental-model.md` |
| Cognee integration | `oideachais/cognee_integration/` |
| API reader | `oideachais/api/ducklake_reader.py` |

For the quadrant map and project identity, see
[`docs/00-core/CLAUDE.md`](../../00-core/CLAUDE.md).
For the canonical data-platform docs, see
[`docs/02-data-platform/`](../../02-data-platform/).
