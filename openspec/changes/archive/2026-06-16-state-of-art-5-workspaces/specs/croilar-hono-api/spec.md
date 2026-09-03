# Spec Delta: croilar-hono-api

## ADDED Requirements

### Requirement: SIWE Authentication Plugin
The Hono API SHALL support Sign-In With Ethereum:
- `auth.ts` SHALL add `siwe()` Better Auth plugin
- Wallet providers: MetaMask, WalletConnect, Coinbase Wallet
- SIWE challenge SHALL follow EIP-4361 (Sign-In With Ethereum)
- Wallet address SHALL be linked to Better Auth user account

#### Scenario: Wallet sign-in
- **WHEN** client sends `GET /api/auth/sign-in/siwe?address=0x...&chainId=1`
- **THEN** server returns a SIWE challenge message
- **AND** client signs the challenge with their wallet
- **AND** server verifies the signature and creates/returns a session

### Requirement: Convex Auth Provider
The Hono API SHALL serve as the OIDC issuer for Convex:
- `/.well-known/openid-configuration` SHALL advertise JWT issuer
- `/.well-known/jwks.json` SHALL expose RS256 public keys
- Convex SHALL validate JWTs against this JWKS endpoint
- Audience SHALL be `convex_backend`

#### Scenario: Convex validates JWT from Hono
- **WHEN** sruth/oideachais/web makes a Convex query with a JWT from this Hono
- **THEN** Convex calls `/.well-known/jwks.json` to get the public key
- **AND** Convex verifies the JWT signature
- **AND** `ctx.auth.getUserIdentity()` returns the user

### Requirement: Real DuckDB Connection
The data layer SHALL use a real DuckDB connection:
- `src/data/duckdb.ts` SHALL lazy-load the `duckdb` native module
- In Docker, DuckDB SHALL connect to `/data/croilar.duckdb`
- In dev (bun), DuckDB SHALL be mocked with `console.log` stubs
- `data/spotify.ts`, `data/github.ts`, `data/cv.ts` SHALL use real query helpers

#### Scenario: Query GitHub stars
- **WHEN** sruth/croilar/apps/web calls `GET /api/v1/github/stars`
- **THEN** DuckDB queries the ingested GitHub data table
- **AND** returns an array of repo objects with star counts

### Requirement: MCP Server Registration
The Hono API SHALL expose 5 MCP servers (filesystem, codeolas, firecrawl, browserbase, cognee) via a LiteLLM proxy route at `POST /mcp/*`, with each server configurable via environment variables and the server list queryable via `GET /mcp/servers`.

#### Scenario: List registered MCP servers
- **WHEN** client sends `GET /mcp/servers`
- **THEN** response returns a JSON array of 5 server entries
- **AND** each entry includes `name`, `description`, `tools` count, and `enabled` status

### Requirement: Expanded Database Schema
The Drizzle ORM schema SHALL include all tables required by Better Auth: `organization`, `member`, `invitation`, `jwks`, `passkey`, `oauth_account`, `oauth_application`, and `two_factor`, in addition to the existing `user`, `session`, and `account` tables.

#### Scenario: Database migration creates all tables
- **WHEN** `bun run db:migrate` is executed
- **THEN** all 11 tables are created in the Postgres database
- **AND** foreign key constraints are enforced between dependent tables
- **AND** unique indexes are created on email, token, and organization name columns

### Requirement: Drizzle Migrations + Seed
The database SHALL be initialized with an auto-generated Drizzle migration and a seed script that creates 4 organizations (aleyum, cianfhoghlaim, croilar-admin, croilar-collab) plus one admin user per org and one test user.

#### Scenario: Run seed script on fresh database
- **WHEN** `bun run src/seed.ts` is executed after migration
- **THEN** 4 organization rows are inserted
- **AND** 4 admin user rows are inserted (one per org)
- **AND** 1 test user row is inserted with membership in `cianfhoghlaim`
- **AND** the script is idempotent (safe to run multiple times)

### Requirement: Health + Metrics Endpoint
The API SHALL expose observability endpoints: `GET /api/health` (JSON health check), `GET /api/metrics` (Prometheus-format container stats, request count, latency histograms), `GET /api/version` (git SHA, timestamp, version), and `GET /api/admin/stacks` (Komodo-managed stack list, org-scoped).

#### Scenario: Prometheus scrape endpoint
- **WHEN** Prometheus scrapes `GET /api/metrics`
- **THEN** response includes `http_requests_total`, `http_request_duration_ms_bucket`, and `process_resident_memory_bytes`
- **AND** response is in Prometheus text exposition format
- **AND** latency histogram buckets are correctly labeled by route and method

## MODIFIED Requirements

### Requirement: DuckDB Stub → Real Connection
The DuckDB data layer SHALL lazy-load the real `duckdb` native module, connecting to `/data/croilar.duckdb` in Docker-deployed environments while providing console.log stubs in bun development mode, allowing all existing routes (`/api/v1/spotify`, `/api/v1/github`, `/api/v1/cv`) to return real data when deployed.

#### Scenario: DuckDB query in Docker
- **WHEN** the API runs in Docker and receives `GET /api/v1/github/stars`
- **THEN** DuckDB connects to `/data/croilar.duckdb`
- **AND** the query returns real rows from the ingested GitHub data table
- **AND** the response includes star counts, repo names, and last-updated timestamps

#### Scenario: DuckDB query in bun dev
- **WHEN** the API runs in bun dev mode and receives `GET /api/v1/github/stars`
- **THEN** DuckDB is not loaded (native module unavailable in bun)
- **AND** the query stub returns an empty array
- **AND** a console.log message indicates the query that would have run
