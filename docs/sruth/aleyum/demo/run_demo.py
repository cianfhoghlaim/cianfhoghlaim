#!/usr/bin/env python3
"""
Aleyum - Portfolio/Portal Demo.

Demonstrates the complete flow:
1. DLT data pipelines (Spotify, SoundCloud, GitHub)
2. DuckLake lakehouse storage (DuckDB + Parquet)
3. Marimo notebooks for analytics
4. TanStack Start web application
5. Cloudflare R2 asset storage
6. Artwork embedding and semantic search

Usage:
    cd sruth/aleyum
    python demo/run_demo.py
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path

# This demo uses mock data and requires no external dependencies
# All demonstrations are offline with pre-populated example data


# ============================================================================
# MOCK DATA FOR OFFLINE DEMO
# ============================================================================

MOCK_SPOTIFY_DATA = {
    "artist": {
        "id": "2vLlk2CcC4NnN7yoNSTmX2",
        "name": "Aleyum",
        "followers": 1520,
        "genres": ["Electronic", "Ambient", "Chill"],
        "popularity": 45,
    },
    "albums": [
        {
            "id": "album1",
            "name": "Ethereal Dreams",
            "release_date": "2023-06-15",
            "total_tracks": 8,
            "tracks": [
                {"name": "Opening", "duration_ms": 180000, "track_number": 1},
                {"name": "Nebula", "duration_ms": 240000, "track_number": 2},
                {"name": "Voyage", "duration_ms": 210000, "track_number": 3},
            ],
        },
        {
            "id": "album2",
            "name": "Midnight Sessions",
            "release_date": "2024-01-20",
            "total_tracks": 6,
            "tracks": [
                {"name": "City Lights", "duration_ms": 195000, "track_number": 1},
                {"name": "After Hours", "duration_ms": 225000, "track_number": 2},
            ],
        },
    ],
    "audio_features": {
        "tempo": 120.5,
        "energy": 0.65,
        "danceability": 0.58,
        "valence": 0.72,
        "acousticness": 0.45,
        "instrumentalness": 0.82,
    },
}

MOCK_SOUNDCLOUD_DATA = {
    "profile": {
        "username": "aleyummusic",
        "followers": 850,
        "track_count": 12,
        "likes": 2400,
    },
    "tracks": [
        {
            "title": "Sunset Vibes",
            "plays": 12500,
            "likes": 320,
            "comments": 45,
            "duration": 245000,
        },
        {
            "title": "Ocean Waves",
            "plays": 8900,
            "likes": 210,
            "comments": 28,
            "duration": 198000,
        },
    ],
}

MOCK_GITHUB_DATA = {
    "repositories": [
        {
            "name": "mogadishu",
            "description": "Cianfhoghlaim - Celtic language education platform",
            "stars": 45,
            "forks": 8,
            "language": "TypeScript",
            "updated_at": "2024-01-10",
        },
        {
            "name": "sruth",
            "description": "Data pipelines for curriculum processing",
            "stars": 23,
            "forks": 3,
            "language": "Python",
            "updated_at": "2024-01-08",
        },
    ],
}

MOCK_ANALYTICS = {
    "music": {
        "total_tracks": 18,
        "total_duration_ms": 3_600_000,
        "avg_tempo": 118.5,
        "most_popular": "Nebula",
        "platforms": {"spotify": 14, "soundcloud": 12},
    },
    "code": {
        "total_repos": 15,
        "total_stars": 156,
        "top_language": "TypeScript",
        "total_commits": 342,
    },
}


# ============================================================================
# DEMO FUNCTIONS
# ============================================================================

async def demo_dlt_pipelines():
    """Demonstrate DLT data pipelines."""
    print("\n" + "=" * 80)
    print("1. DLT PIPELINES DEMO")
    print("=" * 80)

    print("\n--- Available Pipelines ---")
    pipelines = [
        ("Spotify", "REST API", "Artist, albums, tracks, audio features"),
        ("SoundCloud", "Crawl4AI Scraper", "Profile data, track metadata"),
        ("GitHub", "REST API", "Repositories, languages, commits"),
    ]

    print(f"{'Pipeline':<15} {'Source Type':<15} {'Data Extracted'}")
    print("-" * 80)
    for name, source_type, data in pipelines:
        print(f"{name:<15} {source_type:<15} {data}")

    print("\n--- Spotify Pipeline Configuration ---")
    print("""
