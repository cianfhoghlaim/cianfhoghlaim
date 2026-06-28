"""SoundCloud Pipeline.

Crawl4AI-based scraper for SoundCloud profile data.
Extracts track metadata, play stats, and downloads audio files to R2.
"""

from pipelines.soundcloud.downloader import download_tracks_to_r2
from pipelines.soundcloud.scraper import (
    SoundCloudScraper,
    run_soundcloud_pipeline,
    scrape_soundcloud_profile,
)

__all__ = [
    "SoundCloudScraper",
    "download_tracks_to_r2",
    "run_soundcloud_pipeline",
    "scrape_soundcloud_profile",
]
