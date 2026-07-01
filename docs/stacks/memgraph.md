# memgraph

## Purpose for the Cianfhoghlaim project

Memgraph is a high-performance, in-memory graph database compatible with the Cypher query language (Neo4j's query language). It includes MAGE (Memgraph Advanced Graph Extensions) — a library of graph algorithms for pathfinding, community detection, centrality analysis, and more.

## Why it stays in komodo/pangolin/infisical GitOps

Runs on bunchloch as part of the agent runtime (Agno + Google ADK + OpenClaw). All agent tools + prompts are versioned in cianfhoghlaim/agents/. LLM credentials from LiteLLM; tracing from Langfuse.

## Cross-references

- **Ops**: `bonneagar/stacks/memgraph/` (the 6-file GOLD_STANDARD)
- **Code**: `cianfhoghlaim/<code-path>` (if any — see the linked Dagster assets / BAML schemas / DLT sources)
- **IaC**: registered in `bonneagar/iac/komodo/deploy-stacks.ts` with tags `host:bunchloch` + `tier:agent-platform`
- - **Pangolin**: `https://memgraph.cianfhoghlaim.ie` (if exposed)

## Tags

- `host:bunchloch`
- `tier:agent-platform`
- `project:cianfhoghlaim` (if cianfhoghlaim-relevant)
