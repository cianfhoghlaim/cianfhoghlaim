# Dozzle — Container Log Viewer

## Overview

Dozzle is a lightweight, real-time log viewer for Docker containers. It provides a web UI for browsing, searching, and monitoring container logs without needing to SSH into a server or use `docker logs`. Written in Go and Vue.js, it runs as a single binary with minimal resource footprint.

## Why This Matters for Kings' College Galway

With 89 Docker Compose stacks producing logs across 3 physical servers, SSH-ing into each host and running `docker logs` is not viable. Dozzle provides a single web interface showing real-time logs from every container — critical for debugging failed Dagster pipeline runs, investigating LiteLLM routing errors, or monitoring LLM inference performance. It also supports remote hosts, so a single Dozzle instance can aggregate logs from the ARM1, Hetzner, and MacBook nodes.

## Key Features

- **Real-time log streaming** — Live container logs with search and filtering
- **Multi-host** — Connect to remote Docker daemons via TCP
- **Simple auth** — Built-in simple authentication provider
- **No analytics** — `DOZZLE_NO_ANALYTICS=1` ensures zero telemetry
- **Lightweight** — <20 MB binary, sub-100 MB memory

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/dozzle
docker compose up -d
```

### Production (via Komodo)

Deployed via Komodo on arm1-oci as a public resource (debugging tool needs access without VPN).

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `DOZZLE_FILTER` | No | Container name filter | `name=dozzle` |
| `DOZZLE_NO_ANALYTICS` | Yes | Disable analytics | `1` |
| `DOZZLE_HOSTNAME` | No | Display hostname | `localhost` |
| `DOZZLE_LEVEL` | No | Log level | `debug` |
| `DOZZLE_AUTH_PROVIDER` | No | Auth provider (`simple` for basic auth) | — |
| `DOZZLE_REMOTE_HOST` | No | Remote Docker daemon URL | — |

## Access

- **Web UI**: `https://dozzle.cianfhoghlaim.ie` (public with basic auth)
- **Auth**: Simple username/password provider

## Upstream

- **Repository**: <https://github.com/amir20/dozzle>
- **Documentation**: <https://dozzle.dev>
- **Latest**: v8.x (2025) — Vue 3 rewrite, fuzzy search, multi-host agent support, improved performance with large log volumes

## Screenshot

Dozzle's web UI displays a sidebar with all running containers grouped by host, and a main panel showing scrolling log output with ANSI colour support. The search bar filters logs in real-time, and the top bar shows CPU/memory usage per container.
