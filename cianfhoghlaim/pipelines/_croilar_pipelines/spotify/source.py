"""Spotify REST API Source.

Defines DLT sources for ingesting Spotify data via the Web API.
Uses Client Credentials flow for automatic token management.

Usage:
    import dlt
    from pipelines.spotify import spotify_source

    pipeline = dlt.pipeline(
        pipeline_name="spotify_croilar",
        destination="duckdb",
        dataset_name="spotify_data",
    )

    # Credentials from env vars or secrets.toml
    source = spotify_source(artist_id="2vLlk2CcC4NnN7yoNSTmX2")
    load_info = pipeline.run(source)
"""

import base64
import contextlib
import os
from collections.abc import Iterator
from typing import Any

import dlt
import requests
from dlt.sources.rest_api import RESTAPIConfig, rest_api_resources
from pipelines.spotify.resources import get_artist_endpoints

# Croílár (Aleyum) Spotify Artist ID
CROILAR_ARTIST_ID = "2vLlk2CcC4NnN7yoNSTmX2"


def get_spotify_token(client_id: str, client_secret: str) -> str:
    """Get Spotify access token using Client Credentials flow.

    Args:
        client_id: Spotify application client ID
        client_secret: Spotify application client secret

    Returns:
        Access token string

    Raises:
        ValueError: If token request fails
    """
    # Debug: check if we're getting 1Password references instead of actual values
    if client_id and client_id.startswith("op://"):
        raise ValueError(
            f"Got 1Password reference instead of resolved value for client_id: {client_id}. "
            "Run with: op run --env-file=.env -- dagster dev ..."
        )
    if client_secret and client_secret.startswith("op://"):
        raise ValueError(
            "Got 1Password reference instead of resolved value for client_secret. "
            "Run with: op run --env-file=.env -- dagster dev ..."
        )

    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

    response = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={"grant_type": "client_credentials"},
    )

    if response.status_code != 200:
        # Include debug info about credential lengths
        raise ValueError(
            f"Failed to get Spotify token: {response.status_code} - {response.text}. "
            f"client_id length: {len(client_id) if client_id else 0}, "
            f"client_secret length: {len(client_secret) if client_secret else 0}"
        )

    return response.json()["access_token"]


@dlt.resource(name="artist", write_disposition="merge", primary_key="id")
def get_artist(
    artist_id: str,
    access_token: str,
) -> Iterator[dict[str, Any]]:
    """Fetch artist profile (single object endpoint).

    Args:
        artist_id: Spotify artist ID
        access_token: Spotify access token

    Yields:
        Artist data as a single-item iterator
    """
    response = requests.get(
        f"https://api.spotify.com/v1/artists/{artist_id}",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        },
    )

    if response.status_code == 200:
        yield response.json()
    else:
        raise ValueError(f"Failed to fetch artist: {response.status_code} - {response.text}")


@dlt.source(name="spotify_api")
def spotify_source(
    artist_id: str = CROILAR_ARTIST_ID,
    client_id: str | None = None,
    client_secret: str | None = None,
    include_audio_features: bool = True,
) -> Iterator[Any]:
    """DLT source for Spotify Web API.

    Uses Client Credentials flow to automatically obtain access tokens.
    Credentials can be provided via:
    - Environment variables: SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET (preferred)
    - DLT secrets.toml: [sources.spotify_api] client_id, client_secret
    - Direct parameters

    Args:
        artist_id: Spotify artist ID (default: Aleyum)
        client_id: Spotify application client ID
        client_secret: Spotify application client secret
        include_audio_features: Whether to fetch audio features for tracks

    Yields:
        DLT resources for artist, albums, tracks, and audio features
    """
    # Priority: env vars > parameters > DLT secrets
    _client_id = os.environ.get("SPOTIFY_CLIENT_ID") or client_id
    _client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET") or client_secret

    # Fall back to DLT secrets if still not found
    if not _client_id:
        with contextlib.suppress(Exception):
            _client_id = dlt.secrets.get("sources.spotify_api.client_id")
    if not _client_secret:
        with contextlib.suppress(Exception):
            _client_secret = dlt.secrets.get("sources.spotify_api.client_secret")

    if not _client_id or not _client_secret:
        raise ValueError(
            "Spotify credentials required. Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET "
            "environment variables or configure in .dlt/secrets.toml"
        )

    # Get access token via Client Credentials flow
    access_token = get_spotify_token(_client_id, _client_secret)

    # Yield artist profile (single object - custom resource)
    yield get_artist(artist_id=artist_id, access_token=access_token)

    # Build resource configurations for albums and tracks (list endpoints)
    resource_configs = get_artist_endpoints(artist_id, include_artist=False)

    config: RESTAPIConfig = {
        "client": {
            "base_url": "https://api.spotify.com/v1",
            "auth": {"type": "bearer", "token": access_token},
            "headers": {"Accept": "application/json"},
        },
        "resources": resource_configs,
        "resource_defaults": {
            "primary_key": "id",
            "write_disposition": "merge",
        },
    }

    yield from rest_api_resources(config)


