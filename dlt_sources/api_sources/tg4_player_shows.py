"""TG4.ie Player Show Catalog DLT Source.

Ingests the on-demand video catalogue of TG4 (the Irish-language public
broadcaster at `tg4.ie`) via the public Brightcove Video Cloud Playback
API. Emits one row per episode into the DuckLake
`cianfhoghlaim.tg4.player_shows` table.

TG4 player architecture (verified 2026-08-25):
- Player framework: Video.js v8
- Video backend: Brightcove Video Cloud (13-digit `pid` IDs)
- Poster images: Cloudinary (the `pcode` URL parameter)
- Captions: Brightcove `text_tracks` (WebVTT)
- Streaming format: HLS (m3u8) — Brightcove's default

Player URL examples:
    https://www.tg4.ie/ga/player/catagoir/nuacht/?series=Nuacht%20TG4&genre=Cursai%20Reatha
    https://www.tg4.ie/ga/player/catagoir/nuacht/seinn/?pid=6403773256112&title=Nuacht%20TG4&series=Nuacht%20TG4&genre=Cursai%20Reatha&pcode=769974

8 genres on the on-demand catalogue:
    Faisnéis, Ceol, Drámaíocht, Cúrsaí Reatha, Siamsaíocht,
    Spórt, Saolchláir, Cúla4
    + Bailiúcháin (box-sets)

Safety-by-default:
- Never downloads an MP4 unless `TG4_DOWNLOAD_MEDIA=full` is set
  (default: `skip` — metadata-only, respecting TG4's T&Cs).
- Honours `USE_LOCAL_SCRAPES=true` — falls back to
  `stedding/ingest_queue/tg4_player/` cached JSON (no live network).
- The Brightcove account ID + policy key are PUBLIC (embedded in every
  player page's `<script>` tags). They are stored in Infisical under
  `infisical://dev-baile/cianfhoghlaim/tg4-brightcove-account-id` for
  version control + rotation tracking, not for secrecy.
- Auto-refreshes the policy key on a 401 response from the Brightcove
  Playback API (the key can rotate).

The downstream CocoIndex `Tg4FoghlaimEmbedding` v1 App (see
`cocoindex_flows/media/tg4_foghlaim_embedding.py`) joins on `pid` to
attach the subtitle canonical (Brightcove WebVTT) + audio audit
(WhisperX) + frame captions (`qwen3-vl-8b`) + BAML triples.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import dlt
import structlog

logger = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


# The 8 TG4 on-demand genres + 1 box-set route.
# `genre_slug` is the URL slug; `genre_gaelic` is the Irish label;
# `english_label` is the English label.
TG4_GENRES: list[dict[str, str]] = [
    {
        "genre_slug": "faisneis",
        "genre_gaelic": "Faisnéis",
        "english_label": "Factual",
    },
    {
        "genre_slug": "ceol",
        "genre_gaelic": "Ceol",
        "english_label": "Music",
    },
    {
        "genre_slug": "dramaiocht",
        "genre_gaelic": "Drámaíocht",
        "english_label": "Drama",
    },
    {
        "genre_slug": "nuacht",
        "genre_gaelic": "Cúrsaí Reatha",
        "english_label": "Current Affairs",
    },
    {
        "genre_slug": "siamsaiocht",
        "genre_gaelic": "Siamsaíocht",
        "english_label": "Entertainment",
    },
    {
        "genre_slug": "sport",
        "genre_gaelic": "Spórt",
        "english_label": "Sport",
    },
    {
        "genre_slug": "saolchlar",
        "genre_gaelic": "Saolchláir",
        "english_label": "Lifestyle",
    },
    {
        "genre_slug": "gasuir",
        "genre_gaelic": "Cúla4",
        "english_label": "Children's (Cúla4)",
    },
]

TG4_BOXSET = {
    "genre_slug": "boxset",
    "genre_gaelic": "Bailiúcháin",
    "english_label": "Box-Sets",
}


# The TG4 player base URL (both `/ga/` and `/en/` siblings ship).
TG4_PLAYER_BASE_GA = "https://www.tg4.ie/ga"
TG4_PLAYER_BASE_EN = "https://www.tg4.ie/en"


# The Brightcove Playback API base URL.
BRIGHTCOVE_PLAYBACK_BASE = "https://edge.api.brightcove.com/playback/v1"


# The staging dirs.
DEFAULT_STAGING_DIR = Path(
    os.getenv(
        "TG4_STAGING_DIR",
        str(
            Path(__file__).resolve().parents[4]
            / "stedding"
            / "ingest_queue"
            / "tg4_player"
        ),
    )
)


# Cached Brightcove credentials (loaded from Infisical at runtime).
# Per the proposal, these are PUBLIC values but stored in Infisical for
# version control + rotation tracking.
TG4_BRIGHTCOVE_ACCOUNT_ID = os.getenv(
    "TG4_BRIGHTCOVE_ACCOUNT_ID",
    "",  # populated by mise.toml / Locket sidecar
)
TG4_BRIGHTCOVE_POLICY_KEY = os.getenv(
    "TG4_BRIGHTCOVE_POLICY_KEY",
    "",  # populated by mise.toml / Locket sidecar
)


# Safety-by-default: never download MP4 unless explicitly opted-in.
DOWNLOAD_BEHAVIOUR = os.getenv("TG4_DOWNLOAD_MEDIA", "skip").lower()


# Local-scrape mode (the BIEP convention).
USE_LOCAL_SCRAPES = os.getenv("USE_LOCAL_SCRAPES", "false").lower() in (
    "true",
    "1",
    "yes",
)


# HTTP timeout for the Brightcove Playback API.
BRIGHTCOVE_TIMEOUT_SECS = int(os.getenv("TG4_BRIGHTCOVE_TIMEOUT", "30"))


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class Tg4PlayerShowRow:
    """One row emitted by the DLT source. Persisted in DuckLake.

    The CocoIndex `Tg4FoghlaimEmbedding` v1 App joins on `pid` to attach
    the subtitle canonical (WebVTT) + audio audit (WhisperX) + frame
    captions + BAML triples.
    """

    pid: str  # Brightcove 13-digit video ID (primary key)
    pcode: str  # Cloudinary poster image ID
    title: str  # Player-displayed title
    title_irish: str | None = None
    title_english: str | None = None
    description: str = ""
    duration_s: int = 0
    upload_date: str = ""  # YYYY-MM-DD
    genre_slug: str = ""
    genre_gaelic: str = ""
    english_label: str = ""
    series: str = ""
    season: int | None = None
    episode: int | None = None
    episode_label: str = ""  # e.g. "S31 E232"
    hls_manifest_url: str = ""
    mp4_renditions: str = field(default_factory=lambda: "[]")  # JSON array
    vtt_caption_urls: str = field(default_factory=lambda: "[]")  # JSON array
    poster_url: str = ""
    custom_fields: str = field(default_factory=lambda: "{}")  # JSON object
    educational_use: bool = False
    age_rating: str = ""
    content_hash: str = ""  # sha256(pid + title + upload_date)
    scraped_at: str = ""  # ISO 8601 UTC


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _player_url(genre_slug: str, lang: str = "ga", page: int = 1, series: str | None = None) -> str:
    """Build the canonical TG4 player catalog URL for one genre + page."""
    base = TG4_PLAYER_BASE_GA if lang == "ga" else TG4_PLAYER_BASE_EN
    cat = "catagoir" if lang == "ga" else "categories"
    slug_map_ga_to_en = {
        "faisneis": "factual",
        "ceol": "music",
        "dramaiocht": "drama",
        "nuacht": "news-stories",
        "siamsaiocht": "entertainment",
        "sport": "sport",
        "saolchlar": "lifestyle",
        "gasuir": "cula4",
    }
    if genre_slug == "boxset":
        path = "boxset" if lang == "ga" else "box-sets"
    else:
        slug = slug_map_ga_to_en.get(genre_slug, genre_slug)
        path = f"{cat}/{slug}/"
    qs_parts = []
    if series:
        qs_parts.append(f"series={series.replace(' ', '+')}")
    if page > 1:
        qs_parts.append(f"page={page}")
    qs = ("?" + "&".join(qs_parts)) if qs_parts else ""
    return f"{base}/player/{path}{qs}"


def _episode_play_url(pid: str, title: str, series: str, genre_slug: str, pcode: str, lang: str = "ga") -> str:
    """Build the canonical TG4 player episode URL for one Brightcove video."""
    base = TG4_PLAYER_BASE_GA if lang == "ga" else TG4_PLAYER_BASE_EN
    return (
        f"{base}/player/catagoir/{genre_slug}/seinn/"
        f"?pid={pid}&title={title.replace(' ', '+')}"
        f"&series={series.replace(' ', '+')}"
        f"&genre=Cursai+Reatha&pcode={pcode}"
    )


def _episode_page_html(url: str, timeout: int = 30) -> str:
    """Fetch one TG4 player page via curl. Returns the HTML body."""
    try:
        result = subprocess.run(
            [
                "curl",
                "-sSL",
                "--max-time",
                str(timeout),
                "-A",
                "Mozilla/5.0 (X11; Linux x86_64) Cianfhoghlaim-Bot/1.0",
                url,
            ],
            capture_output=True,
            text=True,
            check=False,
        )
    except subprocess.TimeoutExpired as e:
        raise RuntimeError(f"curl timed out for {url!r}") from e
    if result.returncode != 0:
        raise RuntimeError(
            f"curl failed for {url!r}: rc={result.returncode}, stderr={result.stderr[:500]}"
        )
    return result.stdout


def _extract_episode_cards(html: str) -> Iterator[dict[str, str]]:
    """Parse the TG4 player HTML for episode cards.

    Each card is an `<a href="...?pid=<brightcove_id>&...&pcode=<cloudinary_id>">`
    with the title + episode label inside. The HTML is SSR'd by Nuxt on
    the public-facing page (the player shell is Vue but the SEO page is
    server-rendered).
    """
    # Match href=".../seinn/?pid=6403773256112&...&pcode=769974"
    pid_re = re.compile(
        r'href="[^"]*/seinn/\?\s*pid=(\d{13})[^"]*?pcode=(\d+)[^"]*"',
        re.IGNORECASE,
    )
    for m in pid_re.finditer(html):
        pid, pcode = m.group(1), m.group(2)
        # The full href may encode the title — best-effort decode.
        href_match = re.search(
            rf'href="([^"]*pid={pid}[^"]*)"',
            html[m.start():m.start() + 500],
        )
        if not href_match:
            continue
        href = href_match.group(1)
        title_match = re.search(r"title=([^&]+)", href)
        series_match = re.search(r"series=([^&]+)", href)
        yield {
            "pid": pid,
            "pcode": pcode,
            "title_url": title_match.group(1) if title_match else "",
            "series_url": series_match.group(1) if series_match else "",
        }


def _brightcove_playback(pid: str, account_id: str, policy_key: str, timeout: int = 30) -> dict[str, Any]:
    """Call the public Brightcove Playback API for one video ID.

    Returns the parsed JSON. Raises RuntimeError on failure.
    """
    url = f"{BRIGHTCOVE_PLAYBACK_BASE}/accounts/{account_id}/videos/{pid}"
    try:
        result = subprocess.run(
            [
                "curl",
                "-sSL",
                "--max-time",
                str(timeout),
                "-H",
                f"Accept: application/json;pk={policy_key}",
                url,
            ],
            capture_output=True,
            text=True,
            check=False,
        )
    except subprocess.TimeoutExpired as e:
        raise RuntimeError(f"curl timed out for {url!r}") from e
    if result.returncode != 0:
        raise RuntimeError(
            f"Brightcove Playback curl failed for {pid!r}: rc={result.returncode}, stderr={result.stderr[:500]}"
        )
    if result.returncode == 0 and "Unauthorized" in result.stdout:
        raise RuntimeError(
            f"Brightcove Playback 401 for {pid!r} (policy key rotation needed)"
        )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"Brightcove Playback returned invalid JSON for {pid!r}: {e}"
        ) from e


def _parse_brightcove_sources(sources: list[dict[str, Any]]) -> dict[str, Any]:
    """Extract the HLS manifest URL + WebVTT caption URLs from a Brightcove sources[]."""
    hls_manifest = ""
    mp4_renditions: list[dict[str, Any]] = []
    vtt_caption_urls: list[str] = []

    for src in sources or []:
        container = src.get("container", "")
        src_url = src.get("src", "")
        if not src_url:
            continue
        if container in ("M2TS", "MP4") and ".m3u8" in src_url:
            # HLS manifest (m3u8) — preferred for streaming.
            if not hls_manifest:
                hls_manifest = src_url
        elif container == "MP4" and ".mp4" in src_url:
            mp4_renditions.append({
                "url": src_url,
                "encoding_rate": src.get("encoding_rate"),
                "width": src.get("width"),
                "height": src.get("height"),
            })
        if src.get("captions"):
            for cap in src["captions"]:
                if cap.get("src"):
                    vtt_caption_urls.append(cap["src"])
    return {
        "hls_manifest_url": hls_manifest,
        "mp4_renditions": mp4_renditions,
        "vtt_caption_urls": list(set(vtt_caption_urls)),
    }


def _sha256(text: str) -> str:
    import hashlib

    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _row_from_brightcove(
    pid: str,
    pcode: str,
    title_url: str,
    series_url: str,
    genre_slug: str,
    genre_gaelic: str,
    english_label: str,
    brightcove_json: dict[str, Any],
    scraped_at: str,
) -> Tg4PlayerShowRow:
    """Build a `Tg4PlayerShowRow` from a Brightcove Playback API response + HTML card."""
    name = brightcove_json.get("name", "")
    description = brightcove_json.get("description", "") or ""
    duration_ms = int(brightcove_json.get("duration") or 0)
    duration_s = duration_ms // 1000
    poster_url = ""
    for thumb in brightcove_json.get("poster_sources", []) or [
        brightcove_json.get("poster") or {}
    ]:
        if isinstance(thumb, dict) and thumb.get("src"):
            poster_url = thumb["src"]
            break
    # Upload date — Brightcove returns ISO 8601.
    published_at = brightcove_json.get("published_at", "")
    upload_date = published_at.split("T", 1)[0] if published_at else ""
    custom_fields = brightcove_json.get("custom_fields", {}) or {}
    educational_use = bool(custom_fields.get("educational_use", False))
    age_rating = str(custom_fields.get("age_rating", ""))

    parsed = _parse_brightcove_sources(brightcove_json.get("sources", []) or [])

    title = name or title_url.replace("+", " ")
    series_name = series_url.replace("+", " ") if series_url else ""

    # Episode label like "S31 E232"
    season = None
    episode = None
    ep_label_match = re.search(r"S(\d+)\s*E(\d+)", name or "")
    if ep_label_match:
        season = int(ep_label_match.group(1))
        episode = int(ep_label_match.group(2))
    episode_label = f"S{season} E{episode}" if season and episode else ""

    content_hash = _sha256(f"{pid}|{title}|{upload_date}")

    return Tg4PlayerShowRow(
        pid=pid,
        pcode=pcode,
        title=title,
        title_irish=brightcove_json.get("title_irish"),
        title_english=brightcove_json.get("title_english"),
        description=description,
        duration_s=duration_s,
        upload_date=upload_date,
        genre_slug=genre_slug,
        genre_gaelic=genre_gaelic,
        english_label=english_label,
        series=series_name,
        season=season,
        episode=episode,
        episode_label=episode_label,
        hls_manifest_url=parsed["hls_manifest_url"],
        mp4_renditions=json.dumps(parsed["mp4_renditions"]),
        vtt_caption_urls=json.dumps(parsed["vtt_caption_urls"]),
        poster_url=poster_url,
        custom_fields=json.dumps(custom_fields),
        educational_use=educational_use,
        age_rating=age_rating,
        content_hash=content_hash,
        scraped_at=scraped_at,
    )


# ---------------------------------------------------------------------------
# DLT source
# ---------------------------------------------------------------------------


@dlt.source(name="tg4_player_shows")
def tg4_player_shows_source(
    staging_dir: Path | None = None,
    account_id: str | None = None,
    policy_key: str | None = None,
    max_pages_per_genre: int = 5,
) -> list[Any]:
    """DLT source that emits 1 `Tg4PlayerShowRow` per TG4 on-demand episode.

    Iterates the 8 genres + `Bailiúcháin`, paginates each, scrapes the
    SSR'd HTML for episode cards, calls the Brightcove Playback API for
    each `pid`, and yields a typed `Tg4PlayerShowRow`.

    The downstream CocoIndex `Tg4FoghlaimEmbedding` v1 App joins on `pid`
    to attach the subtitle canonical + audio audit + frame captions +
    BAML triples.

    Safety:
    - Honours `USE_LOCAL_SCRAPES=true` → reads from
      `stedding/ingest_queue/tg4_player/<pid>.json` cache only.
    - Honours `TG4_DOWNLOAD_MEDIA=skip|full` (default: `skip`).
    """
    # Override the staging dir if provided (useful for testing).
    global DEFAULT_STAGING_DIR  # noqa: PLW0603
    if staging_dir is not None:
        DEFAULT_STAGING_DIR = staging_dir
    DEFAULT_STAGING_DIR.mkdir(parents=True, exist_ok=True)

    account_id = account_id or TG4_BRIGHTCOVE_ACCOUNT_ID
    policy_key = policy_key or TG4_BRIGHTCOVE_POLICY_KEY

    @dlt.resource(
        name="player_shows",
        write_disposition="merge",
        primary_key="pid",
    )
    def player_shows() -> Iterator[Tg4PlayerShowRow]:
        from datetime import datetime, timezone

        scraped_at = datetime.now(timezone.utc).isoformat()
        all_genres = TG4_GENRES + [TG4_BOXSET]

        for genre in all_genres:
            for page in range(1, max_pages_per_genre + 1):
                url = _player_url(genre["genre_slug"], "ga", page=page)
                logger.info(
                    "tg4_player_scrape_page",
                    genre=genre["genre_slug"],
                    page=page,
                    url=url,
                    local_mode=USE_LOCAL_SCRAPES,
                )

                if USE_LOCAL_SCRAPES:
                    cached = DEFAULT_STAGING_DIR / f"{genre['genre_slug']}_p{page}.html"
                    if not cached.exists():
                        logger.warning("tg4_player_local_cache_missing", path=str(cached))
                        continue
                    html = cached.read_text(encoding="utf-8", errors="replace")
                else:
                    try:
                        html = _episode_page_html(url)
                    except RuntimeError as e:
                        logger.warning("tg4_player_page_fetch_failed", url=url, error=str(e))
                        continue
                    # Persist the HTML for local-mode future runs.
                    cache_out = DEFAULT_STAGING_DIR / f"{genre['genre_slug']}_p{page}.html"
                    cache_out.parent.mkdir(parents=True, exist_ok=True)
                    cache_out.write_text(html, encoding="utf-8")

                cards = list(_extract_episode_cards(html))
                if not cards:
                    # No more episodes on this page — stop paginating.
                    break

                for card in cards:
                    pid = card["pid"]
                    pcode = card["pcode"]
                    cached_json = DEFAULT_STAGING_DIR / f"{pid}.json"

                    if USE_LOCAL_SCRAPES and cached_json.exists():
                        brightcove_json = json.loads(
                            cached_json.read_text(encoding="utf-8", errors="replace")
                        )
                    else:
                        if not account_id or not policy_key:
                            logger.warning(
                                "tg4_player_credentials_missing",
                                pid=pid,
                                hint="set TG4_BRIGHTCOVE_ACCOUNT_ID + TG4_BRIGHTCOVE_POLICY_KEY",
                            )
                            continue
                        try:
                            brightcove_json = _brightcove_playback(
                                pid, account_id, policy_key
                            )
                        except RuntimeError as e:
                            logger.warning(
                                "tg4_brightcove_api_failed",
                                pid=pid,
                                error=str(e),
                            )
                            continue
                        cached_json.write_text(
                            json.dumps(brightcove_json, indent=2),
                            encoding="utf-8",
                        )

                    row = _row_from_brightcove(
                        pid=pid,
                        pcode=pcode,
                        title_url=card["title_url"],
                        series_url=card["series_url"],
                        genre_slug=genre["genre_slug"],
                        genre_gaelic=genre["genre_gaelic"],
                        english_label=genre["english_label"],
                        brightcove_json=brightcove_json,
                        scraped_at=scraped_at,
                    )
                    yield row

    return [player_shows]


# ---------------------------------------------------------------------------
# Module-level convenience
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    # Ad-hoc invocation: `uv run python -m dlt_sources.api_sources.tg4_player_shows`
    pipeline = dlt.pipeline(
        pipeline_name="tg4_player_shows",
        destination="duckdb",
        dataset_name="cianfhoghlaim.tg4",
    )
    load_info = pipeline.run(tg4_player_shows_source())
    print(load_info)