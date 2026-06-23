# MCPJungle

## Overview
MCPJungle is a browser UI and gateway for managing Model Context Protocol (MCP) servers — the standard protocol for connecting LLMs to external tools and data sources. Created by the MCPJungle team and distributed as `mcpjungle/mcpjungle`, it provides a central dashboard for discovering, configuring, and routing MCP servers. The stack includes a Postgres backend for persistent configuration and a browser-accessible management UI on port 8080.

## Why This Matters for Kings' College Galway
MCPJungle serves as the unified MCP server management console for all AI agent workflows at Kings' College Galway. When the oideachais AgentOS needs to query curriculum data or the browser AgentOS needs filesystem access, MCPJungle routes these tool calls through the appropriate MCP servers. It acts as the control plane for the `oideachais-mcp-filesystem` server and any future MCP servers that expose the Dagster pipeline, LanceDB vector store, or DuckDB analytics layer to AI agents — essential infrastructure for the self-hosted AI agent architecture.

## Key Features
- Centralized MCP server registry and configuration UI
- Gateway mode for routing LLM tool calls to multiple backend MCP servers
- Postgres-backed persistent configuration storage
- Filesystem MCP server access via host mount (read-only)
- Configurable OpenTelemetry tracing support

## Deployment

### Docker Compose (Local Development)
```bash
cd infrastructure/stacks/MCPJungle
docker compose up -d
```

### Docker Compose (Production with Locket Secret Injection)
```bash
cd infrastructure/stacks/MCPJungle
docker compose -f compose.yaml -f sidecar.yaml -f pangolin.yaml up -d
```

### Komodo (GitOps)
This stack is deployed via Komodo on arm1-oci. Komodo syncs from the Forgejo repository and applies `compose.yaml` + `sidecar.yaml`. No `.env` file is needed — Locket resolves all secrets from the Infisical `dev-baile` vault at runtime.

## Environment Variables
| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `POSTGRES_USER` | No | Postgres username | `mcpjungle` |
| `POSTGRES_PASSWORD` | Yes | Postgres password | — |
| `POSTGRES_DB` | No | Postgres database name | `mcpjungle` |
| `DATABASE_URL` | Yes | Full Postgres connection URL | `postgres://mcpjungle:mcpjungle@db:5432/mcpjungle` |
| `SERVER_MODE` | No | Server runtime mode | `development` |
| `OTEL_ENABLED` | No | OpenTelemetry tracing | `false` |
| `HOST_PORT` | No | Host port for the web UI | `8080` |
| `MCPJUNGLE_IMAGE_TAG` | No | Image tag | `latest-stdio` |

## Access
- **URL**: `https://mcpjungle.cianfhoghlaim.ie` (private, Pangolin Member role required)
- **Internal port**: 8080
- **Auth**: No built-in auth — protected by Pangolin/TinyAuth upstream

## Health Check
```bash
docker ps --filter name=mcpjungle --format "table {{.Names}}\t{{.Status}}"
```

## Upstream
- **Repository**: https://github.com/mcpjungle/mcpjungle
- **Documentation**: https://mcpjungle.com
- **Latest release**: Pulls `mcpjungle/mcpjungle:latest-stdio` — a continuously updated MCP server management gateway.
