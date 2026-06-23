# Hosting LanceDB: Reference Index

The LanceDB skill has been restructured as a router + reference
files. This file is the **reference index** for hosting / deployment
topics. The full `docs/lance/lancedb-reference.md` (2,672 lines) and
the per-section deep dives were in the docs subdirectory (deleted
with the `sync-skills-from-docs` change). The same content is now in
the references below.

## Hosting patterns

- **Self-hosted Docker** (local-only) — see
  `hosting-lancedb-docker-compose.md` (a generic Docker Compose
  pattern for the LanceDB REST API server)
- **Cloudflare R2 + rclone sidecar** (the KCG production target) —
  see `hosting-lancedb-r2.md`
- **LanceDB Cloud** (managed, serverless, 4 regions) — see
  `lancedb-cloud.md`

## Search performance

- **HNSW index selection** — see the `SKILL.md` "Index Selection Guide"
- **`refine_factor` for high-accuracy queries** — see the `SKILL.md`
  "Hybrid Search" section
- **Distributed indexing for > 1M rows** — see
  `lance-ray-distributed.md`

## Schema patterns

- **Time-travel / versioned RAG** — see `time-travel-rag.md`
- **Embeddings registry (10+ providers)** — see
  `embed-functions-registry.md`
- **Multimodal "fat table"** (text + image + vector in one row) —
  see `multimodal-fat-tables.md`
- **Lance Namespace / Iceberg** (expose Lance as Iceberg) — see
  `lance-namespace-and-iceberg.md`
- **Ibis + DuckDB `lance_scan()`** (federated SQL over Lance) —
  see `ibis-integration.md`

## RAG patterns

- **Context Enrichment Window** (sliding-neighbour chunking)
- **LOTR (Lost in the Middle) reordering**
- **Agentic RAG (ReAct)**
- **ColPali multi-vector for PDFs**
- **GraphRAG (with Cognee)**
- **Hybrid search with multiple embedders**

See `advanced-rag-patterns.md` for the full set.

## TypeScript

- **Modern API (`search()`, not deprecated `vectorSearch()`)** —
  see `typescript-modern-api.md`
- **LanceDB Cloud via TS** — see the SKILL.md "TypeScript Usage" section

## Canonical upstream examples

The 14 example apps in `docs/lance/examples/` (deleted with the docs
subdirectory) are the canonical LanceDB patterns. The same examples
are mirrored in the upstream
[lancedb/vectordb-recipes](https://github.com/lancedb/vectordb-recipes)
GitHub repo:

- `quickstart/` — minimal Python + TS getting-started
- `hybrid-search/` — BM25 + vector hybrid retrieval (TS)
- `time-travel-rag/` — versioned RAG, A/B testing
- `multimodal-search/` — CLIP image+text search
- `multimodal-recipe-agent/` — multimodal agent (image + text)
- `multi-document-agentic-rag/` — agentic RAG across many docs
- `cognee-RAG/` — GraphRAG via Cognee
- `Multilingual_RAG/` — Cohere + Argos Translate
- `Geospatial-Recommendation-System/` — FTS + geo combo
- `Advanced_RAG_Context_Enrichment_Window/` — context-enrichment
- `Advance_RAG_LOTR/` — Lost in the Middle reordering
- `Chatbot_with_Parler_TTS/` — chatbot with TTS (less relevant)
- `js-transformers/` — JS/TS embedding client
- `Chunking_Analysis/` — chunking-strategy comparison
