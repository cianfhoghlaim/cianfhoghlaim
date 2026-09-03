"""Filesystem DLT sources for the Cianfhoghlaim platform.

These dlt sources read from local filesystem paths (PDFs, images,
CSV/JSON files) and produce structured records for downstream BAML
extraction. Per the v3 consolidation plan (consolidate-cianfhoghlaim-subdirs
Phase A.6), the 8 filesystem-source modules are consolidated here
from the legacy top-level dirs (artwork/, cv/, labels/, soundcloud/,
spotify/, teaching/).

Modules:
- artwork — author artwork image downloads + metadata
- cv — author CV PDF reads
- labels — music label discography scraping
- soundcloud — SoundCloud downloader + scraper
- spotify — Spotify resources + source
- teaching — teaching placement PDFs
"""
from .artwork import *
from .cv import *
from .labels_base import *
from .labels_scraper import *
from .soundcloud_downloader import *
from .soundcloud_scraper import *
from .spotify_resources import *
from .spotify_source import *
from .teaching import *