# DLT Pipeline: Spotify Data Extraction
import dlt
from pipelines.spotify import spotify_source

pipeline = dlt.pipeline(
    pipeline_name="spotify_aleyum",
    destination="duckdb",
    dataset_name="music_data",
)

# Extract artist data
source = spotify_source(
    artist_id="2vLlk2CcC4NnN7yoNSTmX2",
    include_albums=True,
    include_tracks=True,
    include_audio_features=True,
)

info = pipeline.run(source)
print(f"Loaded {info.loads_count} resources")
    """)

    print("\n--- SoundCloud Scraper ---")
    print("""
# Crawl4AI-based SoundCloud Scraper
from pipelines.soundcloud import soundcloud_scraper

scraper = soundcloud_scraper(profile_url="soundcloud.com/aleyummusic")
tracks = await scraper.scrape()

# Download audio to R2
for track in tracks:
    await download_to_r2(track.audio_url, track.title)
    """)


async def demo_spotify_data():
    """Demonstrate Spotify data extraction."""
    print("\n" + "=" * 80)
    print("2. SPOTIFY DATA DEMO")
    print("=" * 80)

    data = MOCK_SPOTIFY_DATA

    print("\n--- Artist Profile ---")
    artist = data["artist"]
    print(f"  Name: {artist['name']}")
    print(f"  ID: {artist['id']}")
    print(f"  Followers: {artist['followers']:,}")
    print(f"  Genres: {', '.join(artist['genres'])}")
    print(f"  Popularity: {artist['popularity']}/100")

    print("\n--- Albums ---")
    for album in data["albums"]:
        print(f"\n  {album['name']}")
        print(f"    Released: {album['release_date']}")
        print(f"    Tracks: {album['total_tracks']}")
        print(f"    Sample Tracks:")
        for track in album["tracks"][:2]:
            print(f"      {track['track_number']}. {track['name']} ({track['duration_ms']//1000}s)")

    print("\n--- Audio Features (Averages) ---")
    features = data["audio_features"]
    print(f"  Tempo: {features['tempo']:.1f} BPM")
    print(f"  Energy: {features['energy']:.2f}")
    print(f"  Danceability: {features['danceability']:.2f}")
    print(f"  Valence: {features['valence']:.2f}")
    print(f"  Acousticness: {features['acousticness']:.2f}")


async def demo_soundcloud_data():
    """Demonstrate SoundCloud data extraction."""
    print("\n" + "=" * 80)
    print("3. SOUNDCLOUD DATA DEMO")
    print("=" * 80)

    data = MOCK_SOUNDCLOUD_DATA

    print("\n--- Profile Stats ---")
    profile = data["profile"]
    print(f"  Username: {profile['username']}")
    print(f"  Followers: {profile['followers']:,}")
    print(f"  Tracks: {profile['track_count']}")
    print(f"  Total Likes: {profile['likes']:,}")

    print("\n--- Top Tracks ---")
    for track in data["tracks"]:
        mins, secs = divmod(track["duration"] // 1000, 60)
        print(f"\n  {track['title']}")
        print(f"    Plays: {track['plays']:,}")
        print(f"    Likes: {track['likes']:,}")
        print(f"    Comments: {track['comments']:,}")
        print(f"    Duration: {mins}:{secs:02d}")


async def demo_github_data():
    """Demonstrate GitHub data extraction."""
    print("\n" + "=" * 80)
    print("4. GITHUB DATA DEMO")
    print("=" * 80)

    data = MOCK_GITHUB_DATA

    print("\n--- Repositories ---")
    for repo in data["repositories"]:
        print(f"\n  {repo['name']}")
        print(f"    Description: {repo['description']}")
        print(f"    Language: {repo['language']}")
        print(f"    Stars: {repo['stars']}")
        print(f"    Forks: {repo['forks']}")
        print(f"    Updated: {repo['updated_at']}")

    print("\n--- Pipeline Configuration ---")
    print("""
