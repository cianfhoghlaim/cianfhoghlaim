# Change: 2026-06-28-browserbase-phase-1b-decisions

> **STUB — TO BE FILLED BY PHASE 1B RESEARCH AGENT.** This change
> consolidates the 5 Phase 1B decisions that emerge from the 2026-06-28
> BrowserBase 6,000-credit research program.
>
> See `openspec/research/2026-06-28-browserbase-credit-program/phase-1b/`
> for the actual research output.

## Why

Phase 1B covers the **vector + graph + storage tier** — 5 prompts × 180
credits = 900 total credits spent on the secondary data plane:

- **P1B-06 LanceDB + Lance Blob + Lance Namespace** — vector + blob
  hybrid; REST Catalog bridge; CocoIndex `mount_table_target` consumer
- **P1B-07 FalkorDB + Graphiti + Dragonfly + RisingWave** — vector-graph
  hybrid (FalkorDB), bi-temporal knowledge graph (Graphiti), Redis-compat
  cache (Dragonfly), streaming SQL (RisingWave)
- **P1B-08 Garage S3 + Iceberg REST Catalog + Lakekeeper** — S3-compat
  storage; Iceberg ACID transactions on object storage; time-travel
- **P1B-09 Cognee + Letta** — knowledge graph memory; agent persistent
  memory layer; cross-session recall
- **P1B-10 Cloudflare R2 + Workers + D1** — edge storage + compute;
  wrangler.toml binding for oideachais-web

## Cross-links

- Cross-references 2 canonical specs: `oideachais-storage` and
  `meaisinfhoghlaim-platform`
- Companion to: `complete-cognee-knowledge-graph` (Cognee cognify spec)
- Output tree: `openspec/research/2026-06-28-browserbase-credit-program/phase-1b/`

## Requirements

_Filled by Phase 1B research agent after each prompt completes._
