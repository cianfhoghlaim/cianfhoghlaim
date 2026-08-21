# DEPRECATED — 2026-08-21

> **The 2026-06-28 BrowserBase 6,000-credit research program is
> deprecated.** It is retained for historic reference only.

## Why deprecated

Browserbase is no longer part of the Cianfhoghlaim agent MCP surface.
The canonical research surface is now **crawl4ai MCP** (open-source,
self-hosted, JWT-authed, v0.9.x native MCP server on port 11235).

Per user directive (2026-08-21):

> "we no longer will be using browserbase, we would rather revive
> our previous plan to fully set up and use crawl4ai"

The 6,000 credits spent on the research program informed several
downstream decisions (Cognee + Graphiti + LanceDB storage topology,
Garage S3 + Lakekeeper Iceberg stack, dlt + Dagster orchestration),
but the Browserbase-specific recommendations have been superseded by
the v0.9.x crawl4ai native MCP integration.

## What was in this research program

The 2026-06-28 BrowserBase 6,000-credit program produced 5 phases:

- **Phase 1A** (5 prompts × 180 credits = 900 credits): data plane
  foundations (dlt + Dagster + CocoIndex + DuckDB + MotherDuck)
- **Phase 1B** (5 prompts × 180 credits = 900 credits): storage +
  memory + knowledge (LanceDB + FalkorDB + Garage S3 + Cognee +
  Cloudflare)
- **Phase 2** (21 prompts × 180 credits = 3,780 credits): architectural
  decisions + adoption patterns
- **Phase 3** (12 prompts × 180 credits = 2,160 credits): production
  hardening + rollout

The Phase 1A + 1B outputs informed the `agent-platform-cluster`
spec and the `centralized-model-registry` skill. The Phase 2 + 3
outputs were never finalized (the stub proposals at
`openspec/changes/archive/2026-06-28-browserbase-phase-{2,3}-decisions/`
were never filled in).

## Replacement

See: [`2026-08-21-complete-browserbase-archive-and-crawl4ai-mcp-v1`](../changes/2026-08-21-complete-browserbase-archive-and-crawl4ai-mcp-v1/proposal.md)

For Cognee + Graphiti specifically, see:
[`2026-08-21-bring-up-knowledge-and-design-mcps-v1`](../changes/2026-08-21-bring-up-knowledge-and-design-mcps-v1/proposal.md)

## DO NOT

- DO NOT link to this research output from new docs (use the replacement)
- DO NOT re-enable the `browserbase` MCP entry in `opencode.json`
- DO NOT re-spend credits on Browserbase via any future program

## Cross-references

- Replacement: [`2026-08-21-complete-browserbase-archive-and-crawl4ai-mcp-v1`](../changes/2026-08-21-complete-browserbase-archive-and-crawl4ai-mcp-v1/proposal.md)
- Companion knowledge work: [`2026-08-21-bring-up-knowledge-and-design-mcps-v1`](../changes/2026-08-21-bring-up-knowledge-and-design-mcps-v1/proposal.md)
- 4 deprecated stubbed decisions: `openspec/changes/archive/2026-06-28-browserbase-phase-{1a,1b,2,3}-decisions/_DEPRECATED.md`