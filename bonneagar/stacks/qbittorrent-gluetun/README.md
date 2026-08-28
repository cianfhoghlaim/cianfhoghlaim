# qBittorrent + gluetun — VPN-egress torrent client

## Overview

qBittorrent is an open-source BitTorrent client. This stack runs it
**inside the `gluetun` VPN sidecar's network namespace** — every
peer connection, tracker announce, and DHT packet exits through a
WireGuard tunnel rather than the MacBook's real egress. The pattern
mirrors the canonical gluetun sidecar setup used by the *Arr stack
ecosystem.

This stack exists to give **Mylar3** (and Kapowarr) a torrent
download client that respects privacy and bypasses ISP throttling.

## Why This Matters for the Platform

The cianfhoghlaim platform has several bandwidth-intensive consumers
(`crawl4ai`, the `langfuse` telemetry pipeline, the `lakehouse` S3
gateway). Egressing torrents through the real MacBook IP would:

1. **Leak the user's home IP** to every peer swarm
2. **Mix torrent traffic** with platform telemetry in the same
   network namespace (privacy + ops hygiene)
3. **Likely trigger ISP throttling** of the MacBook's residential
   connection

Running qBittorrent inside gluetun's namespace isolates torrent
traffic in its own tunnel and gives it a clean exit IP.

## Why a separate gluetun stack?

The existing `stacks/gluetun/` is shared with `crawl4ai` (port 11235).
Adding qBittorrent as another consumer would require modifying that
stack's port mappings. Keeping a **private gluetun sidecar inside
this stack**:

- Keeps the existing gluetun stack untouched
- Lets qBittorrent pick its own WebUI port without colliding
- Allows independent health-check / restart of the VPN tunnel
- Matches the "one VPN container per consumer" pattern that the
  LinuxServer gluetun docs recommend

You can either share the same WireGuard key (single tunnel IP) or
use separate keys for isolation. The `secrets.env` references both
keys from Infisical — they can be the same value or different.

## Stack Composition

| Container                  | Image                                      | Purpose                        |
|:---------------------------|:-------------------------------------------|:-------------------------------|
| `gluetun`                  | `qmcgaw/gluetun:latest`                    | WireGuard VPN client           |
| `qbittorrent`              | `lscr.io/linuxserver/qbittorrent:latest`   | Torrent client (in gluetun NS) |
| `qbittorrent-gluetun-locket` | `ghcr.io/cianfhoghlaim/locket-shim:infisical-0.2.1` | Infisical → tmpfs secrets  |

## How the network namespace sharing works

```
┌─────────────────────────────────────────────────────────────┐
│  gluetun container                                          │
│    - holds /dev/net/tun                                     │
│    - holds NET_ADMIN cap                                    │
│    - establishes WireGuard tunnel                           │
│    - publishes 8080 → 8080 (host loopback only)             │
│                                                             │
│    ┌────────────────────────────────────────────────────┐   │
│    │  qbittorrent container                             │   │
│    │    network_mode: service:gluetun                   │   │
│    │    ─ shares gluetun's network namespace            │   │
│    │    ─ same IP, same ports, same egress              │   │
│    │    ─ torrent traffic exits via WireGuard           │   │
│    └────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

Because qBittorrent shares gluetun's network namespace:

- **All peer connections** → WireGuard tunnel
- **All tracker announces** → WireGuard tunnel
- **WebUI traffic** (8080) → gluetun:8080 → qBittorrent:8080

## Pairing with Mylar3 / Kapowarr

After both stacks are up:

1. **qBittorrent WebUI**: open `https://qbittorrent.cianfhoghlaim.ie`
   → Pocket ID SSO → login with `admin` + the WebUI password from
   Infisical (`dev-baile/qbittorrent-gluetun/webui_password`)
2. **Mylar3 WebUI**: open `https://mylar3.cianfhoghlaim.ie`
   → Settings → Download Clients → Add → qBittorrent:
   - Host: `qbittorrent-gluetun`
   - Port: `8080`
   - Username: `admin`
   - Password: from Infisical
