# Headplane — Web UI for Headscale

## Overview

Headplane is a web-based management interface for Headscale, the self-hosted Tailscale coordination server. It provides a graphical dashboard for managing nodes, users, ACL rules, and pre-auth keys — replacing the CLI-only workflow of Headscale with a browser UI.

## Why This Matters for Kings' College Galway

Managing a mesh VPN of 3+ nodes via CLI alone becomes tedious quickly. Headplane provides a clean web UI for adding new devices to the mesh, revoking access, viewing connected peers, and managing pre-auth keys. When onboarding a new developer device or adding a temporary research VM, the Headplane UI eliminates the need to SSH into the control plane and run `headscale` CLI commands. It bridges the convenience of Tailscale's SaaS dashboard with the privacy of a self-hosted control plane.

## Key Features

- **Node management** — View, approve, and remove connected devices
- **User management** — Create users, assign nodes, manage pre-auth keys
- **ACL editor** — Visual interface for Headscale access control rules
- **Lightweight** — Single container, Svelte-based UI, <100 MB memory
- **Headscale-native** — Connects directly to Headscale's internal API

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/infrastructure/headplane
docker compose up -d
```

### Production (via Komodo)

Deployed via Komodo on arm1-oci. Requires a running Headscale instance. Configured via environment variables for Headscale API URLs.

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `HEADPLANE_SERVER_URL` | Yes | Headplane public URL | `https://hp.cianfhoghlaim.ie` |
| `HEADSCALE_INTERNAL_URL` | Yes | Headscale internal API URL | `http://headscale:8080` |
| `HEADSCALE_PUBLIC_URL` | Yes | Headscale public URL | `https://hs.cianfhoghlaim.ie` |
| `HEADPLANE_COOKIE_SECRET` | Yes | Session cookie encryption secret | — |

## Access

- **Web UI**: `https://hp.cianfhoghlaim.ie` (private, Admin role)
- **Auth**: Headscale API key + session cookies

## Upstream

- **Repository**: <https://github.com/tale/headplane>
- **Documentation**: <https://github.com/tale/headplane#readme>
- **Latest**: Active development (2025) — SvelteKit rewrite, improved ACL editor, multi-user dashboard

## Screenshot

Headplane's web UI shows a dashboard with: connected device list (hostname, IP, last seen, online status), user management panel, pre-auth key generator, ACL rules editor, and node approval queue for new devices joining the mesh.
