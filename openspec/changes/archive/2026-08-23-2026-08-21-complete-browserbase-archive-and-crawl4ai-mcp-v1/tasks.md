# Tasks: 2026-08-21-complete-browserbase-archive-and-crawl4ai-mcp-v1

## Phase A: Archive browserbase (1st priority)

- [ ] A.1 — Remove `browserbase` entry from `opencode.json` (lines 178-186; the `enabled: false` block)
- [ ] A.2 — Remove `browserbase` entry from `.mcp.json` (if present)
- [ ] A.3 — Write `_DEPRECATED.md` header to `openspec/changes/archive/2026-06-28-browserbase-phase-1a-decisions/` referencing this change
- [ ] A.4 — Write `_DEPRECATED.md` header to `openspec/changes/archive/2026-06-28-browserbase-phase-1b-decisions/`
- [ ] A.5 — Write `_DEPRECATED.md` header to `openspec/changes/archive/2026-06-28-browserbase-phase-2-decisions/`
- [ ] A.6 — Write `_DEPRECATED.md` header to `openspec/changes/archive/2026-06-28-browserbase-phase-3-decisions/`
- [ ] A.7 — Write `_DEPRECATED.md` to `openspec/research/2026-06-28-browserbase-credit-program/`

## Phase B: Wire native crawl4ai MCP (2nd priority)

- [ ] B.1 — Add `crawl4ai` entry to `opencode.json` (remote entry pointing at `https://crawl4ai-mcp.cianfhoghlaim.ie/sse` via Pangolin)
- [ ] B.2 — Add `crawl4ai` entry to `.mcp.json` (stdio variant via `bunx -y crawl4ai-mcp` OR local socket — pick the lower-friction option)
- [ ] B.3 — Verify `bun run mcp:smoke:crawl4ai` registers all 7 tools (`md`, `html`, `screenshot`, `pdf`, `execute_js`, `crawl`, `ask`)

## Phase C: Promote `bonneagar/stacks/crawl4ai/` to full GOLD_STANDARD (3rd priority)

- [ ] C.1 — Add the missing `.env.example` file (closes 1 of the 12 GOLD_STANDARD outliers per `bonneagar/AGENTS.md`)
- [ ] C.2 — Pin `unclecode/crawl4ai:v0.9.2` in `compose.yaml` (was `${TAG:-latest}`)
- [ ] C.3 — Add the 2 MCP endpoints (`/mcp/sse`, `/mcp/ws`) to the healthcheck block
- [ ] C.4 — Add the 3 Pangolin resource rows (`crawl4ai-mcp-sse`, `crawl4ai-mcp-ws`, `crawl4ai-mcp-schema`) to `pangolin.yaml`
- [ ] C.5 — Add a `config.yml` overlay with `security.jwt_enabled: true`

## Phase D: Refactor `bonneagar/stacks/browser/` for port-collision + browserbase-as-fallback (4th priority)

- [ ] D.1 — Remove the duplicate `crawl4ai` service from `bonneagar/stacks/browser/compose.yaml` (the `:11235` collision with the `crawl4ai` stack)
- [ ] D.2 — Strip the 3 `BROWSER_BROWSERBASE_*` env vars from the compose
- [ ] D.3 — Replace the Browserbase cloud integration code in `stagehand_proxy.py` with a top-of-file comment: "browserbase retained as opt-in fallback — see 2026-08-21-complete-browserbase-archive-and-crawl4ai-mcp-v1"
- [ ] D.4 — Add top-of-file comment to `compose.yaml` declaring browserbase OPTIONAL
- [ ] D.5 — Add the missing `sidecar.yaml` (Locket Infisical secret injection)
- [ ] D.6 — Add the missing `secrets.env` (Infisical `infisical://...` references)
- [ ] D.7 — Add the missing `blueprint.yaml` (Pangolin private resource blueprint)
- [ ] D.8 — Add the missing `.env.example` (closes 1 of the 12 GOLD_STANDARD outliers)
- [ ] D.9 — Verify `mise run stack-doctor:strict` passes for the `browser` stack

## Phase E: Update the `browser-tools` skill (5th priority)

- [ ] E.1 — Add `crawl4ai-mcp` as the 6th backend entry in `.agents/skills/browser-tools/SKILL.md` (alongside the existing 5)
- [ ] E.2 — Update the decision tree to route "MCP-native, JWT-authed, open-source" → `crawl4ai-mcp`
- [ ] E.3 — Update the frontmatter description to mention the new 6th backend
- [ ] E.4 — Add an "MCP vs REST" subsection explaining when to use `crawl4ai-mcp` (MCP clients) vs `crawl4ai` (Python SDK)

## Phase F: JWT secret in Infisical (6th priority)

- [ ] F.1 — Add `CRAWL4AI_JWT_SECRET` entry to `.infisical.env` as `infisical://dev-baile/cianfhoghlaim/crawl4ai-jwt-secret`
- [ ] F.2 — Run `bun run secrets:init` (a.k.a. `mise run secrets:init`) to sync to the Infisical vault
- [ ] F.3 — Verify the secret is resolvable at session start (`mise run secrets:exec -- env | grep CRAWL4AI_JWT_SECRET`)

## Phase G: New `mcp:smoke:crawl4ai` mise task (7th priority)

- [ ] G.1 — Add the 7-check harness to `mise.toml` (per the v0.9.x analysis):
  1. `GET /health` → 200 with `version` field
  2. `GET /mcp/sse` reachability (200 or 401 with auth)
  3. `GET /mcp/schema` → ≥7 tools
  4. `GET /monitor/health` → `janitor.memory_pressure` = LOW/MEDIUM
  5. `GET /monitor/browsers` → `summary.reuse_rate_percent` ≥ 80
  6. `GET /monitor/endpoints/stats["/crawl"].success_rate_percent` ≥ 95
  7. `GET /metrics` → non-empty Prometheus exposition format
- [ ] G.2 — Wire `mise run lint:mcp-runtime` to invoke `bun run mcp:smoke:crawl4ai` for the crawl4ai MCP entry

## Validation gate

- [ ] V.1 `openspec validate 2026-08-21-complete-browserbase-archive-and-crawl4ai-mcp-v1 --strict` exits 0
- [ ] V.2 `bun run mcp:smoke:crawl4ai` passes all 7 checks
- [ ] V.3 `bun run mcp:smoke:firecrawl` (regression) still passes
- [ ] V.4 `mise run stack-doctor:strict` passes for both `crawl4ai` and `browser` stacks
- [ ] V.5 `mise run lint:skills` passes (skill count: `browser-tools` + `firecrawl` + `firecrawl-cli` + `crawl4ai`)
- [ ] V.6 `git grep -nE "browserbase" openspec/changes/ openspec/research/` returns 0 results in active/non-deprecated paths