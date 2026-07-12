# Audiobookshelf — Self-Hosted Audiobook and Podcast Server

## Overview

Audiobookshelf is an open-source, self-hosted media server for audiobooks and podcasts. It provides a web UI and mobile apps (iOS/Android) for streaming, downloading, and managing audiobook and podcast libraries, with chapter navigation, playback speed control, sleep timer, and library management features.

## Why This Matters for Kings' College Galway

The project maintains a growing library of Irish-language audio resources: TG4 educational broadcasts, Raidió na Gaeltachta language-learning segments, Irish-medium lecture recordings, and text-to-speech outputs from the Chatterbox TTS model. Audiobookshelf provides a Netflix-like interface for browsing and streaming these resources. For a platform focused on bilingual education, having a self-hosted audio library where Irish-language content is first-class (rather than buried in a general-purpose media server) is essential for content discoverability and user engagement.

## Key Features

- **Audiobook + podcast support** — Single server for both formats
- **Mobile apps** — iOS and Android apps with offline download
- **Chapter navigation** — Skip to specific chapters or timestamps
- **Playback speed** — 0.5x to 3x with pitch correction
- **Multi-user** — Per-user progress tracking and libraries

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/audiobookshelf
docker compose up -d
```

### Production (via Komodo)

Deployed via Komodo on arm1-oci. Media files are stored in bind-mounted directories (`./audiobooks`, `./podcasts`).

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `AUDIOBOOKSHELF_PORT` | No | Web UI port | `13378` (internal: 80) |
| `CONFIG_PATH` | No | Config directory | `./config` |
| `METADATA_PATH` | No | Metadata directory | `./metadata` |

## Access

- **Web UI**: `https://audiobookshelf.cianfhoghlaim.ie` (private, Member role)
- **Mobile Apps**: Connect to server URL with user credentials
- **Auth**: Email/password (per-user accounts)

## Upstream

- **Repository**: <https://github.com/advplyr/audiobookshelf>
- **Documentation**: <https://audiobookshelf.org>
- **Latest**: v2.x (2025) — podcast download improvements, chapter editor, metadata scanner v2, iOS CarPlay support

## Screenshot

Audiobookshelf's web UI resembles a streaming service: a library grid with cover art, a now-playing bar at the bottom with playback controls, a chapter list sidebar, and an admin panel for library management. The audiobook detail view shows metadata (author, narrator, duration, series), chapter list, and listening progress.
