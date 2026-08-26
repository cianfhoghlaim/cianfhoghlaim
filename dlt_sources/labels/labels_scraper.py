import dlt

"""Label Scraper using Firecrawl.

Scrapes artist profiles and releases from record label websites.
Uses Firecrawl for reliable extraction from JavaScript-heavy sites.

Usage:
    from pipelines.labels import label_source, scrape_all_labels

    # DLT pipeline
    pipeline = dlt.pipeline(
        pipeline_name="label_releases",
        destination="duckdb",
        dataset_name="label_data",
    )
    source = label_source(artist_slug="aleyum")
    pipeline.run(source)

    # Direct scraping
    async with LabelScraper() as scraper:
        profile = await scraper.scrape_monstercat("aleyum")
        print(profile.releases)
"""

import asyncio
import os
import re
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any

import dlt_sources
import httpx
from .labels_base import (
    LabelName,
    LabelProfile,
    LabelRelease,
    get_label_url,
    normalize_artwork_url,
)

# Firecrawl API configuration
FIRECRAWL_API_URL = os.environ.get("FIRECRAWL_API_URL", "https://api.firecrawl.dev/v1")
FIRECRAWL_API_KEY = os.environ.get("FIRECRAWL_API_KEY", "")


@dataclass
class FirecrawlResult:
    """Result from Firecrawl scrape."""

    markdown: str = ""
    html: str = ""
    metadata: dict[str, Any] | None = None
    links: list[str] | None = None
    success: bool = False
    error: str = ""


