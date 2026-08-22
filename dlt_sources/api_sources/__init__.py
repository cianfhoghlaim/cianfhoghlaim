"""REST API DLT sources for the Cianfhoghlaim platform.

These dlt sources consume REST APIs (GitHub, LinkedIn, ResearchGate, ...)
and produce structured records for downstream BAML extraction. Per the
v3 consolidation plan (consolidate-cianfhoghlaim-subdirs Phase A.6),
the 3 API-source modules are consolidated here from the legacy top-level
dirs (github/, linkedin/, researchgate/).

Modules:
- github — GitHub repos, languages, READMEs
- linkedin — LinkedIn profile extraction
- researchgate — ResearchGate profile + publications
- youtube_videos — curated YouTube channels via yt-dlp (Phase 1 of multimodal-code-and-media-intel)
- tg4_player_shows — TG4.ie on-demand video catalog via Brightcove Playback API (tg4-foghlaim-corpus)
- foghlaim_lessons — Foghlaim.tg4.ie Nuxt.js lesson corpus via Firecrawl MCP (tg4-foghlaim-corpus)
- soundcloud_downloader — SoundCloud audio via yt-dlp
- spotify_* — Spotify catalogue (multiple sub-modules)
"""
from .github import *
from .linkedin import *
from .researchgate import *
from .youtube_videos import *
from .tg4_player_shows import *
from .foghlaim_lessons import *
