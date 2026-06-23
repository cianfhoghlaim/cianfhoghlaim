---
title: 'Cognee Python SDK — GraphRAG Memory System'
domain: 'cognee'
status: 'stable'
description: 'The Cognee Python SDK provides programmatic access to Cognee''''s AI memory and knowledge graph framework. It enables document ingestion, entity extraction, relationship inference, and GraphRAG queries — building dynamic knowledge graphs from unstructured text using LLM-powered proc'
read_when:
  - looking for documentation on this topic
updated: '2026-06-10'
supersedes:
  - docs/cognee-sdk.md
ccc_query_hints:
  - cognee python sdk — graphrag memory syst
---

# Cognee Python SDK — GraphRAG Memory System

## Overview

The Cognee Python SDK provides programmatic access to Cognee's AI memory and knowledge graph framework. It enables document ingestion, entity extraction, relationship inference, and GraphRAG queries — building dynamic knowledge graphs from unstructured text using LLM-powered processing.

## Why This Matters for Kings' College Galway

The curriculum knowledge graph — connecting learning outcomes, prerequisite concepts, assessment criteria, and study assets — is built and queried through Cognee's SDK. When a Dagster asset ingests a new syllabus document, Cognee extracts entities (topics, concepts, skills), infers relationships (prerequisite-of, assesses, includes), and stores them in Neo4j/Memgraph/FalkorDB. The GraphRAG capability enables the web app to answer queries like "what are the foundational concepts a student must understand before tackling differential calculus?" by traversing the inferred knowledge graph.

## Key Features

- **Document ingestion** — Automatic entity extraction from unstructured text
- **Relationship inference** — LLM-powered edge creation between concepts
- **GraphRAG** — Retrieval-augmented generation over knowledge graphs
- **Multi-backend** — Neo4j, Memgraph, FalkorDB
- **Temporal awareness** — Track concept evolution across curriculum versions

## Installation

```bash
uv add cognee
```

## Integration with Our Stack

Cognee SDK is used in Dagster assets for knowledge graph construction. The Docker stack at `infrastructure/stacks/cognee/` runs the Cognee server with Neo4j backend. Complements Graphiti for bi-temporal tracking and Memgraph for low-latency graph traversal.

## Upstream

- **Repository**: <https://github.com/topoteretes/cognee>
- **Documentation**: <https://cognee.ai>
- **Latest**: Active development — GraphRAG improvements, multi-model LLM, MCP server integration

## Screenshot

The Cognee SDK is headless. Knowledge graph data is visible in Neo4j Browser (port 7474) showing entity-relationship networks. The optional frontend (`--profile ui`) at port 3000 provides graph visualisation and natural language querying. The `.agents/skills/cognee/` directory documents Cognee patterns.
