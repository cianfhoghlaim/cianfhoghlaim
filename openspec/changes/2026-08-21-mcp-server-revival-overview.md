# MCP Server Revival — Consolidated Overview (2026-08-21)

> **6 openspec changes that together complete the prior
> `2026-06-29-browser-stack-crawl4ai-refactor` at the IaC/MCP
> layer + add new MCP capabilities.**
>
> Scope: cianfhoghlaim + bonneagar IaC (no `leabharlann` worktree
> touched). All 6 changes are independent and can ship in parallel.

## Context

The prior `2026-06-29-browser-stack-crawl4ai-refactor` change
(archived) shipped the Python-level browserbase refactor (Phases
A–F.3 checked off) but **the IaC/MCP layer was never touched**. As
a result:

1. `opencode.json` + `.mcp.json` still have a `browserbase` MCP entry
2. `bonneagar/stacks/browser/compose.yaml` still has Browserbase cloud
   integration
3. The native crawl4ai MCP server (added in v0.9.x) was never wired
4. The `cognee`, `graphiti`, `langfuse`, `infisical` MCPs are
   `enabled: false`
5. `chrome-devtools-mcp` + `dlt-workspace-mcp` are wired but not
   loading at runtime
6. The in-house `design-system-server.py` MCP is fully implemented
   but not wired
7. A phantom MCP gateway at
   `web/apps/croilar-portal/src/routes/api/mcp.gateway.ts` claims
   to proxy through LiteLLM, which doesn't actually proxy MCPs

This overview documents the 6 changes that address all 7 gaps.

## The 6 changes

| # | Change ID | Scope | Dependencies |
|--:|:--|:--|:--|
| 1 | [`2026-08-21-complete-browserbase-archive-and-crawl4ai-mcp-v1`](2026-08-21-complete-browserbase-archive-and-crawl4ai-mcp-v1/proposal.md) | Archive browserbase; wire native crawl4ai MCP v0.9.2; promote `crawl4ai` stack to GOLD_STANDARD; add browserbase-as-fallback comment to `browser` stack | none |
| 2 | [`2026-08-21-archive-legacy-sruth-mcp-servers-v1`](2026-08-21-archive-legacy-sruth-mcp-servers-v1/proposal.md) | Add `_DEPRECATED.md` to 3 historic `sruth/*/mcp_server/` directories (no file deletions per user directive) | none |
| 3 | [`2026-08-21-bring-up-knowledge-and-design-mcps-v1`](2026-08-21-bring-up-knowledge-and-design-mcps-v1/proposal.md) | Wire `cognee` + `graphiti` + `design-system` MCPs; promote both stacks to GOLD_STANDARD | none |
| 4 | [`2026-08-21-flip-observability-mcps-v1`](2026-08-21-flip-observability-mcps-v1/proposal.md) | Wire `langfuse` + `infisical` MCPs (populate missing Infisical credentials) | none |
| 5 | [`2026-08-21-fix-wired-but-unloaded-mcps-v1`](2026-08-21-fix-wired-but-unloaded-mcps-v1/proposal.md) | Diagnose + fix `chrome-devtools-mcp` + `dlt-workspace-mcp` (wired-but-not-loaded); add `mise run lint:mcp-runtime` CI gate | none |
| 6 | [`2026-08-21-document-phantom-mcp-gateway-gap-v1`](2026-08-21-document-phantom-mcp-gateway-gap-v1/proposal.md) | Add `KNOWN-ISSUE` header + `TODO(mcp-bridge)` to the phantom MCP gateway; add `mise run lint:mcp-gateway` CI gate | none (soft-blocks on future BAML→oRPC→MCP bridge) |

## Dependency graph

```
#5 (chrome + dlt-workspace fix)
#4 (langfuse + infisical flip)
#3 (cognee + graphiti + design-system)
#1 (browserbase archive + crawl4ai MCP)
#2 (sruth/*/mcp_server archive — historic reference)
#6 (phantom gateway docs, independent)
```

