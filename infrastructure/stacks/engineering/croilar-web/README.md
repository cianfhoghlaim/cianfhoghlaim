# Croilar Web

## Overview
The Croilar Web stack serves the Croilar personal portfolio website — a Node.js web application built with Cloudflare integration. It uses a custom `ghcr.io/cianfhoghlaim/croilar-web:0.1.0` image running on port 3000 (mapped to host port 3003), with HMAC-based request signing and encryption for sensitive data.

## Why This Matters for Kings' College Galway
Croilar Web is the public-facing portfolio and CV site that demonstrates the full Cianfhoghlaim platform's capabilities in a personal context. It integrates with Cloudflare for edge deployment, GitHub for activity metrics, and streaming APIs (Spotify, SoundCloud, YouTube) for the "data-driven CV" feature — showing real-time professional and creative activity. While distinct from the Celtic education platform, it serves as both a personal website and a living reference implementation of the infrastructure patterns used across all Cianfhoghlaim services: Pangolin routing, Locket secret injection, Komodo GitOps deployment, and Infisical-backed configuration.

## Key Features
- Node.js web application with Cloudflare integration for edge deployment
- HMAC-based request signing for webhook verification
- Spotify, SoundCloud, and YouTube streaming data integration
- GitHub activity metrics for the data-driven CV feature
- Encryption-at-rest for sensitive personal data

## Deployment

### Docker Compose (Local Development)
```bash
cd infrastructure/stacks/engineering/croilar-web
docker compose up -d
```

### Docker Compose (Production with Locket Secret Injection)
```bash
cd infrastructure/stacks/engineering/croilar-web
docker compose -f compose.yaml -f sidecar.yaml -f pangolin.yaml up -d
```

### Komodo (GitOps)
This stack is deployed via Komodo on arm1-oci. Komodo syncs from the Forgejo repository and applies `compose.yaml` + `sidecar.yaml`. No `.env` file is needed — Locket resolves all secrets from the Infisical `dev-baile` vault at runtime.

## Environment Variables
| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `CROILAR_WEB_PORT` | No | Host port for the web server | `3003` |
| `NODE_ENV` | No | Node.js environment | `production` |
| `PORT` | No | HTTP listen port | `3000` |
| `CLOUDFLARE_ACCOUNT_ID` | No | Cloudflare account ID | — |
| `CLOUDFLARE_API_TOKEN` | No | Cloudflare API token | — |
| `GITHUB_TOKEN` | No | GitHub personal access token | — |
| `SPOTIFY_CLIENT_ID` | No | Spotify API client ID | — |
| `SOUNDCLOUD_CLIENT_ID` | No | SoundCloud API client ID | — |
| `YOUTUBE_API_KEY` | No | YouTube Data API key | — |
| `CROILAR_HMAC_SECRET` | No | HMAC secret for request signing | — |
| `CROILAR_ENCRYPTION_KEY` | No | Encryption key for sensitive data | — |

## Access
- **URL**: `https://web.croilar.cianfhoghlaim.ie` (private, Pangolin Member role required)
- **Internal port**: 3000 (mapped to host port 3003)
- **Auth**: HMAC-based request signing

## Health Check
```bash
docker ps --filter name=croilar-web --format "table {{.Names}}\t{{.Status}}"
```

## Upstream
- **Repository**: Internal — built as `ghcr.io/cianfhoghlaim/croilar-web:0.1.0`
- **Documentation**: Internal — part of the Croilar monorepo
- **Latest release**: Custom image `ghcr.io/cianfhoghlaim/croilar-web:0.1.0`.
