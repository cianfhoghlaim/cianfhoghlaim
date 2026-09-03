"""YouTube Video DLT Source.

Ingests curated YouTube channels / playlists via yt-dlp + emits one row
per video into the DuckLake `youtube_videos` table. The CocoIndex
`YoutubeKgEmbedding` App (see `cianfhoghlaim/cocoindex/youtube_kg_embedding.py`)
picks up the rows and runs the BAML knowledge-graph extraction.

Mirrors the `soundcloud_downloader.py` pattern (yt-dlp + json metadata +
write to local file). Designed to be safe-by-default:

* Never downloads a video that is not in the curated YAML watchlist.
* Honours `YT_DLP_DOWNLOAD=skip` for "metadata-only" mode (no MP4
  download; useful for first-pass ingestion).
* Writes metadata + `.info.json` to `stedding/ingest_queue/youtube/<video_id>.info.json`
  and the MP4 (if downloaded) to
  `stedding/ingest_queue/youtube/<video_id>.mp4`.

The curated watchlist lives at `stedding/youtube_curated.yaml` (a list
of `{channel_id, playlist_id?, max_videos?, label}` dicts). The
default watchlist (if the YAML is missing) is the 3Blue1Brown math
channel + the Khan Academy channel, scoped to the first 5 videos per
channel.
"""

from __future__ import annotations
import dlt


import hashlib
import json
import os
import subprocess
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import dlt_sources
import yaml

# The curated watchlist (a small YAML document). Loaded at import time so
# DLT's `dagster:oideachais` UI can show what's in scope.
DEFAULT_WATCHLIST_PATH = Path(
    os.getenv(
        "YOUTUBE_CURATED_PATH",
        str(
            Path(__file__).resolve().parents[4]
            / "stedding"
            / "youtube_curated.yaml"
        ),
    )
)

# The download staging dir. The CocoIndex App reads from here after the
# `download_video()` helper finishes writing the MP4.
DEFAULT_STAGING_DIR = Path(
    os.getenv(
        "YOUTUBE_STAGING_DIR",
        str(
            Path(__file__).resolve().parents[4]
            / "stedding"
            / "ingest_queue"
            / "youtube"
        ),
    )
)

# Default download behaviour: download the MP4. Set
# `YT_DLP_DOWNLOAD=skip` to skip the actual download and only emit
# metadata rows.
DOWNLOAD_BEHAVIOUR = os.getenv("YT_DLP_DOWNLOAD", "download").lower()


@dataclass
class YouTubeVideoRow:
    """One row emitted by the DLT source. Persisted in DuckLake.

    The CocoIndex App joins on `video_id` to attach audio transcripts +
    frame captions + BAML triples.
    """

    video_id: str
    channel_id: str
    channel_title: str
    title: str
    description: str
    duration_s: int
    upload_date: str  # YYYYMMDD
    webpage_url: str
    uploader_id: str
    uploader_name: str
    tags: list[str] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)
    language: str | None = None
    file_path: str | None = None  # relative to stedding/ingest_queue/youtube/
    info_json_path: str | None = None
    sha256: str | None = None
    bytes_on_disk: int = 0
    downloaded_at: str | None = None  # ISO 8601 UTC
    curated_label: str | None = None


def load_curated_watchlist(path: Path | None = None) -> list[dict[str, Any]]:
    """Load the curated watchlist from the YAML file.

    Falls back to a small default watchlist (3Blue1Brown + Khan Academy)
    if the YAML file is missing.
    """
    p = path or DEFAULT_WATCHLIST_PATH
    if not p.exists():
        return _DEFAULT_WATCHLIST

    with p.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, list):
        raise ValueError(
            f"Expected `stedding/youtube_curated.yaml` to be a list, got {type(data).__name__}"
        )
    return data


