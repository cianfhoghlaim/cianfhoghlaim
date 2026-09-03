# Aleyum Demo

Standalone demonstration of the Music Producer & Software Developer portfolio platform.

## Quick Start

```bash
cd sruth/aleyum
python demo/run_demo.py
```

## What This Demo Demonstrates

### 1. DLT Data Pipelines
- **Spotify**: REST API (artist, albums, tracks, audio features)
- **SoundCloud**: Crawl4AI scraper (profile, track metadata)
- **GitHub**: REST API (repositories, languages, commits)

### 2. DuckLake Storage
- **DuckDB**: Hot data (fast in-memory queries)
- **Parquet**: Warm data (columnar storage on disk)
- **R2**: Cold data (Cloudflare object storage)

### 3. Marimo Notebooks
- **music_analytics.py**: Audio feature distributions, platform comparison
- **github_insights.py**: Language breakdown, commit activity
- Reactive cells, interactive plots, WASM support

### 4. TanStack Start Web App
- **File-based routing**: /, /music, /code, /about
- **AudioCard component**: Track playback, analytics display
- **ProjectCard component**: Repository showcase
- Tailwind CSS 4 styling

### 5. Cloudflare R2
- Audio file storage (Spotify previews, SoundCloud tracks)
- Image storage (Album artwork, project screenshots)
- Public CDN delivery
- Custom domain: assets.aleyum.com

### 6. Artwork Embedding
- **CLIP ViT-B/32** for visual features
- Multi-modal embeddings (visual + metadata + audio)
- Similarity search for playlist generation

## Requirements

This demo uses mock data and requires minimal dependencies:

```bash
pip install httpx
```

For the full platform:

```bash
# Python dependencies
cd sruth/aleyum
uv pip install -e .

# Web dependencies
cd web
bun install
```

## Demo Structure

```
demo/
├── __init__.py
├── run_demo.py       # Main demo script
└── README.md         # This file

pipelines/
├── spotify/          # Spotify API pipeline
├── soundcloud/       # SoundCloud scraper
└── github/           # GitHub repos pipeline

notebooks/
├── music_analytics.py
└── github_insights.py

web/
└── src/
    ├── routes/
    │   ├── index.tsx
    │   ├── music.tsx
    │   ├── code.tsx
    │   └── about.tsx
    └── components/
        ├── music/AudioCard.tsx
        └── code/ProjectCard.tsx
```

## Running the Demo

The demo runs entirely offline with mock data.

```bash
# From the sruth/aleyum directory
python demo/run_demo.py
```

The demo will showcase:
- All 11 major features
- Mock data for Spotify, SoundCloud, GitHub
- Analytics dashboards
- Deployment configuration

## Full Platform Setup

To run the complete platform with real data:

### 1. Configure Secrets

```bash
cp .dlt/secrets.toml.example .dlt/secrets.toml
```

Edit `.dlt/secrets.toml` with your credentials:
```toml
[spotify]
client_id = "your-client-id"
client_secret = "your-client-secret"

[github]
access_token = "your-github-token"

[r2]
account_id = "your-account-id"
access_key_id = "your-access-key"
secret_access_key = "your-secret-key"
```

### 2. Run Data Pipelines

```bash
# Spotify data
python -m pipelines.spotify.source

# SoundCloud data
python -m pipelines.soundcloud.scraper

# GitHub repos
python -m pipelines.github.source
```

### 3. Explore with Marimo

```bash
marimo run notebooks/music_analytics.py
marimo run notebooks/github_insights.py
```

### 4. Start Web App

```bash
cd web
bun run dev
```

### 5. Build for Production

```bash
cd web
bun run build
```

### 6. Deploy

```bash
wrangler pages deploy .output/public
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      ALEYUM PORTFOLIO                         │
└─────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│ Data Sources│      │ DLT         │      │ DuckLake    │
│             │      │ Pipelines   │      │ Storage     │
│ • Spotify   │──────│ • spotify/  │──────│ • DuckDB    │
│ • SoundCl.  │      │ • soundcl/  │      │ • Parquet   │
│ • GitHub    │      │ • github/   │      │ • R2        │
└─────────────┘      └─────────────┘      └─────────────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│ Marimo      │      │ TanStack    │      │ Cloudflare  │
│ Notebooks   │      │ Start App   │      │ R2 + Pages  │
│             │      │             │      │             │
│ • Analytics │      │ • /         │      │ • Audio     │
│ • Viz       │      │ • /music    │      │ • Images    │
└─────────────┘      │ • /code     │      │ • CDN       │
                     └─────────────┘      └─────────────┘
```

