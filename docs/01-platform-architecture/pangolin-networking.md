---
title: "Pangolin Networking — Zero-Trust Reverse Proxy & Service Mesh"
domain: architecture
status: stable
description: "Complete Pangolin zero-trust networking covering Traefik reverse proxy, WireGuard VPN, Pocket ID OIDC, CrowdSec IDS, Blueprints, Docker label configuration, and multi-site HA"
supersedes:
  - docs/bonneagar/PANGOLIN_COMPLETE_GUIDE.md
  - docs/bonneagar/pangolin.md
  - docs/bonneagar/pangolin-patterns.md
  - docs/bonneagar/pangolin-openapi-specification-research.md
  - docs/bonneagar/generating-typescript-client-pangolin-api-openapi-spec.md
  - docs/bonneagar/hosting-litellm-pangolin-public-vs-private-access-models.md
  - docs/bonneagar/cloudflare-tunnel-research.md
  - docs/bonneagar/cloudflare.md
  - docs/bonneagar/cloudflare-backpine-summary.md
  - docs/bonneagar/cloudflare-workers-research.md
  - docs/bonneagar/cloudflare-d1-research.md
  - docs/bonneagar/cloudflare-containers-research.md
  - docs/bonneagar/cloudflare-openapi-specification-research.md
  - docs/bonneagar/Docker Provider.md
entities:
  - Pangolin
  - Traefik
  - WireGuard
  - PocketID
  - CrowdSec
  - NewtAgent
  - Gerbil
related_skills:
  - .agents/skills/pangolin/SKILL.md
  - .agents/skills/stack-ops/SKILL.md
ccc_query_hints:
  - "pangolin reverse proxy setup"
  - "how does wireguard vpn work with pangolin"
  - "pocket id authentication"
  - "crowdsec integration"
  - "pangolin blueprint configuration"
  - "docker label pangolin auto registration"
last_reviewed: 2026-06-06
truth: partial

---

# Pangolin Networking — Zero-Trust Reverse Proxy & Service Mesh

Pangolin is an open-source identity-aware reverse proxy by Fosrl. It combines WireGuard VPN tunnels, Traefik reverse proxy, Pocket ID OIDC authentication, and CrowdSec intrusion detection into a single stack for zero-trust service access.

## Architecture

```
Internet → Traefik (TLS) → Pangolin Gateway → WireGuard → Newt → Internal Services
                ↓
           Pocket ID (OIDC)
                ↓
           CrowdSec (IDS)
```

### Components

| Component | Role |
|-----------|------|
| **Pangolin Core** | Public-facing gateway, SSL termination, access control |
| **Newt Agent** | User-space WireGuard client on each site |
| **Gerbil** | WireGuard peer management controller |
| **Traefik** | Underlying reverse proxy |
| **Pocket ID** | OIDC identity provider for SSO (Passkey-based) |
| **TinyAuth** | Forward authentication middleware |
| **Middleware Manager** | Traefik middleware configuration UI/API |
| **CrowdSec** | Intrusion detection at the edge |

### In the Cianfhoghlaim Stack

Pangolin is the outermost security layer. Every one of the 89 stacks is exposed as a private Pangolin resource behind WireGuard tunnels and Pocket ID SSO.

**Key patterns:**

- **Private by default**: All services require WireGuard + Pocket ID Member role
- **Traefik middleware**: TinyAuth forward auth, CrowdSec IDS, TLS termination
- **Gerbil controller**: WireGuard peer management without manual key distribution
- **Docker label-based config**: `pangolin.private-resources.<name>.*` labels

## Network Flow

```
External Request → Traefik → TinyAuth (forwardAuth) → Pocket ID (OIDC)
    ↓
Gerbil (WireGuard controller) → Newt (site connector) → Internal Service
```

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

## Configuration

### Environment Variables

| Variable | Description |
|----------|-------------|
| `PANGOLIN_DOMAIN` | Public domain for VPN access |
| `WIREGUARD_PEERS` | Number of peer configs to generate |
| `AUTH_PROVIDER_URL` | OIDC provider endpoint |
| `DATABASE_URL` | Backend database connection |

### Configuration File (config.yaml)

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
  auto_provision: true
  default_role: member
```

### Database Options

| Database | Use Case |
|----------|----------|
| **SQLite** | Default, single-node |
| **PostgreSQL** | Production, multi-node |
| **MySQL/MariaDB** | Alternative RDBMS |

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

### Native Mode (Full IP Routing)

```bash
newt --native --pangolin-url=https://pangolin.example.com
```

Enables IP-level routing through the tunnel for non-HTTP services.

## Access Models

### Public Resources (Internet-facing)

```yaml
# pangolin.yaml
public-resources:
  web-app:
    subdomain: app
    upstream: http://web-app:3000
    auth: pocket_id
