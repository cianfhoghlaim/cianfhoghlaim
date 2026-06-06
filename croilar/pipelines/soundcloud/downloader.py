"""SoundCloud Audio Downloader.

Downloads SoundCloud audio files to Cloudflare R2 for portfolio streaming.
Uses yt-dlp as a reliable backend for audio extraction.

Note: Only download audio you have rights to use. This is intended for
downloading your own published tracks for portfolio purposes.
"""

import hashlib
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

import dlt

from pipelines.shared.r2_client import R2Client


@dataclass
class DownloadedTrack:
    """Metadata for a downloaded track."""

    track_id: str
    title: str
    soundcloud_url: str
    r2_url: str
    r2_key: str
    file_size: int
    duration_ms: int
    format: str
    bitrate: int


def download_track(url: str, output_dir: Path) -> Path | None:
    """Download a single track using yt-dlp.

    Args:
        url: SoundCloud track URL
        output_dir: Directory to save the file

    Returns:
        Path to downloaded file or None if failed
    """
    import json
    import subprocess

    # Get track info first
    info_cmd = ["yt-dlp", "--dump-json", "--no-download", url]
    try:
        result = subprocess.run(info_cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            print(f"Failed to get info for {url}: {result.stderr}")
            return None

        info = json.loads(result.stdout)
        track_id = info.get("id", hashlib.md5(url.encode()).hexdigest()[:12])
        ext = info.get("ext", "mp3")
        output_file = output_dir / f"{track_id}.{ext}"

    except (subprocess.TimeoutExpired, json.JSONDecodeError) as e:
        print(f"Error getting track info: {e}")
        return None

    # Download the track
    download_cmd = [
        "yt-dlp",
        "-x",  # Extract audio
        "--audio-format", "mp3",
        "--audio-quality", "0",  # Best quality
        "-o", str(output_file.with_suffix(".%(ext)s")),
        url,
    ]

    try:
        result = subprocess.run(download_cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            print(f"Failed to download {url}: {result.stderr}")
            return None

        # Find the output file (extension might have changed)
        for f in output_dir.iterdir():
            if f.stem == track_id:
                return f

        return None

    except subprocess.TimeoutExpired:
        print(f"Download timed out for {url}")
        return None


def upload_to_r2(
    file_path: Path,
    track_id: str,
    r2_client: R2Client,
    prefix: str = "audio/soundcloud/",
) -> tuple[str, str]:
    """Upload audio file to R2.

    Args:
        file_path: Path to the audio file
        track_id: Track identifier
        r2_client: R2 client instance
        prefix: Key prefix in R2

    Returns:
        Tuple of (r2_url, r2_key)
    """
    key = f"{prefix}{track_id}{file_path.suffix}"

    # Determine content type
    content_type = "audio/mpeg"
    if file_path.suffix == ".ogg":
        content_type = "audio/ogg"
    elif file_path.suffix == ".wav":
        content_type = "audio/wav"
    elif file_path.suffix == ".flac":
        content_type = "audio/flac"

    with open(file_path, "rb") as f:
        r2_url = r2_client.upload_file(key, f, content_type=content_type)

    return r2_url, key


@dlt.resource(name="downloaded_tracks", write_disposition="merge", primary_key="track_id")
def download_tracks_to_r2(
    tracks: list[dict[str, Any]],
    r2_bucket: str = "aleyum-assets",
) -> Iterator[dict[str, Any]]:
    """Download SoundCloud tracks and upload to R2.

    Args:
        tracks: List of track dicts with 'id', 'title', 'permalink_url'
        r2_bucket: R2 bucket name

    Yields:
        Downloaded track metadata with R2 URLs
    """
    r2_client = R2Client()

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        for track in tracks:
            url = track.get("permalink_url", "")
            track_id = track.get("id", "")
            title = track.get("title", "")

            if not url or not track_id:
                continue

            print(f"Downloading: {title}")

            # Download the track
            downloaded_file = download_track(url, temp_path)
            if not downloaded_file:
                print(f"  Failed to download: {title}")
                continue

            # Get file info
            file_size = downloaded_file.stat().st_size

            # Upload to R2
            try:
                r2_url, r2_key = upload_to_r2(downloaded_file, track_id, r2_client)

                yield {
                    "track_id": track_id,
                    "title": title,
                    "soundcloud_url": url,
                    "r2_url": r2_url,
                    "r2_key": r2_key,
                    "file_size": file_size,
                    "duration_ms": track.get("duration_ms", 0),
                    "format": downloaded_file.suffix.lstrip("."),
                    "bitrate": 320,  # yt-dlp default best quality
                }

                print(f"  Uploaded to: {r2_key}")

            except Exception as e:
                print(f"  Failed to upload: {e}")

            finally:
                # Clean up downloaded file
                if downloaded_file.exists():
                    downloaded_file.unlink()


def run_download_pipeline(
    username: str = "aleyummusic",
    destination: str = "duckdb",
    dataset_name: str = "soundcloud_data",
    limit: int = 20,
) -> Any:
    """Run the download pipeline for SoundCloud tracks.

    First scrapes track metadata, then downloads audio to R2.

    Args:
        username: SoundCloud username
        destination: DLT destination
        dataset_name: Dataset name
        limit: Maximum tracks to download

    Returns:
        LoadInfo from the pipeline run
    """
    import asyncio

    from pipelines.soundcloud.scraper import SoundCloudScraper

    # First, scrape track metadata
    print(f"Scraping tracks from {username}...")
    scraper = SoundCloudScraper()
    try:
        tracks = asyncio.run(scraper.scrape_tracks(username, limit=limit))
    finally:
        asyncio.run(scraper.close())

    # Convert to dicts
    track_dicts = [
        {
            "id": t.id,
            "title": t.title,
            "permalink_url": t.permalink_url,
            "duration_ms": t.duration_ms,
        }
        for t in tracks
        if t.permalink_url
    ]

    print(f"Found {len(track_dicts)} tracks, starting downloads...")

    # Run download pipeline
    pipeline = dlt.pipeline(
        pipeline_name=f"soundcloud_downloads_{username}",
        destination=destination,
        dataset_name=dataset_name,
        progress="log",
    )

    download_resource = download_tracks_to_r2(tracks=track_dicts)
    load_info = pipeline.run(download_resource)

    print(load_info)
    return load_info


if __name__ == "__main__":
    # Example: Download your own tracks
    load_info = run_download_pipeline(
        username="aleyummusic",
        limit=10,  # Start with a small batch
    )
