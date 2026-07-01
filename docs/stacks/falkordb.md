# falkordb

## Purpose for the Cianfhoghlaim project

FalkorDB is the **vector + graph hybrid database** for the platform.
It's Redis-compatible, combines Cypher/OpenCypher graph queries with
HNSW-powered vector search in a single engine, and gives us
hybrid queries like "find learning outcomes similar to this one AND
trace their prerequisite chain" in one database call. It's the
backend for graphiti (the temporal KG) and the MMO skill-tree
cross-realm mastery graph.

## Why it stays in komodo/pangolin/infisical GitOps

FalkorDB is a **Stage 1 prerequisite** for both graphiti (the
temporal KG stack) and the MMO agent fleet (SkillTreeBadge
queries). The komodo `deploy-falkordb-bunchloch` procedure
deploys the standalone instance; the OCI variant is at
`deploy-falkordb-oci`. The Infisical vault holds
`falkordb/password`. The dev password was REMOVED in 2026-07-30
(falls back to a required Locket-resolved secret).

## Service Inventory

| Container | Port | Role |
|:--|--:|:--|
| `falkordb` | 6379 | Redis-compatible protocol (consumed by graphiti, MMO agents) |
| `falkordb` | 3000 | HTTP UI (browser / API explorer) |

## Cross-references

- **Ops**: `bonneagar/stacks/falkordb/` (the 6-file GOLD_STANDARD)
- **Code**: `meaisinfhoghlaim/memory/` (FalkorDB-backed memory patterns)
- **Komodo procedure**: `deploy-falkordb-bunchloch.toml` (2-stage: deploy + health checks)
- **Pangolin**: `https://falkordb.cianfhoghlaim.ie/api/v1/health` (Member role)

## Tags

- `host:bunchloch` (primary) / `host:arm1-oci` (production)
- `tier:data-engineering` + `tier:agent-platform`
- `project:cianfhoghlaim`
- `group:foundation` (Stage 1 prerequisite for graphiti) + `group:memory` (consumed by agents)
