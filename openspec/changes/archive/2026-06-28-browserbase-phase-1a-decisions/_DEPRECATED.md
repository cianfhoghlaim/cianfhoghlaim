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

## Replacement

See: [`2026-08-21-complete-browserbase-archive-and-crawl4ai-mcp-v1`](../2026-08-21-complete-browserbase-archive-and-crawl4ai-mcp-v1/proposal.md)

The browserbase **stack** is retained at `bonneagar/stacks/browser/`
as an **opt-in fallback** per the user directive — but the **MCP
entry** is removed from `opencode.json` + `.mcp.json`.

## DO NOT

- DO NOT re-enable the `browserbase` MCP entry in `opencode.json`
- DO NOT migrate any of the stubbed Phase 1A prompts into
  production code (the data-plane foundations have been
  established via other changes)
- DO NOT link to this change from new docs (use the replacement)

## Cross-references

- Replacement: [`2026-08-21-complete-browserbase-archive-and-crawl4ai-mcp-v1`](../2026-08-21-complete-browserbase-archive-and-crawl4ai-mcp-v1/proposal.md)
- Original proposal: `proposal.md` in this directory
- Phase 1A research output (5 prompts × 180 credits = 900 credits on
  data-plane foundations): `openspec/research/2026-06-28-browserbase-credit-program/phase-1a/`
- v7-flatten context: [`2026-07-17-v7-flatten-cianfhoghlaim-merge-bonneagar-rewrite-readme-license-v1`](../2026-07-17-v7-flatten-cianfhoghlaim-merge-bonneagar-rewrite-readme-license-v1/)