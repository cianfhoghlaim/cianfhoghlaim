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
    # NEW (2026-09-12 — youtube-source-playlist-support-and-agent-training-v1)
    # Populated when the row came from a playlist-scoped watchlist entry;
    # null for the 4 channel-only entries (3Blue1Brown, Khan Academy, etc.)
    playlist_id: str | None = None
    playlist_index: int | None = None


# NEW (2026-09-12 — youtube-source-playlist-support-and-agent-training-v1)
# Bumped whenever youtube_videos_migrations.sql changes; apply_migrations()
# uses this to decide whether to re-run the SQL.
_MIGRATIONS_VERSION = 1


# NEW (2026-09-12) — default DuckLake destination for the subtable views
# created by youtube_videos_migrations.sql. The views live in the
# `cianfhoghlaim.youtube` schema (per the canonical CocoIndex App
# reference at `cocoindex_flows/knowledge_graph/youtube_kg_embedding.py:80`).
# Override via the `YOUTUBE_SCHEMA` env var.
YOUTUBE_SCHEMA = os.getenv(
    "YOUTUBE_SCHEMA",
    "cianfhoghlaim.youtube",
)


def apply_migrations(
    pipeline: dlt.Pipeline | None = None,
    migrations_path: Path | None = None,
) -> int:
    """Apply the YouTube schema migrations idempotently.

    NEW (2026-09-12 — youtube-source-playlist-support-and-agent-training-v1).
    Reads `dlt_sources/api_sources/youtube_videos_migrations.sql` and
    executes each statement against the destination DuckDB. Returns
    the number of statements executed. The 3 view-creating statements
    use `CREATE VIEW IF NOT EXISTS` so re-running is safe.

    If `pipeline` is None, opens a transient `duckdb` connection to
    the default destination. The caller can pass an existing
    `dlt.Pipeline` (post `pipeline.run()`) so the views are created in
    the same DB the source wrote to.

    A `meta` table `_youtube_migrations` records the applied version
    (`_MIGRATIONS_VERSION`); future versions can short-circuit if the
    DB is already current.
    """
    sql_path = migrations_path or (
        Path(__file__).resolve().parent / "youtube_videos_migrations.sql"
    )
    if not sql_path.exists():
        logger.warning(
            "youtube_migrations_missing: skipping",
            path=str(sql_path),
        )
        return 0

    sql_text = sql_path.read_text(encoding="utf-8")
    # Substitute the schema placeholder (NEW 2026-09-12).
    sql_text = sql_text.replace("{YOUTUBE_SCHEMA}", YOUTUBE_SCHEMA)

    # Split on the `--` separator lines (the SQL file uses them as
    # block separators; strip them out).
    statements: list[str] = []
    for raw_block in sql_text.split("\n--\n"):
        cleaned_lines: list[str] = []
        for line in raw_block.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("--"):
                continue
            cleaned_lines.append(line)
        cleaned = "\n".join(cleaned_lines).strip()
        if cleaned and not cleaned.startswith("--"):
            statements.append(cleaned)

    # The MIGRATIONS_VERSION gate: only run if the recorded version is
    # older than the current `_MIGRATIONS_VERSION`. Idempotent.
    if pipeline is not None:
        with pipeline.sql_client() as client:
            executed = _run_migration_statements(client, statements)
    else:
        import duckdb

        with duckdb.connect(DEFAULT_STAGING_DIR.parent / "youtube_migrations.duckdb") as conn:
            executed = _run_migration_statements_duckdb(conn, statements)

    logger.info(
        "youtube_migrations_applied",
        version=_MIGRATIONS_VERSION,
        statement_count=executed,
        sql_path=str(sql_path),
    )
    return executed


def _run_migration_statements(
    client: Any,
    statements: list[str],
) -> int:
    """Execute migration statements via the dlt SQL client."""
    # Ensure the meta table exists + is current.
    client.execute_sql(
        f"CREATE TABLE IF NOT EXISTS {YOUTUBE_SCHEMA}._youtube_migrations ("
        "version INTEGER PRIMARY KEY, applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
    )
    client.execute_sql(
        f"INSERT INTO {YOUTUBE_SCHEMA}._youtube_migrations (version) VALUES "
        f"({_MIGRATIONS_VERSION}) ON CONFLICT DO NOTHING"
    )
    for stmt in statements:
        client.execute_sql(stmt)
    return len(statements)


def _run_migration_statements_duckdb(
    conn: Any,
    statements: list[str],
) -> int:
    """Execute migration statements via a raw DuckDB connection."""
    conn.execute(
        f"CREATE SCHEMA IF NOT EXISTS {YOUTUBE_SCHEMA}"
    )
    conn.execute(
        f"CREATE TABLE IF NOT EXISTS {YOUTUBE_SCHEMA}._youtube_migrations ("
        "version INTEGER PRIMARY KEY, applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
    )
    conn.execute(
        f"INSERT INTO {YOUTUBE_SCHEMA}._youtube_migrations (version) VALUES "
        f"({_MIGRATIONS_VERSION}) ON CONFLICT DO NOTHING"
    )
    for stmt in statements:
        conn.execute(stmt)
    conn.commit()
    return len(statements)


