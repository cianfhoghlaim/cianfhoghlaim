# Crypteolas Setup Guide

This guide covers setting up the Crypteolas sub-package for local
development. Crypteolas lives at `sruth/tuatha/crypteolas/` after the
[consolidation refactor](../../../../openspec/changes/consolidate-external-libs-into-sruth/tuatha/).
See [`../STATUS.md`](../STATUS.md) for the full refactor history.

## Prerequisites

- Python 3.12+
- Node.js 20+ (for the TanStack UI — the new frontend is at
  `sruth/tuatha/apps/crypteolas demo/`; the legacy `sruth/tuatha/crypteolas/ui/`
  directory is no longer the canonical frontend)
- [1Password CLI](https://developer.1password.com/docs/cli/) (`brew install 1password-cli`)
- [Wrangler CLI](https://developers.cloudflare.com/workers/wrangler/install-and-update/) (`npm install -g wrangler`)
- [uv](https://github.com/astral-sh/uv) package manager (`brew install uv`)
- [Bun](https://bun.sh) 1.3+ (for the new frontend)
- Docker & Docker Compose

## Quick Start

```bash
# Navigate to the monorepo root
cd /Users/cianmacandeisigh/dev/kings_college_galway

# Toolchain + secrets + LLM backend (from repo root)
bun run setup

# Sync the tuath workspace member (resolves crypteolas)
cd tuatha && uv sync

# Start the unified Dagster UI (loads all 3 code-locations)
cd tuatha && uv run dagster dev
# → http://localhost:3000

# Or run crypteolas in isolation
cd tuatha && uv run dagster dev -m crypteolas.definitions
```

## 1. 1Password Setup

The secrets are now managed by the **Infisical** vault at
`dev-baile/crypteolas/` (not 1Password). The 1Password CLI used by the
prior setup script has been replaced by the Locket sidecar / Infisical
hydration flow. To seed the vault for the first time:

```bash
# From the monorepo root
bun run secrets:env     # create the dev-baile environment
bun run secrets:init    # seed the vault from .infisical.env template
```

The crypteolas-specific secrets (LITELLM_MASTER_KEY, OPENAI_API_KEY,
GITHUB_ACCESS_TOKEN, etc.) are referenced as
`infisical://dev-baile/crypteolas/<key>` in
[`../.env.lakekeeper.example`](../.env.lakekeeper.example) and
[`../dagster.yaml.example`](../dagster.yaml.example).

### Required Secrets (in Infisical)

| Item | Field | Description | Where to Get |
|------|-------|-------------|--------------|
| `sruth/crypteolas/openai` | `api_key` | OpenAI API key | platform.openai.com |
| `sruth/crypteolas/litellm` | `master_key` | LiteLLM master key | Generate: `openssl rand -hex 32` |
| `sruth/crypteolas/litellm` | `salt_key` | LiteLLM salt key | Generate: `openssl rand -hex 16` |
| `sruth/crypteolas/github` | `access_token` | GitHub PAT | github.com/settings/tokens |
| `sruth/crypteolas/postgresql` | `password` | PostgreSQL password | Generate: `openssl rand -hex 16` |
| `sruth/crypteolas/dagster_postgresql` | `password` | Dagster DB password | Generate: `openssl rand -hex 16` |
| `sruth/crypteolas/better_auth` | `secret` | Auth secret | Generate: `openssl rand -base64 32` |
| `sruth/crypteolas/cloudflare` | `account_id` | Cloudflare account ID | Cloudflare dashboard |
| `sruth/crypteolas/cloudflare` | `api_token` | API token (Workers edit) | cloudflare.com/profile/api-tokens |
| `sruth/crypteolas/cloudflare_r2` | `access_key_id` | R2 API access key | R2 dashboard > Manage R2 API Tokens |
| `sruth/crypteolas/cloudflare_r2` | `secret_access_key` | R2 secret key | Same as above |
| `sruth/crypteolas/payment_wallet` | `address` | Your EVM wallet address | Your wallet |

### Optional Secrets (in Infisical)

| Item | Field | Description |
|------|-------|-------------|
| `sruth/crypteolas/coingecko` | `api_key` | CoinGecko Pro API key |
| `sruth/crypteolas/etherscan` | `api_key` | Etherscan API key |
| `sruth/crypteolas/firecrawl` | `api_key` | Firecrawl API key |
| `sruth/crypteolas/walletconnect` | `project_id` | WalletConnect project ID |
| `sruth/crypteolas/github_oauth` | `client_id`, `client_secret` | GitHub OAuth app |

## 2. Dagster Development

### Install Dependencies

```bash
# From the sruth/tuatha/ root (the crypteolas workspace member is a sub-package)
cd tuatha && uv sync
```

The `uv sync` command resolves the crypteolas sub-package plus all its
runtime dependencies (dlt, cocoindex, cognee, fastapi, etc.).

### Start Dagster Dev Server

```bash
# From the sruth/tuatha/ root (loads the unified UI with 3 code-locations)
cd tuatha
uv run dagster dev
# → http://localhost:3000

# Or just the crypteolas code-location
cd tuatha
uv run dagster dev -m crypteolas.definitions
```

The Dagster UI will be available at http://localhost:3000. The
`uv.lock` at the monorepo root is the single source of truth for all
workspace members; the per-member `uv.lock` was removed during the
consolidation.

### Available Jobs

| Job | Description |
|-----|-------------|
| `crypto_api_ingestion` | Fetch data from CoinGecko, DeFiLlama, Aave, Pendle |
| `crypto_document_processing` | Scrape and index protocol documentation |
| `crypto_analytics` | Run analytics transformations |
| `funding_rate_pipeline` | Binance funding rate data (hourly partitioned) |
| `embedding_pipeline` | Code + docs embedding into LanceDB |
| `knowledge_graph_pipeline` | Cognee + Graphiti entity extraction |

### Available Schedules

| Schedule | Cron | Description |
|----------|------|-------------|
| Hourly API | `0 * * * *` | API data refresh |
| Weekly Docs | `0 3 * * 0` | Documentation refresh |

## 3. Cloudflare Setup

### Login to Cloudflare

```bash
wrangler login
```

### Create R2 Buckets

```bash
wrangler r2 bucket create crypto-data
wrangler r2 bucket create lance-embeddings
wrangler r2 bucket create raw-documents
```

### Create KV Namespaces

```bash
wrangler kv:namespace create PAYMENT_STATE
wrangler kv:namespace create SESSION_CACHE
wrangler kv:namespace create RATE_LIMITS
```

Update [`../wrangler.toml`](../wrangler.toml) with the namespace IDs from
the output. The `wrangler.toml` is preserved with a `# TODO` comment for
the missing `workers/index.ts` (the Workers code is not yet implemented;
see `../STATUS.md`).

### Set Worker Secrets

```bash
# Read secrets from Infisical and set in Cloudflare
infisical export --path=/crypteolas/openai/api_key | wrangler secret put OPENAI_API_KEY
infisical export --path=/crypteolas/payment_wallet/address | wrangler secret put PAYMENT_RECIPIENT
infisical export --path=/crypteolas/better_auth/secret | wrangler secret put BETTER_AUTH_SECRET
```

### Deploy Workers (when ready)

```bash
# Development
cd sruth/tuatha/crypteolas && wrangler dev

# Production
cd sruth/tuatha/crypteolas && wrangler deploy --env production
```

## 4. Frontend Development

The new TanStack Start frontend lives at
`sruth/tuatha/apps/crypteolas demo/` (not in `sruth/tuatha/crypteolas/ui/`, which is
legacy).

```bash
cd sruth/tuatha/apps/crypteolas demo

# Install dependencies
bun install

# Start development server
bun run dev
# → http://localhost:3000 (proxies /api → localhost:8001)
```

> The TanStack app is currently a buildable shell of stubs. See
> [`../../apps/crypteolas demo/STATUS.md`](../../apps/crypteolas_demo/STATUS.md)
> for the inventory of stubbed `src/lib/*` modules and `models/*` packages.

### Database Setup (for the demo)

```bash
cd sruth/tuatha/apps/crypteolas demo
bun run db:push      # push Drizzle schema to PostgreSQL
```

## 5. Docker Compose (Full Stack)

For running all services together:

```bash
# Start all services
cd sruth/tuatha/crypteolas
docker compose -f compose.yaml -f compose.dev.yaml up -d

# View logs
cd sruth/tuatha/crypteolas
docker compose logs -f dagster-webserver

# Stop services
cd sruth/tuatha/crypteolas
docker compose down
```

### Services

| Service | Port | Description |
|---------|------|-------------|
| `dagster-webserver` | 3000 | Dagster UI |
| `dagster-daemon` | - | Background scheduler |
| `postgres` | 5432 | PostgreSQL database |
| `dragonfly` | 6379 | Redis-compatible cache |
| `memgraph` | 7687 | Static knowledge graph |
| `memgraph-lab` | 3000 | Memgraph Lab UI |
| `langfuse` | 3000 | LLM observability |
| `lance-viewer` | 3030 | LanceDB viewer |
| `api` | 8000 | Crypteolas FastAPI backend |
| `ui` | 3000 | Legacy TanStack Start UI |

> The `restate` and `mcp-server` services from the prior setup are no
> longer in the stack. The Crypteolas MCP server now runs as a stdio
> process (`uv run python -m crypteolas.mcp_server`) rather than as a
> container. Marimo notebooks are run with `marimo edit` rather than as
> a containerised service.

## Directory Structure

```
tuatha/crypteolas/
├── STATUS.md
├── __init__.py
├── definitions.py              # Dagster code-location
├── pyproject.toml              # name = "crypteolas"
├── dg.toml                     # Dagster project config
├── compose.yaml, compose.dev.yaml
├── docker/                     # Dockerfile.api, Dockerfile.ui
├── _shims/                     # sruth.shared.* compatibility shims
├── agent_os/                   # AgentOS production runtime
├── agents/                     # ADK + Agno + HITL + MCP server
├── api/                        # FastAPI backend
├── baml_src/                   # 6 crypto BAML schemas
├── cocoindex_flows/            # unified_embedding, live_docs, protocol_graph
├── config/                     # repos.yaml, protocol configs
├── crates/                     # SpacetimeDB crypteolas-sync
├── dagster_assets/             # github + defi + embedding + lakekeeper
├── dagster_assets/components/  # YAML PipelineComponent loader
├── demo/                       # mock data
├── dlt_sources/                # defi/, github/, local/, documentation/
├── dlt_utils/                  # destinations
├── graphiti/                   # top-level Graphiti client
├── knowledge_graph/            # cognee/ + graphiti/
├── mcp_server/                 # top-level MCP server
├── notebooks/                  # 4 marimo (post-dedup)
├── pipelines/                  # older Dagster pipelines
├── storage/                    # LanceCatalog, Garage, DuckLake, Lakekeeper
├── tests/                      # 61 passing + pre-existing failures
├── transformations/            # Ibis-based crypto analytics
├── ui/                         # legacy TanStack (deferred to apps/crypteolas demo/)
├── docs/                       # 7 historical design docs
├── wrangler.toml               # Cloudflare Workers (TODO)
├── dagster.yaml.example
├── .env.example
└── .env.lakekeeper.example
```

## Troubleshooting

### Infisical CLI Not Working

```bash
# Sign in
infisical login

# Verify
infisical whoami
```

### Dagster Module Import Errors

```bash
# Ensure you're using the project venv
cd tuatha && uv sync

# Re-resolve the workspace
uv lock
```

### Port Already in Use

```bash
# Find process using port 3000
lsof -i :3000

# Kill process
kill -9 <PID>
```

### Cloudflare Deployment Issues

```bash
# Check wrangler config
wrangler whoami

# Validate config
cd sruth/tuatha/crypteolas && wrangler config check
```

### Crypteolas Demo `bun run dev` Fails

The TanStack frontend is a stub. See
`sruth/tuatha/apps/crypteolas demo/STATUS.md` for the inventory of stubs and
what needs to be implemented.

## Environment Variable Reference

See [`../.env.example`](../.env.example) for the complete list. Key
variables:

- `OPENAI_API_KEY` — required for LLM features
- `ANTHROPIC_API_KEY` — required if not going through LiteLLM
- `LITELLM_API_BASE` — `http://localhost:4000` if using the gateway
- `DUCKDB_PATH` — local analytics database path
- `LANCEDB_URI` — vector database path
- `GITHUB_ACCESS_TOKEN` — GitHub PAT for ingestion
- `COINGECKO_API_KEY` — optional, for higher rate limits
- `FIRECRAWL_API_KEY` — required for doc scraping
- `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` — LLM observability

## See Also

- [`../STATUS.md`](../STATUS.md) — the full refactor history
- [`../QUICKSTART.md`](../QUICKSTART.md) — quickstart for local dev
- [`../DEVELOPMENT.md`](../DEVELOPMENT.md) — development workflow
- [`../ARCHITECTURE.md`](../ARCHITECTURE.md) — 25 KB architecture deep-dive
- [`../../README.md`](../../README.md) — the tuath workspace README