3. **Kapowarr WebUI**: same config, same host (Kapowarr discovers via
   the shared `cianfhoghlaim` Docker network)
4. Mylar3 will now automatically push wanted comic issues to
   qBittorrent, monitor download progress, and post-process completed
   files into `${COMICS_PATH}` for Komga to consume.

## Deployment

### Docker Compose (Local — bunchloch MacBook)

```bash
cd infrastructure/stacks/qbittorrent-gluetun
cp .env.example .env.local
# edit .env.local — paste the WireGuard credentials from the existing
# gluetun stack's .env, or from Infisical
docker compose --env-file .env.local up -d
```

### Production (via Komodo on arm1-oci)

```bash
cd infrastructure/stacks/qbittorrent-gluetun
docker compose -f compose.yaml -f sidecar.yaml up -d
```

## Environment Variables

| Variable                       | Required | Description                            | Default       |
|:-------------------------------|:---------|:---------------------------------------|:--------------|
| `QBITTORRENT_WEBUI_PORT`       | No       | Host port for qBittorrent WebUI        | `8080`        |
| `DOWNLOADS_PATH`               | No       | Host path to download staging area     | `./downloads` |
| `COMICS_STAGING_PATH`          | No       | Sub-path where completed comics land   | `./downloads/comics` |
| `PUID` / `PGID`                | No       | File ownership                         | `1000` / `1000` |
| `TZ`                           | No       | Timezone                               | `Europe/Dublin` |
| `WIREGUARD_PRIVATE_KEY`        | Yes      | WireGuard private key                  | from Locket   |
| `WIREGUARD_PRESHARED_KEY`      | Yes      | WireGuard preshared key                | from Locket   |
| `WIREGUARD_ADDRESSES`          | Yes      | Tunnel IP (e.g. `10.x.x.x/32`)         | from Locket   |
| `WIREGUARD_PUBKEY`             | Yes      | VPN server public key                  | from Locket   |
| `WIREGUARD_ENDPOINT`           | Yes      | `host:port`                            | from Locket   |
| `VPN_PORT_FORWARDING`          | No       | `on` if provider supports port fwd     | `off`         |
| `VPN_PORT_FORWARDING_PROVIDER` | No       | Provider name for port forwarding API  | empty         |
| `WEBUI_USERNAME`               | No       | qBittorrent admin user                 | `admin`       |
| `WEBUI_PASSWORD`               | Yes      | qBittorrent admin password             | from Locket   |

## Access

- **WebUI**: `https://qbittorrent.cianfhoghlaim.ie` (private, Member role)
- **Local dev**: `http://localhost:8080` (binds to 127.0.0.1 only)
- **Auth**: Pocket ID passkey SSO via the Pangolin mesh, then
  qBittorrent's local admin login

## Health Check

```bash
docker ps --filter name=qbittorrent-gluetun
docker ps --filter name=qbittorrent
docker exec qbittorrent-gluetun curl -fsS http://localhost:9999/  # gluetun's own API
curl -fsS http://localhost:8080/api/v2/app/version
```

## Upstream

- **qBittorrent**: <https://github.com/qbittorrent/qBittorrent>
- **Docker image**: `lscr.io/linuxserver/qbittorrent`
- **gluetun**: <https://github.com/qmcgaw/gluetun>
- **License**: GPL-2.0 (both)

## Cross-references

- [`stacks/mylar3/`](../mylar3/) — primary consumer of this download client
- [`stacks/Kapowarr/`](../Kapowarr/) — secondary consumer
- [`stacks/gluetun/`](../gluetun/) — the original VPN stack (shared with crawl4ai)
- [`stacks/komga/`](../komga/) — consumes the comic library after Mylar3
  post-processes it
- [`stacks/crawl4ai/`](../crawl4ai/) — also egresses through the main
  gluetun stack (sister VPN consumer)
