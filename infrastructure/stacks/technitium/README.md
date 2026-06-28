# Technitium DNS Server — Local DNS Resolution

## Overview

Technitium DNS Server is a self-hosted, authoritative and recursive DNS server with a web-based management console. It supports DNS-over-HTTPS, DNS-over-TLS, DNS-over-QUIC, blocklists, and split-horizon DNS. Written in C#/.NET, it is a full-featured alternative to BIND or Unbound.

## Why This Matters for Kings' College Galway

The Cianfhoghlaim infrastructure uses internal domain names (`*.cianfhoghlaim.ie`) for all 89 stacks. Technitium provides local DNS resolution so that containers and services can reach each other by name without relying on public DNS or `/etc/hosts` entries. It also enables DNS-level blocking of telemetry, tracking, and ad domains — reducing noise in Langfuse traces and MLflow logs. The recursive resolver with forwarders to Cloudflare (1.1.1.1) and Google (8.8.8.8) ensures fallback for external domains.

## Key Features

- **Web management console** — Full DNS configuration via browser UI at port 5380
- **DNS-over-HTTPS/TLS/QUIC** — Encrypted DNS for privacy
- **Blocklists** — Built-in domain blocking for ad/tracker domains
- **Split-horizon** — Different DNS responses for internal vs external queries
- **Recursive resolver** — Configurable forwarders with access control lists

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/DnsServer
docker compose up -d
```

### Production (via Komodo)

Deployed via Komodo on arm1-oci. Must be running before any stack that depends on internal DNS resolution.

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `DNS_SERVER_DOMAIN` | Yes | Primary domain for this DNS server | `dns-server` |
| `DNS_SERVER_ADMIN_PASSWORD` | No | Admin console password | — |
| `DNS_SERVER_FORWARDERS` | No | Upstream DNS forwarders | `1.1.1.1, 8.8.8.8` |
| `DNS_SERVER_ENABLE_BLOCKING` | No | Enable domain blocking | `false` |

## Access

- **Web Console**: `http://localhost:5380` (HTTP)
- **DNS Service**: Port 53 (UDP+TCP)
- **Auth**: Admin password (configured via env var)

## Upstream

- **Repository**: <https://github.com/TechnitiumSoftware/DnsServer>
- **Documentation**: <https://technitium.com/dns/>
- **Latest**: Active development — DNS-over-QUIC support, improved blocklist management, DHCP server integration

## Screenshot

Technitium's web console at port 5380 shows a dashboard with: DNS query statistics, cache hit ratio, active blocklists, zone editor, forwarder configuration, and DNS-over-HTTPS/TLS certificate management.
