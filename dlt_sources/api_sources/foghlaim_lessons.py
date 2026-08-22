"""Foghlaim.tg4.ie Lesson Corpus DLT Source.

Ingests the educational lesson catalogue at `foghlaim.tg4.ie` (TG4's
parallel education portal) as one row per `/ceacht/<lesson-id>` URL.
Foghlaim is a Nuxt.js SSR + client-hydration site; lessons ship with
rich educational metadata (keywords, worksheets, learning outcomes,
subject tags, level) + an upstream video reference that is EITHER:

- **13-digit Brightcove ID** (e.g. `6395898596112`) → reuse the
  Brightcove Playback API call from `tg4_player_shows.py`
- **11-character YouTube ID** (e.g. `IZDzeqJ80K0`) → shell `yt-dlp
  --dump-json` to get the canonical metadata

Foghlaim architecture (verified 2026-08-25):
- Framework: Nuxt.js (the `<div id="__nuxt">` SSR marker)
- 3 educational levels: Bunscoil (Primary) / Sraith Shóisearach & GCSE
  (Junior Cycle) / Ardteist, AS/A2 & Foghlaimeoirí Fásta (Senior +
  Adult Learners)
- 11+ subjects: Gaeilge, Béaltriail, Filíocht, Saothar Litríochta,
  Scéalta Reatha, Stair, Tíreolaíocht, Eolaíocht, Matamaitic, Ealaín,
  Ceol, Rannta, Amhráin, Corpoideachas, Folláine, Gnó, Nuacht Cúla4,
  Nuacht TG4, Athrú Aeráide
- Per-lesson metadata: title, level, subject, duration, source suffix
  (FO | BC | MO | YT), keywords (`Eochairfhocail`), worksheets
  (`Bileoga Oibre agus Freagraí`), support material, learning outcomes
  (`Spriocanna Foghlama`)

Emits one row per lesson into `cianfhoghlaim.tg4.foghlaim_lessons` in
DuckLake. Adds 3 derived columns via the BIEP taxonomy table:
`biep_subject`, `biep_stage`, `has_worksheet`.

Safety-by-default:
- Honours `USE_LOCAL_SCRAPES=true` → falls back to
  `stedding/ingest_queue/foghlaim/` cached JSON.
- Honours `TG4_DOWNLOAD_MEDIA=skip` (default) — no MP4 downloads.
- The Firecrawl MCP credentials are loaded from Infisical under
  `infisical://dev-baile/cianfhoghlaim/firecrawl-api-key`.

The downstream CocoIndex `Tg4FoghlaimEmbedding` v1 App joins on
`lesson_id` to attach the subtitle canonical (Brightcove WebVTT) +
audio audit (WhisperX) + frame captions + BAML triples. The
worksheet extraction (`ExtractWorksheetAnswers`) runs only when
`has_worksheet=true`.
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


FOGHLAIM_BASE = "https://foghlaim.tg4.ie"

# The 3 top-level Foghlaim routes.
FOGHLAIM_LEVELS: list[dict[str, str]] = [
    {
        "level_slug": "bunscoil",
        "level_gaelic": "Bunscoil",
        "biep_stage": "bunscoil",
        "english_label": "Primary",
    },
    {
        "level_slug": "tsraith_shoisearach",
        "level_gaelic": "Sraith Shóisearach & GCSE",
        "biep_stage": "junior_cycle",
        "english_label": "Junior Cycle & GCSE",
    },
    {
        "level_slug": "tsraith_shinsearach",
        "level_gaelic": "Ardteist, AS/A2 & Foghlaimeoirí Fásta",
        "biep_stage": "senior_cycle",
        "english_label": "Senior Cycle, A-Level & Adult Learners",
    },
]


# The BIEP subject taxonomy — maps Foghlaim subject strings → BIEP v3
# subject slugs. Mirrors the canonical `baml_src/celtic/grammar_patterns.baml`
# subject vocabulary. Order matters: longer/more-specific keys first.
BIEP_SUBJECT_TAXONOMY: list[tuple[str, str]] = [
    ("Béaltriail", "gaeilge_oral"),
    ("Saothar Litríochta", "gaeilge_literature"),
    ("Filíocht", "gaeilge_poetry"),
    ("Scéalta Reatha", "gaeilge_current_affairs"),
    ("Nuacht TG4", "gaeilge_current_affairs"),
    ("Nuacht Cúla4", "gaeilge_children"),
    ("Gaeilge", "gaeilge"),
    ("Stair", "history"),
    ("Tíreolaíocht", "geography"),
    ("Matamaitic", "mathematics"),
    ("Eolaíocht", "science"),
    ("Ceol, Rannta & Amhráin", "music"),
    ("Ceol", "music"),
    ("Rannta", "music_songs"),
    ("Amhráin", "music_songs"),
    ("Ealaín", "art"),
    ("Corpoideachas", "physical_education"),
    ("Folláine", "wellbeing"),
    ("Gnó", "business"),
    ("Athrú Aeráide", "geography_climate"),
    # Sensible defaults for unrecognised subjects:
]


# The 4 source-suffix codes visible in Foghlaim lesson titles:
#   FO = Foghlaim (Senior / standard lessons)
#   BC = Bunscoil (Primary)
#   MO = Meánscoil (Secondary)
#   YT = YouTube source (the lesson video is on Cúla4's YouTube channel)
FOGHLAIM_SOURCE_SUFFIXES = {"FO", "BC", "MO", "YT"}


# The staging dirs.
DEFAULT_STAGING_DIR = Path(
    os.getenv(
        "FOGHLAIM_STAGING_DIR",
        str(
            Path(__file__).resolve().parents[4]
            / "stedding"
            / "ingest_queue"
            / "foghlaim"
        ),
    )
)


# Safety-by-default: never download MP4 unless explicitly opted-in.
DOWNLOAD_BEHAVIOUR = os.getenv("TG4_DOWNLOAD_MEDIA", "skip").lower()

# Local-scrape mode (the BIEP convention).
USE_LOCAL_SCRAPES = os.getenv("USE_LOCAL_SCRAPES", "false").lower() in (
    "true",
    "1",
    "yes",
)

# HTTP timeout for Firecrawl MCP calls.
FIRECRAWL_TIMEOUT_SECS = int(os.getenv("FOGHLAIM_FIRECRAWL_TIMEOUT", "60"))


# Brightcove account / policy key (reused from tg4_player_shows.py).
TG4_BRIGHTCOVE_ACCOUNT_ID = os.getenv("TG4_BRIGHTCOVE_ACCOUNT_ID", "")
TG4_BRIGHTCOVE_POLICY_KEY = os.getenv("TG4_BRIGHTCOVE_POLICY_KEY", "")


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class FoghlaimLessonRow:
    """One row emitted by the DLT source. Persisted in DuckLake.

    The CocoIndex `Tg4FoghlaimEmbedding` v1 App joins on `lesson_id` to
    attach the subtitle canonical + audio audit + frame captions +
    BAML triples.
    """

    lesson_id: str  # The path-segment after `/ceacht/` (primary key)
    source_kind: str  # "brightcove" | "youtube"
    title: str
    level_slug: str  # "bunscoil" | "tsraith_shoisearach" | "tsraith_shinsearach"
    level_gaelic: str
    english_label: str
    source_suffix: str = ""  # "FO" | "BC" | "MO" | "YT"
    subject_foghlaim: str = ""  # As-tagged by Foghlaim (raw)
    biep_subject: str = ""  # Derived via BIEP_SUBJECT_TAXONOMY
    biep_stage: str = ""  # "bunscoil" | "junior_cycle" | "senior_cycle" | "adult"
    duration_s: int = 0
    description: str = ""
    keywords: str = field(default_factory=lambda: "[]")  # JSON array
    learning_outcomes: str = field(default_factory=lambda: "[]")  # JSON array
    worksheet_urls: str = field(default_factory=lambda: "[]")  # JSON array
    has_worksheet: bool = False
    series: str = ""
    related_lessons: str = field(default_factory=lambda: "[]")  # JSON array
    # Conditional: only one of these is populated.
    brightcove_video: str = field(default_factory=lambda: "{}")  # JSON object
    youtube_metadata: str = field(default_factory=lambda: "{}")  # JSON object
    content_hash: str = ""
    scraped_at: str = ""  # ISO 8601 UTC


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _is_brightcove_lesson_id(lesson_id: str) -> bool:
    """Brightcove video IDs are 13-digit numeric strings."""
    return bool(re.fullmatch(r"\d{13}", lesson_id))


def _is_youtube_lesson_id(lesson_id: str) -> bool:
    """YouTube video IDs are 11-character alphanumeric strings."""
    return bool(re.fullmatch(r"[A-Za-z0-9_-]{11}", lesson_id))


def _derive_biep_subject(subject_foghlaim: str) -> str:
    """Map a Foghlaim subject string to a BIEP v3 subject slug.

    Returns `non_curriculum` for any subject that doesn't map (entertainment,
    music, sport, etc.) — those rows are excluded from the BIEP join in
    `british-isles-education-pipeline-v3/spec.md` (Requirement:
    `MediaStreamingEnrichmentLink`).
    """
    subject = subject_foghlaim.strip()
    if not subject:
        return "non_curriculum"
    for needle, slug in BIEP_SUBJECT_TAXONOMY:
        if needle in subject:
            return slug
    return "non_curriculum"


def _firecrawl_map(search_term: str = "ceacht", limit: int = 2000) -> list[str]:
    """Enumerate all `/ceacht/<id>` URLs via the canonical Firecrawl SDK.

    Uses `dlt_sources.common.firecrawl_source.map_urls` (the canonical
    DLT-side wrapper, NOT the FirecrawlMCPClient — the latter is for
    agent runtime, the former is for DLT ingestion per the
    `agents/meaisinfhoghlaim/firecrawl_mcp/AGENTS.md` DO NOT rule).

    Returns a list of absolute URLs. Falls back to an empty list on
    error (logged as a warning).
    """
    try:
        from dlt_sources.common.firecrawl_source import map_urls

        urls = list(
            map_urls(
                base_url=FOGHLAIM_BASE,
                search=search_term,
                max_urls=limit,
            )
        )
        return [u for u in urls if "/ceacht/" in u]
    except Exception as e:  # noqa: BLE001 — degrade gracefully
        logger.warning("firecrawl_map_failed", error=str(e))
        return []


def _firecrawl_scrape_lesson_json(url: str) -> dict[str, Any]:
    """Scrape one Foghlaim lesson page via the canonical Firecrawl SDK.

    Uses `dlt_sources.common.firecrawl_source.scrape_page` (the
    canonical DLT-side wrapper — NOT the FirecrawlMCPClient).

    Returns the parsed dict with `markdown` + `links` + `metadata`.
    Structured-field extraction (level, keywords, etc.) is done
    downstream by the BAML `ClassifyTg4Episode` fn (not here).

    Returns the dict (or empty dict on error).
    """
    try:
        from dlt_sources.common.firecrawl_source import scrape_page

        return scrape_page(url, formats=["markdown", "links"])
    except Exception as e:  # noqa: BLE001 — degrade gracefully
        logger.warning("firecrawl_scrape_failed", url=url, error=str(e))
        return {}


def _brightcove_playback(pid: str, account_id: str, policy_key: str) -> dict[str, Any]:
    """Call the public Brightcove Playback API for one video ID."""
    try:
        from dlt_sources.api_sources.tg4_player_shows import (
            _brightcove_playback as _brightcove_call,
        )

        return _brightcove_call(pid, account_id, policy_key)
    except ImportError:
        # Fall back to a local copy if the sibling module is unavailable
        # (e.g. when foghlaim_lessons is imported standalone in tests).
        from .tg4_player_shows import _brightcove_playback as _brightcove_call  # type: ignore[no-redef]

        return _brightcove_call(pid, account_id, policy_key)


def _yt_dlp_dump_json(url: str, timeout: int = 120) -> dict[str, Any]:
    """Run `yt-dlp --dump-json` and return the parsed metadata dict."""
    cmd = ["yt-dlp", "--dump-json", "--no-download", url]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
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
        raise RuntimeError(f"yt-dlp returned invalid JSON for {url!r}: {e}") from e


def _lesson_id_from_url(url: str) -> str:
    """Extract the lesson ID (the last path segment) from a `/ceacht/<id>` URL."""
    return url.rstrip("/").rsplit("/", 1)[-1]


def _sha256(text: str) -> str:
    import hashlib

    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _row_from_lesson(
    lesson_id: str,
    level: dict[str, str],
    lesson_json: dict[str, Any],
    brightcove_json: dict[str, Any] | None,
    youtube_json: dict[str, Any] | None,
    scraped_at: str,
) -> FoghlaimLessonRow:
    """Build a `FoghlaimLessonRow` from the scraped lesson metadata + the
    upstream video reference (Brightcove JSON or YouTube JSON).
    """
    title = str(lesson_json.get("title", "")).strip() or lesson_id
    source_suffix = str(lesson_json.get("source_suffix", "")).strip().upper()
    if source_suffix not in FOGHLAIM_SOURCE_SUFFIXES:
        source_suffix = ""
    subject_foghlaim = str(lesson_json.get("subject_foghlaim", "")).strip()
    biep_subject = _derive_biep_subject(subject_foghlaim)
    keywords = lesson_json.get("keywords") or []
    learning_outcomes = lesson_json.get("learning_outcomes") or []
    worksheet_urls = lesson_json.get("worksheet_urls") or []
    has_worksheet = bool(worksheet_urls)
    duration_s = int(lesson_json.get("duration_s") or 0)
    description = str(lesson_json.get("description", "")).strip()
    series = str(lesson_json.get("series", "")).strip()
    related_lessons = lesson_json.get("related_lessons") or []
    content_hash = _sha256(
        f"{lesson_id}|{title}|{duration_s}|{subject_foghlaim}|{series}"
    )

    if brightcove_json is not None:
        source_kind = "brightcove"
    elif youtube_json is not None:
        source_kind = "youtube"
    else:
        source_kind = "unknown"

    return FoghlaimLessonRow(
        lesson_id=lesson_id,
        source_kind=source_kind,
        title=title,
        level_slug=level["level_slug"],
        level_gaelic=level["level_gaelic"],
        english_label=level["english_label"],
        source_suffix=source_suffix,
        subject_foghlaim=subject_foghlaim,
        biep_subject=biep_subject,
        biep_stage=level["biep_stage"],
        duration_s=duration_s,
        description=description,
        keywords=json.dumps(keywords),
        learning_outcomes=json.dumps(learning_outcomes),
        worksheet_urls=json.dumps(worksheet_urls),
        has_worksheet=has_worksheet,
        series=series,
        related_lessons=json.dumps(related_lessons),
        brightcove_video=json.dumps(brightcove_json or {}),
        youtube_metadata=json.dumps(youtube_json or {}),
        content_hash=content_hash,
        scraped_at=scraped_at,
    )


# ---------------------------------------------------------------------------
# DLT source
# ---------------------------------------------------------------------------


@dlt.source(name="foghlaim_lessons")
def foghlaim_lessons_source(
    staging_dir: Path | None = None,
    account_id: str | None = None,
    policy_key: str | None = None,
    max_lessons_per_level: int = 2000,
    firecrawl_map_limit: int = 2000,
) -> list[Any]:
    """DLT source that emits 1 `FoghlaimLessonRow` per Foghlaim lesson.

    Iterates the 3 educational levels, enumerates `/ceacht/<id>` URLs via
    the Firecrawl MCP `map` tool, `scrape`s each with `formats=[json]` +
    a schema that extracts the educational metadata, then for each lesson
    resolves the upstream video reference (Brightcove Playback API for
    13-digit IDs, `yt-dlp --dump-json` for 11-char IDs).

    The downstream CocoIndex `Tg4FoghlaimEmbedding` v1 App joins on
    `lesson_id` to attach the subtitle canonical + audio audit + frame
    captions + BAML triples. `ExtractWorksheetAnswers` BAML fn runs only
    on lessons with `has_worksheet=true`.

    Safety:
    - Honours `USE_LOCAL_SCRAPES=true` → reads from
      `stedding/ingest_queue/foghlaim/<lesson_id>.json` cache only.
    - Honours `TG4_DOWNLOAD_MEDIA=skip|full` (default: `skip`).
    """
    global DEFAULT_STAGING_DIR  # noqa: PLW0603
    if staging_dir is not None:
        DEFAULT_STAGING_DIR = staging_dir
    DEFAULT_STAGING_DIR.mkdir(parents=True, exist_ok=True)

    account_id = account_id or TG4_BRIGHTCOVE_ACCOUNT_ID
    policy_key = policy_key or TG4_BRIGHTCOVE_POLICY_KEY

    @dlt.resource(
        name="lessons",
        write_disposition="merge",
        primary_key="lesson_id",
    )
    def lessons() -> Iterator[FoghlaimLessonRow]:
        from datetime import datetime, timezone

        scraped_at = datetime.now(timezone.utc).isoformat()

        # Step 1 — enumerate `/ceacht/<id>` URLs across all 3 levels.
        all_lesson_urls: list[tuple[dict[str, str], str]] = []
        for level in FOGHLAIM_LEVELS:
            level_url = f"{FOGHLAIM_BASE}/{level['level_slug']}"
            logger.info(
                "foghlaim_enumerate_level",
                level=level["level_slug"],
                url=level_url,
                local_mode=USE_LOCAL_SCRAPES,
            )
            if USE_LOCAL_SCRAPES:
                cached_list = DEFAULT_STAGING_DIR / f"_urls_{level['level_slug']}.json"
                if not cached_list.exists():
                    logger.warning("foghlaim_local_cache_missing", path=str(cached_list))
                    continue
                urls = json.loads(cached_list.read_text(encoding="utf-8", errors="replace"))
            else:
                urls = _firecrawl_map(
                    search_term=level["level_slug"], limit=firecrawl_map_limit
                )
                cached_list = DEFAULT_STAGING_DIR / f"_urls_{level['level_slug']}.json"
                cached_list.parent.mkdir(parents=True, exist_ok=True)
                cached_list.write_text(
                    json.dumps(urls, indent=2), encoding="utf-8"
                )
            for url in urls[:max_lessons_per_level]:
                all_lesson_urls.append((level, url))

        # Step 2 — for every lesson URL, scrape the metadata + resolve
        # the upstream video reference.
        for level, url in all_lesson_urls:
            lesson_id = _lesson_id_from_url(url)
            cached_json = DEFAULT_STAGING_DIR / f"{lesson_id}.json"

            if USE_LOCAL_SCRAPES and cached_json.exists():
                bundle = json.loads(
                    cached_json.read_text(encoding="utf-8", errors="replace")
                )
                lesson_json = bundle.get("lesson", {})
                brightcove_json = bundle.get("brightcove")
                youtube_json = bundle.get("youtube")
            else:
                lesson_json = _firecrawl_scrape_lesson_json(url)
                if not lesson_json:
                    logger.warning(
                        "foghlaim_scrape_empty", url=url, lesson_id=lesson_id
                    )
                    continue
                brightcove_json = None
                youtube_json = None
                if _is_brightcove_lesson_id(lesson_id):
                    if account_id and policy_key:
                        try:
                            brightcove_json = _brightcove_playback(
                                lesson_id, account_id, policy_key
                            )
                        except RuntimeError as e:
                            logger.warning(
                                "foghlaim_brightcove_api_failed",
                                lesson_id=lesson_id,
                                error=str(e),
                            )
                elif _is_youtube_lesson_id(lesson_id):
                    try:
                        youtube_json = _yt_dlp_dump_json(
                            f"https://www.youtube.com/watch?v={lesson_id}"
                        )
                    except RuntimeError as e:
                        logger.warning(
                            "foghlaim_ytdlp_failed",
                            lesson_id=lesson_id,
                            error=str(e),
                        )
                bundle = {
                    "lesson": lesson_json,
                    "brightcove": brightcove_json,
                    "youtube": youtube_json,
                }
                cached_json.write_text(
                    json.dumps(bundle, indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )

            row = _row_from_lesson(
                lesson_id=lesson_id,
                level=level,
                lesson_json=lesson_json,
                brightcove_json=brightcove_json,
                youtube_json=youtube_json,
                scraped_at=scraped_at,
            )
            yield row

    return [lessons]


# ---------------------------------------------------------------------------
# Module-level convenience
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    # Ad-hoc invocation: `uv run python -m dlt_sources.api_sources.foghlaim_lessons`
    pipeline = dlt.pipeline(
        pipeline_name="foghlaim_lessons",
        destination="duckdb",
        dataset_name="cianfhoghlaim.tg4",
    )
    load_info = pipeline.run(foghlaim_lessons_source())
    print(load_info)