# DLT Pipeline: GitHub Repositories
from pipelines.github import github_source

pipeline = dlt.pipeline(
    pipeline_name="github_aleyum",
    destination="duckdb",
    dataset_name="code_data",
)

source = github_source(
    username="Yedya",
    include_repos=True,
    include_languages=True,
    include_commits=True,
)

info = pipeline.run(source)
    """)


async def demo_ducklake_storage():
    """Demonstrate DuckLake lakehouse."""
    print("\n" + "=" * 80)
    print("5. DUCKLAKE LAKEHOUSE DEMO")
    print("=" * 80)

    print("\n--- DuckLake Architecture ---")
    print("""
DuckLake = DuckDB + Parquet + Iceberg-style Time Travel

Storage Layers:
  1. Hot Data: DuckDB in-memory (fast queries)
  2. Warm Data: Parquet files on disk (columnar storage)
  3. Cold Data: Cloudflare R2 (object storage)

Benefits:
  - ACID transactions on object storage
  - Time travel queries (point-in-time)
  - Schema evolution without breaking changes
  - Columnar pruning for fast analytics
    """)

    print("\n--- Storage Layout ---")
    storage_layout = {
        "music_data": {
            "spotify_albums": "Parquet",
            "spotify_tracks": "Parquet",
            "soundcloud_tracks": "Parquet",
            "audio_features": "Parquet",
        },
        "code_data": {
            "github_repos": "Parquet",
            "github_commits": "Parquet",
            "languages": "Parquet",
        },
    }

    print("\nDataset Structure:")
    for dataset, tables in storage_layout.items():
        print(f"\n  {dataset}/")
        for table, format_type in tables.items():
            print(f"    {table}/  (Parquet)")

    print("\n--- Query Example ---")
    print("""
# DuckDB query on Parquet data
import duckdb

conn = duckdb.connect("storage/aleyum.duckdb")

# Query Parquet files directly
result = conn.execute("""
    SELECT
        album_name,
        AVG(tempo) as avg_tempo,
        AVG(energy) as avg_energy
    FROM read_parquet('storage/music_data/spotify_tracks/*.parquet')
    GROUP BY album_name
""").fetchall()
    """)


async def demo_marimo_notebooks():
    """Demonstrate Marimo analytics notebooks."""
    print("\n" + "=" * 80)
    print("6. MARIMO NOTEBOOKS DEMO")
    print("=" * 80)

    print("\n--- Available Notebooks ---")
    notebooks = [
        ("music_analytics.py", "Audio feature distribution, platform comparison"),
        ("github_insights.py", "Language breakdown, commit activity"),
    ]

    for notebook, description in notebooks:
        print(f"  - {notebook}")
        print(f"    {description}")

    print("\n--- Sample Analysis ---")
    analytics = MOCK_ANALYTICS["music"]
    print(f"\nMusic Analytics:")
    print(f"  Total Tracks: {analytics['total_tracks']}")
    print(f"  Total Duration: {analytics['total_duration_ms'] // 60000} minutes")
    print(f"  Avg Tempo: {analytics['avg_tempo']:.1f} BPM")
    print(f"  Most Popular: {analytics['most_popular']}")
    print(f"  Platform Distribution:")
    for platform, count in analytics["platforms"].items():
        print(f"    {platform.capitalize()}: {count} tracks")

    print("\n--- Interactive Features ---")
    print("""
Marimo notebooks provide:
  - Reactive cells (auto-update on data changes)
  - Interactive plots (Altair, Plotly)
  - SQL editor with DuckDB backend
  - Export as Python script or HTML
  - WASM support (run in browser)
    """)


async def demo_tanstack_app():
    """Demonstrate TanStack Start web application."""
    print("\n" + "=" * 80)
    print("7. TANSTACK START WEB APP DEMO")
    print("=" * 80)

    print("\n--- Application Structure ---")
    print("""
