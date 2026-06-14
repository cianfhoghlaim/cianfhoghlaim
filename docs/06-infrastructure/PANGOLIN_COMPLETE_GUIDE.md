---
truth: partial
---

# Pangolin — Complete Zero-Trust Networking Guide

> **Merged From:** `docs/bonneagar/pangolin/` (27 files)
> Consolidated: pangolin.md, KCG_SUMMARY.md, Pangolin 1.18 release notes, Configuration File.md, Docker Compose.md, Database Options.md, Google OAuth.md, Pocket ID OAuth.md, GitHub OAuth.md, Integration API.md, Enable Integration API.md, Middleware Manager.md, Blueprints.md, Telemetry.md, Set up Pangolin Zero Trust VPN.md, Implementing External Authentication.md, Traefik Dashboard debugging, CrowdSec integration, Visualizing Traefik Logs, Guide to Securing Traefik, fosrl_olm.md, old_Implementing External Auth.md, and root-level pangolin-*.md files.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Newt Agent](#newt-agent)
6. [Public Resources](#public-resources)
7. [Private Resources](#private-resources)
8. [Zero-Trust VPN (ZTNA)](#zero-trust-vpn-ztna)
9. [Authentication & Identity](#authentication--identity)
10. [Middleware Manager](#middleware-manager)
11. [Blueprints (Declarative Config)](#blueprints-declarative-config)
12. [Docker Label Configuration](#docker-label-configuration)
13. [Multi-Site Routing (HA)](#multi-site-routing-ha)
14. [HTTPS on Private Resources](#https-on-private-resources)
15. [Health Checks & Alerting](#health-checks--alerting)
16. [Wildcard Resources](#wildcard-resources)
17. [Integration API](#integration-api)
18. [CrowdSec Integration](#crowdsec-integration)
19. [Traefik Debugging](#traefik-debugging)
20. [Integration with Komodo](#integration-with-komodo)

---

## Overview

Pangolin is an open-source identity-aware reverse proxy by Fosrl. It combines WireGuard VPN tunnels, Traefik reverse proxy, Pocket ID OIDC authentication, and CrowdSec intrusion detection into a single stack for zero-trust service access.

### In the Cianfhoghlaim Stack

Pangolin is the outermost security layer. Every one of the 89 stacks is exposed as a private Pangolin resource behind WireGuard tunnels and Pocket ID SSO. The `pangolin.yaml` and `blueprint.yaml` files in every stack directory define routing and access rules.

**Key patterns:**
- **Private by default**: All services require WireGuard + Pocket ID Member role
- **Traefik middleware**: TinyAuth forward auth, CrowdSec IDS, TLS termination
- **Gerbil controller**: WireGuard peer management without manual key distribution
- **Docker label-based config**: `pangolin.private-resources.<name>.*` labels

---

## Architecture

```
Internet → Traefik (TLS) → Pangolin Gateway → WireGuard → Newt → Internal Services
                ↓
           Pocket ID (OIDC)
```

### Components

| Component | Role |
|-----------|------|
| **Pangolin Core** | Public-facing gateway, SSL termination, access control |
| **Newt Agent** | User-space WireGuard client on each site |
| **Gerbil** | WireGuard peer management controller |
| **Traefik** | Underlying reverse proxy |
| **Pocket ID** | OIDC identity provider for SSO |
| **Middleware Manager** | Traefik middleware configuration UI/API |

---

## Installation

### Docker Compose

```yaml
services:
  pangolin:
    image: fosrl/pangolin:latest
    cap_add:
      - NET_ADMIN
      - SYS_MODULE
    sysctls:
      - net.ipv4.conf.all.src_valid_mark=1
    volumes:
      - ./config:/config
      - ./gerbil:/gerbil
    ports:
      - "51820:51820/udp"   # WireGuard
      - "443:443"           # HTTPS
      - "80:80"             # HTTP (redirect)
    environment:
      - PANGOLIN_DOMAIN=${PANGOLIN_DOMAIN}
      - DATABASE_URL=${DATABASE_URL}
```

---

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PANGOLIN_DOMAIN` | Public domain for VPN access | — |
| `WIREGUARD_PEERS` | Number of peer configs to generate | 5 |
| `AUTH_PROVIDER_URL` | OIDC provider endpoint | — |
| `DATABASE_URL` | Backend database connection | — |

### Configuration File

Pangolin uses a YAML configuration file at `/config/config.yaml`:

```yaml
app:
  dashboard_url: "https://pangolin.cianfhoghlaim.ie"
  
server:
  domain: pangolin.cianfhoghlaim.ie
  http_port: 80
  https_port: 443

wireguard:
  port: 51820
  interface: wg0
  
auth:
  provider: pocket_id
  provider_url: "https://id.cianfhoghlaim.ie"
```

### Database Options

Pangolin supports:
- **SQLite** (default, single-node)
- **PostgreSQL** (production, multi-node)
- **MySQL/MariaDB**

---

## Newt Agent

Newt is a user-space WireGuard agent that runs on each site/server.

### Key Advantages

- **No root required** (user-space WireGuard implementation)
- **Multiplexing**: Single Newt connection routes traffic for multiple services
- **Auto-registration**: Automatically registers with Pangolin Core

### Deployment

```yaml
services:
  newt:
    image: fosrl/newt:latest
    environment:
      - PANGOLIN_URL=https://pangolin.cianfhoghlaim.ie
      - NEWT_ID=${NEWT_ID}
      - NEWT_SECRET=${NEWT_SECRET}
    cap_add:
      - NET_ADMIN
```

### Native Mode

With `--native`, Newt creates a TUN device for full IP routing:

```bash
newt --native --pangolin-url=https://pangolin.example.com
```

This enables IP-level routing through the tunnel, useful for non-HTTP services.

---

## Public Resources

Public resources are accessible from the internet through Pangolin's TLS-terminated proxy.

```yaml
# pangolin.yaml
public-resources:
  web-app:
    subdomain: app
    upstream: http://web-app:3000
    auth: pocket_id
```

---

## Private Resources

Private resources are only reachable through an active Pangolin client (WireGuard) connection.

```yaml
private-resources:
  internal-dashboard:
    upstream: http://dashboard:8080
    auth: pocket_id
    roles: [member]
```

---

## Zero-Trust VPN (ZTNA)

Pangolin 1.13+ introduces Zero-Trust Network Access:

1. User connects via WireGuard client
2. Traffic routes through Pangolin tunnel
3. Pocket ID verifies identity
4. Access granted based on role membership
5. Request forwarded to private resource

### Client Setup

1. Generate client config: `./scripts/add-peer.sh <client-name>`
2. Import WireGuard config on client device
3. Enable VPN connection
4. Access private resources via their Pangolin URLs

---

## Authentication & Identity

### Pocket ID (Recommended)

Pocket ID is the primary OIDC provider for Pangolin:

```yaml
auth:
  provider: pocket_id
  provider_url: "https://id.cianfhoghlaim.ie"
  auto_provision: true
  default_role: member
```

### Google OAuth

```yaml
auth:
  provider: google
  client_id: ${GOOGLE_CLIENT_ID}
  client_secret: ${GOOGLE_CLIENT_SECRET}
  allowed_domains: [cianfhoghlaim.ie]
```

### GitHub OAuth

```yaml
auth:
  provider: github
  client_id: ${GITHUB_CLIENT_ID}
  client_secret: ${GITHUB_CLIENT_SECRET}
  allowed_orgs: [cianfhoghlaim]
```

---

## Middleware Manager

The Middleware Manager bridges Pangolin's abstraction with Traefik's native middleware features.

### ForwardAuth with TinyAuth

```yaml
# Define in Middleware Manager
middlewares:
  tinyauth-protection:
    forwardAuth:
      address: "http://tinyauth:3000/api/auth/traefik"
      trustForwardHeader: true
      authResponseHeaders:
        - X-User
        - X-Email
```

### Referencing in Blueprints

```yaml
resources:
  my-app:
    middleware: tinyauth-protection
```

---

## Blueprints (Declarative Config)

Blueprints define routing and access rules declaratively:

```yaml
# blueprint.yaml
version: "1"
resources:
  - name: vikunja
    type: private
    upstream: http://vikunja:3456
    auth: pocket_id
    roles: [member]
    
  - name: grafana
    type: private
    upstream: http://grafana:3000
    auth: pocket_id
    roles: [admin]
```

---

## Docker Label Configuration

The preferred method for Komodo integration. Labels on containers auto-register with Pangolin:

```yaml
services:
  vikunja:
    image: vikunja/vikunja:latest
    labels:
      - "pangolin.private-resources.vikunja.upstream=http://vikunja:3456"
      - "pangolin.private-resources.vikunja.auth=pocket_id"
      - "pangolin.private-resources.vikunja.roles=member"
```

### Comparison of Configuration Methods

| Feature | Pangolin UI | YAML Blueprint | Docker Labels |
|---------|-------------|----------------|---------------|
| Source of Truth | Database | File System | Git (via Komodo) |
| Automation | Low | Medium | **High** |
| Komodo Synergy | Low | Medium | **Maximum** |

---

## Multi-Site Routing (HA)

Pangolin 1.18+ supports multiple site connectors per resource for high availability:

- Attach multiple sites to a single resource
- Pangolin routes traffic through the best available path
- Automatic failover when a site goes offline
- No manual reconfiguration needed

**Requirement**: Every attached site must have routable access to the resource's destination.

---

## HTTPS on Private Resources

Pangolin 1.18 introduces "Private HTTP" — real domain names with valid TLS, but only reachable through an active Pangolin client connection:

- Traffic flows through the reverse proxy with valid TLS
- Certificate provisioned by the control plane
- Scheme and destination port are configurable
- Nothing exposed on the public internet

---

## Health Checks & Alerting

### Standalone Health Checks

Pick a site, give it a target, choose HTTP or TCP:

```yaml
health-checks:
  - name: printer-check
    site: bunchloch
    target: "192.168.1.100"
    type: tcp
    port: 9100
    interval: 60s
```

### Alert Rules

Subscribe to state changes across sites, resources, and health checks:

**Actions:**
- Email (users, roles, or arbitrary addresses)
- Webhooks (POST JSON payload)
- PagerDuty, Opsgenie, ServiceNow, incident.io

---

## Wildcard Resources

Public resources support wildcard subdomains:

```yaml
resources:
  - name: wildcard-app
    subdomain: "*"
    upstream: http://app:3000
```

**Requirements:**
- DNS-01 validation for TLS certificates
- Wildcard DNS records configured
- Traefik configured for DNS-01 with Let's Encrypt

---

## Integration API

Enable the Pangolin Integration API for programmatic control:

```yaml
integration_api:
  enabled: true
  token: ${PANGOLIN_API_TOKEN}
```

### Example: Shadow-IT Detector

```python
import requests

headers = {"Authorization": f"Bearer {PANGOLIN_API_TOKEN}"}
resources = requests.get(
    "https://pangolin.cianfhoghlaim.ie/api/v1/resources",
    headers=headers
).json()
```

---

## CrowdSec Integration

Install and activate CrowdSec in the Pangolin stack:

```yaml
services:
  crowdsec:
    image: crowdsecurity/crowdsec:latest
    environment:
      - COLLECTIONS=crowdsecurity/traefik
    volumes:
      - crowdsec_data:/var/lib/crowdsec
      - traefik_logs:/var/log/traefik:ro
```

CrowdSec reads Traefik logs and blocks malicious IPs at the edge.

---

## Traefik Debugging

### Access Traefik Dashboard

The Traefik dashboard is essential for debugging Pangolin routing:

```yaml
services:
  traefik:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.dashboard.rule=Host(`traefik.internal`)"
      - "traefik.http.routers.dashboard.service=api@internal"
```

### Log Visualization

Deploy the Traefik Log Dashboard with the Pangolin stack for real-time log analysis.

---

## Integration with Komodo

Every Komodo stack includes a `pangolin.yaml` that defines how the service is exposed:

```
infrastructure/stacks/tools/vikunja/
├── compose.yaml      # Service definition
├── sidecar.yaml      # Locket secrets
├── pangolin.yaml     # Pangolin routing
└── blueprint.yaml    # Access rules
```

### Related Tools

- **Komodo** — Deploys and manages all stacks including Pangolin itself
- **Locket** — Injects Pangolin secrets (WireGuard keys, OIDC credentials)
- **Pocket ID** — Identity provider for all Pangolin authentication
- **TinyAuth** — Forward authentication middleware
- **CrowdSec** — Intrusion detection at the edge
