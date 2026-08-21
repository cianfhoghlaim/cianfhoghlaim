# DEPRECATED — 2026-08-21

> **This change is deprecated and will NOT be implemented.**
> It is retained for historic reference only.

## Why deprecated

Browserbase is no longer part of the Cianfhoghlaim agent MCP surface.
The canonical research surface is now **crawl4ai MCP** (open-source,
self-hosted, JWT-authed, v0.9.x native MCP server on port 11235).

Per user directive (2026-08-21):

> "we no longer will be using browserbase, we would rather revive
> our previous plan to fully set up and use crawl4ai"

## What was Phase 1B

Phase 1B covered the **storage + memory + knowledge** layer — 5
prompts × 180 credits = 900 total credits:

- P1B-06 LanceDB + Lance Blob + Lance Namespace
- P1B-07 FalkorDB + Graphiti + Dragonfly + RisingWave
- P1B-08 Garage S3 + Iceberg REST + Lakekeeper
- P1B-09 Cognee + Letta
- P1B-10 Cloudflare R2 + Workers + D1

## Replacement

See: [`2026-08-21-complete-browserbase-archive-and-crawl4ai-mcp-v1`](../2026-08-21-complete-browserbase-archive-and-crawl4ai-mcp-v1/proposal.md)

For Cognee + Graphiti specifically, see:
[`2026-08-21-bring-up-knowledge-and-design-mcps-v1`](../2026-08-21-bring-up-knowledge-and-design-mcps-v1/proposal.md)

The Phase 1B research output IS retained (the storage + memory
foundations informed the 8-stack cluster spec) but no production
code changes come from this stubbed change.

## DO NOT

- DO NOT link to this change from new docs (use the replacement)
- DO NOT re-enable the `browserbase` MCP entry in `opencode.json`

## Cross-references

- Replacement: [`2026-08-21-complete-browserbase-archive-and-crawl4ai-mcp-v1`](../2026-08-21-complete-browserbase-archive-and-crawl4ai-mcp-v1/proposal.md)
- Companion knowledge work: [`2026-08-21-bring-up-knowledge-and-design-mcps-v1`](../2026-08-21-bring-up-knowledge-and-design-mcps-v1/proposal.md)
- Original proposal: `proposal.md` in this directory
- Phase 1B research output: `openspec/research/2026-06-28-browserbase-credit-program/phase-1b/`