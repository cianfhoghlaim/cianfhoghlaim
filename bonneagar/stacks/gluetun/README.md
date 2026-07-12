# Gluetun

## Overview
Gluetun is a lightweight VPN client container that supports WireGuard and OpenVPN providers. Created by qmcgaw and distributed at `qmcgaw/gluetun:latest`, it acts as a network sidecar — any container that joins its network stack routes all egress traffic through the VPN tunnel. This stack is configured for a custom WireGuard provider with DNS over TLS, health checking, and port forwarding.

## Why This Matters for Kings' College Galway
Gluetun provides geo-resilient network egress for the Crawl4AI web scraping pipeline. When the Celtic education platform scrapes Irish curriculum websites (`curriculumonline.ie`, `examinations.ie`) or UK exam board sites (`aqa.org.uk`, `eduqas.co.uk`), traffic routes through the Gluetun WireGuard tunnel — ensuring consistent access regardless of the hosting provider's geo-restrictions and protecting the scraper's originating IP. The integrated DNS over TLS (Cloudflare) prevents DNS-based blocking, and the health check ensures the VPN tunnel is established before Crawl4AI starts processing jobs. It's the privacy layer that keeps curriculum ingestion reliable and geo-resilient.

## Key Features
- WireGuard VPN client with custom provider configuration
- DNS over TLS via Cloudflare (1.1.1.1) for encrypted DNS resolution
- Container network sidecar pattern — Crawl4AI joins the Gluetun network
- Port 11235 forwarded through the VPN tunnel for Crawl4AI traffic
- Health check verifies VPN tunnel establishment before marking healthy

## Deployment

### Docker Compose (Local Development)
```bash
cd infrastructure/stacks/gluetun
docker compose up -d
```

### Docker Compose (Production with Locket Secret Injection)
```bash
cd infrastructure/stacks/gluetun
docker compose -f compose.yaml -f sidecar.yaml -f pangolin.yaml up -d
```

### Komodo (GitOps)
This stack is deployed via Komodo on arm1-oci. Komodo syncs from the Forgejo repository and applies `compose.yaml` + `sidecar.yaml`. No `.env` file is needed — Locket resolves all secrets from the Infisical `dev-baile` vault at runtime.

## Environment Variables
| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `VPN_SERVICE_PROVIDER` | No | VPN provider type | `custom` |
| `VPN_TYPE` | No | VPN protocol | `wireguard` |
| `WIREGUARD_PRIVATE_KEY` | Yes | WireGuard private key | — |
| `WIREGUARD_ADDRESSES` | Yes | WireGuard tunnel addresses | — |
| `WIREGUARD_PUBKEY` | Yes | WireGuard peer public key | — |
| `WIREGUARD_PRESHARED_KEY` | Yes | WireGuard preshared key | — |
| `WIREGUARD_ENDPOINT` | Yes | WireGuard endpoint (host:port) | — |
| `DNS_OVER_TLS` | No | Enable DNS over TLS | `1` |
| `DOT_PROVIDERS` | No | DoT provider list | `1.1.1.1, cloudflare` |
| `VPN_PORT_FORWARDING` | No | Enable port forwarding | `off` |
| `HEALTH_VPN_DURATION_INITIAL` | No | Initial health check wait | `30s` |

## Access
- **URL**: `https://gluetun.cianfhoghlaim.ie` (private, Pangolin Member role required)
- **Internal port**: 11235 (Crawl4AI proxy through VPN)
- **Auth**: WireGuard key-based authentication

## Health Check
```bash
docker ps --filter name=gluetun --format "table {{.Names}}\t{{.Status}}"
```

## Upstream
- **Repository**: https://github.com/qdm12/gluetun
- **Documentation**: https://github.com/qdm12/gluetun/wiki
- **Latest release**: Pulls `qmcgaw/gluetun:latest` — lightweight VPN client with WireGuard and OpenVPN support.
