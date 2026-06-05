# Networking Toolbox

## Overview
Networking Toolbox is a web-based suite of network diagnostic and debugging tools. Created by lissy93, it bundles WHOIS lookups, DNS record queries, ping tests, traceroute, port scanning, SSL certificate inspection, HTTP header analysis, and subnet calculations into a single Docker container available at `lissy93/networking-toolbox:latest`. The stack runs on port 3000 with minimal configuration.

## Why This Matters for Kings' College Galway
Networking Toolbox provides on-demand network diagnostics within the Pangolin VPN for troubleshooting the multi-service architecture. When a stack fails to route through Traefik, when Garage S3 becomes unreachable, or when the PlanetScale Postgres connection drops, engineers can open the toolbox at `networking-toolbox.cianfhoghlaim.ie` and diagnose DNS resolution, port reachability, and SSL chain issues without leaving the private network. It's a lightweight but essential debugging tool for the 23+ Docker Compose stacks that form the Cianfhoghlaim platform.

## Key Features
- WHOIS lookup and DNS record querying (A, AAAA, MX, TXT, CNAME, NS)
- ICMP ping, TCP traceroute, and port scanning
- SSL/TLS certificate inspection with chain validation
- HTTP header analysis and status code checking
- Subnet calculator and IP geolocation

## Deployment

### Docker Compose (Local Development)
```bash
cd infrastructure/stacks/engineering/networking-toolbox
docker compose up -d
```

### Docker Compose (Production with Locket Secret Injection)
```bash
cd infrastructure/stacks/engineering/networking-toolbox
docker compose -f compose.yaml -f sidecar.yaml -f pangolin.yaml up -d
```

### Komodo (GitOps)
This stack is deployed via Komodo on arm1-oci. Komodo syncs from the Forgejo repository and applies `compose.yaml` + `sidecar.yaml`. No `.env` file is needed — this stack has no secrets; all environment variables are non-sensitive defaults.

## Environment Variables
| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `NODE_ENV` | No | Node.js environment | `production` |
| `PORT` | No | HTTP listen port | `3000` |
| `HOST` | No | HTTP listen host | `0.0.0.0` |

## Access
- **URL**: `https://networking-toolbox.cianfhoghlaim.ie` (private, Pangolin Member role required)
- **Internal port**: 3000
- **Auth**: No built-in auth — protected by Pangolin/TinyAuth upstream

## Health Check
```bash
docker ps --filter name=networking-toolbox --format "table {{.Names}}\t{{.Status}}"
```

## Upstream
- **Repository**: https://github.com/lissy93/networking-toolbox
- **Documentation**: https://github.com/lissy93/networking-toolbox
- **Latest release**: Pulls `lissy93/networking-toolbox:latest` — a web-based network diagnostic toolkit.
