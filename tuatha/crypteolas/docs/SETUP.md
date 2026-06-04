# Crypteolas Setup Guide

This guide covers setting up the Crypteolas project for local development with Dagster orchestration and Cloudflare services.

## Prerequisites

- Python 3.12+
- Node.js 20+ (for frontend)
- [1Password CLI](https://developer.1password.com/docs/cli/) (`brew install 1password-cli`)
- [Wrangler CLI](https://developers.cloudflare.com/workers/wrangler/install-and-update/) (`npm install -g wrangler`)
- [uv](https://github.com/astral-sh/uv) package manager (`brew install uv`)

## Quick Start

```bash
# Navigate to project
cd src/crypteolas

# Set up 1Password vault and secrets (first time only)
./scripts/setup_1password.sh

# Start Dagster (with 1Password secret injection)
op run --env-file .env -- dagster dev -w workspace.local.yaml
```

## 1. 1Password Setup

### Create the Vault

Run the setup script to create the 1Password vault and empty secret items:

```bash
chmod +x scripts/setup_1password.sh
./scripts/setup_1password.sh
```

### Fill in Required Secrets

After running the script, fill in these required values in 1Password:

| Item | Field | Description | Where to Get |
|------|-------|-------------|--------------|
| `openai` | `api_key` | OpenAI API key | platform.openai.com |
| `postgresql` | `password` | PostgreSQL password | Generate: `openssl rand -hex 16` |
| `dagster_postgresql` | `password` | Dagster DB password | Generate: `openssl rand -hex 16` |
| `better_auth` | `secret` | Auth secret | Generate: `openssl rand -base64 32` |
| `cloudflare` | `account_id` | Cloudflare account ID | Cloudflare dashboard |
| `cloudflare` | `api_token` | API token (Workers edit) | cloudflare.com/profile/api-tokens |
| `cloudflare_r2` | `access_key_id` | R2 API access key | R2 dashboard > Manage R2 API Tokens |
| `cloudflare_r2` | `secret_access_key` | R2 secret key | Same as above |
| `payment_wallet` | `address` | Your EVM wallet address | Your wallet |

### Optional Secrets

| Item | Field | Description |
|------|-------|-------------|
| `coingecko` | `api_key` | CoinGecko Pro API key |
| `etherscan` | `api_key` | Etherscan API key |
| `firecrawl` | `api_key` | Firecrawl API key |
| `walletconnect` | `project_id` | WalletConnect project ID |
| `github_oauth` | `client_id`, `client_secret` | GitHub OAuth app |

## 2. Dagster Development

### Install Dependencies

```bash
# Activate virtual environment
source ../../.venv/bin/activate

# Or use uv to install to the project venv
uv pip install --python .venv/bin/python dagster-dlt dagster-postgres
```

### Start Dagster Dev Server

```bash
# With 1Password secret injection
op run --env-file .env -- dagster dev -w workspace.local.yaml

# Or export secrets first
eval $(op inject -i .env)
dagster dev -w workspace.local.yaml
```

The Dagster UI will be available at http://localhost:3000

### Available Jobs

| Job | Description |
|-----|-------------|
| `crypto_api_ingestion` | Fetch data from CoinGecko, DeFiLlama, Aave, Pendle |
| `crypto_document_processing` | Scrape and index protocol documentation |
| `crypto_analytics` | Run analytics transformations |
| `funding_rate_pipeline` | Binance funding rate data (hourly partitioned) |

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

Update `wrangler.toml` with the namespace IDs from the output.

### Set Worker Secrets

```bash
# Read secrets from 1Password and set in Cloudflare
op read op://crypteolas/openai/api_key | wrangler secret put OPENAI_API_KEY
op read op://crypteolas/payment_wallet/address | wrangler secret put PAYMENT_RECIPIENT
op read op://crypteolas/better_auth/secret | wrangler secret put BETTER_AUTH_SECRET
```

### Deploy Workers (when ready)

```bash
# Development
wrangler dev

# Production
wrangler deploy --env production
```

## 4. Frontend Development

### Install Dependencies

```bash
cd demo
bun install
```

### Start Development Server

```bash
# With 1Password secret injection
op run --env-file .env -- bun run dev

# Or
eval $(op inject -i .env)
bun run dev
```

### Database Setup

```bash
# Run migrations
bun run db:migrate

# Seed initial data
bun run db:seed
```

## 5. Docker Compose (Full Stack)

For running all services together:

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f dagster-webserver

# Stop services
docker compose down
```

### Services

| Service | Port | Description |
|---------|------|-------------|
| `dagster-webserver` | 3000 | Dagster UI |
| `dagster-daemon` | - | Background scheduler |
| `postgres` | 5432 | PostgreSQL database |
| `restate` | 8080, 9070 | Durable workflows |
| `marimo` | 2718 | Notebooks |
| `mcp-server` | 3001 | Agent tools |

## Directory Structure

```
src/crypteolas/
├── .env                  # Environment config (1Password refs)
├── workspace.local.yaml  # Dagster workspace (local dev)
├── workspace.yaml        # Dagster workspace (Docker)
├── dagster.yaml          # Dagster instance config
├── wrangler.toml         # Cloudflare Workers config
├── orchestration/        # Dagster assets and jobs
├── pipelines/            # DLT data pipelines
├── demo/                 # TanStack Start frontend
├── agents/               # Agno AI agents
├── workflows/            # Restate workflows
└── scripts/              # Setup scripts
```

## Troubleshooting

### 1Password CLI Not Working

```bash
# Sign in
op signin

# Verify account
op account list
```

### Dagster Module Import Errors

```bash
# Ensure you're using the project venv
source ../../.venv/bin/activate

# Or use uv
uv pip install --python .venv/bin/python <package>
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
wrangler config check
```

## Environment Variable Reference

See `.env` for the complete list. Key variables:

- `OPENAI_API_KEY` - Required for LLM features
- `DUCKDB_PATH` - Local analytics database path
- `LANCEDB_URI` - Vector database path
- `COINGECKO_API_KEY` - Optional, for higher rate limits
- `FIRECRAWL_API_KEY` - Required for doc scraping
