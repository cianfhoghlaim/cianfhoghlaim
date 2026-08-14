# Change: Firecrawl MCP × CocoIndex Code (ccc) Dual-Search Architecture

## Why

The Cianfhoghlaim agent stack has **two local knowledge surfaces** —
`ccc` (semantic code search via CocoIndex Code at `.cocoindex_code/`)
and Cognee (local docs cognition graph) — but **no live web surface**.
The only live-web path today is ad-hoc `webfetch` calls in
`openspec/research/.../live-docs/*.md` generators and the existing
Firecrawl Python SDK (`dlt_sources/common/firecrawl_source.py`)
reserved for DLT ingestion.

This forces a pattern where agents researching upstream package state
have to switch tools, lose context, and cannot benefit from Firecrawl's
structured output (JSON formats with prompts + schemas, change-tracking
markdown diffs, the 43M-paper Research Index, the Developer Index of
GitHub issues + READMEs).

The platform-level Firecrawl MCP is already configured (per the
`firecrawl` MCP server in the runtime). **This change wires the MCP
into the agent stack** so every agent session can run
`firecrawl_search` alongside `bun run ccc:search "..."` — the canonical
3-way dual-search architecture:

```
        ccc (code)              cognee (docs)       firecrawl_mcp (live web)
            │                       │                       │
            │   semantic/local      │   semantic/local      │   semantic/external
            │   FREE                │   FREE                │   metered (credits)
            │                       │                       │
            ▼                       ▼                       ▼
        ──────────────┬─────────────┴───────────────┬───────────────────
                      ▼                             ▼
              Local-fast lane                  External-deep lane
                      │                             │
                      └──────────────┬──────────────┘
                                     ▼
                            Agent (3-way merged)
```

## What Changes

- **New `FirecrawlMCPClient` wrapper** at
  `agents/meaisinfhoghlaim/firecrawl_mcp/client.py` — exposes all 12
  MCP tools (`search`, `scrape`, `crawl`, `map`, `agent`, `interact`,
  `batch_scrape`, `monitor_*`, `research_*`, `developer_search`,
  `parse`, `ask`) wrapped in Pydantic + Langfuse `@observe`.
- **5 new concept guides in `.cocoindex_code/guides.yml`** (entries
  27-31): `firecrawl-search`, `firecrawl-mcp-tools`,
  `firecrawl-research-index`, `firecrawl-developer-index`,
  `firecrawl-corpus`.
- **New `scripts/sync/firecrawl-ccc.sh`** mirroring the existing
  `scripts/sync/{baml,notebooks,stacks,agents}-ccc.sh` pattern +
  wired as `mise run sync:firecrawl`.
- **Routing table + dual-search diagram** appended to `AGENTS.md`
  (extends the existing CCC + Cognee diagram at `AGENTS.md:115`) +
  the openspec research workflow table at `openspec/AGENTS.md`.
- **6 SKILL.md updates** (one paragraph each in `browser-tools`,
  `centralized-registry`, `agent-fleet-orchestration`,
  `secrets-management`, `knowledge-sync-loop`,
  `indexing-and-cognition`) noting the Firecrawl MCP complement.
- **Bring-up smoke test** appended to `scripts/bring-up-smoke-test.sh`
  (grep for `firecrawl-search` in `.cocoindex_code/guides.yml`).
- **1 new capability spec** `dual-search-architecture` + per-spec
  `AGENTS.md` sibling.

## Why now (post-2026-08-15 model + schema + control-panel trilogy)

The 2026-08-15 trilogy (`centralized-model-registry` +
`centralized-schema-registry` + `deployment-control-panel`) established
the pattern of "one canonical surface for X, audited by a mise
linter". This change extends that pattern to **agent knowledge
acquisition**: instead of a federated mess of webfetch + grep +
adhoc Firecrawl SDK calls, agents now have a single MCP surface
mirroring the CCC + Cognee duality.

## Dependencies

`Blocked by: none`. `Blocked by (soft): 2026-08-15-knowledge-sync-loop-v1`
(the 5-layer sync architecture — this change adds a new sync layer).
`Affected repos: cianfhoghlaim (single repo) + 1 platform-level MCP
server (no worktree changes)`.

## Impact

- **Capabilities**: NEW `dual-search-architecture` (1 spec, 4
  Requirements, 8 Scenarios).
- **Code**: ~12 new files (`agents/meaisinfhoghlaim/firecrawl_mcp/*.py`
  × 3 + sync script + smoke test + 2 spec files); ~8 modified files
  (guides.yml +5 entries, AGENTS.md × 2, mise.toml × 1, 6 SKILL.md × 1
  paragraph each).
- **Risk**: low — no production behaviour change in DLT pipelines
  (Firecrawl SDK is unchanged); only adds a new MCP wrapper + 5 CCC
  guides. Authless MCP tier (`firecrawl_search`, `firecrawl_scrape`,
  `firecrawl_parse`) is available out-of-the-box; authenticated tier
  required for the other 9 tools.
- **Credit cost**: zero (no calls made yet; Phase 4a adds the corpus
  crawl + examinations.ie Interact which DO cost).

## Success criteria

1. `mise run sync:firecrawl` runs cleanly and writes
   `stedding/sync-reports/firecrawl-ccc-{date}.md`.
2. `bun run ccc:search "firecrawl dual search"` returns ≥1 hit
   pointing at the new AGENTS.md section + the 5 new guides.
3. `mise run lint:guides-yml` passes (31 entries, all paths resolve).
4. `mise run lint:ccc-freshness` passes (index <7d on `main`).
5. `openspec validate 2026-08-14-firecrawl-mcp-ccc-dual-search-v1
   --strict` exits 0.
6. `mise run lint:skills && mise run lint:drift-docs` exit 0.
7. The new `FirecrawlMCPClient` imports cleanly + has Langfuse
   `@observe` decorators on every public method (verified by
   `bun run ccc:search "@observe" agents/meaisinfhoghlaim/firecrawl_mcp/`).