"""Spotify Pipeline.

DLT source for Spotify Web API data extraction.
Handles artists, albums, tracks, and audio features with image caching to R2.
"""

from pipelines.spotify.resources import SPOTIFY_RESOURCES
from pipelines.spotify.source import run_spotify_pipeline, spotify_source

__all__ = ["spotify_source", "run_spotify_pipeline", "SPOTIFY_RESOURCES"]