@dlt.resource(name="track_audio_features", write_disposition="merge", primary_key="id")
def get_audio_features(
    track_ids: list[str],
    client_id: str | None = None,
    client_secret: str | None = None,
) -> Iterator[dict[str, Any]]:
    """Fetch audio features for a batch of tracks.

    Args:
        track_ids: List of Spotify track IDs (max 100)
        client_id: Spotify application client ID
        client_secret: Spotify application client secret

    Yields:
        Audio features for each track
    """
    # Priority: env vars > parameters
    _client_id = os.environ.get("SPOTIFY_CLIENT_ID") or client_id
    _client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET") or client_secret

    if not _client_id or not _client_secret:
        print("Warning: Spotify credentials not configured, skipping audio features")
        return

    access_token = get_spotify_token(_client_id, _client_secret)

    # Spotify allows max 100 IDs per request
    batch_size = 100
    for i in range(0, len(track_ids), batch_size):
        batch = track_ids[i : i + batch_size]
        ids_param = ",".join(batch)

        response = requests.get(
            f"https://api.spotify.com/v1/audio-features?ids={ids_param}",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            },
        )

        if response.status_code == 200:
            data = response.json()
            for features in data.get("audio_features", []):
                if features:  # Can be null for unavailable tracks
                    yield features
        else:
            print(f"Error fetching audio features: {response.status_code}")


@dlt.resource(name="cached_images", write_disposition="merge", primary_key="url")
def cache_images_to_r2(
    image_urls: list[dict[str, Any]],
    r2_bucket: str = "aleyum-assets",
    r2_prefix: str = "images/",
) -> Iterator[dict[str, Any]]:
    """Cache Spotify images to Cloudflare R2.

    Spotify image URLs expire within 24 hours, so we need to download
    and store them in R2 for persistent access.

    Args:
        image_urls: List of dicts with 'url', 'width', 'height', 'entity_id', 'entity_type'
        r2_bucket: R2 bucket name
        r2_prefix: Prefix for stored images

    Yields:
        Image metadata with R2 URLs
    """
    import hashlib

    import boto3
    import requests
    from botocore.config import Config

    # Get R2 credentials from environment
    r2_account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
    r2_access_key = os.environ.get("R2_ACCESS_KEY_ID")
    r2_secret_key = os.environ.get("R2_SECRET_ACCESS_KEY")

    if not all([r2_account_id, r2_access_key, r2_secret_key]):
        print("Warning: R2 credentials not configured, skipping image caching")
        return

    # Configure S3-compatible client for R2
    s3 = boto3.client(
        "s3",
        endpoint_url=f"https://{r2_account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=r2_access_key,
        aws_secret_access_key=r2_secret_key,
        config=Config(signature_version="s3v4"),
    )

    for img in image_urls:
        try:
            # Download image from Spotify
            response = requests.get(img["url"])
            if response.status_code != 200:
                continue

            # Generate unique filename based on URL hash
            url_hash = hashlib.md5(img["url"].encode()).hexdigest()[:12]
            entity_id = img.get("entity_id", "unknown")
            entity_type = img.get("entity_type", "image")
            width = img.get("width", 0)

            # Determine file extension from content type
            content_type = response.headers.get("Content-Type", "image/jpeg")
            ext = "jpg" if "jpeg" in content_type else content_type.split("/")[-1]

            key = f"{r2_prefix}{entity_type}/{entity_id}/{width}w_{url_hash}.{ext}"

            # Upload to R2
            s3.put_object(
                Bucket=r2_bucket,
                Key=key,
                Body=response.content,
                ContentType=content_type,
            )

            # Generate public URL (requires R2 public access or custom domain)
            r2_url = f"https://{r2_bucket}.{r2_account_id}.r2.dev/{key}"

            yield {
                "url": img["url"],
                "r2_url": r2_url,
                "r2_key": key,
                "width": width,
                "height": img.get("height", 0),
                "entity_id": entity_id,
                "entity_type": entity_type,
                "content_type": content_type,
            }

        except Exception as e:
            print(f"Error caching image {img.get('url', 'unknown')}: {e}")


