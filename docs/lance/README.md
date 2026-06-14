# LanceDB Reference Library

LanceDB is an open-source, embedded, multimodal vector database for production-scale AI applications. Built on the **Lance** columnar data format with Apache Arrow + DataFusion, it supports vector search, full-text search, and hybrid search at billion-scale.

---

## Strategic Documents

| Document | Description |
|----------|-------------|
| [Lancedb Research Report](lancedb-research-report.md) | Executive overview — serverless architecture, multimodal support, billion-scale benchmarks |
| [Lancedb Reference](lancedb-reference.md) | 2,672-line API + integration reference (the canonical doc) |
| [Ibis, LanceDB, and Data Stack Integration](Ibis,%20LanceDB,%20and%20Data%20Stack%20Integration.md) | Ibis + LanceDB composition for analytical/transactional workloads |
| [Lancedb Multimodal Lakehouse](lancedb-multimodal-lakehouse.pdf) | PDF — multimodal architecture paper |

## Configuration (for local dev)

- `pyproject.toml` — Python project manifest
- `lancedb.compose.yaml` — Docker Compose for local LanceDB + dependencies
- `iceberg.py` — Iceberg integration reference

## Examples

14 runnable example apps in [`examples/`](examples/) (each with its own `README.md`):

- `Advance_RAG_LOTR/` — RAG over *Lord of the Rings* corpus
- `Advanced_RAG_Context_Enrichment_Window/` — sliding-window context for long docs
- `Chatbot_with_Parler_TTS/` — chatbot with Parler text-to-speech
- `Chunking_Analysis/` — chunking-strategy comparison tool
- `cognee-RAG/` — Cognee knowledge-graph RAG
- `Geospatial-Recommendation-System/` — geo-vector recommendation
- `hybrid-search/` — BM25 + vector hybrid retrieval
- `js-transformers/` — JS/TS embedding client (incl. cloud subdir)
- `multi-document-agentic-rag/` — agentic RAG across many docs
- `Multilingual_RAG/` — multilingual embedding + retrieval
- `multimodal-recipe-agent/` — multimodal (image + text) recipe agent
- `multimodal-search/` — CLIP-style image+text search
- `quickstart/` — minimal LanceDB getting-started
- `time-travel-rag/` — versioned RAG over Lance table history
