"""Spotify API Resource Definitions.

Defines REST API endpoint configurations for Spotify Web API resources.
These follow the RESTAPIConfig pattern from dlt's rest_api source.

Reference: https://developer.spotify.com/documentation/web-api
Artist ID for Aleyum: 2vLlk2CcC4NnN7yoNSTmX2
"""

from typing import Any


# Spotify API resource configurations
# Each resource defines an endpoint with pagination, data selection, and merge keys

artist_resource: dict[str, Any] = {
    "name": "artist",
    "endpoint": {
        "path": "artists/{artist_id}",
        "method": "GET",
        "data_selector": "$",  # Single object response (not array)
    },
    "primary_key": "id",
    "write_disposition": "merge",
}

artist_albums_resource: dict[str, Any] = {
    "name": "albums",
    "endpoint": {
        "path": "artists/{artist_id}/albums",
        "method": "GET",
        "params": {
            "limit": 50,
            "include_groups": "album,single,compilation",
            "market": "IE",  # Ireland
        },
        "data_selector": "items",
        "paginator": {
            "type": "offset",
            "limit": 50,
            "offset_param": "offset",
            "limit_param": "limit",
            "total_path": "total",
        },
    },
    "primary_key": "id",
    "write_disposition": "merge",
}

artist_top_tracks_resource: dict[str, Any] = {
    "name": "top_tracks",
    "endpoint": {
        "path": "artists/{artist_id}/top-tracks",
        "method": "GET",
        "params": {
            "market": "IE",
        },
        "data_selector": "tracks",
    },
    "primary_key": "id",
    "write_disposition": "merge",
}

album_tracks_resource: dict[str, Any] = {
    "name": "album_tracks",
    "endpoint": {
        "path": "albums/{album_id}/tracks",
        "method": "GET",
        "params": {
            "limit": 50,
            "market": "IE",
        },
        "data_selector": "items",
        "paginator": {
            "type": "offset",
            "limit": 50,
            "offset_param": "offset",
            "limit_param": "limit",
            "total_path": "total",
        },
    },
    "primary_key": "id",
    "write_disposition": "merge",
}

tracks_resource: dict[str, Any] = {
    "name": "tracks",
    "endpoint": {
        "path": "tracks",
        "method": "GET",
        "params": {
            "market": "IE",
        },
        "data_selector": "tracks",
    },
    "primary_key": "id",
    "write_disposition": "merge",
}

audio_features_resource: dict[str, Any] = {
    "name": "audio_features",
    "endpoint": {
        "path": "audio-features",
        "method": "GET",
        "data_selector": "audio_features",
    },
    "primary_key": "id",
    "write_disposition": "merge",
}

# Note: audio-features endpoint is deprecated but still works
# Provides: danceability, energy, key, loudness, mode, speechiness,
# acousticness, instrumentalness, liveness, valence, tempo, duration_ms

# Mapping of resource names to their configurations
SPOTIFY_RESOURCES: dict[str, dict[str, Any]] = {
    "artist": artist_resource,
    "albums": artist_albums_resource,
    "top_tracks": artist_top_tracks_resource,
    "album_tracks": album_tracks_resource,
    "tracks": tracks_resource,
    "audio_features": audio_features_resource,
}


def get_artist_endpoints(artist_id: str, include_artist: bool = True) -> list[dict[str, Any]]:
    """Get resource configurations for a specific artist.

    Args:
        artist_id: Spotify artist ID
        include_artist: Whether to include artist profile endpoint (default: True).
                       Set to False when using a custom resource for artist.

    Returns:
        List of resource configurations with path parameters filled in
    """
    resources = []

    # Artist profile (only if requested - single object endpoints need custom handling)
    if include_artist:
        artist = artist_resource.copy()
        endpoint = artist["endpoint"].copy()
        endpoint["path"] = endpoint["path"].format(artist_id=artist_id)
        artist["endpoint"] = endpoint
        resources.append(artist)

    # Artist albums
    albums = artist_albums_resource.copy()
    endpoint = albums["endpoint"].copy()
    endpoint["path"] = endpoint["path"].format(artist_id=artist_id)
    albums["endpoint"] = endpoint
    resources.append(albums)

    # Top tracks
    top = artist_top_tracks_resource.copy()
    endpoint = top["endpoint"].copy()
    endpoint["path"] = endpoint["path"].format(artist_id=artist_id)
    top["endpoint"] = endpoint
    resources.append(top)

    return resources
