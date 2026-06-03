# ChunkHound Code Search

## Overview
ChunkHound is a semantic and regex search tool designed to transform codebases into searchable knowledge bases. It enables efficient navigation and understanding of large codebases through AI-native interfaces.

## Core Capabilities
- **Semantic Search**: Natural language queries to find conceptually related code.
- **Regex Search**: Exact pattern matching for precise symbol discovery.
- **Indexing**: Structure-aware chunking (cAST) and vector storage (DuckDB/LanceDB).
- **Multi-Hop Exploration**: Iterative discovery of architectural relationships.
- **MCP Integration**: Exposes search capabilities to AI assistants via Model Context Protocol.

## Usage
- **CLI**: `chunkhound` for indexing and direct search.
- **MCP**: `chunkhound mcp` for integration with AI assistants.

## Key Constraints
- Indexing MUST respect `.gitignore`.
- Embedding batching is MANDATORY for performance.
- Single-threaded database access (DuckDB/LanceDB) via `SerialDatabaseProvider`.
