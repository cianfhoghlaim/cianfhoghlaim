---
name: agent-memory-systems
description: Router for the agent memory capability. Use when an agent needs to remember, recall, search, or learn across sessions. The 5 memory backends are Cognee (knowledge graph), Graphiti (temporal knowledge graph), LanceDB (vector search), FalkorDB (vector + graph hybrid), and Memgraph (production graph). The KCG-recommended default is Cognee for structured knowledge + Graphiti for temporal + LanceDB for vector RAG. Triggers: 'agent memory', 'cognee', 'graphiti', 'falkordb', 'memgraph', 'lancedb memory', 'cognify', 'remember', 'recall', 'long-term memory', 'episodic memory', 'temporal knowledge graph', 'knowledge graph for agents'.
---

# Agent Memory Systems — Router

The Cianfhoghlaim platform has 5 memory backends. This skill is
the router — pick the right one for the task.

## The 5 backends

| If you need to… | Use this backend | Skill |
|:--|:--|:--|
| Build a knowledge graph from documents (chunks → entities → relationships) | **Cognee** | `cognee` |
| Track how knowledge changes over time (bi-temporal, episodic) | **Graphiti** | `graphiti` or `graphiti-core` |
| Store + search embeddings (vector RAG, hybrid search) | **LanceDB** | `lancedb` |
| Vector + graph hybrid (Redis-compatible graph queries) | **FalkorDB** | `falkordb` |
| Production-grade graph (Cypher, MAGE algorithms, Lab UI) | **Memgraph** | `memgraph` |

## Decision tree

```
Need to remember past conversations + decisions?   → Graphiti (temporal)
Need to build a knowledge graph from documents?     → Cognee
Need hybrid vector + graph in one store?            → FalkorDB
Need pure vector RAG with HNSW?                     → LanceDB
Need Cypher + production graph analytics?           → Memgraph
```

## The KCG memory stack (the recommended pattern)

For KCG agents, the canonical pattern is:

```
  [agent runtime]
       │
       ├──► Cognee  (structured knowledge: entities + relationships)
       │
       ├──► Graphiti  (temporal: when did this fact become true?)
       │
       └──► LanceDB  (vector RAG: similar past context)
```

**Why all 3** (not just 1):

- **Cognee** turns documents into a knowledge graph. It handles
  the "this is about X, related to Y" relationships that vector
  search can't.
- **Graphiti** adds the temporal dimension. "The Leaving Cert
  syllabus changed in 2024" is true after 2024 and false before.
  A vector index would return it for any query, regardless of
  when the question is asked.
- **LanceDB** handles the raw vector search. "Find me a chunk
  that's similar to this question" — no need for a graph.

**Why not FalkorDB / Memgraph**:

- **FalkorDB** is great for Redis-compatible graph + vector in
  one store. KCG does not use it in production (the 3 above are
  the canonical choice). It shines when you want one store, not
  three.
- **Memgraph** is the production graph for teams that need
  Cypher + MAGE algorithms + a Lab UI. KCG does not use it for
  agent memory (Cognee + Graphiti + LanceDB cover the use cases).

## KCG conventions (the rules)

1. **All agent memory calls go through the LiteLLM gateway**
   (`http://litellm:4000/v1`). Never call the underlying LLM
   provider directly. This is for cost tracking + Langfuse
   observability.
2. **All Cognee + Graphiti calls are wrapped in the
   `agents/` shim**. The actual model-layer lives
   in `agents/meaisinfhoghlaim/memory/`.
3. **All FalkorDB + Memgraph calls go through
   `storage/graph/`** (the application-layer client).
4. **LanceDB schemas** follow the `cocoindex/`
   v1 App pattern. Do NOT create ad-hoc LanceDB tables.

## Pair this skill with

- `cianfhoghlaim-storage/SKILL.md` — the KCG storage mental model
  (which backends store what)
- `cognee/SKILL.md` — the Cognee detail
- `graphiti/SKILL.md` — the Graphiti detail
- `lancedb/SKILL.md` — the LanceDB detail
- `agent-observability/SKILL.md` — how to trace memory calls

## Cross-references

- [Cognee docs](https://docs.cognee.ai)
- [Graphiti docs](https://help.getzep.com)
- [LanceDB docs](https://lancedb.github.io/lancedb)
- [FalkorDB docs](https://docs.falkordb.com)
- [Memgraph docs](https://memgraph.com/docs)
- [cianfhoghlaim-cognify-knowledge-graph spec](.agents/skills/cianfhoghlaim-storage/SKILL.md)