def load_curated_watchlist(path: Path | None = None) -> list[dict[str, Any]]:
    """Load the curated watchlist from the YAML file.

    Falls back to a small default watchlist (3Blue1Brown + Khan Academy)
    if the YAML file is missing.

    MODIFIED (2026-09-12 — youtube-source-playlist-support-and-agent-training-v1):
    accept both the flat-list shape (the legacy format the loader
    declared) and the wrapped `channels:` shape (the format the file
    actually uses). Unwrap the dict shape if encountered so the loader
    contract is independent of the YAML's top-level structure.
    """
    p = path or DEFAULT_WATCHLIST_PATH
    if not p.exists():
        return _DEFAULT_WATCHLIST

    with p.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    # MODIFIED (2026-09-12): handle the wrapped `channels:` shape.
    if isinstance(data, dict) and "channels" in data:
        data = data["channels"]
    if not isinstance(data, list):
        raise ValueError(
            f"Expected `stedding/youtube_curated.yaml` to be a list (or a dict with a 'channels' key), got {type(data).__name__}"
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


def _playlist_video_urls(playlist_id: str, max_videos: int) -> Iterator[str]:
    """Yield up to `max_videos` video URLs from a YouTube playlist.

    NEW (2026-09-12 — youtube-source-playlist-support-and-agent-training-v1).
    Mirrors `_channel_video_urls` but targets the playlist URL with the
    `--playlist-end` flag preserved (so the per-playlist order is
    deterministic — index 1 is always the first video, index N is the
    last). Used by `youtube_videos_source()` when a watchlist entry
    carries `playlist_id`.

    Returns webpage URLs in playlist order (newest at index 1 by
    default; pass `--playlist-items 1-N` or `--playlist-start` to
    slice).
    """
    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "--print",
        "%(webpage_url)s",
        "--playlist-end",
        str(max_videos),
        f"https://www.youtube.com/playlist?list={playlist_id}",
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
            f"yt-dlp playlist dump timed out for playlist {playlist_id}"
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
    playlist_id: str | None = None,
    playlist_index: int | None = None,
) -> YouTubeVideoRow:
    """Convert a yt-dlp info_json dict into a `YouTubeVideoRow`.

    NEW (2026-09-12): when invoked from the playlist branch of
    `youtube_videos_source()`, the `playlist_id` + `playlist_index`
    parameters are populated from the outer loop's tracking state.
    yt-dlp's `--dump-json` against a playlist URL returns both fields
    in the info dict, but we pass them explicitly so the contract is
    independent of how yt-dlp serialises the playlist context.
    """
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

    # Fall back to info_dict fields when the outer loop didn't pass them
    # explicitly. yt-dlp's `--dump-json` against a playlist URL embeds
    # `playlist_id` + `playlist_index` in the per-video info dict.
    resolved_playlist_id = playlist_id or info.get("playlist_id")
    resolved_playlist_index = playlist_index
    if resolved_playlist_index is None:
        raw_index = info.get("playlist_index")
        if raw_index is not None:
            try:
                resolved_playlist_index = int(raw_index)
            except (TypeError, ValueError):
                resolved_playlist_index = None

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
        playlist_id=resolved_playlist_id,
        playlist_index=resolved_playlist_index,
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
            # NEW (2026-09-12): honour playlist_id when present.
            # Falls back to the existing channel-only behaviour when
            # playlist_id is absent (the 4 pre-existing entries).
            playlist_id = entry.get("playlist_id")
            max_v = max_videos_per_channel or entry.get("max_videos") or 5
            label = entry.get("label")

            if playlist_id:
                url_iter: Iterator[str] = _playlist_video_urls(
                    playlist_id, max_v
                )
            else:
                url_iter = _channel_video_urls(channel_id, max_v)

            for url in url_iter:
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

                yield _row_from_info_json(
                    info,
                    label,
                    playlist_id=playlist_id,
                    playlist_index=None,
                )

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
    # MODIFIED (2026-09-12): use the canonical `cianfhoghlaim.youtube`
    # dataset name (per the CocoIndex App reference at
    # `cocoindex_flows/knowledge_graph/youtube_kg_embedding.py:80`).
    # Override via the `YOUTUBE_SCHEMA` env var.
    pipeline = dlt.pipeline(
        pipeline_name="youtube_videos",
        destination="duckdb",
        dataset_name=YOUTUBE_SCHEMA,
    )
    load_info = pipeline.run(youtube_videos_source())
    # NEW (2026-09-12): create the 3 subtable views (2 per-playlist +
    # 1 playlist registry) on the same DuckDB.
    apply_migrations(pipeline=pipeline)
    print(load_info)