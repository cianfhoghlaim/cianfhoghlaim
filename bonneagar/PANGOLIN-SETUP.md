# Pangolin Setup Guide

> **v5 slimmed version.** The full 395-line bring-up playbook has
> been condensed to ~150 lines. The canonical bring-up flow is
> now `iac:bootstrap` (see `iac/README.md`); this file
> documents the few manual steps the IaC doesn't automate +
> the architecture overview + troubleshooting + runbook.

## Architecture Overview

```
                        Internet
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Gerbil (WireGuard)                          │
│                      Ports: 80, 443, 51820                       │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Traefik (Reverse Proxy)                       │
│  - Wildcard TLS (Cloudflare DNS-01)                              │
│  - CrowdSec Bouncer                                             │
│  - Security Headers Middleware                                 │
└─────────────────────────────────────────────────────────────────┘
                            │
   ┌────────────────────────┼────────────────────────┐
   ▼                        ▼                        ▼
┌─────────────┐      ┌─────────────┐        ┌─────────────┐
│  Pangolin   │      │  Pocket ID  │        │  TinyAuth   │
│  Dashboard  │      │ OIDC/Passkey│        │ ForwardAuth │
└─────────────┘      └─────────────┘        └─────────────┘
                            │
                            ▼
                  ┌──────────────────┐
                  │  SQLite DB       │  ← config/db/db.sqlite, NOT the
                  │  (see note)      │    postgres:17 container alongside it
                  └──────────────────┘
```

> **Database:** the stack declares a `postgres:17` service, but Pangolin runs
> on SQLite — `POSTGRES_CONNECTION_STRING` is never injected, so it falls back
> and the Postgres database stays empty. This determines which image family you
> must use (`ee-*` = SQLite, `ee-postgresql-*` = Postgres); getting it wrong on
> an upgrade points Pangolin at the empty database. Details in
> [`stacks/pangolin/compose.yaml`](stacks/pangolin/compose.yaml).

**The diagram above is only the public path.** Pangolin serves two kinds of
resource over entirely separate routes:

```
PUBLIC (proxy resources)              PRIVATE (client resources)
Internet → Gerbil :443                Olm client on an enrolled device
        → Traefik (terminates TLS)            │ WireGuard
        → TinyAuth / Pocket ID                ▼
        → target                       Gerbil :51820/udp
                                              │
                                              ▼
                                       Newt on the workload host
                                       (terminates TLS itself)
                                              │
                                              ▼
                                           target
```

A private resource still has a public DNS record, and visiting it without the
client connected correctly returns Pangolin's "connect via the client" page.
That is the public path declining to serve it — not a fault.

Private resources are declared declaratively in
[`pangolin/private-resources.blueprint.yaml`](pangolin/private-resources.blueprint.yaml)
and applied with `pangolin/apply-blueprint.sh`. Full treatment:
[`docs/private-resources-architecture.md`](docs/private-resources-architecture.md)
and [`docs/deploy-private-resource-from-scratch.md`](docs/deploy-private-resource-from-scratch.md).

The OLM TCP tunnel client (stack: `stacks/olm-arm1-oci/`)
provides SSH + database access through the Pangolin mesh.

## Service Components

| Service | Port | URL | Stack |
|---------|------|-----|-------|
| Pangolin Dashboard | 3000-3003 | `pangolin.cianfhoghlaim.ie` | `stacks/pangolin/` |
| Pocket ID | 1411 | `auth.cianfhoghlaim.ie` | `stacks/pocket-id/` |
| TinyAuth | 10000 | `tinyauth.cianfhoghlaim.ie` | (bundled in pangolin) |
| Gerbil (WireGuard) | 51820/udp | - | (bundled in pangolin) |
| Traefik | 80, 443 | - | (bundled in pangolin) |
| OLM (TCP tunnel) | - | - | `stacks/olm-arm1-oci/` |

## Bring-up

The canonical flow is `bun run iac:bootstrap` (8-phase
state machine; see `iac/README.md`). This file documents
the 4 manual steps the IaC doesn't automate.

### Manual Step 1: Mint Pocket ID OIDC Client

