---
title: 'Neo4j Python Driver — Graph Database SDK'
domain: 'infrastructure'
status: 'stable'
description: 'The Neo4j Python Driver is the official client library for connecting to Neo4j graph databases from Python. It provides a Bolt protocol implementation for executing Cypher queries, managing transactions, and handling results. Neo4j is the world''''s leading graph database, used by C'
read_when:
  - looking for documentation on this topic
updated: '2026-06-10'
supersedes:
  - docs/neo4j.md
ccc_query_hints:
  - neo4j python driver — graph database sdk
---

# Neo4j Python Driver — Graph Database SDK

## Overview

The Neo4j Python Driver is the official client library for connecting to Neo4j graph databases from Python. It provides a Bolt protocol implementation for executing Cypher queries, managing transactions, and handling results. Neo4j is the world's leading graph database, used by Cognee and Graphiti for knowledge graph storage.

## Why This Matters for Kings' College Galway

The curriculum knowledge graph — connecting learning outcomes, prerequisite concepts, assessment criteria, and study assets — is stored in Neo4j via Cognee and Graphiti. The Python driver enables Dagster assets to query the graph ("find all prerequisites for differentiation"), traverse prerequisite chains for study path generation, and populate the graph with new curriculum extractions. Neo4j's Cypher query language is the standard for querying educational dependency graphs.

## Key Features

- **Bolt protocol** — High-performance binary protocol for graph queries
- **Transaction management** — Read/write transactions with retry logic
- **Cypher execution** — Parameterised queries with result streaming
- **Bookmark-based consistency** — Causal consistency across cluster nodes
- **Async support** — `neo4j.AsyncDriver` for asyncio applications

## Installation

```bash
uv add neo4j
```

## Integration with Our Stack

Cognee and Graphiti use Neo4j as their primary graph backend. The Docker Compose stacks for both include a Neo4j container (version 5.26). The Python driver enables direct Cypher queries from Dagster assets and FastAPI endpoints.

## Upstream

- **Repository**: <https://github.com/neo4j/neo4j-python-driver>
- **Documentation**: <https://neo4j.com/docs/python-manual/current/>
- **Latest**: v5.x (2025) — async support, Bolt 5.8, improved connection pooling

## Screenshot

The Neo4j Browser at port 7474 provides a graph visualisation interface showing nodes (concepts, learning outcomes) and edges (prerequisites, related-to). The Python driver is headless — query results appear as structured records in code.
