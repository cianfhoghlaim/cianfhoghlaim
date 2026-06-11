---
title: 'Graphiti Python SDK — Temporal Knowledge Graph'
domain: 'cognee'
status: 'stable'
description: 'The Graphiti Python SDK provides programmatic access to the Graphiti temporal knowledge graph system. It enables building and querying bi-temporal graphs — tracking facts with both \\\\"valid time\\\\" (when something was true) and \\\\"transaction time\\\\" (when it was recorded). S'
read_when:
  - looking for documentation on this topic
updated: '2026-06-10'
supersedes:
  - docs/graphiti-sdk.md
ccc_query_hints:
  - graphiti python sdk — temporal knowledge
---

# Graphiti Python SDK — Temporal Knowledge Graph

## Overview

The Graphiti Python SDK provides programmatic access to the Graphiti temporal knowledge graph system. It enables building and querying bi-temporal graphs — tracking facts with both "valid time" (when something was true) and "transaction time" (when it was recorded). Supports Neo4j and FalkorDB backends with embedding-based semantic search.

## Why This Matters for Kings' College Galway

Curriculum data is inherently temporal: syllabus documents have effective dates, exam specifications change year-over-year, and prerequisite chains evolve as educational standards are reformed. Graphiti's bi-temporal model captures all of this — you can query "what were the prerequisite concepts for calculus in the 2023 Leaving Cert syllabus?" and get accurate results even after the 2027 reform replaces that syllabus. The Python SDK enables Dagster assets to programmatically build and query these temporal graphs from structured curriculum extraction output.

## Key Features

- **Bi-temporal model** — Separate valid time and transaction time per fact
- **Episodic memory** — Track knowledge across syllabus versions
- **Semantic search** — Embedding-based retrieval of related concepts
- **Incremental updates** — Add new curriculum data without rebuilding
- **Multi-backend** — Neo4j (primary) and FalkorDB

## Installation

```bash
uv add graphiti-core
```

## Integration with Our Stack

Graphiti SDK is used within Dagster assets to build prerequisite chains from BAML extraction output. The Docker stack at `infrastructure/stacks/machine_learning/graphiti/` runs the Graphiti server. Cognee provides complementary GraphRAG capabilities on the same Neo4j graph.

## Upstream

- **Repository**: <https://github.com/getzep/graphiti>
- **Documentation**: <https://help.getzep.com/graphiti>
- **Latest**: Active development — bi-temporal search improvements, FalkorDB backend, incremental ingestion

## Screenshot

The Graphiti SDK is headless. Query results are Python objects with temporal metadata. The Neo4j Browser at port 7474 visualises the graph with nodes (concepts, outcomes) and edges (prerequisites) coloured by validity period. The `.agents/skills/graphiti-core/` and `.agents/skills/graphiti/` directories document Graphiti patterns.
