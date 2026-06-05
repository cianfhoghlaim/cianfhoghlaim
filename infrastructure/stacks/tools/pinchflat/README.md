# Pinchflat — YouTube Channel Downloader and Media Manager

## Overview

Pinchflat is an open-source, self-hosted YouTube channel downloader and media manager. It monitors YouTube channels and playlists, automatically downloads new videos, extracts metadata (titles, descriptions, thumbnails), and organises them in a browsable library. Built on yt-dlp, it supports format selection, sponsorship skipping (SponsorBlock), and automatic retry on failure.

## Why This Matters for Kings' College Galway

Educational YouTube is a massive untapped content source: Irish-medium mathematics tutorials, NCCA curriculum explainers, recorded Leaving Cert grinds, academic lectures on Celtic languages, and educational documentaries in Irish and English. Pinchflat monitors channels from TG4, RTÉ, Irish-language educators, and academic institutions, automatically downloading new content and making it available offline. This is especially important for Irish-language content, which frequently disappears from YouTube due to copyright claims or channel closures — Pinchflat ensures a local archive that persists regardless of the original source's availability.

## Key Features

- **Channel monitoring** — Automatically download new videos from subscribed channels
- **yt-dlp powered** — Supports all YouTube formats, playlists, and metadata extraction
- **SponsorBlock integration** — Skip sponsored segments automatically
- **Format selection** — Choose video quality, audio-only, or custom formats
- **Web UI** — Browse, search, and play downloaded videos

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/tools/pinchflat
docker compose up -d
```

### Production (via Komodo)

Deployed via Komodo on arm1-oci. Downloaded videos are stored in a bind-mounted directory.

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `PINCHFLAT_PORT` | No | Web UI port | `8000` |
| `PINCHFLAT_DOWNLOAD_PATH` | No | Download directory | `/downloads` |
| `TZ` | No | Timezone | `Europe/Dublin` |

## Access

- **Web UI**: `https://pinchflat.cianfhoghlaim.ie` (private, Member role)
- **Auth**: Built-in user management

## Upstream

- **Repository**: <https://github.com/kieraneglin/pinchflat>
- **Latest**: Active development — SponsorBlock integration, download retry logic, web UI improvements

## Screenshot

Pinchflat's web UI shows a dashboard with subscribed channels (thumbnail, name, new video count), a video library with search and filter, and a download queue showing active and queued downloads with progress bars. Individual video views show metadata (title, description, duration, upload date) and playback controls.