```

### Private Resources (VPN-only)

```yaml
private-resources:
  internal-dashboard:
    upstream: http://dashboard:8080
    auth: pocket_id
    roles: [member]
```

### Hybrid Access

```yaml
resources:
  - name: api
    type: http
    target: http://api:4000
    access: public
    domain: api.example.com

  - name: api-internal
    type: http
    target: http://api:4000/internal
    access: private  # Internal endpoints VPN-only
```

## Zero-Trust VPN (ZTNA)

Pangolin 1.13+ introduces Zero-Trust Network Access:

1. User connects via WireGuard client
2. Traffic routes through Pangolin tunnel
3. Pocket ID verifies identity
4. Access granted based on role membership
5. Request forwarded to private resource

### Client Setup

```bash
# Generate client config
./scripts/add-peer.sh <client-name>

# Import WireGuard config on client device
# Enable VPN connection
# Access private resources via Pangolin URLs
```

## Authentication & Identity

### Pocket ID (Recommended)

Pocket ID is the primary OIDC provider with Passkey (WebAuthn) support:

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

## Middleware Manager

Bridge Pangolin's abstraction with Traefik's native middleware features.

### ForwardAuth with TinyAuth

```yaml
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

## Blueprints (Declarative Config)

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

## Multi-Site Routing (HA)

Pangolin 1.18+ supports multiple site connectors per resource:

- Attach multiple sites to a single resource
- Pangolin routes traffic through the best available path
- Automatic failover when a site goes offline
- No manual reconfiguration needed

**Requirement**: Every attached site must have routable access to the resource's destination.

## HTTPS on Private Resources

Pangolin 1.18 introduces "Private HTTP" — real domain names with valid TLS, only reachable through an active Pangolin client:

- Traffic flows through the reverse proxy with valid TLS
- Certificate provisioned by the control plane
- Nothing exposed on the public internet

## Wildcard Resources

```yaml
resources:
  - name: wildcard-app
    subdomain: "*"
    upstream: http://app:3000
```

Requirements:
- DNS-01 validation for TLS certificates
- Wildcard DNS records configured
- Traefik configured for DNS-01 with Let's Encrypt

## Health Checks & Alerting

### Standalone Health Checks

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

Alert on state changes across sites, resources, and health checks.

**Actions:**
- Email (users, roles, or arbitrary addresses)
- Webhooks (POST JSON payload)
- PagerDuty, Opsgenie, ServiceNow, incident.io

## CrowdSec Integration

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

## Integration API

```yaml
integration_api:
  enabled: true
  token: ${PANGOLIN_API_TOKEN}
```

```python
import requests

headers = {"Authorization": f"Bearer {PANGOLIN_API_TOKEN}"}
resources = requests.get(
    "https://pangolin.cianfhoghlaim.ie/api/v1/resources",
    headers=headers
).json()
```

## Traefik Debugging

### Access Traefik Dashboard

```yaml
services:
  traefik:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.dashboard.rule=Host(`traefik.internal`)"
      - "traefik.http.routers.dashboard.service=api@internal"
```

### Traefik Configuration for Komodo

```yaml
# pangolin/config/traefik/dynamic_config.yml
http:
  routers:
    komodo-ui:
      rule: "Host(`komodo.network.example.com`)"
      service: komodo-service
      tls:
        certResolver: letsencrypt
      middlewares:
        - pangolin-auth

  services:
    komodo-service:
      loadBalancer:
        servers:
          - url: "http://komodo-core:9120"

  middlewares:
    pangolin-auth:
      forwardAuth:
        address: "http://pangolin:8080/verify"
        trustForwardHeader: true
```

## Tunneled Periphery Access

For Periphery agents behind NAT/firewalls:

```yaml
services:
  newt:
    image: ghcr.io/fosrl/newt:latest
    environment:
      - PANGOLIN_SERVER=wg.network.example.com:51820
      - NEWT_HOSTNAME=remote-server
      - NEWT_PORT=8120  # Expose Periphery port through tunnel
    network_mode: host
```

**Result:** Periphery accessible at `http://remote-server.pangolin.internal:8120` with no public port exposure and WireGuard-encrypted traffic.

## Stack Integration Pattern

Every Komodo stack includes Pangolin routing:

```
infrastructure/stacks/tools/vikunja/
├── compose.yaml      # Service definition
├── sidecar.yaml      # Locket secrets
├── pangolin.yaml     # Pangolin routing
└── blueprint.yaml    # Access rules
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| VPN not connecting | Verify UDP port 51820: `nc -vzu localhost 51820` |
| WireGuard config incorrect | Check client config in Pangolin dashboard |
| Gerbil not running | `docker ps | grep gerbil` |
| Traefik routing issues | Check Traefik dashboard at `traefik.internal` |
| OIDC auth failing | Verify Pocket ID provider URL and client credentials |
