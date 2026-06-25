"""Base classes for label scrapers.

Provides shared dataclasses and utilities for extracting data
from record label websites.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class LabelName(str, Enum):
    """Supported record labels."""

    MONSTERCAT = "monstercat"
    LEMONGRASS = "lemongrass"
    FOKUZ = "fokuz"
    IMMERSED = "immersed"
    OFFWORLD = "offworld"
    SOUL_DEEP = "soul_deep"


@dataclass
class LabelRelease:
    """A release (single, EP, album) from a label."""

    id: str
    title: str
    artist: str
    label: str
    release_type: str = "single"  # single, ep, album, remix
    release_date: str = ""
    catalog_number: str = ""
    artwork_url: str = ""
    artwork_url_large: str = ""
    genre: str = ""
    subgenre: str = ""
    bpm: int = 0
    key: str = ""
    duration_ms: int = 0
    isrc: str = ""
    upc: str = ""
    spotify_url: str = ""
    beatport_url: str = ""
    bandcamp_url: str = ""
    description: str = ""
    tracks: list[dict[str, Any]] = field(default_factory=list)
    credits: dict[str, str] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    page_url: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for DLT."""
        return {
            "id": self.id,
            "title": self.title,
            "artist": self.artist,
            "label": self.label,
            "release_type": self.release_type,
            "release_date": self.release_date,
            "catalog_number": self.catalog_number,
            "artwork_url": self.artwork_url,
            "artwork_url_large": self.artwork_url_large,
            "genre": self.genre,
            "subgenre": self.subgenre,
            "bpm": self.bpm,
            "key": self.key,
            "duration_ms": self.duration_ms,
            "isrc": self.isrc,
            "upc": self.upc,
            "spotify_url": self.spotify_url,
            "beatport_url": self.beatport_url,
            "bandcamp_url": self.bandcamp_url,
            "description": self.description,
            "tracks": self.tracks,
            "credits": self.credits,
            "tags": self.tags,
            "page_url": self.page_url,
        }


@dataclass
class LabelProfile:
    """Artist profile on a label's website."""

    id: str
    artist_name: str
    label: str
    profile_url: str
    bio: str = ""
    avatar_url: str = ""
    banner_url: str = ""
    location: str = ""
    genres: list[str] = field(default_factory=list)
    social_links: dict[str, str] = field(default_factory=dict)
    release_count: int = 0
    releases: list[LabelRelease] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for DLT."""
        return {
            "id": self.id,
            "artist_name": self.artist_name,
            "label": self.label,
            "profile_url": self.profile_url,
            "bio": self.bio,
            "avatar_url": self.avatar_url,
            "banner_url": self.banner_url,
            "location": self.location,
            "genres": self.genres,
            "social_links": self.social_links,
            "release_count": self.release_count,
        }


# Label URL templates
LABEL_URLS = {
    LabelName.MONSTERCAT: "https://www.monstercat.com/artist/{slug}",
    LabelName.LEMONGRASS: "https://lemongrassmusic.de/artists/{slug}/",
    LabelName.FOKUZ: "https://www.fokuzrecordings.com/artists/{slug}/",
    LabelName.IMMERSED: "https://www.immersedrec.com/artists/{slug}/",
    LabelName.OFFWORLD: "https://offworldrecordings.com/artists/{slug}/",
    LabelName.SOUL_DEEP: "https://souldeeprecordings.com/artists/{slug}/",
}


def get_label_url(label: LabelName, slug: str) -> str:
    """Get the artist page URL for a label.

    Args:
        label: Label enum value
        slug: Artist slug/username

    Returns:
        Full URL to artist page
    """
    template = LABEL_URLS.get(label)
    if not template:
        raise ValueError(f"Unknown label: {label}")
    return template.format(slug=slug)


def normalize_artwork_url(url: str, size: str = "large") -> str:
    """Normalize artwork URL to get highest quality version.

    Different labels use different CDN patterns. This normalizes
    to get the largest available image.

    Args:
        url: Original artwork URL
        size: Desired size (small, medium, large)

    Returns:
        Normalized URL
    """
    if not url:
        return ""

    # Monstercat uses Imgix
    if "monstercat" in url or "imgix" in url:
        # Remove existing size params and add large
        if "?" in url:
            url = url.split("?")[0]
        return f"{url}?w=1400&h=1400&fit=crop&auto=format"

    # Many labels use Cloudinary
    if "cloudinary" in url:
        # Transform to get large version
        url = url.replace("/upload/", "/upload/w_1400,h_1400,c_fill/")
        return url

    # Bandcamp pattern
    if "bcbits" in url or "bandcamp" in url:
        # Replace _10 or _16 suffixes with _0 for original
        import re

        url = re.sub(r"_\d+\.jpg$", "_0.jpg", url)
        return url

    return url


def parse_duration(duration_str: str) -> int:
    """Parse duration string to milliseconds.

    Handles formats like:
        - "3:45" (mm:ss)
        - "1:23:45" (hh:mm:ss)
        - "225" (seconds)
        - "225000" (milliseconds)

    Args:
        duration_str: Duration string

    Returns:
        Duration in milliseconds
    """
    if not duration_str:
        return 0

    duration_str = duration_str.strip()

    # Already in ms (large number)
    if duration_str.isdigit() and len(duration_str) > 5:
        return int(duration_str)

    # Just seconds
    if duration_str.isdigit():
        return int(duration_str) * 1000

    # mm:ss or hh:mm:ss format
    parts = duration_str.split(":")
    if len(parts) == 2:
        minutes, seconds = map(int, parts)
        return (minutes * 60 + seconds) * 1000
    elif len(parts) == 3:
        hours, minutes, seconds = map(int, parts)
        return (hours * 3600 + minutes * 60 + seconds) * 1000

    return 0