def extract_images_from_albums(albums: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Extract image URLs from album data for caching.

    Args:
        albums: List of Spotify album objects

    Returns:
        List of image metadata dicts ready for caching
    """
    images = []
    for album in albums:
        album_id = album.get("id", "")
        for img in album.get("images", []):
            images.append({
                "url": img.get("url"),
                "width": img.get("width", 0),
                "height": img.get("height", 0),
                "entity_id": album_id,
                "entity_type": "album",
            })
    return images


def extract_images_from_artist(artist: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract image URLs from artist data for caching.

    Args:
        artist: Spotify artist object

    Returns:
        List of image metadata dicts ready for caching
    """
    artist_id = artist.get("id", "")
    images = []
    for img in artist.get("images", []):
        images.append({
            "url": img.get("url"),
            "width": img.get("width", 0),
            "height": img.get("height", 0),
            "entity_id": artist_id,
            "entity_type": "artist",
        })
    return images


def run_spotify_pipeline(
    artist_id: str = CROILAR_ARTIST_ID,
    destination: str | Any | None = None,
    dataset_name: str = "spotify_data",
    cache_images: bool = True,
    fetch_audio_features: bool = True,
    client_id: str | None = None,
    client_secret: str | None = None,
) -> Any:
    """Run a Spotify API pipeline.

    Convenience function to ingest Spotify data with optional image caching
    and audio features extraction. Uses Client Credentials flow.

    Args:
        artist_id: Spotify artist ID
        destination: DLT destination (default: DuckLake via shared factory)
        dataset_name: Name of the dataset in the destination
        cache_images: Whether to cache images to R2
        fetch_audio_features: Whether to fetch audio features for tracks
        client_id: Spotify client ID (or set SPOTIFY_CLIENT_ID env var)
        client_secret: Spotify client secret (or set SPOTIFY_CLIENT_SECRET env var)

    Returns:
        LoadInfo from the pipeline run
    """
    # Use shared destination factory for concurrency-safe DuckLake
    if destination is None:
        from dlt_utils import get_dlt_destination
        destination = get_dlt_destination()

    # Get credentials from env if not provided
    _client_id = client_id or os.environ.get("SPOTIFY_CLIENT_ID", "")
    _client_secret = client_secret or os.environ.get("SPOTIFY_CLIENT_SECRET", "")

    pipeline = dlt.pipeline(
        pipeline_name=f"spotify_{artist_id}",
        destination=destination,
        dataset_name=dataset_name,
        progress="log",
    )

    # Run main source
    source = spotify_source(
        artist_id=artist_id,
        client_id=_client_id,
        client_secret=_client_secret,
    )
    load_info = pipeline.run(source)

    print(f"Initial load: {load_info}")

    # Post-process: extract track IDs and fetch audio features
    if fetch_audio_features:
        # Query loaded tracks to get IDs
        with pipeline.sql_client() as client:
            # Get track IDs from top_tracks table
            result = client.execute_sql(
                f"SELECT id FROM {dataset_name}.top_tracks"
            )
            track_ids = [row[0] for row in result]

            if track_ids:
                features_source = get_audio_features(
                    track_ids=track_ids,
                    client_id=_client_id,
                    client_secret=_client_secret,
                )
                features_info = pipeline.run(features_source)
                print(f"Audio features load: {features_info}")

    return load_info


if __name__ == "__main__":
    # Example usage
    load_info = run_spotify_pipeline(
        artist_id=CROILAR_ARTIST_ID,
        destination="duckdb",
        cache_images=False,  # Set True when R2 is configured
        fetch_audio_features=True,
    )
