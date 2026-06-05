# CocoIndex — Data Transformation Pipeline SDK

## Overview

CocoIndex is an open-source framework for building data transformation pipelines with incremental processing. It provides a Python API for defining flows that transform data through multiple stages — embedding documents, building knowledge graphs, creating search indexes — with automatic change tracking and incremental updates.

## Why This Matters for Kings' College Galway

CocoIndex powers the codebase indexing used by the project's agents. The `.cocoindex_code/` directory contains a semantic search index of the entire monorepo, enabling agents to find relevant code by meaning rather than text matching. This is essential for navigating a polyglot monorepo with 5 programming languages and 89 Docker Compose stacks — an agent can search "Dagster asset partition definition" and get relevant Python files without knowing exact function names or file paths.

## Key Features

- **Incremental processing** — Only process changed data, not full rebuilds
- **Flow-based architecture** — Define multi-stage data transformation pipelines
- **Embedding integration** — Built-in support for embedding models and vector databases
- **CLI + API** — Operate flows via `cocoindex` CLI or Python API
- **CCC integration** — Powers `ccc search` for semantic code search

## Installation

```bash
uv add cocoindex
```

## Integration with Our Stack

CocoIndex flows process curriculum documents into embeddings (BGE-M3) and store them in LanceDB. The `ccc mcp` command exposes a semantic search MCP server that agents use via the `cocoindex-code_search` tool. The `.cocoindex_code/` directory is the agent's primary code navigation tool.

## Upstream

- **Repository**: <https://github.com/cocoindex/cocoindex>
- **Documentation**: <https://cocoindex.ai>
- **Latest**: Active development — incremental indexing, MCP server, multi-language support

## Screenshot

CocoIndex is a programmatic library and CLI tool. The `ccc search "query"` CLI command returns ranked code snippets with file paths and line numbers. The MCP server provides the same functionality to AI agents. The `.cocoindex_code/target_sqlite.db` file is the semantic index database.
