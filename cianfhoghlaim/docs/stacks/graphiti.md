# graphiti

## Purpose for the Cianfhoghlaim project

Graphiti is an open-source temporal knowledge graph system that builds and queries bi-temporal graphs — tracking not just what is true now, but what was true at any point in time. It supports Neo4j and FalkorDB as graph backends, embeddings for semantic search, and incremental updates as new information arrives.

## Why it stays in komodo/pangolin/infisical GitOps

Runs on bunchloch as part of the lakehouse data plane (Dagster + DuckLake + Lance). State persists to Garage S3; embeddings to LanceDB; code lives in cianfhoghlaim/ as Python modules. Reproducible via the IaC bootstrap.

## Cross-references

- **Ops**: `bonneagar/stacks/graphiti/` (the 6-file GOLD_STANDARD)
- **Code**: `cianfhoghlaim/<code-path>` (if any — see the linked Dagster assets / BAML schemas / DLT sources)
- **IaC**: registered in `bonneagar/iac/komodo/deploy-stacks.ts` with tags `host:bunchloch` + `tier:data-engineering`
- - **Pangolin**: `https://graphiti.cianfhoghlaim.ie` (if exposed)

## Tags

- `host:bunchloch`
- `tier:data-engineering`
- `project:cianfhoghlaim` (if cianfhoghlaim-relevant)
