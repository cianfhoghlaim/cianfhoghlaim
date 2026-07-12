# Kapowarr — Comic and Manga Download Manager

## Overview

Kapowarr is an open-source, self-hosted comic and manga download manager. It automates the process of discovering, downloading, and organising digital comics, with support for multiple download sources, metadata management, and library organisation.

## Why This Matters for Kings' College Galway

The project's visual content strategy includes educational comics and graphic-novel-style study materials — particularly for subjects where visual narratives aid comprehension (history timelines, scientific processes, mathematical problem-solving sequences). Kapowarr provides the comic library management infrastructure for organising these educational graphic resources alongside traditional study materials. The metadata management ensures each resource is properly tagged by subject, level, and language, making them discoverable through the curriculum search system.

## Key Features

- **Automated downloads** — Monitor series and download new issues automatically
- **Metadata management** — Auto-tag and organise by series, publisher, genre
- **Library organisation** — Folder-based organisation with configurable naming
- **Multiple sources** — Configurable download source plugins
- **Web UI** — Browser-based library browser and download manager

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/Kapowarr
docker compose up -d
```

### Production (via Komodo)

Deployed via Komodo on arm1-oci.

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `PUID` | No | User ID for file permissions | `1000` |
| `PGID` | No | Group ID for file permissions | `1000` |
| `TZ` | No | Timezone | `Etc/UTC` |

## Access

- **Web UI**: `https://kapowarr.cianfhoghlaim.ie` (private, Member role)
- **Auth**: Built-in user management

## Upstream

- **Repository**: <https://github.com/Casvt/Kapowarr>
- **Latest**: Active development — download source improvements, metadata scanner enhancements, library organisation features

## Screenshot

Kapowarr's web UI shows a library grid with comic cover thumbnails, a series detail view with issue lists and download status, a search interface for finding new content, and a download queue showing active and queued downloads with progress bars.
