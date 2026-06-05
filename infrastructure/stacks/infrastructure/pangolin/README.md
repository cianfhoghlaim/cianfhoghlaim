# Pangolin — Identity-Aware Tunneled Reverse Proxy

## Overview

Pangolin is an open-source identity-aware reverse proxy built by Fosrl that combines WireGuard VPN tunnels, Traefik reverse proxy, Pocket ID OIDC authentication, and CrowdSec intrusion detection into a single stack. It provides zero-trust access to private services — no open ports, no public IPs, every request authenticated before it reaches the backend.

## Why This Matters for Kings' College Galway

Pangolin is the outermost security layer of the entire Cianfhoghlaim infrastructure. Every one of the 89 Docker Compose stacks is exposed as a private Pangolin resource behind WireGuard tunnels. A teacher accessing curriculum data, a developer deploying a pipeline, or an AI agent calling the LiteLLM gateway — every request passes through Pangolin's identity layer. This means the exam paper corpus, the HuggingFace model cache, and the student-facing web app are all protected by the same zero-trust envelope, regardless of which physical server they run on.

## Key Features

- **WireGuard tunnels** — Gerbil controller manages WireGuard peers; no open ports on backend services
- **Pocket ID OIDC** — Passkey-based single sign-on; Member/Admin role-based access
- **Traefik reverse proxy** — Dynamic configuration via Docker labels; automatic TLS via Let's Encrypt
- **CrowdSec IDS** — Intrusion detection and IP reputation filtering
- **TinyAuth** — Lightweight forward authentication for services without native SSO

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/infrastructure/pangolin
docker compose up -d
```

### Production (with Locket)

```bash
docker compose -f compose.yaml -f sidecar.yaml -f pangolin.yaml up -d
```

### Komodo (GitOps)

Deployed via Komodo on arm1-oci as the primary control-plane service. This stack MUST be running before any other stack — all other services depend on Pangolin for routing and authentication.

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `POSTGRES_USER` | No | Pangolin database user | `pangolin` |
| `POSTGRES_PASSWORD` | Yes | Pangolin database password | — |
| `POSTGRES_DB` | No | Database name | `pangolin` |
| `PANGOLIN_DASHBOARD_PASSWORD` | Yes | Admin dashboard password | — |
| `PANGOLIN_NEW_USER_REGISTRATION` | No | Allow new user registration | `false` |
| `POCKET_ID_OIDC_CLIENT_ID` | Yes | OIDC client ID for Pocket ID | — |
| `POCKET_ID_OIDC_CLIENT_SECRET` | Yes | OIDC client secret | — |

## Access

- **Admin Dashboard**: `https://pangolin.cianfhoghlaim.ie` (private, Admin role)
- **WireGuard**: Port 51820/udp (public)
- **Traefik Dashboard**: Internal only
- **Auth**: Pocket ID passkey-based SSO for users; WireGuard key pairs for machines

## Upstream

- **Repository**: <https://github.com/fosrl/pangolin>
- **Documentation**: <https://docs.pangolin.sh>
- **Latest**: Active development (2025) — PostgreSQL backend support, Gerbil WireGuard controller rewrite, CrowdSec integration

## Screenshot

Pangolin provides a web dashboard showing: organisation/site hierarchy, resource management (private/public services with role assignments), WireGuard peer status, and real-time connection logs. The Traefik dashboard is available internally showing route mappings and middleware chains.
