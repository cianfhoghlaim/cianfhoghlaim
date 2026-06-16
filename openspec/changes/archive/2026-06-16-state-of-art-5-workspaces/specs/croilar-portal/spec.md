# Spec Delta: croilar-portal

## ADDED Requirements

### Requirement: AG-UI Agent Chat via AI SDK
The portal SHALL provide a real-time agent chat interface:
- `useAgentChat` hook SHALL use `ai-sdk` v5 `useChat` with `streamProtocol: 'ag-ui'`
- Chat SHALL stream tool calls, state updates, and text in real-time
- Tool call results SHALL render inline with expand/collapse
- Error SHALL display with retry button

#### Scenario: Chat with portal agent
- **WHEN** user sends "What stacks are running?"
- **THEN** agent calls Komodo MCP tool via LiteLLM proxy
- **AND** tool call progress is streamed to the UI
- **AND** response includes stack health status from Komodo API

### Requirement: Real MCP Gateway to LiteLLM
The MCP gateway API SHALL proxy to real LiteLLM:
- `routes/api/mcp.gateway.ts` SHALL forward MCP requests to `http://litellm:4000`
- Gateway SHALL validate JSON-RPC 2.0 format
- Gateway SHALL log tool calls to Langfuse
- Supported servers: browserbase, chrome-devtools, firecrawl-mcp, cognee-mcp, qdrant, memgraph, dagster-mcp, dlt-workspace, codeolas, chunkhound, docker-mcp, postgres, clickhouse

#### Scenario: Firecrawl scrape via MCP
- **WHEN** client sends `{method: "tools/call", params: {server: "firecrawl-mcp", name: "scrape", arguments: {url: "https://example.com"}}}`
- **THEN** gateway proxies to LiteLLM which routes to Firecrawl MCP
- **AND** response includes scraped markdown content
- **AND** trace is logged to Langfuse

### Requirement: MCP-UI Component Rendering
Agent chat responses SHALL render MCP-UI components for structured tool results, wrapping data tables, code blocks, browser screenshots, and graphs in `<mcp-ui>` server-rendered components that are themeable via CSS variables.

#### Scenario: Tool result with table data
- **WHEN** agent calls a Komodo list-stacks tool and receives JSON array
- **THEN** the response is rendered as an `<mcp-ui>` data table component
- **AND** the table shows stack name, status, CPU, memory columns
- **AND** the table uses the tenant's CSS variable theme colors

### Requirement: Komodo Stack Management
The stacks page SHALL manage real Komodo stacks:
- `routes/_layout/stacks/index.tsx` SHALL list stacks from Komodo API
- Each stack SHALL show: status, CPU, memory, containers, uptime, URL
- Actions: start, stop, restart (via Komodo API `POST /api/stack/{id}/action`)

#### Scenario: Restart a failing stack
- **WHEN** admin clicks "Restart" on a stack showing "unhealthy" status
- **THEN** Komodo API is called with `{action: "restart"}`
- **AND** stack status shows "restarting" during operation
- **AND** status refreshes to "healthy" on completion

### Requirement: Prometheus Monitoring
The monitoring pages SHALL display real container metrics by querying Docker container logs via `docker logs` API and scraping the Prometheus endpoint for container-level CPU, memory, network, and disk metrics, displayed as Recharts line and bar charts.

#### Scenario: View container metrics
- **WHEN** admin navigates to `/monitoring/metrics`
- **THEN** the page displays Recharts line charts for CPU usage, memory consumption, and network I/O
- **AND** metrics are fetched from the Prometheus endpoint
- **AND** charts update every 15 seconds with fresh data points

### Requirement: Dagster Pipeline Status
The data pipelines page SHALL query the real Dagster instance via a `createServerFn` that calls the Dagster GraphQL endpoint, displaying pipeline runs with asset name, status, duration, and materialization time, with failed runs linking to the Dagster UI for debugging.

#### Scenario: List recent pipeline runs
- **WHEN** admin navigates to `/data/pipelines`
- **THEN** server function queries Dagster GraphQL for recent runs
- **AND** the page displays each run with its asset name, status badge, and duration
- **AND** clicking a failed run opens a link to the Dagster UI run detail page

### Requirement: Langfuse + MotherDuck Analytics
The analytics page SHALL integrate observability data by querying Langfuse for trace metrics and embedding a MotherDuck Dive for cohort analytics, with an adjustable time range selector (24h, 7d, 30d).

#### Scenario: View 7-day trace analytics
- **WHEN** admin navigates to `/analytics` and selects "Last 7 days"
- **THEN** Langfuse trace data is queried for the selected time range
- **AND** the page displays trace count, latency p50/p95/p99, and error rate
- **AND** the MotherDuck Dive embed renders cohort retention analytics

### Requirement: Multi-Tenant Theme Injection
The portal SHALL apply tenant CSS variables:
- `lib/tenant/tenant-context.tsx` SHALL inject a `<style>` tag with CSS custom properties
- Properties SHALL include: `--color-primary`, `--color-secondary`, `--color-accent`, `--color-bg`, `--color-fg`, `--font-family`, `--font-heading`, `--border-radius`
- Theme SHALL change per tenant without page reload

#### Scenario: Switch to aleyum tenant
- **WHEN** user accesses `aleyum.cianfhoghlaim.ie`
- **THEN** `TenantProvider` loads `config/tenants/aleyum.yaml`
- **AND** CSS variables are injected matching aleyum's theme
- **AND** navigation shows aleyum-specific routes and features

## MODIFIED Requirements

None — portal pages retain existing structure; mocks become real.

## REMOVED Requirements

### Requirement: Mock Stack Data Arrays
**Reason**: Replaced by real Komodo API calls.
**Migration**: Remove static `stacks` array from `stacks/index.tsx`; wire to createServerFn.
