"""SoundCloud Scraper.

Crawl4AI-based scraper for extracting SoundCloud profile data.
Since SoundCloud doesn't have a public API, we scrape the profile page
to extract track metadata, play counts, likes, and comments.

Usage:
    from pipelines.soundcloud import scrape_soundcloud_profile

    data = await scrape_soundcloud_profile("aleyummusic")
"""

import asyncio
import json
import re
from dataclasses import dataclass, field
from typing import Any

import dlt


# SoundCloud profile URL for Aleyum
ALEYUM_SOUNDCLOUD_URL = "https://soundcloud.com/aleyummusic"


@dataclass
class SoundCloudTrack:
    """Extracted SoundCloud track data."""

    id: str
    title: str
    permalink_url: str
    duration_ms: int = 0
    playback_count: int = 0
    likes_count: int = 0
    reposts_count: int = 0
    comment_count: int = 0
    genre: str = ""
    tag_list: str = ""
    description: str = ""
    artwork_url: str = ""
    waveform_url: str = ""
    stream_url: str = ""
    created_at: str = ""
    user_id: str = ""


@dataclass
class SoundCloudProfile:
    """Extracted SoundCloud profile data."""

    id: str
    username: str
    permalink_url: str
    full_name: str = ""
    description: str = ""
    avatar_url: str = ""
    followers_count: int = 0
    followings_count: int = 0
    track_count: int = 0
    playlist_count: int = 0
    likes_count: int = 0
    city: str = ""
    country: str = ""
    tracks: list[SoundCloudTrack] = field(default_factory=list)


