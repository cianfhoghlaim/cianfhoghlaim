# Delta: infrastructure-stacks

## ADDED Requirements

### Requirement: Native crawl4ai MCP server on port 11235

The system SHALL expose the native Crawl4AI v0.9.x Model Context Protocol
(MCP) server as a first-class MCP surface for the agent fleet. The MCP
server ships inside the `unclecode/crawl4ai:v0.9.2` Docker image on the
same port 11235 as the REST API; no separate container is required.

The MCP server exposes exactly 7 tools, confirmed via
`firecrawl_scrape` of `https://docs.crawl4ai.com/core/self-hosting/` on
2026-08-21:

| Tool | Purpose |
|:--|:--|
| `md` | Render the page as LLM-ready Markdown |
| `html` | Return the cleaned HTML |
| `screenshot` | Capture a page screenshot (returns `artifact_id`) |
| `pdf` | Render the page as a PDF (returns `artifact_id`) |
| `execute_js` | Run arbitrary JS in the page context |
| `crawl` | The full deep-crawl primitive |
| `ask` | LLM-mediated page query |

The MCP endpoints are:

- **SSE:** `http://localhost:11235/mcp/sse`
- **WebSocket:** `ws://localhost:11235/mcp/ws`
- **Schema introspection:** `http://localhost:11235/mcp/schema`

#### Scenario: The MCP server is reachable from the agent fleet

- **GIVEN** the `bonneagar/stacks/crawl4ai/` stack is running on port 11235
- **AND** `security.jwt_enabled: true` is set in the runtime `config.yml`
- **AND** the JWT secret in `CRAWL4AI_JWT_SECRET` (sourced from
  `infisical://dev-baile/cianfhoghlaim/crawl4ai-jwt-secret`) matches the
  server's `JWT_SECRET`
- **WHEN** the agent runtime connects via `https://crawl4ai-mcp.cianfhoghlaim.ie/sse`
  (the Pangolin-routed entry)
- **THEN** the SSE handshake completes with HTTP 200
- **AND** `bun run mcp:smoke:crawl4ai` registers all 7 tools (`md`,
  `html`, `screenshot`, `pdf`, `execute_js`, `crawl`, `ask`)

#### Scenario: The smoke task detects a dead crawl4ai server

- **GIVEN** the crawl4ai container is stopped
- **WHEN** `bun run mcp:smoke:crawl4ai` runs as part of CI
- **THEN** check #1 (`GET /health`) returns non-200 or connection-refused
- **AND** the smoke task exits non-zero
- **AND** the CI gate `mise run lint:mcp-runtime` fails the build

### Requirement: JWT auth for crawl4ai MCP (v0.9.0 secure-by-default)

The system SHALL enable JWT bearer-token authentication on the crawl4ai
server per the v0.9.0 secure-by-default contract. The JWT secret SHALL
be sourced from the Infisical vault and SHALL be unique to the crawl4ai
service (no reuse with other stacks).

#### Scenario: Unauthenticated requests are rejected

- **GIVEN** the crawl4ai server is running with `security.jwt_enabled: true`
- **WHEN** any MCP tool call arrives without an `Authorization: Bearer <jwt>` header
- **THEN** the server returns HTTP 401
- **AND** no tool is invoked

#### Scenario: Authenticated requests succeed

- **GIVEN** the crawl4ai server is running with `security.jwt_enabled: true`
- **AND** the `CRAWL4AI_JWT_SECRET` env var matches the server's `JWT_SECRET`
- **WHEN** an MCP tool call arrives with `Authorization: Bearer <jwt>`
- **THEN** the server returns HTTP 200 with the tool result
- **AND** the call is logged in the Langfuse trace as `tool.crawl4ai.<name>`

### Requirement: browserbase is removed from the MCP surface

The system SHALL NOT register a `browserbase` MCP server in either
`opencode.json` or `.mcp.json`. The `Bonneagar/stacks/browser/` stack
SHALL remain as an **optional fallback** stack (per user directive)
with browserbase integrations explicitly marked as opt-in.

The 4 archived `2026-06-28-browserbase-phase-{1a,1b,2,3}-decisions/`
changes and `openspec/research/2026-06-28-browserbase-credit-program/`
SHALL each carry a `_DEPRECATED.md` header referencing this change.

#### Scenario: No browserbase MCP entry exists

