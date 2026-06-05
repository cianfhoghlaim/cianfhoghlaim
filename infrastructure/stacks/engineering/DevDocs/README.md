# DevDocs

## Overview
DevDocs is a developer documentation search and ingestion platform that crawls, indexes, and serves technical documentation from multiple sources. The stack consists of four services — a Next.js frontend (port 3001), a Python backend (port 24125), an MCP bridge, and an embedded Crawl4AI instance (port 11235) — all communicating over an internal `devdocs-network`.

## Why This Matters for Kings' College Galway
DevDocs indexes and serves the technical documentation backstop for the entire Celtic education platform. It crawls and locally mirrors Python package docs (Dagster, DLT, ibis, pydantic), TypeScript library docs (TanStack Start, Hono, Effect-TS), and Celtic education data standards — all accessible offline within the Pangolin VPN. The embedded Crawl4AI instance handles JavaScript-heavy documentation sites, and the MCP bridge exposes documentation search as an MCP tool that AI agents (LiteLLM, AgentOS) can query during code generation tasks for the data pipeline and curriculum extraction codebases.

## Key Features
- Next.js frontend with configurable backend URL
- Python backend with Crawl4AI-powered ingestion pipeline
- Embedded MCP server for AI agent documentation queries
- Local markdown storage at `./storage/markdown` for offline search
- Configurable discovery polling timeout and concurrent task limits

## Deployment

### Docker Compose (Local Development)
```bash
cd infrastructure/stacks/engineering/DevDocs
docker compose up -d
```

### Docker Compose (Production with Locket Secret Injection)
```bash
cd infrastructure/stacks/engineering/DevDocs
docker compose -f compose.yaml -f sidecar.yaml -f pangolin.yaml up -d
```

### Komodo (GitOps)
This stack is deployed via Komodo on arm1-oci. Komodo syncs from the Forgejo repository and applies `compose.yaml` + `sidecar.yaml`. No `.env` file is needed — Locket resolves all secrets from the Infisical `dev-baile` vault at runtime.

## Environment Variables
| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `NEXT_PUBLIC_BACKEND_URL` | Yes | Backend URL for the frontend | — |
| `CRAWL4AI_API_TOKEN` | Yes | Crawl4AI API authentication token | `devdocs-demo-key` |
| `CRAWL4AI_URL` | No | Crawl4AI service URL | `http://crawl4ai:11235` |
| `DISCOVERY_POLLING_TIMEOUT_SECONDS` | No | Crawl discovery timeout | `300` |
| `MCP_HOST` | No | MCP service hostname | `mcp` |
| `MAX_CONCURRENT_TASKS` | No | Max concurrent crawl tasks | `5` |
| `DISABLE_AUTH` | No | Disable Crawl4AI auth | `false` |

## Access
- **URL**: `https://devdocs.cianfhoghlaim.ie` (private, Pangolin Member role required)
- **Internal ports**: 3001 (frontend), 24125 (backend), 11235 (crawl4ai)
- **Auth**: Crawl4AI API token

## Health Check
```bash
docker ps --filter name=devdocs --format "table {{.Names}}\t{{.Status}}"
```

## Upstream
- **Repository**: Custom-built stack for the Cianfhoghlaim platform
- **Documentation**: Internal — managed as part of the platform infrastructure
- **Latest release**: Built from local Dockerfiles; tracks platform release cycles.
