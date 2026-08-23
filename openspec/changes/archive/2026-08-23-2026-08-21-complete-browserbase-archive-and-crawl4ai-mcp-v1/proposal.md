# Change: 2026-08-21-complete-browserbase-archive-and-crawl4ai-mcp-v1

## Why

The prior `2026-06-29-browser-stack-crawl4ai-refactor` change (archived)
shipped the Python-level browserbase refactor (Phases A–F.3 checked
off), but **the IaC/MCP layer was never touched**. As a result:

1. **Browserbase artifacts are still live in IaC.** `opencode.json`
   and `.mcp.json` still carry a `browserbase` MCP entry
   (`enabled: false`); `bonneagar/stacks/browser/compose.yaml` still
   has `BROWSER_BROWSERBASE_API_KEY` + `BROWSER_BROWSERBASE_PROJECT_ID`
   env vars; `stagehand_proxy.py` still has Browserbase cloud
   integration code.
2. **Browserbase research is still live in openspec.** The 4 archived
   `2026-06-28-browserbase-phase-{1a,1b,2,3}-decisions/` changes +
   `openspec/research/2026-06-28-browserbase-credit-program/` carry
   stub proposals and never received a `_DEPRECATED.md` header.
3. **The native crawl4ai MCP server was never wired.** Crawl4AI v0.9.x
   ships with a built-in MCP server (`/mcp/sse` + `/mcp/ws` +
   `/mcp/schema`) on the same port 11235 as the REST API — confirmed
   via Firecrawl scrape of `https://docs.crawl4ai.com/core/self-hosting/`
   on 2026-08-21. We never picked this up.
4. **`bonneagar/stacks/browser/` is one of the 12 GOLD_STANDARD
   outliers.** Missing `sidecar.yaml`, `secrets.env`, `blueprint.yaml`,
   `.env.example`. (Per `bonneagar/AGENTS.md`.)
5. **`bonneagar/stacks/crawl4ai/` is one of the 12 GOLD_STANDARD
   outliers.** Missing only `.env.example`; needs promotion to full
   GOLD_STANDARD.

This change **finishes** the prior plan at the IaC/MCP layer and adds
the native crawl4ai MCP integration. Browserbase is retained as an
**opt-in fallback stack** at `bonneagar/stacks/browser/` per user
directive — but no longer appears in the agent MCP surface.

## What Changes

### 1. Drop browserbase from MCP surface

- Remove `browserbase` entries from `opencode.json` and `.mcp.json`
  (the user wants canonical research via crawl4ai, not browserbase)
- Add a `_DEPRECATED.md` header to each of:
  - `openspec/changes/archive/2026-06-28-browserbase-phase-1a-decisions/`
  - `openspec/changes/archive/2026-06-28-browserbase-phase-1b-decisions/`
  - `openspec/changes/archive/2026-06-28-browserbase-phase-2-decisions/`
  - `openspec/changes/archive/2026-06-28-browserbase-phase-3-decisions/`
  - `openspec/research/2026-06-28-browserbase-credit-program/`

### 2. Wire native crawl4ai MCP server