web/
├── src/
│   ├── routes/           # File-based routing
│   │   ├── __root.tsx    # Root layout
│   │   ├── index.tsx     # Home page
│   │   ├── music.tsx     # Music portfolio
│   │   ├── code.tsx      # Code projects
│   │   └── about.tsx     # About/Resume
│   └── components/
│       ├── music/AudioCard.tsx
│       └── code/ProjectCard.tsx
    """)

    print("\n--- Routes Overview ---")
    routes = [
        ("/", "Home", "Landing page with navigation"),
        ("/music", "Music Portfolio", "Spotify + SoundCloud tracks"),
        ("/code", "Code Projects", "GitHub repositories"),
        ("/about", "About", "Resume and contact info"),
    ]

    print(f"{'Route':<15} {'Page':<20} {'Description'}")
    print("-" * 80)
    for route, page, description in routes:
        print(f"{route:<15} {page:<20} {description}")

    print("\n--- AudioCard Component ---")
    print("""
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
    """)


async def demo_cloudflare_r2():
    """Demonstrate Cloudflare R2 integration."""
    print("\n" + "=" * 80)
    print("8. CLOUDFLARE R2 STORAGE DEMO")
    print("=" * 80)

    print("\n--- R2 Bucket Configuration ---")
    print("""
Bucket: aleyum-assets

Purpose:
  - Audio file storage (Spotify previews, SoundCloud tracks)
  - Image storage (Album artwork, project screenshots)
  - Static asset hosting (Direct CDN delivery)

Public Access:
  - Enabled for audio streaming
  - CORS configured for playback
  - Custom domain: assets.aleyum.com
    """)

    print("\n--- Storage Stats ---")
    storage_stats = {
        "total_files": 45,
        "audio_files": 18,
        "image_files": 27,
        "total_size_mb": 250,
    }

    print(f"  Total Files: {storage_stats['total_files']}")
    print(f"  Audio Files: {storage_stats['audio_files']}")
    print(f"  Image Files: {storage_stats['image_files']}")
    print(f"  Total Size: {storage_stats['total_size_mb']} MB")

    print("\n--- Upload Example ---")
    print("""
from pipelines.shared import R2Client

r2 = R2Client(
    account_id="CLOUDFLARE_ACCOUNT_ID",
    access_key_id="R2_ACCESS_KEY_ID",
    secret_access_key="R2_SECRET_ACCESS_KEY",
    bucket_name="aleyum-assets",
)

# Upload audio file
url = r2.upload(
    file_path="audio/nebula.mp3",
    key="tracks/nebula.mp3",
    content_type="audio/mpeg",
)

print(f"Public URL: {url}")
# Output: https://assets.aleyum.com/tracks/nebula.mp3
    """)


async def demo_artwork_embedding():
    """Demonstrate artwork embedding and semantic search."""
    print("\n" + "=" * 80)
    print("9. ARTWORK EMBEDDING DEMO")
    print("=" * 80)

    print("\n--- Multi-Modal Embeddings ---")
    print("""
Artwork embeddings combine:
  1. Visual features (CLIP ViT-B/32)
  2. Metadata (title, artist, genre)
  3. Audio features (tempo, energy, mood)

Use Cases:
  - Visual similarity search
  - Playlist generation by mood
  - Album art recommendations
    """)

    print("\n--- Similarity Search Example ---")
    print("""
Query: "Find albums with similar blue, dreamy artwork"

Results:
  1. Ethereal Dreams (Aleyum)      [similarity: 0.91]
     - Dominant colors: #4A90E2, #50E3C2
     - Mood: ethereal, ambient

  2. Midnight Sessions (Aleyum)     [similarity: 0.87]
     - Dominant colors: #2C3E50, #3498DB
     - Mood: chill, late-night

  3. Ocean Waves (SoundCloud)       [similarity: 0.84]
     - Dominant colors: #1ABC9C, #16A085
     - Mood: calm, aquatic
    """)


async def demo_analytics_dashboard():
    """Demonstrate analytics dashboard."""
    print("\n" + "=" * 80)
    print("10. ANALYTICS DASHBOARD DEMO")
    print("=" * 80)

    print("\n--- Key Metrics ---")
    print("\nMusic Metrics:")
    music = MOCK_ANALYTICS["music"]
    print(f"  Total Tracks: {music['total_tracks']}")
    print(f"  Total Duration: {music['total_duration_ms'] // 60000} minutes")
    print(f"  Average Tempo: {music['avg_tempo']:.1f} BPM")
    print(f"  Most Popular Track: {music['most_popular']}")

    print("\nCode Metrics:")
    code = MOCK_ANALYTICS["code"]
    print(f"  Total Repositories: {code['total_repos']}")
    print(f"  Total Stars: {code['total_stars']}")
    print(f"  Top Language: {code['top_language']}")
    print(f"  Total Commits: {code['total_commits']}")

    print("\n--- Platform Comparison ---")
    print("""
