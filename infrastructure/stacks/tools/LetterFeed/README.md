# LetterFeed — Self-Hosted RSS Reader

## Overview

LetterFeed is an open-source, self-hosted RSS feed reader with a clean, minimal web UI. It aggregates RSS/Atom feeds from multiple sources, provides full-text search across articles, and supports feed organisation with folders and tags. Built with a Go backend and a modern frontend.

## Why This Matters for Kings' College Galway

Educational policy, curriculum changes, and examination announcements from official sources (NCCA, SEC, Department of Education, Teaching Council) are published on websites with RSS feeds, but these are easy to miss without an aggregator. LetterFeed centralises all education-related feeds — Irish curriculum updates, UK Ofqual announcements, European EdTech news, research paper RSS feeds — into a single reading interface. This ensures the team never misses a curriculum reform announcement or a new research publication relevant to the platform's development.

## Key Features

- **RSS/Atom aggregation** — Subscribe to unlimited feeds from any source
- **Full-text search** — Search across all feed articles
- **Folder organisation** — Group feeds by category (curriculum, research, infrastructure)
- **Clean reading UI** — Distraction-free article reader
- **Go backend** — Lightweight, fast, single-binary server

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/tools/LetterFeed
docker compose up -d
```

### Production (via Komodo)

Deployed via Komodo on arm1-oci. Uses a local volume for data persistence.

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `LETTERFEED_PORT` | No | Frontend port | `3000` |

## Access

- **Web UI**: `https://letterfeed.cianfhoghlaim.ie` (private, Member role)
- **Auth**: Pocket ID SSO

## Upstream

- **Repository**: <https://github.com/leonmuscoden/letterfeed>
- **Latest**: Active development — full-text search, feed organisation, API improvements

## Screenshot

LetterFeed's web UI resembles a three-panel email client: a left sidebar with feed folders and subscription list, a middle panel showing article titles and snippets sorted by date, and a right reading panel displaying the full article content with embedded images and links.