All 6 changes are independent (no `Blocked by:`). They share the
common `mise run lint:mcp-runtime` + `mcp:smoke:*` task pattern
(introduced by #5).

## The MCP surface after these 6 changes ship

| MCP | Status after | Used for |
|---|---|---|
| `cocoindex-code` (ccc) | ✓ Active | Semantic code search |
| `firecrawl` | ✓ Active | Paid anti-bot + agent research |
| `motherduck` | ✓ Active | SQL analytics (in-memory or remote) |
| `huggingface` | ✓ Active | Model + dataset hub |
| `chrome-devtools-mcp` | ✓ Active (after #5) | Local Chrome debugging |
| `dlt-workspace-mcp` | ✓ Active (after #5) | DLT pipeline workspace |
| `crawl4ai` | ✓ Active (after #1) | **Open-source bulk scraping via native MCP, JWT-authed, v0.9.2** |
| `cognee` | ✓ Active (after #3) | Knowledge graph memory |
| `graphiti` | ✓ Active (after #3) | Temporal knowledge graph memory |
| `design-system-server` | ✓ Active (after #3) | AG-UI self-heal |
| `langfuse` | ✓ Active (after #4) | LLM trace observability |
| `infisical` | ✓ Active (after #4) | Runtime secret mutation |
| `browserbase` | ❌ Archived from MCP (after #1) | Retained as opt-in fallback stack at `bonneagar/stacks/browser/` |

That's **12 active MCPs** organized as:

- **code search** (1): ccc
- **web data** (3): firecrawl + crawl4ai + chrome
- **data engineering** (2): dlt-workspace + motherduck
- **knowledge/memory** (3): cognee + graphiti + design-system
- **observability** (1): langfuse
- **secrets** (1): infisical
- **model hub** (1): huggingface

## Firecrawl-sourced evidence (per the openspec/AGENTS.md citation rule)

The crawl4ai v0.9.x native MCP integration is grounded in 3 Firecrawl
calls (per the triple-search architecture):

- `firecrawl_search` (id `01a023da-4f80-751d-834b-768c9e9ec83e`):
  Crawl4AI v0.8.0 → v0.9.2 release timeline + MCP support discovery
- `firecrawl_search` (id `01a023da-577a-769c-876c-6fb41ddc8699`):
  Native MCP endpoints at `http://localhost:11235/mcp/sse` +
  `ws://localhost:11235/mcp/ws`
- `firecrawl_scrape` (scrapeId
  `01a01018-0f37-727e-98cf-7b605b79e612`): full self-hosting guide
  analysed by the `general` subagent (83,288-char full report)

Plus the mandatory companion `ccc:search` query (BAAI bge-m3
embedder search) so both tool names appear in the Langfuse trace.

## Cross-references

- Prior plan this completes: [`2026-06-29-browser-stack-crawl4ai-refactor`](../archive/2026-06-29-2026-06-29-browser-stack-crawl4ai-refactor/proposal.md)
- v7-flatten context: [`2026-07-17-v7-flatten-cianfhoghlaim-merge-bonneagar-rewrite-readme-license-v1`](../archive/2026-07-17-v7-flatten-cianfhoghlaim-merge-bonneagar-rewrite-readme-license-v1/)
- Browserbase archive target: 4 stubbed changes + 1 research
  program, all with `_DEPRECATED.md` headers added by #1
- Sruth historic reference: 3 directories with `_DEPRECATED.md`
  headers added by #2

## Validation gate (per-change)

For each of the 6 changes:

- `openspec validate <change-id> --strict` MUST pass (verified for
  all 6 on 2026-08-21)
- Each change's own `Validation gate` section (in `tasks.md`) MUST
  pass before the change archives

## Implementation order (suggested)

While all 6 changes are independent, the suggested implementation
order is:

1. **#5** first — the `lint:mcp-runtime` CI gate is the harness for
   the others
2. **#6** second — doc-only, no functional change
3. **#1, #2, #3, #4** in parallel — all add new MCPs and use the
   shared `mcp:smoke:*` task pattern