Spotify vs SoundCloud:

  Spotify:
    - Pros: High-quality audio (320kbps), API access
    - Cons: Limited free tier, geo-restrictions
    - Reach: 184 markets

  SoundCloud:
    - Pros: Artist-friendly, direct fan engagement
    - Cons: Lower audio quality (128kbps), no official API
    - Reach: Global (web-based)
    """)

    print("\n--- Audience Insights ---")
    print("""
Top Listening Regions:
  1. Ireland (Dublin, Cork)
  2. United Kingdom (London, Manchester)
  3. United States (New York, San Francisco)
  4. Germany (Berlin, Munich)

Peak Listening Times:
  - Weekdays: 18:00 - 22:00 (after work)
  - Weekends: 10:00 - 14:00 (morning chill)
    """)


async def demo_deployment():
    """Show deployment configuration."""
    print("\n" + "=" * 80)
    print("11. DEPLOYMENT DEMO")
    print("=" * 80)

    print("\n--- Cloudflare Pages Configuration ---")
    print("""
Build Command: bun run build
Output Directory: .output/public

Environment Variables:
  - VITE_SPOTIFY_CLIENT_ID
  - VITE_GITHUB_TOKEN
  - VITE_R2_PUBLIC_URL

Custom Domain: aleyum.com
    """)

    print("\n--- Deployment Workflow ---")
    print("""
1. Build TanStack Start app:
   bun run build

2. Deploy to Cloudflare Pages:
   wrangler pages deploy .output/public

3. Configure R2 custom domain:
   assets.aleyum.com -> aleyum-assets.r2.dev

4. Set up DNS records:
   aleyum.com -> CNAME cloudflare.pages.dev
   assets.aleyum.com -> CNAME aleyum-assets.r2.dev
    """)

    print("\n--- CI/CD Pipeline ---")
    print("""
# .github/workflows/deploy.yml
on: push
  branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: bun install
      - run: bun run build
      - uses: cloudflare/pages-action@v1
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
    """)


async def main():
    """Run all demos."""
    print("\n" + "=" * 80)
    print("ALEYUM - PORTFOLIO/PORTAL")
    print("Music Producer & Software Developer Portfolio")
    print("=" * 80)
    print(f"Started: {datetime.now().isoformat()}")
    print(f"Demo Mode: Offline (using mock data)")

    try:
        await demo_dlt_pipelines()
        await demo_spotify_data()
        await demo_soundcloud_data()
        await demo_github_data()
        await demo_ducklake_storage()
        await demo_marimo_notebooks()
        await demo_tanstack_app()
        await demo_cloudflare_r2()
        await demo_artwork_embedding()
        await demo_analytics_dashboard()
        await demo_deployment()

        print("\n" + "=" * 80)
        print("DEMO COMPLETE")
        print("=" * 80)

        print("\n--- Next Steps ---")
        print("\nTo install dependencies:")
        print("  cd sruth/aleyum")
        print("  uv pip install -e .")
        print("  cd web && bun install")
        print("\nTo run data pipelines:")
        print("  python -m pipelines.spotify.source")
        print("  python -m pipelines.soundcloud.scraper")
        print("  python -m pipelines.github.source")
        print("\nTo explore with Marimo:")
        print("  marimo run notebooks/music_analytics.py")
        print("  marimo run notebooks/github_insights.py")
        print("\nTo start web app:")
        print("  cd web")
        print("  bun run dev")
        print("\nTo build for production:")
        print("  bun run build")
        print("\nTo deploy:")
        print("  wrangler pages deploy .output/public")

    except Exception as e:
        print(f"\n[!] Demo error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
