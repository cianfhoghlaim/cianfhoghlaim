# Pangolin Full-Featured Setup Guide

Complete documentation for the Pangolin identity-aware tunneled reverse proxy with security enhancements.

## Architecture Overview

```
                                    Internet
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         Gerbil (WireGuard)                         │
│                         Ports: 80, 443, 51820                       │
└─────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     Traefik (Reverse Proxy)                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │
│  │  TLS Wildcard   │  │ CrowdSec Plugin │  │ Security Headers│     │
│  │  (Cloudflare)   │  │   (Bouncer)     │  │   Middleware   │     │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘     │
└─────────────────────────────────────────────────────────────────────┘
                                        │
          ┌─────────────────────────────┼─────────────────────────────┐
          ▼                             ▼                             ▼
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│    Pangolin     │         │   Pocket ID     │         │    TinyAuth     │
│  (Dashboard)    │         │  (OIDC/Passkey) │         │  (ForwardAuth)  │
└─────────────────┘         └─────────────────┘         └─────────────────┘
          │                             │                             │
          └─────────────────────────────┼─────────────────────────────┘
                                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         PostgreSQL Database                         │
└─────────────────────────────────────────────────────────────────────┘
```

## Service Components

| Service | Port | Purpose | URL |
|---------|------|---------|-----|
| Pangolin | 3000-3003 | Identity-aware proxy management | pangolin.cianfhoghlaim.ie |
| Gerbil | 51820/udp | WireGuard tunnel controller | - |
| Traefik | 80, 443 | Reverse proxy with TLS | - |
| Pocket ID | 1411 | Passkey-based OIDC provider | auth.cianfhoghlaim.ie |
| TinyAuth | 10000 | Forward authentication | tinyauth.cianfhoghlaim.ie |
| Middleware Manager | 3456 | Traefik middleware UI | middleware.cianfhoghlaim.ie |
| Log Dashboard | 3000 | Access log visualization | logs.cianfhoghlaim.ie |
| CrowdSec | 8080, 7422 | Intrusion detection/prevention | - |
| PostgreSQL | 5432 | Production database | - |

## Quick Start

### Development (without secrets injection)
```bash
cd bonneagar/pangolin
docker compose up -d
```

### Production (with Locket secrets)
```bash
cd bonneagar/pangolin
docker compose -f compose.yaml -f sidecar.yaml up -d
```

## Authentication Flow

```
User Request → Traefik → TinyAuth (forwardAuth)
                              │
                              ▼
                         Pocket ID (OIDC)
                              │
                              ▼
                         Passkey Auth (WebAuthn)
                              │
                              ▼
                         Return JWT to TinyAuth
                              │
                              ▼
                         Forward to Protected Service
```

### Setting Up PocketID + TinyAuth Integration

#### Step 1: Create OIDC Client in PocketID
1. Navigate to `https://auth.cianfhoghlaim.ie`
2. Log in as admin
3. Go to **Admin Panel** → **OIDC Clients** → **Add OIDC Client**
4. Configure:
   - **Name**: TinyAuth
   - **Callback URL**: `https://tinyauth.cianfhoghlaim.ie/api/oauth/callback/pocketid`
   - **Scopes**: openid, email, profile, groups
5. Save and note the **Client ID** and **Client Secret**

#### Step 2: Store Credentials in Infisical
```bash
op item create --vault taisce-secrets --category login --title "pocketid-tinyauth" \
  "client_id=<client-id-from-pocketid>" \
  "client_secret[password]=<client-secret-from-pocketid>"
```

#### Step 3: Deploy with Sidecar
```bash
docker compose -f compose.yaml -f sidecar.yaml up -d
```

### Protecting Services with TinyAuth

Add the `tinyauth` middleware to any router in `dynamic_config.yml`:

```yaml
my-protected-router:
  rule: "Host(`myapp.cianfhoghlaim.ie`)"
  service: my-service
  entryPoints:
    - websecure
  middlewares:
    - secure-headers
    - tinyauth  # Add this line
```

## TLS Certificate Configuration

### Wildcard Certificates (DNS-01 Challenge)

The setup uses Cloudflare DNS challenge for wildcard certificates covering `*.cianfhoghlaim.ie`.

#### Required Infisical Item
```bash
op item create --vault taisce-secrets --category "API Credential" --title "cloudflare" \
  "dns_api_token[password]=<your-cloudflare-dns-api-token>"
```