class SoundCloudScraper:
    """Scraper for SoundCloud using Crawl4AI."""

    def __init__(self, headless: bool = True):
        """Initialize the scraper.

        Args:
            headless: Run browser in headless mode
        """
        self.headless = headless
        self._crawler = None

    async def _get_crawler(self) -> Any:
        """Lazy-initialize the Crawl4AI crawler."""
        if self._crawler is None:
            from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

            browser_config = BrowserConfig(
                headless=self.headless,
                # Use stealth mode to avoid detection
                extra_args=["--disable-blink-features=AutomationControlled"],
            )

            self._crawler = AsyncWebCrawler(config=browser_config)
            await self._crawler.start()

        return self._crawler

    async def close(self) -> None:
        """Close the crawler."""
        if self._crawler:
            await self._crawler.close()
            self._crawler = None

    async def scrape_profile(self, username: str) -> SoundCloudProfile:
        """Scrape a SoundCloud user profile.

        Args:
            username: SoundCloud username

        Returns:
            SoundCloudProfile with extracted data
        """
        from crawl4ai import CrawlerRunConfig
        from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

        crawler = await self._get_crawler()
        url = f"https://soundcloud.com/{username}"

        # Define extraction schema for profile data
        # SoundCloud loads data via JavaScript, so we need to wait for it
        run_config = CrawlerRunConfig(
            wait_for="css:.userMain",  # Wait for main profile content
            js_code="""
                // Scroll to load all tracks
                window.scrollTo(0, document.body.scrollHeight);
            """,
            delay_before_return_html=2.0,  # Wait for content to load after scroll
        )

        result = await crawler.arun(url=url, config=run_config)

        if not result.success:
            raise Exception(f"Failed to scrape profile: {result.error_message}")

        # Extract data from the page
        profile = self._parse_profile_html(result.html, username)

        # Try to extract from embedded JSON (SoundCloud hydrates data)
        if result.html:
            json_data = self._extract_hydration_data(result.html)
            if json_data:
                profile = self._merge_json_data(profile, json_data)

        return profile

    async def scrape_tracks(self, username: str, limit: int = 50) -> list[SoundCloudTrack]:
        """Scrape tracks from a SoundCloud profile.

        Args:
            username: SoundCloud username
            limit: Maximum number of tracks to fetch

        Returns:
            List of SoundCloudTrack objects
        """
        from crawl4ai import CrawlerRunConfig

        crawler = await self._get_crawler()
        url = f"https://soundcloud.com/{username}/tracks"

        # Scroll to load more tracks
        # Note: Crawl4AI js_code doesn't support await/async, so we use synchronous scrolling
        scroll_count = max(1, limit // 10)
        run_config = CrawlerRunConfig(
            wait_for="css:.soundList__item",
            js_code=f"""
                // Scroll to bottom to trigger lazy loading
                window.scrollTo(0, document.body.scrollHeight);
            """,
            delay_before_return_html=2.0 * scroll_count,  # Wait for content to load
        )

        result = await crawler.arun(url=url, config=run_config)

        if not result.success:
            raise Exception(f"Failed to scrape tracks: {result.error_message}")

        tracks = self._parse_tracks_html(result.html)

        # Try to get more data from hydration
        json_data = self._extract_hydration_data(result.html)
        if json_data:
            tracks = self._enrich_tracks_from_json(tracks, json_data)

        return tracks[:limit]

    def _extract_hydration_data(self, html: str) -> dict[str, Any] | None:
        """Extract hydration data from SoundCloud page.

        SoundCloud embeds JSON data in script tags for hydration.

        Args:
            html: Page HTML

        Returns:
            Extracted JSON data or None
        """
        # Look for hydration script
        pattern = r"<script>window\.__sc_hydration\s*=\s*(\[.*?\]);</script>"
        match = re.search(pattern, html, re.DOTALL)

        if match:
            try:
                data = json.loads(match.group(1))
                return {"hydration": data}
            except json.JSONDecodeError:
                pass

        # Also try to find JSON-LD data
        pattern = r'<script type="application/ld\+json">(.*?)</script>'
        match = re.search(pattern, html, re.DOTALL)

        if match:
            try:
                return {"ld_json": json.loads(match.group(1))}
            except json.JSONDecodeError:
                pass

        return None

    def _parse_profile_html(self, html: str, username: str) -> SoundCloudProfile:
        """Parse profile data from HTML.

        Args:
            html: Page HTML
            username: Username for fallback

        Returns:
            SoundCloudProfile with basic data
        """
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "html.parser")

        profile = SoundCloudProfile(
            id="",
            username=username,
            permalink_url=f"https://soundcloud.com/{username}",
        )

        # Extract profile info
        name_elem = soup.select_one(".profileHeaderInfo__userName")
        if name_elem:
            profile.full_name = name_elem.get_text(strip=True)

        bio_elem = soup.select_one(".truncatedUserDescription__content")
        if bio_elem:
            profile.description = bio_elem.get_text(strip=True)

        avatar_elem = soup.select_one(".profileHeaderInfo__avatar span")
        if avatar_elem and avatar_elem.get("style"):
            # Extract URL from background-image style
            style = avatar_elem.get("style", "")
            url_match = re.search(r'url\("([^"]+)"\)', style)
            if url_match:
                profile.avatar_url = url_match.group(1)

        # Extract follower count
        followers_elem = soup.select_one('.infoStats__statLink[href*="followers"]')
        if followers_elem:
            count_text = followers_elem.get_text(strip=True)
            profile.followers_count = self._parse_count(count_text)

        return profile

    def _parse_tracks_html(self, html: str) -> list[SoundCloudTrack]:
        """Parse tracks from HTML.

        Args:
            html: Page HTML

        Returns:
            List of SoundCloudTrack objects
        """
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "html.parser")
        tracks = []

        for item in soup.select(".soundList__item"):
            track = SoundCloudTrack(
                id="",
                title="",
                permalink_url="",
            )

            # Extract title and URL
            title_elem = item.select_one(".soundTitle__title")
            if title_elem:
                track.title = title_elem.get_text(strip=True)
                href = title_elem.get("href", "")
                if href:
                    track.permalink_url = f"https://soundcloud.com{href}"

            # Extract play count
            plays_elem = item.select_one(".sc-ministats-item[title*='plays']")
            if plays_elem:
                track.playback_count = self._parse_count(plays_elem.get_text(strip=True))

            # Extract likes
            likes_elem = item.select_one(".sc-ministats-item[title*='likes']")
            if likes_elem:
                track.likes_count = self._parse_count(likes_elem.get_text(strip=True))

            # Extract artwork
            artwork_elem = item.select_one(".sound__coverArt span")
            if artwork_elem and artwork_elem.get("style"):
                style = artwork_elem.get("style", "")
                url_match = re.search(r'url\("([^"]+)"\)', style)
                if url_match:
                    track.artwork_url = url_match.group(1)

            if track.title:
                tracks.append(track)

        return tracks

    def _merge_json_data(
        self, profile: SoundCloudProfile, json_data: dict[str, Any]
    ) -> SoundCloudProfile:
        """Merge JSON hydration data into profile.

        Args:
            profile: Existing profile
            json_data: Extracted JSON data

        Returns:
            Updated profile
        """
        if "hydration" in json_data:
            for item in json_data["hydration"]:
                if item.get("hydratable") == "user":
                    user_data = item.get("data", {})
                    profile.id = str(user_data.get("id", ""))
                    profile.full_name = user_data.get("full_name", profile.full_name)
                    profile.description = user_data.get("description", profile.description)
                    profile.avatar_url = user_data.get("avatar_url", profile.avatar_url)
                    profile.followers_count = user_data.get(
                        "followers_count", profile.followers_count
                    )
                    profile.track_count = user_data.get("track_count", 0)
                    profile.city = user_data.get("city", "")
                    profile.country = user_data.get("country_code", "")

        return profile

    def _enrich_tracks_from_json(
        self, tracks: list[SoundCloudTrack], json_data: dict[str, Any]
    ) -> list[SoundCloudTrack]:
        """Enrich track data from JSON hydration.

        Args:
            tracks: Existing tracks
            json_data: Extracted JSON data

        Returns:
            Updated tracks list
        """
        if "hydration" not in json_data:
            return tracks

        # Build lookup by title
        track_lookup = {t.title.lower(): t for t in tracks}

        for item in json_data["hydration"]:
            if item.get("hydratable") == "sound":
                sound_data = item.get("data", {})
                title = sound_data.get("title", "").lower()

                if title in track_lookup:
                    track = track_lookup[title]
                    track.id = str(sound_data.get("id", ""))
                    track.duration_ms = sound_data.get("duration", 0)
                    track.playback_count = sound_data.get("playback_count", track.playback_count)
                    track.likes_count = sound_data.get("likes_count", track.likes_count)
                    track.reposts_count = sound_data.get("reposts_count", 0)
                    track.comment_count = sound_data.get("comment_count", 0)
                    track.genre = sound_data.get("genre", "")
                    track.tag_list = sound_data.get("tag_list", "")
                    track.description = sound_data.get("description", "")
                    track.artwork_url = sound_data.get("artwork_url", track.artwork_url)
                    track.waveform_url = sound_data.get("waveform_url", "")
                    track.created_at = sound_data.get("created_at", "")

        return tracks

    @staticmethod
    def _parse_count(text: str) -> int:
        """Parse count text like '1.2K' or '500' to integer.

        Args:
            text: Count text

        Returns:
            Integer count
        """
        text = text.strip().upper()
        if not text:
            return 0

        # Remove commas
        text = text.replace(",", "")

        # Handle K, M suffixes
        multiplier = 1
        if text.endswith("K"):
            multiplier = 1000
            text = text[:-1]
        elif text.endswith("M"):
            multiplier = 1000000
            text = text[:-1]

        try:
            return int(float(text) * multiplier)
        except ValueError:
            return 0


