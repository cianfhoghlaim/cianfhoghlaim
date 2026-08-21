"""Spotify Pipeline.

DLT source for Spotify Web API data extraction.
Handles artists, albums, tracks, and audio features with image caching to R2.
"""

from pipelines.spotify.source import spotify_source, run_spotify_pipeline
from pipelines.spotify.resources import SPOTIFY_RESOURCES

__all__ = ["spotify_source", "run_spotify_pipeline", "SPOTIFY_RESOURCES"]