#### Cloudflare Token Permissions
- Zone:DNS:Edit for your domain
- Zone:Zone:Read for your domain

### Certificate Resolvers

| Resolver | Challenge | Use Case |
|----------|-----------|----------|
| `letsencrypt-wildcard` | DNS-01 (Cloudflare) | All `*.cianfhoghlaim.ie` domains (primary) |
| `letsencrypt` | HTTP-01 | Individual domains (backup) |

## Security Features

### Security Headers

All HTTPS traffic receives these headers:

| Header | Value | Purpose |
|--------|-------|---------|
| Strict-Transport-Security | 2 years, includeSubDomains, preload | Force HTTPS |
| X-Frame-Options | SAMEORIGIN | Clickjacking protection |
| X-Content-Type-Options | nosniff | MIME sniffing prevention |
| X-XSS-Protection | 1; mode=block | XSS filter |
| Referrer-Policy | strict-origin-when-cross-origin | Referrer control |
| Permissions-Policy | camera=(), microphone=(), etc. | Feature restrictions |

### TLS Hardening

- **Minimum TLS**: 1.2
- **Maximum TLS**: 1.3
- **SNI Strict**: Enabled
- **Cipher Suites**: Modern ECDHE suites only
- **Curve Preferences**: X25519, CurveP384

### Rate Limiting

| Middleware | Average | Burst | Period | Use Case |
|------------|---------|-------|--------|----------|
| `rate-limit-api` | 100 | 50 | 1m | API endpoints |
| `rate-limit-auth` | 10 | 5 | 1m | Authentication endpoints |
| `rate-limit-strict` | 5 | 3 | 1m | Sensitive endpoints |

## CrowdSec Integration

### How It Works

1. CrowdSec analyzes Traefik access logs
2. Detects attack patterns (brute force, scanning, etc.)
3. Shares threat intelligence with community
4. Traefik bouncer blocks malicious IPs

### Initial Setup

After first deployment:

```bash
# Generate bouncer key
docker exec crowdsec cscli bouncers add traefik-bouncer

# Store in Infisical
op item create --vault taisce-secrets --category login --title "crowdsec" \
  "bouncer_key[password]=<generated-key>"

# Restart with sidecar
docker compose -f compose.yaml -f sidecar.yaml restart
```

### Managing CrowdSec

```bash
# View decisions (blocks)
docker exec crowdsec cscli decisions list

# View alerts
docker exec crowdsec cscli alerts list

# Manually ban IP
docker exec crowdsec cscli decisions add --ip 1.2.3.4 --duration 24h --reason "Manual ban"

# Unban IP
docker exec crowdsec cscli decisions delete --ip 1.2.3.4
```

## Log Dashboard

Access at `https://logs.cianfhoghlaim.ie` (protected by TinyAuth).

Features:
- Real-time access log visualization
- Request statistics
- Response code distribution
- Traffic patterns

## Traefik Configuration

### Static Configuration

Located at `config/traefik/traefik_config.yml`:
- API/Dashboard settings
- Providers (HTTP from Pangolin, File for local)
- Certificate resolvers (ACME)
- Entry points
- Plugins (Badger, CrowdSec)

### Dynamic Configuration

Located at `config/traefik/dynamic_config.yml`:
- Middlewares (security headers, auth, rate limiting)
- Routers (domain to service mapping)
- Services (backend URLs)
- TLS options

### Middleware Manager

Access at `https://middleware.cianfhoghlaim.ie` to:
- Create custom middlewares via UI
- Apply middlewares to routes
- Manage authentication rules

## Troubleshooting

### Certificate Issues

```bash
# Check Traefik logs
docker logs traefik 2>&1 | grep -i cert

# Check ACME storage
docker exec traefik cat /letsencrypt/acme-wildcard.json | jq .

# Force certificate renewal
rm -f config/letsencrypt/acme-wildcard.json
docker compose restart traefik
```

### CrowdSec Not Blocking

```bash
# Check bouncer registration
docker exec crowdsec cscli bouncers list

# Check collections installed
docker exec crowdsec cscli collections list

# Check acquisition
docker exec crowdsec cscli metrics
```

### TinyAuth Not Redirecting to PocketID

1. Verify environment variables:
   ```bash
   docker exec tinyauth env | grep POCKETID
   ```