@dlt.source(name="soundcloud_scraper")
def soundcloud_source(username: str = "aleyummusic"):
    """DLT source for SoundCloud data.

    Args:
        username: SoundCloud username

    Yields:
        DLT resources for profile and tracks
    """

    @dlt.resource(name="profile", write_disposition="merge", primary_key="id")
    def get_profile():
        """Fetch SoundCloud profile."""

        async def _fetch_profile():
            scraper = SoundCloudScraper()
            try:
                return await scraper.scrape_profile(username)
            finally:
                await scraper.close()

        profile = asyncio.run(_fetch_profile())
        yield {
            "id": profile.id,
            "username": profile.username,
            "permalink_url": profile.permalink_url,
            "full_name": profile.full_name,
            "description": profile.description,
            "avatar_url": profile.avatar_url,
            "followers_count": profile.followers_count,
            "followings_count": profile.followings_count,
            "track_count": profile.track_count,
            "city": profile.city,
            "country": profile.country,
        }

    @dlt.resource(name="tracks", write_disposition="merge", primary_key="id")
    def get_tracks():
        """Fetch SoundCloud tracks."""

        async def _fetch_tracks():
            scraper = SoundCloudScraper()
            try:
                return await scraper.scrape_tracks(username)
            finally:
                await scraper.close()

        tracks = asyncio.run(_fetch_tracks())
        for track in tracks:
            yield {
                "id": track.id,
                "title": track.title,
                "permalink_url": track.permalink_url,
                "duration_ms": track.duration_ms,
                "playback_count": track.playback_count,
                "likes_count": track.likes_count,
                "reposts_count": track.reposts_count,
                "comment_count": track.comment_count,
                "genre": track.genre,
                "tag_list": track.tag_list,
                "description": track.description,
                "artwork_url": track.artwork_url,
                "waveform_url": track.waveform_url,
                "created_at": track.created_at,
            }

    yield get_profile
    yield get_tracks


async def scrape_soundcloud_profile(username: str = "aleyummusic") -> SoundCloudProfile:
    """Convenience function to scrape a SoundCloud profile.

    Args:
        username: SoundCloud username

    Returns:
        SoundCloudProfile with full data
    """
    scraper = SoundCloudScraper()
    try:
        profile = await scraper.scrape_profile(username)
        profile.tracks = await scraper.scrape_tracks(username)
        return profile
    finally:
        await scraper.close()


def run_soundcloud_pipeline(
    username: str = "aleyummusic",
    destination: str | dlt.destinations.Destination | None = None,
    dataset_name: str = "soundcloud_data",
) -> Any:
    """Run the SoundCloud scraping pipeline.

    Args:
        username: SoundCloud username
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
        pipeline_name=f"soundcloud_{username}",
        destination=destination,
        dataset_name=dataset_name,
        progress="log",
    )

    source = soundcloud_source(username=username)
    load_info = pipeline.run(source)

    print(load_info)
    return load_info


if __name__ == "__main__":
    # Example usage
    load_info = run_soundcloud_pipeline(username="aleyummusic")
