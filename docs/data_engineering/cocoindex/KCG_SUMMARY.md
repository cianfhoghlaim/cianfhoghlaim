# CocoIndex — KCG Summary

## What It Is
CocoIndex is a Python framework for building real-time data indexing and ETL pipelines with LLM-powered transformation. This directory contains 25+ example flows covering vector search (LanceDB, Qdrant, pgvector), knowledge graph construction (Neo4j, Kuzu), structured extraction (BAML, DSPy), cloud storage sync (S3, Azure Blob, Google Drive), and codebase indexing with Tree-sitter AST chunking. Also includes the full cocoindex-code MCP server documentation with 50+ Claude/AI-oriented docs.

## Why This Matters for Kings' College Galway
CocoIndex is the indexing backbone for the oideachais education data platform — it powers the semantic search index that agents use via `ccc:search`. The knowledge graph from docs flow directly maps to curriculum content ingestion (examination papers → knowledge graph), the structured extraction examples (patient forms) are reusable for exam paper parsing, and the live updates pattern supports incremental curriculum indexing as new Leaving Cert materials are released. The MCP server docs provide the reference architecture for `ccc` integration.

## Key Patterns Preserved
120+ .md files remain, including:
- `README.md` — Example index covering all 25+ flows
- `docs/core/basics.md`, `docs/core/cli-commands.md` — Core CocoIndex concepts
- `docs/examples/examples/*.md` (17 files) — Detailed flow docs: codebase indexing, knowledge graphs, patient forms, HackerNews, image search, product recommendations
- `docs/sources/*.md` (6 files) — Source configuration: S3, Azure, Google Drive, Postgres, local files
- `docs/targets/*.md` (5 files) — Target config: LanceDB, PostgreSQL, Qdrant, Neo4j, Kuzu
- `docs/getting_started/` — Installation, overview, quickstart
- `cocoindex-code-mcp-server/docs/` (50+ .md files) — Claude/AI agent docs: AST chunking, embedding selection, hybrid search, flow debugging, MCP server architecture, tree-sitter integration
- `cocoindex-code-mcp-server/README.md` — MCP server overview
- Flow-specific READMEs (25+): text_embedding, pdf_embedding, image_search, face_recognition, code_embedding, meeting_notes_graph, product_recommendation, etc.

## Source Files
Full source removed (2026-06-06). Available at https://github.com/cocoindex-io/cocoindex

## What Was Removed
Python source (.py), JSON/YAML configs, `.gitignore`/Docker files, shell scripts, test data, CSV/Parquet files, Jupyter notebooks, lock files, .txt/.xml files