2. Check PocketID OIDC client configuration
3. Verify callback URL matches exactly

### Service Unreachable

```bash
# Check Traefik routing
curl -H "Host: myapp.cianfhoghlaim.ie" http://localhost:80 -v

# Check service health
docker compose ps

# Check network connectivity
docker exec traefik wget -q -O- http://pangolin:3001/api/v1/
```

## Secrets Reference

| Secret | Infisical Path | Purpose |
|--------|----------------|---------|
| `SERVER_SECRET` | `taisce-secrets/pangolin-core/server_secret` | Pangolin session encryption |
| `POSTGRES_PASSWORD` | `taisce-secrets/pangolin-core/postgres_password` | Database authentication |
| `CF_DNS_API_TOKEN` | `taisce-secrets/cloudflare/dns_api_token` | Cloudflare DNS challenge |
| `POCKETID_CLIENT_ID` | `taisce-secrets/pocketid-tinyauth/client_id` | TinyAuth OAuth client |
| `POCKETID_CLIENT_SECRET` | `taisce-secrets/pocketid-tinyauth/client_secret` | TinyAuth OAuth secret |
| `CROWDSEC_BOUNCER_KEY` | `taisce-secrets/crowdsec/bouncer_key` | Traefik bouncer auth |

## File Structure

```
bonneagar/pangolin/
├── compose.yaml              # Main compose file
├── sidecar.yaml              # Locket sidecar for secrets
├── secrets.env               # Locket template
├── config/
│   ├── config.yml            # Pangolin config
│   ├── traefik/
│   │   ├── traefik_config.yml    # Static config
│   │   ├── dynamic_config.yml    # Dynamic config
│   │   ├── logs/                 # Access/error logs
│   │   └── rules/                # Middleware Manager rules
│   ├── letsencrypt/
│   │   ├── acme.json             # HTTP challenge certs
│   │   └── acme-wildcard.json    # DNS challenge certs
│   ├── crowdsec/
│   │   └── acquis.yaml           # Log acquisition config
│   ├── tinyauth/
│   │   └── users                 # Local users (fallback)
│   └── middleware-manager/
│       └── templates.yaml        # Middleware templates
└── data/
    └── middleware-manager/       # Middleware Manager DB
```

## Operational Runbook

### Daily Checks
- [ ] Log Dashboard for anomalies
- [ ] CrowdSec decisions: `docker exec crowdsec cscli decisions list`

### Weekly Maintenance
- [ ] Review CrowdSec alerts: `docker exec crowdsec cscli alerts list`
- [ ] Check certificate expiry: SSL Labs test
- [ ] Verify security headers: securityheaders.com

### Monthly Updates
- [ ] Update container images: `docker compose pull && docker compose up -d`
- [ ] Update CrowdSec collections: `docker exec crowdsec cscli hub update`
- [ ] Review and rotate secrets if needed

### Incident Response
1. Check Log Dashboard for attack patterns
2. Review CrowdSec decisions
3. Manually block IPs if needed
4. Review and update rate limits
5. Document incident

## Enterprise Edition Features

Pangolin is now running **Enterprise Edition** (`fosrl/pangolin:ee-latest`).

### Integration API (port 3003)
The Integration API enables programmatic management of resources, sites, and blueprints.
- API docs: `https://api.cianfhoghlaim.ie/v1/docs` (via Pangolin routing)
- Create API keys: Pangolin UI → Server Admin → API Keys
- Use with `pangolin apply blueprint --file ... --api-key <key>`

### Private Resource Discovery
Container labels are auto-discovered by Newt agents with Docker socket access.
To register a container as a private resource, include `pangolin.yaml` in the deploy:
```bash
docker compose -f compose.yaml -f sidecar.yaml -f pangolin.yaml up -d
```

### Licence Management
- EE licence: `PANGOLIN_LICENCE` in `.env` → Infisical via `bun run scripts/init-vault.ts`
- Activate: `docker compose up -d` (licence applied via env var)
- Renew: update `.env` → `bun run scripts/init-vault.ts` → restart pangolin stack

### Accessing Services
All private resources require the Pangolin client (Olm) authenticated with PocketID SSO:
1. Install Olm from https://pangolin.net/downloads
2. Connect to `pangolin.cianfhoghlaim.ie`
3. Login via PocketID at `auth.cianfhoghlaim.ie`
4. Access services at their `*.cianfhoghlaim.ie` domains