# A small default watchlist so the DLT source has something to ingest
# even before the user authors `stedding/youtube_curated.yaml`. The
# 3Blue1Brown channel + Khan Academy are both CC-licensed teaching
# channels commonly referenced for math + science tutorials.
_DEFAULT_WATCHLIST: list[dict[str, Any]] = [
    {
        "channel_id": "UCYO_jab_esuFRV4b17AJtAw",
        "channel_title": "3Blue1Brown",
        "max_videos": 5,
        "label": "math-visual",
    },
    {
        "channel_id": "UC4a-Gbdw7vOaccHmFo40b9g",
        "channel_title": "Khan Academy",
        "max_videos": 5,
        "label": "k12-math",
    },
]


def _yt_dlp_dump_json(url: str) -> dict[str, Any]:
    """Run `yt-dlp --dump-json` and return the parsed metadata dict."""
    cmd = ["yt-dlp", "--dump-json", "--no-download", url]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except subprocess.TimeoutExpired as e:
        raise RuntimeError(f"yt-dlp timed out for {url!r}") from e

    if result.returncode != 0:
        raise RuntimeError(
            f"yt-dlp failed for {url!r}: rc={result.returncode}, stderr={result.stderr[:500]}"
        )

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"yt-dlp returned invalid JSON for {url!r}: {e}"
        ) from e


def _yt_dlp_download(url: str, output_template: Path) -> dict[str, Any]:
    """Download the MP4 + the .info.json sidecar.

    Returns the parsed `.info.json` dict (which contains the metadata
    + file path). Raises RuntimeError on failure.
    """
    output_template.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "yt-dlp",
        "-f",
        "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "--write-info-json",
        "-o",
        str(output_template.with_suffix(".%(ext)s")),
        url,
    ]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=900,  # 15 min — videos can be big
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"yt-dlp download failed for {url!r}: rc={result.returncode}, stderr={result.stderr[:500]}"
        )

    # Find the produced files. yt-dlp writes the MP4 + a sibling .info.json.
    info_json_path = output_template.with_suffix(".info.json")
    if not info_json_path.exists():
        # Try the actual MP4 path
        for candidate in output_template.parent.glob(f"{output_template.stem}.*"):
            if candidate.suffix == ".info.json":
                info_json_path = candidate
                break

    if not info_json_path.exists():
        raise RuntimeError(
            f"yt-dlp finished but no .info.json at {output_template.with_suffix('.info.json')}"
        )

    return json.loads(info_json_path.read_text(encoding="utf-8", errors="replace"))


def _channel_video_urls(channel_id: str, max_videos: int) -> Iterator[str]:
    """Yield up to `max_videos` video URLs from a YouTube channel."""
    # `yt-dlp --flat-playlist -J <channel_url>` returns a JSON list of
    # video metadata. We only need URLs here.
    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "--print",
        "%(webpage_url)s",
        "--playlist-end",
        str(max_videos),
        f"https://www.youtube.com/channel/{channel_id}/videos",
    ]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except subprocess.TimeoutExpired as e:
        raise RuntimeError(
            f"yt-dlp playlist dump timed out for channel {channel_id}"
        ) from e
    if result.returncode != 0:
        # Fall back to empty — the per-video metadata dump will fail later.
        return
    for line in result.stdout.splitlines():
        line = line.strip()
        if line:
            yield line


def _safe_upload_date(raw: str | None) -> str:
    """yt-dlp returns YYYYMMDD as a string; normalize to ISO 8601 date."""
    if not raw or len(raw) != 8:
        return ""
    return f"{raw[0:4]}-{raw[4:6]}-{raw[6:8]}"


