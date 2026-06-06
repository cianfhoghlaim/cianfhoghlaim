# Lance / LanceDB — KCG Summary

## What It Is
Lance is a columnar data format for modern AI/ML workloads and LanceDB is a serverless vector database built on top of it. This directory contains the Lance namespace interface, Lance + Ray distributed indexing examples, and 15+ LanceDB example applications including advanced RAG (LOTR, multi-document agentic, time-travel), multimodal search (ColPali, recipe agent), GeoSpatial recommendation, hybrid search, Multilingual RAG, and JavaScript transformer usage.

## Why This Matters for Kings' College Galway
LanceDB is the vector database for the oideachais platform — it stores curriculum embeddings and powers the `ccc` semantic search index. The hybrid search and multimodal examples directly inform how to build RAG over examination materials (text + diagrams), the time-travel RAG pattern enables querying curriculum changes across academic years, and the Lance + Ray integration provides the blueprint for distributed indexing of large curriculum datasets on the bunchloch MacBook M4.

## Key Patterns Preserved
29 .md files remain, including:
- `README.md` — Lance namespace interface overview
- `lance-ray/README.md` — Distributed indexing with Ray
- `lance-ray/docs/src/*.md` (6 files) — Ray integration docs: data evolution, distributed indexing, read/write patterns
- `lance-ray/CONTRIBUTING.md` — Development guide
- `quickstart/README.md` — LanceDB quick start
- `hybrid-search/README.md` — Combined full-text + vector search pattern
- `Advance_RAG_LOTR/README.md` — Advanced RAG with layered retrieval
- `multi-document-agentic-rag/README.md` — Agentic RAG over multiple documents
- `time-travel-rag/README.md` — Temporal RAG using LanceDB versioning
- `multimodal-search/README.md`, `multimodal-recipe-agent/README.md` — Multimodal search patterns
- `ColPali-vision-retriever/README.md` — Vision-based document retrieval
- `Geospatial-Recommendation-System/README.md` — Geospatial ML recommendations
- `Multilingual_RAG/README.md` — Multilingual retrieval patterns
- `Chunking_Analysis/Readme.md` — Chunking strategy analysis
- `cognee-RAG/README.md` — Cognee + LanceDB integration
- Research notes: `lancedb-research-report.md`, `From BI to AI_ A Modern Lakehouse Stack with Lance and Iceberg.md`, `Ibis, LanceDB, and Data Stack Integration.md`

## Source Files
Full source removed (2026-06-06). Available at:
- Lance: https://github.com/lancedb/lance
- LanceDB: https://github.com/lancedb/lancedb

## What Was Removed
Python source (.py), Jupyter notebooks, JSON/TOML configs, Docker files, shell scripts, CSV/TPCH data files, images, .gitignore/lock files