Per the Firecrawl-confirmed v0.9.x analysis (see "Firecrawl-sourced
evidence" below):

- The MCP server ships inside the `unclecode/crawl4ai:v0.9.2` image
  on port 11235 (no separate container, no shim)
- 7 tools exposed: `md`, `html`, `screenshot`, `pdf`, `execute_js`,
  `crawl`, `ask`
- SSE endpoint: `http://localhost:11235/mcp/sse`
- WebSocket endpoint: `ws://localhost:11235/mcp/ws`
- JWT bearer auth via `security.jwt_enabled: true` (v0.9.0
  secure-by-default)

Wire it into both `opencode.json` (remote entry via Pangolin) and
`.mcp.json`. Add the 3 Pangolin resource rows
(`crawl4ai-mcp-sse`, `crawl4ai-mcp-ws`, `crawl4ai-mcp-schema`) to
`bonneagar/stacks/crawl4ai/pangolin.yaml`.

### 3. Promote `bonneagar/stacks/crawl4ai/` to full GOLD_STANDARD

- Add the missing `.env.example` (closes 1 of the 12 outliers)
- Pin `unclecode/crawl4ai:v0.9.2` (was `latest`)
- Add the 2 MCP endpoints to the healthcheck
- Add a `config.yml` overlay with `security.jwt_enabled: true`

### 4. Refactor `bonneagar/stacks/browser/` for port-collision + browserbase-as-fallback

- **Remove the duplicate `crawl4ai` service** from
  `bonneagar/stacks/browser/compose.yaml` (port-11235 conflict with
  the canonical `crawl4ai` stack)
- **Strip the 3 `BROWSER_BROWSERBASE_*` env vars** from the compose
- **Replace** the Browserbase cloud integration code in
  `stagehand_proxy.py` with a top-of-file comment marking
  "browserbase retained as opt-in fallback"
- Add the 4 missing GOLD_STANDARD files (`sidecar.yaml`,
  `secrets.env`, `blueprint.yaml`, `.env.example`)
- Add a top-of-file comment declaring browserbase OPTIONAL

### 5. Update the `browser-tools` skill

Add `crawl4ai-mcp` as the 6th backend (alongside the existing 5:
Crawl4AI REST + Firecrawl + Playwright CDP + Skyvern opt-in +
Stagehand opt-in). Update the decision tree to route "MCP-native,
JWT-authed, open-source" → `crawl4ai-mcp`.

### 6. JWT secret in Infisical

Add `infisical://dev-baile/cianfhoghlaim/crawl4ai-jwt-secret` to
`.infisical.env` so the v0.9.0 loopback-unlock works for the MCP
clients.

### 7. New `mcp:smoke:crawl4ai` mise task

A 7-check smoke harness (per the v0.9.x analysis):
1. `GET /health` → 200 with `version` field
2. `GET /mcp/sse` reachability (200 or 401 with auth)
3. `GET /mcp/schema` → ≥7 tools
4. `GET /monitor/health` → `janitor.memory_pressure` = LOW/MEDIUM
5. `GET /monitor/browsers` → `summary.reuse_rate_percent` ≥ 80
6. `GET /monitor/endpoints/stats["/crawl"].success_rate_percent` ≥ 95
7. `GET /metrics` → non-empty Prometheus exposition format

## Dependencies

- `Blocked by: none`
- `Blocked by (soft): 2026-08-21-fix-wired-but-unloaded-mcps-v1` (the
  diagnostic harness in #5 shares the `mise run lint:mcp-runtime`
  task pattern)
- `Affected repos: cianfhoghlaim, bonneagar`

## Firecrawl-sourced evidence (per the openspec/AGENTS.md citation rule)

- `firecrawl_search` (id `01a023da-4f80-751d-834b-768c9e9ec83e`):
  Crawl4AI v0.8.0 → v0.9.2 release timeline + MCP support discovery
- `firecrawl_search` (id `01a023da-577a-769c-876c-6fb41ddc8699`):
  Native MCP endpoints at `http://localhost:11235/mcp/sse` +
  `ws://localhost:11235/mcp/ws`
- `firecrawl_scrape` (scrapeId
  `01a01018-0f37-727e-98cf-7b605b79e612`): full self-hosting guide
  analysed by the `general` subagent (full report above)
- `ccc:search` (the mandatory companion): `BAAI/bge-m3 embedder` +
  the 2026-06-28 multilingual-embeddings research files

## Cross-links

- Companion to: `2026-06-29-browser-stack-crawl4ai-refactor` (the
  Python refactor this completes; archived)
- Companion to: `2026-08-21-bring-up-knowledge-and-design-mcps-v1`
  (parallel knowledge-graph MCP enablement)
- Companion to: `2026-08-21-archive-legacy-sruth-mcp-servers-v1`
  (the sruth historic-reference archive)
- Spec delta: `infrastructure-stacks` (stacks + skills + IaC)
- Spec delta: `agent-platform-cluster` (the MCP integration surface)

## Requirements

See `tasks.md` for the 7-phase plan (A: archive, B: MCP wiring,
C: crawl4ai stack promote, D: browser stack refactor, E: skill update,
F: JWT secret, G: smoke harness).

## Validation gate

- [ ] `openspec validate 2026-08-21-complete-browserbase-archive-and-crawl4ai-mcp-v1 --strict` exits 0
- [ ] `bun run mcp:smoke:crawl4ai` passes all 7 checks
- [ ] `bun run mcp:smoke:firecrawl` (regression) still passes
- [ ] `mise run stack-doctor:strict` passes for both `crawl4ai` and `browser` stacks
- [ ] `mise run lint:skills` passes (skill count: `browser-tools` + `firecrawl` + `firecrawl-cli` + `crawl4ai`)
- [ ] `git grep -nE "browserbase" openspec/changes/active/ openspec/research/` returns 0 results