---
title: 'graphiti (agent skill)'
domain: 'core'
status: 'stable'
description: 'Agent skill description for the Graphiti temporal knowledge graph integration. Note: the platform uses Cognee as the primary knowledge graph; Graphiti is a skill that may be invoked for bi-temporal tracking use cases.'
read_when: []
updated: '2026-06-13'
truth: sole
ccc_query_hints:
  - graphiti temporal knowledge graph
---

# Graphiti

**Version:** 1.0 | **Last Updated:** 2026-06-13

## Overview

Graphiti provides temporal reasoning capabilities, enabling tracking
of curriculum changes and prerequisite relationships across time. The
primary knowledge-graph layer for the Cianfhoghlaim platform is
**Cognee** (see `oideachais/cognee_integration/` and
`docs/01-cognee/`); Graphiti is a complementary bi-temporal graph
store that may be invoked when bi-temporal data (valid time + transaction
time) is required.

| Feature | Description |
|---|---|
| Bi-Temporal Model | Valid time + transaction time |
| Knowledge Graphs | Entity and relationship tracking |
| Temporal Queries | Point-in-time and period queries |
| Memory System | Episodic and semantic memory |

## When to use this skill

Activate when users need:

- "Track curriculum changes over time with bi-temporal accuracy"
- "Query historical prerequisite relationships at a specific date"
- "Build a temporal knowledge graph alongside Cognee"
- "Implement AI memory with time awareness"
- "Compare curriculum versions across years"

## Project integration (post-restructure)

| Component | Path |
|---|---|
| Stack config | `infrastructure/stacks/machine_learning/graphiti/` |
| Integration code (Cognee primary) | `oideachais/cognee_integration/` |
| Integration code (Graphiti skill, optional) | `meaisínfhoghlaim/agents/` (when adopted) |

### Reference docs

- [`docs/01-cognee/COGNEE_INTEGRATION.md`](../../01-cognee/COGNEE_INTEGRATION.md) — primary KG layer
- [`docs/04-ai-ml/knowledge-graphs.md`](../../04-ai-ml/knowledge-graphs.md) — KG landscape

For the project identity, see
[`docs/00-core/CLAUDE.md`](../../00-core/CLAUDE.md).