- **GIVEN** this change has been implemented
- **WHEN** the developer runs `git grep -nE '"browserbase"' opencode.json .mcp.json`
- **THEN** zero results are returned
- **AND** the `browserbase` MCP entry from `opencode.json` lines 178-186
  (the prior `enabled: false` block) has been removed

#### Scenario: The browser stack still works for opt-in browserbase users

- **GIVEN** the `bonneagar/stacks/browser/` stack is running
- **WHEN** an operator explicitly sets `BROWSER_ENABLE_BROWSERBASE=1`
- **THEN** the browserbase opt-in path is available
- **AND** a top-of-file comment in `compose.yaml` documents this as
  "browserbase retained as opt-in fallback — see
  2026-08-21-complete-browserbase-archive-and-crawl4ai-mcp-v1"

### Requirement: `browser-tools` skill surfaces crawl4ai-mcp as a 6th backend

The `browser-tools` skill SHALL expose the canonical 6-backend matrix
to the agent runtime, with `crawl4ai-mcp` (the new MCP surface) as a
distinct entry alongside the existing 5 backends.

The 6 backends are:

| # | Backend | Default | Cost |
|--:|:--|:--|:--|
| 1 | **Crawl4AI REST** (self-hosted, port 11235) | ✅ ON | $0 |
| 2 | **Crawl4AI MCP** (self-hosted, JWT-authed, v0.9.x native) | ✅ ON | $0 |
| 3 | **Firecrawl MCP** (paid) | ✅ ON | $0.005-0.05/page |
| 4 | **Playwright CDP** (self-hosted, port 9222) | ✅ ON | $0 |
| 5 | **Skyvern** (opt-in via `BROWSER_ENABLE_SKYVERN=1`) | ⚙️ OFF | $0 |
| 6 | **Stagehand** (opt-in via `BROWSER_ENABLE_STAGEHAND=1`) | ⚙️ OFF | $0 |

#### Scenario: The decision tree routes to crawl4ai-mcp for MCP-native requests

- **GIVEN** the agent is reading `.agents/skills/browser-tools/SKILL.md`
- **WHEN** the user asks "use the MCP server to scrape https://example.com"
- **THEN** the loader matches the `browser-tools` skill (the router)
- **AND** the router points to the `crawl4ai-mcp` backend (not `crawl4ai` REST)
- **AND** the skill recommends the `crawl` MCP tool with the JWT bearer header

## MODIFIED Requirements

### Requirement: 3-skill entry point for browser / scraping / agent-on-the-web

The system SHALL provide exactly 3 skill entry points for the
browser / scraping / agent-on-the-web surface (per the
consolidation rule in this spec's Purpose section).

The 3 entry points are:
- `browser-tools` (the router) — covers the decision between the
  **6 backends** (Crawl4AI REST + Crawl4AI MCP + Firecrawl +
  Playwright CDP + Skyvern opt-in + Stagehand opt-in) + the
  5 corresponding skills + the new Crawl4AI v0.9.x features +
  the KCG safety rules + the opt-in pattern for Skyvern + Stagehand
- `firecrawl` (the MCP variant) — for the agent runtime integration
  with the Firecrawl MCP server
- `firecrawl-cli` (the Bash variant) — for terminal / CI / scheduled
  jobs

The `crawl4ai` skill is kept as the 4th browser skill (the
self-hosted backend reference) but is NOT counted as one of the
3 entry points per the spec mandate.

#### Scenario: An agent needs to scrape a single static page via MCP

- **GIVEN** the agent is reading the `browser-tools/SKILL.md`
- **WHEN** the user asks "scrape https://example.com to markdown via MCP"
- **THEN** the loader matches the `browser-tools` skill (the router)
- **AND** the router points to the `crawl4ai-mcp` backend (NEW in v0.9.x)
- **AND** the skill recommends `client.tools.crawl` with the JWT bearer header

### Requirement: `crawl4ai` stack pinned to v0.9.2

The system SHALL pin the `unclecoder/crawl4ai` Docker image to
`v0.9.2` (the latest stable release confirmed via Firecrawl on
2026-08-21). The previous `${TAG:-latest}` floating pin SHALL be
replaced with the explicit version.

#### Scenario: The pinned version is discoverable

- **GIVEN** the `bonneagar/stacks/crawl4ai/compose.yaml` has been updated
- **WHEN** the developer runs `grep -E "unclecode/crawl4ai" compose.yaml`
- **THEN** the image line reads `image: unclecode/crawl4ai:v0.9.2`
- **AND** no `${TAG:-latest}` floating pin remains