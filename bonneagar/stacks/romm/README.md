# RomM — ROM Manager and Game Library Organiser

## Overview

RomM (ROM Manager) is an open-source, self-hosted game ROM library manager. It scans, organises, and presents retro game ROMs in a clean web UI with cover art, metadata from IGDB (Internet Game Database), and platform-based organisation. Supports multiple platforms from Atari to PlayStation.

## Why This Matters for Kings' College Galway

The `tuatha/` MMO frontend and the BAML-driven image generation pipeline produce game-like educational experiences — interactive simulations, gamified learning modules, and Scratch-style creative coding environments. RomM provides a reference library of retro educational games whose design patterns, interaction models, and visual styles inform the gamification of curriculum content. Understanding how classic educational games structured their learning loops (Number Munchers, Oregon Trail, Where in the World is Carmen Sandiego?) directly feeds into the `tuatha/ui` Scratch-style environment design.

## Key Features

- **Multi-platform** — Organise ROMs from 100+ gaming platforms
- **IGDB metadata** — Automatic cover art, descriptions, ratings from IGDB
- **Web UI** — Clean, responsive library browser
- **Scan and organise** — Automatic detection and sorting of ROM files
- **Emulator integration** — Launch games directly in browser via EmulatorJS

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/romm
docker compose up -d
```

### Production (via Komodo)

Deployed via Komodo on arm1-oci. Requires IGDB API credentials for metadata fetching.

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `IGDB_CLIENT_ID` | No | IGDB API client ID | — |
| `IGDB_CLIENT_SECRET` | No | IGDB API client secret | — |
| `ROMM_PORT` | No | Web UI port | `8080` |
| `ROMM_AUTH_SECRET` | Yes | Session encryption secret | — |

## Access

- **Web UI**: `https://romm.cianfhoghlaim.ie` (private, Member role)
- **Auth**: Email/password + Pocket ID SSO

## Upstream

- **Repository**: <https://github.com/rommapp/romm>
- **Documentation**: <https://romm.app>
- **Latest**: v3.x (2025) — EmulatorJS integration, IGDB v4 API migration, multi-file ROM support, improved scanning

## Screenshot

RomM's web UI shows a Netflix-style grid of game covers organised by platform. Each game card shows the cover art, title, platform badge, and rating. The game detail view shows full metadata, screenshots, genre tags, and an "Open in EmulatorJS" button for in-browser play. The sidebar provides platform filtering and search.