class LabelScraper:
    """Scraper for record label websites using Firecrawl."""

    def __init__(
        self,
        api_key: str = FIRECRAWL_API_KEY,
        api_url: str = FIRECRAWL_API_URL,
    ):
        """Initialize the scraper.

        Args:
            api_key: Firecrawl API key
            api_url: Firecrawl API base URL
        """
        self.api_key = api_key
        self.api_url = api_url
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self):
        """Async context manager entry."""
        self._client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=60.0,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _scrape(
        self,
        url: str,
        formats: list[str] | None = None,
        wait_for: int = 2000,
    ) -> FirecrawlResult:
        """Scrape a URL using Firecrawl.

        Args:
            url: URL to scrape
            formats: Output formats (markdown, html, links)
            wait_for: Time to wait for JS rendering (ms)

        Returns:
            FirecrawlResult with extracted content
        """
        if not self._client:
            raise RuntimeError("Scraper not initialized. Use async context manager.")

        if formats is None:
            formats = ["markdown", "html", "links"]

        try:
            response = await self._client.post(
                f"{self.api_url}/scrape",
                json={
                    "url": url,
                    "formats": formats,
                    "waitFor": wait_for,
                    "onlyMainContent": True,
                },
            )

            if response.status_code != 200:
                return FirecrawlResult(
                    success=False,
                    error=f"HTTP {response.status_code}: {response.text}",
                )

            data = response.json()
            if not data.get("success"):
                return FirecrawlResult(
                    success=False,
                    error=data.get("error", "Unknown error"),
                )

            result_data = data.get("data", {})
            return FirecrawlResult(
                markdown=result_data.get("markdown", ""),
                html=result_data.get("html", ""),
                metadata=result_data.get("metadata"),
                links=result_data.get("links"),
                success=True,
            )

        except Exception as e:
            return FirecrawlResult(success=False, error=str(e))

    async def _extract(
        self,
        urls: list[str],
        prompt: str,
        schema: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Extract structured data using Firecrawl LLM extraction.

        Args:
            urls: URLs to extract from
            prompt: Extraction prompt
            schema: JSON schema for output

        Returns:
            Extracted data
        """
        if not self._client:
            raise RuntimeError("Scraper not initialized. Use async context manager.")

        try:
            payload: dict[str, Any] = {
                "urls": urls,
                "prompt": prompt,
            }
            if schema:
                payload["schema"] = schema

            response = await self._client.post(
                f"{self.api_url}/extract",
                json=payload,
            )

            if response.status_code != 200:
                return {"error": f"HTTP {response.status_code}"}

            data = response.json()
            return data.get("data", {})

        except Exception as e:
            return {"error": str(e)}

    async def scrape_monstercat(self, artist_slug: str) -> LabelProfile:
        """Scrape artist profile from Monstercat.

        Args:
            artist_slug: Artist URL slug (e.g., 'aleyum')

        Returns:
            LabelProfile with releases
        """
        url = get_label_url(LabelName.MONSTERCAT, artist_slug)
        result = await self._scrape(url)

        if not result.success:
            raise Exception(f"Failed to scrape Monstercat: {result.error}")

        profile = LabelProfile(
            id=f"monstercat_{artist_slug}",
            artist_name=artist_slug.title(),
            label="monstercat",
            profile_url=url,
        )

        # Parse markdown content for releases
        releases = self._parse_monstercat_releases(result.markdown, artist_slug)
        profile.releases = releases
        profile.release_count = len(releases)

        # Extract metadata
        if result.metadata:
            profile.bio = result.metadata.get("description", "")
            profile.avatar_url = result.metadata.get("ogImage", "")

        return profile

    def _parse_monstercat_releases(
        self,
        markdown: str,
        artist_slug: str,
    ) -> list[LabelRelease]:
        """Parse releases from Monstercat page markdown.

        Args:
            markdown: Page content as markdown
            artist_slug: Artist slug for ID generation

        Returns:
            List of releases
        """
        releases = []

        # Monstercat pages list releases with titles, dates, and artwork
        # Pattern: ## Title or [Title](link)
        lines = markdown.split("\n")
        current_release: dict[str, Any] = {}

        for line in lines:
            line = line.strip()

            # Check for release title (usually h2 or link)
            title_match = re.match(r"##\s+(.+)", line)
            if title_match:
                if current_release.get("title"):
                    releases.append(self._create_release(current_release, artist_slug))
                current_release = {"title": title_match.group(1)}
                continue

            # Link with image (artwork)
            img_match = re.search(r"!\[.*?\]\(([^)]+)\)", line)
            if img_match and current_release:
                current_release["artwork_url"] = normalize_artwork_url(img_match.group(1))

            # Date pattern
            date_match = re.search(r"(\d{4}[-/]\d{2}[-/]\d{2}|\w+ \d{1,2}, \d{4})", line)
            if date_match and current_release:
                current_release["release_date"] = date_match.group(1)

            # Genre tags
            if "drum & bass" in line.lower() or "dnb" in line.lower():
                current_release.setdefault("genre", "Drum & Bass")
            elif "electronic" in line.lower():
                current_release.setdefault("genre", "Electronic")

        # Don't forget the last release
        if current_release.get("title"):
            releases.append(self._create_release(current_release, artist_slug))

        return releases

    async def scrape_lemongrass(self, artist_slug: str) -> LabelProfile:
        """Scrape artist profile from Lemongrass Music.

        Args:
            artist_slug: Artist URL slug

        Returns:
            LabelProfile with releases
        """
        url = get_label_url(LabelName.LEMONGRASS, artist_slug)
        result = await self._scrape(url)

        if not result.success:
            raise Exception(f"Failed to scrape Lemongrass: {result.error}")

        profile = LabelProfile(
            id=f"lemongrass_{artist_slug}",
            artist_name=artist_slug.title(),
            label="lemongrass",
            profile_url=url,
        )

        # Parse releases from markdown
        releases = self._parse_lemongrass_releases(result.markdown, artist_slug)
        profile.releases = releases
        profile.release_count = len(releases)

        if result.metadata:
            profile.bio = result.metadata.get("description", "")

        return profile

    def _parse_lemongrass_releases(
        self,
        markdown: str,
        artist_slug: str,
    ) -> list[LabelRelease]:
        """Parse releases from Lemongrass page markdown.

        Args:
            markdown: Page content as markdown
            artist_slug: Artist slug

        Returns:
            List of releases
        """
        releases = []

        # Lemongrass uses album covers and links
        # Look for image + title patterns
        album_pattern = re.compile(
            r"!\[([^\]]*)\]\(([^)]+)\).*?(?:\*\*|##)\s*([^*\n]+)",
            re.DOTALL,
        )

        for match in album_pattern.finditer(markdown):
            _alt_text, img_url, title = match.groups()
            release = LabelRelease(
                id=f"lemongrass_{artist_slug}_{self._slugify(title)}",
                title=title.strip(),
                artist=artist_slug.title(),
                label="lemongrass",
                artwork_url=normalize_artwork_url(img_url),
                genre="Chillout",  # Lemongrass specializes in chill/lounge
            )
            releases.append(release)

        return releases

    async def scrape_fokuz(self, artist_slug: str) -> LabelProfile:
        """Scrape artist profile from Fokuz Recordings.

        Fokuz is a liquid drum & bass label.

        Args:
            artist_slug: Artist URL slug

        Returns:
            LabelProfile with releases
        """
        url = get_label_url(LabelName.FOKUZ, artist_slug)
        result = await self._scrape(url)

        if not result.success:
            # Try alternative URL patterns
            alt_url = f"https://fokuzrecordings.com/artist/{artist_slug}/"
            result = await self._scrape(alt_url)
            if not result.success:
                raise Exception(f"Failed to scrape Fokuz: {result.error}")
            url = alt_url

        profile = LabelProfile(
            id=f"fokuz_{artist_slug}",
            artist_name=artist_slug.title(),
            label="fokuz",
            profile_url=url,
        )

        releases = self._parse_generic_releases(
            result.markdown,
            artist_slug,
            "fokuz",
            default_genre="Liquid Drum & Bass",
        )
        profile.releases = releases
        profile.release_count = len(releases)

        return profile

    async def scrape_bandcamp_label(
        self,
        label_url: str,
        artist_name: str,
    ) -> LabelProfile:
        """Scrape artist releases from a Bandcamp label page.

        Many smaller labels use Bandcamp. This extracts releases
        for a specific artist from the label's discography.

        Args:
            label_url: Bandcamp label URL (e.g., "https://souldeeprecordings.bandcamp.com")
            artist_name: Artist name to filter releases

        Returns:
            LabelProfile with releases
        """
        # Scrape the discography page
        disco_url = f"{label_url}/music"
        result = await self._scrape(disco_url)

        if not result.success:
            raise Exception(f"Failed to scrape Bandcamp: {result.error}")

        label_slug = label_url.split("//")[1].split(".")[0]

        profile = LabelProfile(
            id=f"bandcamp_{label_slug}_{self._slugify(artist_name)}",
            artist_name=artist_name,
            label=label_slug,
            profile_url=label_url,
        )

        # Parse releases and filter by artist
        releases = self._parse_bandcamp_releases(
            result.markdown,
            artist_name,
            label_slug,
        )
        profile.releases = releases
        profile.release_count = len(releases)

        return profile

    def _parse_bandcamp_releases(
        self,
        markdown: str,
        artist_name: str,
        label_slug: str,
    ) -> list[LabelRelease]:
        """Parse Bandcamp discography and filter by artist.

        Args:
            markdown: Page markdown content
            artist_name: Artist to filter by
            label_slug: Label identifier

        Returns:
            List of releases by the artist
        """
        releases = []
        artist_lower = artist_name.lower()

        # Bandcamp format: album covers with title links
        # Pattern: [![](image)](link) Title - Artist
        pattern = re.compile(
            r"!\[.*?\]\(([^)]+)\).*?\[([^\]]+)\]\(([^)]+)\)",
            re.MULTILINE,
        )

        for match in pattern.finditer(markdown):
            img_url, title, link = match.groups()

            # Check if this release is by our artist
            if artist_lower not in title.lower():
                # Also check nearby text
                context_start = max(0, match.start() - 100)
                context = markdown[context_start : match.end() + 100].lower()
                if artist_lower not in context:
                    continue

            # Clean up title (remove artist name if present)
            clean_title = re.sub(rf"\s*[-–]\s*{artist_name}\s*", "", title, flags=re.I)

            release = LabelRelease(
                id=f"bandcamp_{label_slug}_{self._slugify(clean_title)}",
                title=clean_title.strip() or title,
                artist=artist_name,
                label=label_slug,
                artwork_url=normalize_artwork_url(img_url),
                bandcamp_url=link if "bandcamp" in link else "",
                page_url=link,
            )
            releases.append(release)

        return releases

    def _parse_generic_releases(
        self,
        markdown: str,
        artist_slug: str,
        label_slug: str,
        default_genre: str = "",
    ) -> list[LabelRelease]:
        """Generic release parser for various label formats.

        Args:
            markdown: Page markdown content
            artist_slug: Artist identifier
            label_slug: Label identifier
            default_genre: Default genre for the label

        Returns:
            List of releases
        """
        releases = []

        # Look for common patterns: heading + image, or image + title
        sections = re.split(r"\n##\s+", markdown)

        for section in sections[1:]:  # Skip first (before first heading)
            lines = section.split("\n")
            if not lines:
                continue

            title = lines[0].strip()
            if not title or title.lower() in ["releases", "discography", "music"]:
                continue

            release_data = {
                "title": title,
                "genre": default_genre,
            }

            # Extract artwork from section
            img_match = re.search(r"!\[.*?\]\(([^)]+)\)", section)
            if img_match:
                release_data["artwork_url"] = normalize_artwork_url(img_match.group(1))

            # Extract date
            date_match = re.search(r"(\d{4}[-/]\d{2}[-/]\d{2})", section)
            if date_match:
                release_data["release_date"] = date_match.group(1)

            releases.append(self._create_release(release_data, artist_slug, label_slug))

        return releases

    def _create_release(
        self,
        data: dict[str, Any],
        artist_slug: str,
        label: str = "unknown",
    ) -> LabelRelease:
        """Create a LabelRelease from extracted data.

        Args:
            data: Extracted release data
            artist_slug: Artist identifier
            label: Label name

        Returns:
            LabelRelease instance
        """
        title = data.get("title", "Unknown")
        release_id = f"{label}_{artist_slug}_{self._slugify(title)}"

        return LabelRelease(
            id=release_id,
            title=title,
            artist=artist_slug.title(),
            label=label,
            release_type=data.get("release_type", "single"),
            release_date=data.get("release_date", ""),
            catalog_number=data.get("catalog_number", ""),
            artwork_url=data.get("artwork_url", ""),
            artwork_url_large=normalize_artwork_url(data.get("artwork_url", ""), "large"),
            genre=data.get("genre", ""),
            subgenre=data.get("subgenre", ""),
            bpm=data.get("bpm", 0),
            key=data.get("key", ""),
            duration_ms=data.get("duration_ms", 0),
            spotify_url=data.get("spotify_url", ""),
            beatport_url=data.get("beatport_url", ""),
            bandcamp_url=data.get("bandcamp_url", ""),
            description=data.get("description", ""),
            tags=data.get("tags", []),
            page_url=data.get("page_url", ""),
        )

    @staticmethod
    def _slugify(text: str) -> str:
        """Convert text to URL-safe slug.

        Args:
            text: Text to slugify

        Returns:
            Lowercase slug with hyphens
        """
        text = text.lower().strip()
        text = re.sub(r"[^\w\s-]", "", text)
        text = re.sub(r"[-\s]+", "-", text)
        return text[:50]  # Limit length


async def scrape_label(
    label: LabelName,
    artist_slug: str,
    api_key: str = FIRECRAWL_API_KEY,
) -> LabelProfile:
    """Scrape a specific label for artist data.

    Args:
        label: Label to scrape
        artist_slug: Artist URL slug
        api_key: Firecrawl API key

    Returns:
        LabelProfile with releases
    """
    async with LabelScraper(api_key=api_key) as scraper:
        if label == LabelName.MONSTERCAT:
            return await scraper.scrape_monstercat(artist_slug)
        elif label == LabelName.LEMONGRASS:
            return await scraper.scrape_lemongrass(artist_slug)
        elif label == LabelName.FOKUZ:
            return await scraper.scrape_fokuz(artist_slug)
        else:
            raise ValueError(f"Unsupported label: {label}")


async def scrape_all_labels(
    artist_slug: str,
    labels: list[LabelName] | None = None,
    api_key: str = FIRECRAWL_API_KEY,
) -> list[LabelProfile]:
    """Scrape all supported labels for artist data.

    Args:
        artist_slug: Artist URL slug
        labels: Labels to scrape (default: all)
        api_key: Firecrawl API key

    Returns:
        List of profiles from each label
    """
    if labels is None:
        labels = [LabelName.MONSTERCAT, LabelName.LEMONGRASS]

    profiles = []
    async with LabelScraper(api_key=api_key) as scraper:
        for label in labels:
            try:
                if label == LabelName.MONSTERCAT:
                    profile = await scraper.scrape_monstercat(artist_slug)
                elif label == LabelName.LEMONGRASS:
                    profile = await scraper.scrape_lemongrass(artist_slug)
                elif label == LabelName.FOKUZ:
                    profile = await scraper.scrape_fokuz(artist_slug)
                else:
                    continue

                profiles.append(profile)
            except Exception as e:
                print(f"Warning: Failed to scrape {label.value}: {e}")

    return profiles


# DLT Source and Resources


@dlt.source(name="label_scraper")
def label_source(
    artist_slug: str = "aleyum",
    labels: list[str] | None = None,
) -> Iterator[Any]:
    """DLT source for label data.

    Args:
        artist_slug: Artist URL slug
        labels: Label names to scrape (default: all supported)

    Yields:
        DLT resources for profiles and releases
    """
    # Convert string labels to enum
    label_enums: list[LabelName] = []
    if labels:
        for label_str in labels:
            try:
                label_enums.append(LabelName(label_str.lower()))
            except ValueError:
                print(f"Warning: Unknown label {label_str}")
    else:
        label_enums = [LabelName.MONSTERCAT, LabelName.LEMONGRASS]

    @dlt.resource(name="profiles", write_disposition="merge", primary_key="id")
    def get_profiles() -> Iterator[dict[str, Any]]:
        """Fetch artist profiles from labels."""
        profiles = asyncio.run(scrape_all_labels(artist_slug, label_enums))
        for profile in profiles:
            yield profile.to_dict()

    @dlt.resource(name="releases", write_disposition="merge", primary_key="id")
    def get_releases() -> Iterator[dict[str, Any]]:
        """Fetch releases from all labels."""
        profiles = asyncio.run(scrape_all_labels(artist_slug, label_enums))
        for profile in profiles:
            for release in profile.releases:
                yield release.to_dict()

    @dlt.resource(name="artwork", write_disposition="merge", primary_key="url")
    def get_artwork() -> Iterator[dict[str, Any]]:
        """Extract artwork URLs for caching."""
        profiles = asyncio.run(scrape_all_labels(artist_slug, label_enums))
        seen_urls: set[str] = set()

        for profile in profiles:
            # Profile artwork
            if profile.avatar_url and profile.avatar_url not in seen_urls:
                seen_urls.add(profile.avatar_url)
                yield {
                    "url": profile.avatar_url,
                    "entity_id": profile.id,
                    "entity_type": "profile_avatar",
                    "label": profile.label,
                }

            # Release artwork
            for release in profile.releases:
                if release.artwork_url and release.artwork_url not in seen_urls:
                    seen_urls.add(release.artwork_url)
                    yield {
                        "url": release.artwork_url,
                        "url_large": release.artwork_url_large,
                        "entity_id": release.id,
                        "entity_type": "release",
                        "label": release.label,
                        "release_title": release.title,
                    }

    yield get_profiles
    yield get_releases
    yield get_artwork


def run_labels_pipeline(
    artist_slug: str = "aleyum",
    labels: list[str] | None = None,
    destination: str | Any | None = None,
    dataset_name: str = "label_data",
) -> Any:
    """Run the labels scraping pipeline.

    Args:
        artist_slug: Artist URL slug
        labels: Labels to scrape
        destination: DLT destination (default: DuckLake via shared factory)
        dataset_name: Dataset name

    Returns:
        LoadInfo from the pipeline run
    """
    # Use shared destination factory for concurrency-safe DuckLake
    if destination is None:
        from dlt_utils import get_dlt_destination
        destination = get_dlt_destination()

    pipeline = dlt.pipeline(
        pipeline_name=f"labels_{artist_slug}",
        destination=destination,
        dataset_name=dataset_name,
        progress="log",
    )

    source = label_source(artist_slug=artist_slug, labels=labels)
    load_info = pipeline.run(source)

    print(load_info)
    return load_info


if __name__ == "__main__":
    # Example usage
    load_info = run_labels_pipeline(
        artist_slug="aleyum",
        labels=["monstercat", "lemongrass"],
    )
