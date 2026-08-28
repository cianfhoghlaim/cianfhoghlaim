# Mylar3 — Comic Book Download Manager

## Overview

Mylar3 is an open-source, self-hosted comic book download manager. It
tracks series (via ComicVine / CV), searches indexers, downloads missing
issues via a downstream download client (qBittorrent, SABnzbd, NZBGet,
Deluge, rTorrent), post-processes them into CBR/CBZ, and organises them
in a folder-based library. First released 2014, it remains the deepest
ComicVine-metadata-driven downloader in the ecosystem.

## Why This Matters for the Platform

The cianfhoghlaim platform already has **Kapowarr** (`stacks/Kapowarr/`)
and **Komga** (`stacks/Komga/`) for the comic pipeline. This stack runs
**Mylar3 side-by-side with Kapowarr** so the operator can compare the
two approaches:

| Feature              | Kapowarr            | Mylar3                            |
|:---------------------|:--------------------|:----------------------------------|
| First release        | 2023                | 2014                              |
| UI framework         | React (modern)      | CherryPy + jQuery (functional)    |
| ComicVine metadata   | Yes                 | Yes (deeper, smarter matching)    |
| Indexer model        | Plugin-based        | Native Newznab + Torznab          |
| Auto-snatch          | Yes                 | Yes (more granular rules)         |
| Series refresh       | Scheduled           | Scheduled + on-demand             |
| Post-processing      | Built-in            | Built-in (more rule options)      |
| NAT / VPN friendly   | Yes                 | Yes                               |

Both write to the same `${COMICS_PATH}` so Komga reads from either — the
comparison is purely about the *fetching* layer.

## Stack Composition

| Container       | Image                              | Purpose                          |
|:----------------|:-----------------------------------|:---------------------------------|
| `mylar3`        | `lscr.io/linuxserver/mylar3:latest`| Web UI + scheduler + indexer     |
| `mylar3-locket` | `ghcr.io/cianfhoghlaim/locket-shim:infisical-0.2.1` | Infisical → tmpfs secrets  |

Mylar3 does **not** download by itself — it needs a downstream download
client. The current pairing is **qBittorrent via the existing gluetun
VPN** (`stacks/qbittorrent-gluetun/`). Configure qBittorrent as the
download client inside the Mylar3 WebUI:

- Host: `qbittorrent-gluetun`
- Port: `8080`
- Username: `admin`
- Password: from Infisical → `dev-baile/qbittorrent-gluetun/webui_password`

## Why This Matters for Kings' College Galway

Comic books in the Kings' College Galway context are most relevant to:

1. **Educational graphic novels** — historical timelines, scientific
   processes, mathematical problem-solving sequences where visual
   narrative aids comprehension.
2. **Reference comics** — biology (人体的構造), chemistry (周期表 infographics),
   computer science (algorithm visualisations) where the visual form
   is intrinsic to the pedagogy.
3. **Later: graphics analysis pipeline** — once the library accumulates,
   the `tuatha-media-intel` stack plus `sam3-server` / `dots-ocr` /
   `paddleocr` can run cover-art embedding, page-level OCR, and
   detection of recurring characters/objects across issues.

## Key Features

- **ComicVine metadata** — auto-tagging, series tracking, missing-issue
  detection
- **Multiple indexer support** — Newznab (usenet) + Torznab (torrent)
- **Download-client agnostic** — qBittorrent, SABnzbd, NZBGet, Deluge,
  rTorrent
- **Post-processing** — CBR/CBZ conversion, naming, optional folder
  rename (e.g. `$Series $Issue ($Year)`)
- **Web UI** — browser-based library + queue management at
  `mylar3.cianfhoghlaim.ie`

## Deployment

### Docker Compose (Local — bunchloch MacBook)

```bash
cd infrastructure/stacks/mylar3
cp .env.example .env.local
# edit .env.local — set COMICS_PATH / DOWNLOADS_PATH to your macOS paths
docker compose --env-file .env.local up -d
```

### Production (via Komodo on arm1-oci)

```bash
cd infrastructure/stacks/mylar3
docker compose -f compose.yaml -f sidecar.yaml up -d
```

Komodo syncs from the Forgejo repository and applies
`compose.yaml` + `sidecar.yaml` + `pangolin.yaml` + `blueprint.yaml`.
No `.env` file is needed — Locket resolves all secrets from the
`dev-baile` Infisical vault at runtime.

## Environment Variables

| Variable              | Required | Description                              | Default               |
|:----------------------|:---------|:-----------------------------------------|:----------------------|
| `MYLAR_PORT`          | No       | Host port (Pangolin routes 8090)         | `8090`                |
| `PUID`                | No       | User ID for file permissions             | `1000`                |
| `PGID`                | No       | Group ID for file permissions            | `1000`                |
| `TZ`                  | No       | Timezone                                 | `Europe/Dublin`       |
| `UMASK`               | No       | File creation mode                       | `022`                 |
| `COMICS_PATH`         | No       | Host path to the comics library          | `./comics`            |
| `DOWNLOADS_PATH`      | No       | Host path to the staging area            | `./downloads`         |
| `INFISICAL_URL`       | Yes      | Local Infisical API URL                  | `http://infisical-backend:8080` |
| `LOCKET_MODE`         | No       | `watch` (live reload) or `oneshot`       | `watch`               |
| `INFISICAL_FALLBACK_FILE` | No   | Offline fallback env file                | `/dev/null`           |
| `COMICVINE_API_KEY`   | No       | ComicVine metadata API key               | from Locket/Infisical |

## Access

- **Web UI**: `https://mylar3.cianfhoghlaim.ie` (private, Member role)
- **Auth**: Pocket ID passkey SSO via the Pangolin mesh
- **Local dev**: `http://localhost:8090` (binds to 127.0.0.1 only)

## Health Check

```bash
docker ps --filter name=mylar3 --format "table {{.Names}}\t{{.Status}}"
curl -fsS http://localhost:8090
curl -fsS https://mylar3.cianfhoghlaim.ie/api/v2/SearchCmds?cmd=showQueue
```

## Network Topology

```
            Internet
                │
                ▼
            Gerbil (WireGuard) ←──────────── Pangolin Core (arm1-oci)
                │
                ▼
            Newt (this MacBook, NEWT_ID 371v82ufn5puohn)
                │
                ▼
            mylar3 (port 8090) ──── Docker network `cianfhoghlaim` ──┐
                │                                                    │
                └── POST /api/v2 ──> qbittorrent-gluetun:8080 ◄─────┘
                                              │
                                              ▼
                                       gluetun VPN
                                              │
                                              ▼
                                          Internet
                                       (torrent swarms)
```

## Upstream

- **Repository**: <https://github.com/mylar3/mylar3>
- **Docker image**: `lscr.io/linuxserver/mylar3:latest`
- **License**: GPL-3.0
- **Status**: Active maintenance (slower cadence than Kapowarr, but
  steady)

## Cross-references

- [`stacks/Kapowarr/`](../Kapowarr/) — sister comic downloader (comparison
  partner)
- [`stacks/qbittorrent-gluetun/`](../qbittorrent-gluetun/) — the
  download client (qBittorrent running inside the existing gluetun VPN)
- [`stacks/komga/`](../komga/) — comic reader/server that consumes the
  library
- [`stacks/tuatha-media-intel/`](../tuatha-media-intel/) — later graphics
  analysis pipeline (cover art, OCR, object detection)
- [`stacks/gluetun/`](../gluetun/) — the VPN sidecar that hosts
  qBittorrent's network namespace
