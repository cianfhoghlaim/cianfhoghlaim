---
title: 'Aleyum Portfolio'
domain: 'architecture'
status: 'stable'
description: 'Music Producer & Software Developer portfolio project combining data engineering with modern web technologies.'
read_when:
  - looking for documentation on this topic
updated: '2026-06-10'
supersedes:
  - docs/ALEYUM_PORTFOLIO.md
ccc_query_hints:
  - aleyum portfolio
truth: partial

---

# Aleyum Portfolio

Music Producer & Software Developer portfolio project combining data engineering with modern web technologies.

## Overview

This project demonstrates a **balanced showcase** of:
- **Data Engineering**: DLT pipelines, DuckLake lakehouse, Marimo notebooks
- **Full-Stack Web**: TanStack Start, React, Tailwind CSS
- **Cloud Infrastructure**: Cloudflare Pages + R2 for assets and streaming

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ALEYUM PORTFOLIO                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Data Sources                                               │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐    │
│  │   Spotify    │   │  SoundCloud  │   │    GitHub    │    │
│  │   (REST API) │   │   (Scraper)  │   │  (REST API)  │    │
│  └──────┬───────┘   └──────┬───────┘   └──────┬───────┘    │
│         │                  │                  │             │
│         └──────────────────┼──────────────────┘             │
│                            │                                │
│  DLT Pipelines             │                                │
│  ┌─────────────────────────┴────────────────────────────┐  │
│  │  pipelines/spotify/  pipelines/soundcloud/  github/  │  │
│  └─────────────────────────┬────────────────────────────┘  │
│                            │                                │
│  Storage Layer             │                                │
│  ┌──────────────┐   ┌──────┴───────┐   ┌──────────────┐   │
│  │   DuckDB     │   │     R2       │   │   LanceDB    │   │
│  │  (Analytics) │   │   (Assets)   │   │  (Vectors)   │   │
│  └──────┬───────┘   └──────────────┘   └──────────────┘   │
│         │                                                   │
│  Analytics                                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Marimo Notebooks (music_analytics, github_insights)│   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Web Application                                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  TanStack Start + React + Tailwind                   │   │
│  │  Routes: / | /music | /code | /about                 │   │
│  │  Components: AudioCard, ProjectCard                  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Deployment: Cloudflare Pages + R2                         │
└─────────────────────────────────────────────────────────────┘
```

## Project Structure

```
aleyum/
├── pipelines/                    # Data pipelines
│   ├── spotify/                  # Spotify API pipeline
│   │   ├── source.py            # DLT source definition
│   │   └── resources.py         # API endpoint configs
│   ├── soundcloud/              # SoundCloud scraper
│   │   ├── scraper.py           # Crawl4AI scraper
│   │   └── downloader.py        # Audio downloader to R2
│   ├── github/                  # GitHub repos pipeline
│   │   └── source.py            # DLT source for repos
│   └── shared/                  # Shared utilities
│       ├── r2_client.py         # Cloudflare R2 client
│       └── destinations.py      # DLT destinations
├── notebooks/                   # Marimo analytics notebooks
│   ├── music_analytics.py       # Music data exploration
│   └── github_insights.py       # GitHub project insights
├── web/                         # TanStack Start application
│   ├── src/
│   │   ├── routes/              # File-based routing
│   │   │   ├── __root.tsx       # Root layout
│   │   │   ├── index.tsx        # Home page
│   │   │   ├── music.tsx        # Music portfolio
│   │   │   ├── code.tsx         # Code projects
│   │   │   └── about.tsx        # About/Resume
│   │   └── components/
│   │       ├── music/
│   │       │   └── AudioCard.tsx # Track card with analytics
│   │       └── code/
│   │           └── ProjectCard.tsx # Repository card
│   └── package.json
├── config/
│   └── sources.yaml             # Data source configuration
├── api/
│   ├── fixed-spotify-open-api.yml  # Spotify OpenAPI spec
│   └── soundcloud.json          # SoundCloud API spec
├── .dlt/
│   ├── config.toml              # DLT configuration
│   └── secrets.toml.example     # Secrets template
└── pyproject.toml               # Python dependencies
```

## Quick Start

### 1. Install Dependencies

```bash
# Python dependencies
uv pip install -e .

# Web dependencies
cd web && bun install
```

### 2. Configure Secrets

```bash
# Copy and edit secrets
cp .dlt/secrets.toml.example .dlt/secrets.toml

# Required environment variables:
# - SPOTIFY_ACCESS_TOKEN
# - GITHUB_ACCESS_TOKEN
# - CLOUDFLARE_ACCOUNT_ID
# - R2_ACCESS_KEY_ID
# - R2_SECRET_ACCESS_KEY
```

### 3. Run Data Pipelines

```bash
# Spotify data
python -m pipelines.spotify.source

# SoundCloud data (requires Crawl4AI)
python -m pipelines.soundcloud.scraper

# GitHub repos
python -m pipelines.github.source
```

### 4. Explore with Marimo

```bash
marimo run notebooks/music_analytics.py
marimo run notebooks/github_insights.py
```

### 5. Start Web App

```bash
cd web
bun run dev
```

## Key Features

### Data Pipelines

- **Spotify Pipeline**: Extracts artist, albums, tracks, and audio features (tempo, energy, danceability)
- **SoundCloud Scraper**: Crawl4AI-based scraper for profile data, downloads audio to R2
- **GitHub Pipeline**: Repository metadata, languages, READMEs, and recent commits

### MCP-UI AudioCard

Full analytics display including:
- Play counts, likes, comments, reposts
- Audio features visualization (tempo, energy, valence)
- Platform-specific badges (Spotify/SoundCloud)
- Embedded player support

### Marimo Notebooks

Interactive analytics notebooks for:
- Audio feature distribution
- Platform comparison (Spotify vs SoundCloud)
- GitHub language breakdown
- Commit activity visualization

## Deployment

### Cloudflare Pages

```bash
# Build static site
cd web && bun run build

# Deploy via Wrangler
wrangler pages deploy .output/public
```

### R2 Configuration

1. Create R2 bucket: `aleyum-assets`
2. Enable public access for streaming
3. Configure CORS for audio playback

## Technologies

| Category | Technologies |
|----------|--------------|
| **Data** | DLT, DuckDB, LanceDB, Ibis, Parquet |
| **Scraping** | Crawl4AI, BeautifulSoup, yt-dlp |
| **Cloud** | Cloudflare R2, Pages, Workers |
| **Web** | TanStack Start, React 19, Tailwind CSS 4 |
| **Analytics** | Marimo, Altair, Polars |
| **Utilities** | boto3, httpx, Pydantic |

## Data Sources

- **Spotify**: Artist ID `2vLlk2CcC4NnN7yoNSTmX2`
- **SoundCloud**: `soundcloud.com/aleyummusic`
- **GitHub**: `github.com/Yedya`

## License

MIT
