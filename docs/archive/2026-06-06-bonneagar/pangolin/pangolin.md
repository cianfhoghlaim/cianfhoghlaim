# Pangolin

Identity-aware VPN with WireGuard and Traefik integration for secure infrastructure access.

## Overview

Pangolin (from [Fossorial/Pangolin](https://github.com/fossorial/pangolin)) provides:

- **WireGuard VPN** - Fast, modern VPN tunnel
- **Traefik Proxy** - Reverse proxy with automatic TLS
- **Identity Awareness** - Authentication via OIDC/OAuth2
- **Zero Trust** - No direct exposure of internal services

## Architecture

```
Internet → Traefik (TLS) → Pangolin Gateway → WireGuard → Internal Services
                ↓
           Auth Provider (Authentik/Keycloak)
```

## Installation

```bash
# From bonneagar/pangolin directory
docker-compose up -d
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PANGOLIN_DOMAIN` | Public domain for VPN access | - |
| `WIREGUARD_PEERS` | Number of peer configs to generate | 5 |
| `AUTH_PROVIDER_URL` | OIDC provider endpoint | - |

### Docker Compose

```yaml
services:
  pangolin:
    image: fossor/pangolin:latest
    cap_add:
      - NET_ADMIN
      - SYS_MODULE
    sysctls:
      - net.ipv4.conf.all.src_valid_mark=1
    volumes:
      - ./config:/config
    ports:
      - 51820:51820/udp
```

## Client Setup

1. Generate client config: `./scripts/add-peer.sh <client-name>`
2. Import WireGuard config on client device
3. Enable VPN connection

## Integration with Traefik

Pangolin works with Traefik for routing authenticated requests:

```yaml
# traefik dynamic config
http:
  routers:
    internal-app:
      rule: "Host(`app.internal.cianfhoghlaim.dev`)"
      service: internal-app
      middlewares:
        - pangolin-auth
```

## Related

- [Komodo](./komodo) - Container orchestration
- [Locket](./locket) - Secret management
- [Infrastructure Overview](./overview)
