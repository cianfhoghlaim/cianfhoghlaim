"""SoundCloud Pipeline.

Crawl4AI-based scraper for SoundCloud profile data.
Extracts track metadata, play stats, and downloads audio files to R2.
"""

from pipelines.soundcloud.scraper import (
    SoundCloudScraper,
    scrape_soundcloud_profile,
    run_soundcloud_pipeline,
)
from pipelines.soundcloud.downloader import download_tracks_to_r2

__all__ = [
    "SoundCloudScraper",
    "scrape_soundcloud_profile",
    "run_soundcloud_pipeline",
    "download_tracks_to_r2",
]
