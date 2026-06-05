# Headscale — Self-Hosted Tailscale-Compatible Coordination Server

## Overview

Headscale is an open-source implementation of the Tailscale control server. It lets you create a private mesh VPN using the Tailscale client (or any WireGuard client) with a self-hosted coordination server — no dependency on Tailscale's SaaS platform. Written in Go, it uses SQLite for state storage.

## Why This Matters for Kings' College Galway

While Pangolin provides the primary zero-trust tunnel infrastructure, Headscale provides an alternative mesh VPN for developer access and cross-server connectivity. It enables direct peer-to-peer WireGuard connections between the MacBook (bunchloch), the ARM server (arm1-oci), and the Hetzner node (cax41-hetzner) without routing through Pangolin. This is useful for high-bandwidth operations like syncing the 124 GB HuggingFace cache between servers or accessing GPU-accelerated services on the MacBook's unified memory from remote locations.

## Key Features

- **Tailscale-compatible** — Use the standard Tailscale client on any OS
- **Self-hosted** — All coordination data stays on your server
- **Mesh VPN** — Peer-to-peer WireGuard tunnels; no central traffic relay
- **ACL rules** — Fine-grained access control between nodes
- **MagicDNS** — Automatic DNS entries for all connected devices

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/infrastructure/headscale
docker compose up -d
```

### Production (via Komodo)

Deployed via Komodo on arm1-oci. Requires the `config/` directory with `config.yaml` defining the server URL, ACL rules, and DNS configuration.

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `HEADSCALE_SERVER_URL` | Yes | Public server URL | `https://hs.cianfhoghlaim.ie` |
| `HEADSCALE_DATABASE_TYPE` | No | Database type | `sqlite3` |
| `HEADSCALE_DATABASE_SQLITE_PATH` | No | SQLite database path | `/data/headscale.db` |

## Access

- **API**: `https://hs.cianfhoghlaim.ie` (public, authenticated by API key)
- **Health**: `http://localhost:9090/health`
- **Auth**: API key (generated via `headscale apikeys create`)

## Upstream

- **Repository**: <https://github.com/juanfont/headscale>
- **Documentation**: <https://headscale.net>
- **Latest**: v0.23.x (2025) — improved Tailscale client compatibility, DERP relay support, OIDC integration for user auth

## Screenshot

Headscale is a headless coordination server with no built-in web UI. The `/health` endpoint returns JSON status. Node status and ACL rules are managed via the `headscale` CLI. Headplane (separate stack) provides a web UI for Headscale management.