def _row_from_info_json(
    info: dict[str, Any],
    curated_label: str | None,
) -> YouTubeVideoRow:
    """Convert a yt-dlp info_json dict into a `YouTubeVideoRow`."""
    video_id = info.get("id", "")
    file_path: str | None = None
    info_json_path: str | None = None
    sha256: str | None = None
    bytes_on_disk = 0

    # If a MP4 was written, compute its sha256 + size.
    for ext in ("mp4", "mkv", "webm"):
        candidate = DEFAULT_STAGING_DIR / f"{video_id}.{ext}"
        if candidate.exists():
            file_path = candidate.name
            bytes_on_disk = candidate.stat().st_size
            # We do not hash by default — too slow for a daily ingestion.
            # If the user wants hashing, opt in via the YT_DLP_HASH=1 env.
            if os.getenv("YT_DLP_HASH") == "1":
                h = hashlib.sha256()
                with candidate.open("rb") as f:
                    for chunk in iter(lambda: f.read(1 << 20), b""):
                        h.update(chunk)
                sha256 = h.hexdigest()
            break

    info_json_file = DEFAULT_STAGING_DIR / f"{video_id}.info.json"
    if info_json_file.exists():
        info_json_path = info_json_file.name

    return YouTubeVideoRow(
        video_id=video_id,
        channel_id=info.get("channel_id", ""),
        channel_title=info.get("channel", ""),
        title=info.get("title", ""),
        description=info.get("description", "") or "",
        duration_s=int(info.get("duration") or 0),
        upload_date=_safe_upload_date(info.get("upload_date")),
        webpage_url=info.get("webpage_url", ""),
        uploader_id=info.get("uploader_id", ""),
        uploader_name=info.get("uploader", ""),
        tags=list(info.get("tags") or []),
        categories=list(info.get("categories") or []),
        language=info.get("language"),
        file_path=file_path,
        info_json_path=info_json_path,
        sha256=sha256,
        bytes_on_disk=bytes_on_disk,
        downloaded_at=info.get("timestamp") and info["timestamp"].isoformat() if hasattr(info.get("timestamp"), "isoformat") else None,
        curated_label=curated_label,
    )


@dlt.source(name="youtube_videos")
def youtube_videos_source(
    watchlist_path: Path | None = None,
    staging_dir: Path | None = None,
    max_videos_per_channel: int | None = None,
) -> list[Any]:
    """DLT source that emits 1 `YouTubeVideoRow` per curated YouTube video.

    Iterates the curated watchlist, fetches the per-video metadata via
    `yt-dlp --dump-json`, optionally downloads the MP4 + .info.json
    sidecar, and yields a typed `YouTubeVideoRow`.

    The downstream CocoIndex `YoutubeKgEmbedding` App joins on
    `video_id` to attach the audio transcripts + frame captions +
    BAML triples.
    """
    # Override the staging dir if provided (useful for testing).
    global DEFAULT_STAGING_DIR  # noqa: PLW0603
    if staging_dir is not None:
        DEFAULT_STAGING_DIR = staging_dir
    DEFAULT_STAGING_DIR.mkdir(parents=True, exist_ok=True)

    watchlist = load_curated_watchlist(watchlist_path)

    @dlt.resource(name="youtube_videos", write_disposition="merge", primary_key="video_id")
    def youtube_videos() -> Iterator[YouTubeVideoRow]:
        for entry in watchlist:
            channel_id = entry.get("channel_id")
            if not channel_id:
                continue
            max_v = max_videos_per_channel or entry.get("max_videos") or 5
            label = entry.get("label")

            for url in _channel_video_urls(channel_id, max_v):
                try:
                    info = _yt_dlp_dump_json(url)
                except RuntimeError:
                    continue

                video_id = info.get("id", "")

                if DOWNLOAD_BEHAVIOUR != "skip":
                    output_template = DEFAULT_STAGING_DIR / video_id
                    try:
                        info = _yt_dlp_download(url, output_template)
                    except RuntimeError:
                        # Keep going with the metadata-only row.
                        pass

                yield _row_from_info_json(info, label)

    return [youtube_videos]


# ---------------------------------------------------------------------------
# DLT transformer: pick up videos that have a downloaded MP4 + run the
# CocoIndex App on each. The transformer returns the typed records the
# CocoIndex App emits (video_segments, video_frame_captions, video_triples).
#
# This is wired up in `youtube_kg_embedding.py:youtube_kg_embedding_app`
# (the CocoIndex v1 App) rather than as a DLT transformer — see the
# App's docstring for the rationale.
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    # Ad-hoc invocation: `uv run python -m cianfhoghlaim.dlt.api_sources.youtube_videos`
    pipeline = dlt.pipeline(
        pipeline_name="youtube_videos",
        destination="duckdb",
        dataset_name="oideachais.youtube",
    )
    load_info = pipeline.run(youtube_videos_source())
    print(load_info)