## Data Sources

### Spotify
- **Artist ID**: 2vLlk2CcC4NnN7yoNSTmX2
- **API**: Web API (Client Credentials flow)
- **Data**: Artist profile, albums, tracks, audio features
- **Update**: Hourly via Dagster schedule

### SoundCloud
- **Profile**: soundcloud.com/aleyummusic
- **Scraper**: Crawl4AI (headless Chrome)
- **Data**: Profile stats, track metadata, play counts
- **Audio**: Downloaded to R2 for streaming

### GitHub
- **Username**: Yedya
- **API**: REST API v3
- **Data**: Repositories, languages, commits, READMEs
- **Update**: Daily via Dagster schedule

## Storage

### DuckLake Architecture

DuckLake = DuckDB + Parquet + Time Travel

**Storage Layers:**
1. **Hot Data**: DuckDB in-memory (sub-second queries)
2. **Warm Data**: Parquet files (columnar, compressed)
3. **Cold Data**: Cloudflare R2 (object storage)

**Benefits:**
- ACID transactions on object storage
- Time travel queries (point-in-time)
- Schema evolution without breaking changes
- Columnar pruning for fast analytics

**Storage Layout:**
```
storage/
├── aleyum.duckdb         # DuckDB database
└── music_data/
    ├── spotify_albums/   # Parquet files
    ├── spotify_tracks/
    └── audio_features/
```

## Web Application

### Routes

| Route | Page | Description |
|-------|------|-------------|
| `/` | Home | Landing page with navigation |
| `/music` | Music | Spotify + SoundCloud tracks |
| `/code` | Code | GitHub repositories |
| `/about` | About | Resume and contact info |

### Components

**AudioCard**
```tsx
<AudioCard
  track={{
    title: "Nebula",
    artist: "Aleyum",
    duration: 240000,
    platforms: {
      spotify: { url: "...", plays: 12500 },
      soundcloud: { url: "...", plays: 8900 }
    },
    audioFeatures: {
      tempo: 120.5,
      energy: 0.65,
      danceability: 0.58
    }
  }}
/>
```

**ProjectCard**
```tsx
<ProjectCard
  repo={{
    name: "mogadishu",
    description: "Celtic language education platform",
    stars: 45,
    language: "TypeScript"
  }}
/>
```

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
4. Set custom domain: `assets.aleyum.com`

### Environment Variables

```bash
# For data pipelines
SPOTIFY_CLIENT_ID=your-client-id
SPOTIFY_CLIENT_SECRET=your-client-secret
GITHUB_ACCESS_TOKEN=your-github-token
CLOUDFLARE_ACCOUNT_ID=your-account-id
R2_ACCESS_KEY_ID=your-access-key
R2_SECRET_ACCESS_KEY=your-secret-key

# For web app
VITE_SPOTIFY_CLIENT_ID=your-client-id
VITE_GITHUB_TOKEN=your-github-token
VITE_R2_PUBLIC_URL=https://assets.aleyum.com
```

## Technologies

| Category | Technologies |
|----------|--------------|
| **Data** | DLT, DuckDB, LanceDB, Ibis, Parquet |
| **Scraping** | Crawl4AI, BeautifulSoup, yt-dlp |
| **Cloud** | Cloudflare R2, Pages, Workers |
| **Web** | TanStack Start, React 19, Tailwind CSS 4 |
| **Analytics** | Marimo, Altair, Polars |
| **Utilities** | boto3, httpx, Pydantic |

## Analytics

The Marimo notebooks provide interactive analytics:

### Music Analytics
- Audio feature distributions (tempo, energy, danceability)
- Platform comparison (Spotify vs SoundCloud)
- Release timeline analysis
- Popular tracks identification

### GitHub Insights
- Language breakdown
- Commit activity over time
- Repository growth
- Contribution patterns

## Support

For issues or questions:
- Main README: [sruth/aleyum/README.md](../README.md)
- Spotify: https://open.spotify.com/artist/2vLlk2CcC4NnN7yoNSTmX2
- SoundCloud: https://soundcloud.com/aleyummusic
- GitHub: https://github.com/Yedya

## License

MIT