1. Log in to Pocket ID at `https://auth.cianfhoghlaim.ie`
2. Settings → OIDC Clients → Create
3. Set redirect URI to `https://pangolin.cianfhoghlaim.ie`
4. Save the `client_id` + `client_secret` to Infisical:

```bash
infisical secrets create --env=dev-baile --path=/pangolin \
  POCKETID_CLIENT_ID=<client-id>
infisical secrets create --env=dev-baile --path=/pangolin \
  POCKETID_CLIENT_SECRET=<client-secret>
```

### Manual Step 2: Cloudflare DNS Token

1. Cloudflare → My Profile → API Tokens → Create Token
2. Use "Edit zone DNS" template; scope to `cianfhoghlaim.ie`
3. Save the token to Infisical:

```bash
infisical secrets create --env=dev-baile --path=/pangolin \
  CF_DNS_API_TOKEN=<token>
```

### Manual Step 3: CrowdSec Bouncer Registration

1. SSH to `arm1-oci`
2. `docker exec crowdsec cscli bouncers add arm1-oci-traefik`
3. Save the bouncer key to Infisical:

```bash
infisical secrets create --env=dev-baile --path=/pangolin \
  CROWDSEC_BOUNCER_KEY=<key-from-cscli>
```

### Manual Step 4: Pangolin Enterprise Licence

Save to Infisical at `dev-baile/pangolin/`:

```bash
infisical secrets create --env=dev-baile --path=/pangolin \
  PANGOLIN_LICENCE=PER-D09BF259-...
```

## Authentication Flow

```
Client → Pocket ID (OIDC) → Pangolin (session) → Service
         (Passkey)            (cookie)          (Pangolin-routed)
```

Pocket ID is the SSO provider; Pangolin consumes OIDC
tokens; services behind Pangolin are accessible via
`<service>.cianfhoghlaim.ie` with SSO.

## TLS Certificate Configuration

- **Wildcard** `*.cianfhoghlaim.ie` cert via Cloudflare
  DNS-01 challenge
- **Cert resolver**: `letsencrypt` (Traefik)
- **Token**: `CF_DNS_API_TOKEN` (manual step 2)

## Security Features

- **HSTS**, `X-Frame-Options`, `X-Content-Type-Options`,
  `Referrer-Policy: strict-origin-when-cross-origin` (set by
  Traefik)
- **CrowdSec** intrusion detection (bouncer plugin)
- **Rate limits**: 100 req/min global, 10 req/min auth
  endpoints (Traefik middleware)

## Troubleshooting

```bash
# Check service health
docker compose -f /etc/komodo/pangolin/compose.yaml ps

# Check Traefik logs
docker logs traefik --tail 100

# Check CrowdSec decisions
docker exec crowdsec cscli decisions list

# Check Pangolin health
curl -I https://pangolin.cianfhoglam.ie/api/v1/
```

## Operational Runbook

### Daily
- [ ] Log Dashboard for anomalies
- [ ] CrowdSec decisions: `cscli decisions list`

### Weekly
- [ ] Review CrowdSec alerts
- [ ] Check certificate expiry (SSL Labs)
- [ ] Verify security headers (securityheaders.com)

### Monthly
- [ ] Update container images
- [ ] Update CrowdSec collections: `cscli hub update`
- [ ] Review and rotate secrets

### Incident Response
1. Check Log Dashboard
2. Review CrowdSec decisions
3. Manually block IPs if needed
4. Review rate limits
5. Document incident

## Cross-references

- `iac/README.md` — the IaC (8-phase bootstrap, secrets
  syncing, resource-sync management)
- `iac/commands/bootstrap.ts` — the canonical bring-up
  state machine
- `stacks/pangolin/` — the 6-file GOLD_STANDARD stack
- `stacks/olm-arm1-oci/` — the OLM TCP tunnel client
  (moved from `pangolin/olm-oracle/` in v5)
- `SECRETS-MANAGEMENT.md` — the Infisial + Locket + mise
  3-way contract
- `DEPLOYMENT-STRATEGY.md` — the 2-host topology
  (`arm1-oci` + `bunchloch`)
