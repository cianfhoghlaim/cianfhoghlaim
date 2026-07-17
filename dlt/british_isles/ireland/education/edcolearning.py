"""
DLT Source for EdcoLearning.ie Exam Audio Resources.

Extracts:
- Leaving Certificate exam audio (Irish, French, German, Spanish)
- Accompanying transcripts and scripts
- Audio metadata (year, level, language, paper type)

Authentication:
- Requires EdcoLearning.ie credentials
- Session-based authentication
- Credentials from 1Password or environment variables

Audio storage:
- Azure Blob: https://edconorth.blob.core.windows.net/resourcespublic/
- Organized by book ID (e.g., book1760)
"""
from __future__ import annotations

import hashlib
import os
import re
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

import dlt
from bs4 import BeautifulSoup
from dlt.sources import DltResource
from observability.logging import get_logger
from cianfhoghlaim.dlt.common._http_factories import HttpClientFactory

logger = get_logger(__name__)

# Base URLs
EDCOLEARNING_BASE = "https://edcolearning.ie"
EDCOLEARNING_API = "https://edcolearning.ie"
AZURE_BLOB_BASE = "https://edconorth.blob.core.windows.net/resourcespublic"


class ExamLevel(StrEnum):
    """Irish examination levels."""

    LEAVING_CERT = "leaving_certificate"
    JUNIOR_CYCLE = "junior_cycle"
    TRANSITION_YEAR = "transition_year"


class ExamSubject(StrEnum):
    """Subjects with oral/aural exams."""

    IRISH = "irish"
    FRENCH = "french"
    GERMAN = "german"
    SPANISH = "spanish"
    MUSIC = "music"


@dataclass
class EdcoCredentials:
    """EdcoLearning.ie authentication credentials."""

    username: str
    password: str

    @classmethod
    def from_env(cls) -> EdcoCredentials:
        """Load credentials from environment variables."""
        username = os.environ.get("EDCOLEARNING_USERNAME")
        password = os.environ.get("EDCOLEARNING_PASSWORD")

        if not username or not password:
            raise ValueError(
                "EDCOLEARNING_USERNAME and EDCOLEARNING_PASSWORD environment variables required"
            )

        return cls(username=username, password=password)

    @classmethod
    def from_1password(cls, item_name: str = "edcolearning") -> EdcoCredentials:
        """Load credentials from 1Password."""
        try:
            import subprocess

            result = subprocess.run(
                ["op", "item", "get", item_name, "--format=json"],
                capture_output=True,
                text=True,
                check=True,
            )
            import json

            item = json.loads(result.stdout)

            username = None
            password = None
            for field in item.get("fields", []):
                if field.get("id") == "username":
                    username = field.get("value")
                elif field.get("id") == "password":
                    password = field.get("value")

            if not username or not password:
                raise ValueError(f"Could not find username/password in 1Password item: {item_name}")

            return cls(username=username, password=password)

        except subprocess.CalledProcessError as e:
            raise ValueError(f"Failed to fetch from 1Password: {e.stderr}") from e


def _edcolearning_client() -> HttpClientFactory:
    """Create HTTP client factory for EdcoLearning.ie."""
    return HttpClientFactory(
        base_url=EDCOLEARNING_BASE,
        rate_limit=2.0,  # Conservative for authenticated scraping
        user_agent="cianfhoghlaim-dlt/1.0",
        timeout=60.0,
    )


def _authenticate_session(
    client: HttpClientFactory,
    credentials: EdcoCredentials,
) -> dict[str, str]:
    """
    Authenticate with EdcoLearning.ie and return session cookies.

    Returns:
        Dict of session cookies for subsequent requests
    """
    with client.create_client() as http:
        # Get login page to extract CSRF token
        login_page = http.get("/login")
        login_page.raise_for_status()

        soup = BeautifulSoup(login_page.text, "html.parser")
        csrf_token = None

        # Look for CSRF token in form
        csrf_input = soup.find("input", {"name": "_token"})
        if csrf_input:
            csrf_token = csrf_input.get("value")

        # Submit login form
        login_data = {
            "email": credentials.username,
            "password": credentials.password,
        }
        if csrf_token:
            login_data["_token"] = csrf_token

        response = http.post(
            "/login",
            data=login_data,
            follow_redirects=True,
        )

        if response.status_code >= 400:
            raise ValueError(f"Login failed with status {response.status_code}")

        # Check for successful login
        if "login" in str(response.url).lower() or "error" in response.text.lower():
            raise ValueError("Login failed - check credentials")

        # Extract session cookies
        return dict(response.cookies)


def _extract_book_id(url: str) -> str | None:
    """Extract book ID from EdcoLearning URL."""
    match = re.search(r"book(\d+)", url)
    return f"book{match.group(1)}" if match else None


def _extract_chapter_id(url: str) -> str | None:
    """Extract chapter ID from URL."""
    match = re.search(r"chapter(\d+)", url)
    return f"chapter{match.group(1)}" if match else None


def _parse_exam_metadata(title: str, url: str) -> dict[str, Any]:
    """
    Parse exam metadata from title and URL.

    Returns dict with:
        - year: Exam year
        - level: OL/HL
        - paper_type: Paper 1, Paper 2, etc.
        - language: Target language code
    """
    metadata: dict[str, Any] = {
        "year": None,
        "level": None,
        "paper_type": None,
        "language": None,
    }

    # Extract year (e.g., 2024, 2025)
    year_match = re.search(r"20\d{2}", title)
    if year_match:
        metadata["year"] = int(year_match.group())

    # Extract level (OL/HL)
    if "HL" in title.upper() or "Higher" in title:
        metadata["level"] = "higher"
    elif "OL" in title.upper() or "Ordinary" in title:
        metadata["level"] = "ordinary"

    # Extract paper type
    paper_match = re.search(r"Paper\s*(\d+)", title, re.IGNORECASE)
    if paper_match:
        metadata["paper_type"] = f"paper_{paper_match.group(1)}"

    # Detect language from URL or title
    url_lower = url.lower()
    title_lower = title.lower()

    if "irish" in url_lower or "gaeilge" in title_lower:
        metadata["language"] = "ga"
    elif "french" in url_lower or "français" in title_lower or "francais" in title_lower:
        metadata["language"] = "fr"
    elif "german" in url_lower or "deutsch" in title_lower:
        metadata["language"] = "de"
    elif "spanish" in url_lower or "español" in title_lower or "espanol" in title_lower:
        metadata["language"] = "es"
    elif "music" in url_lower:
        metadata["language"] = "music"

    return metadata


def _extract_audio_links(
    soup: BeautifulSoup,
    book_id: str,
) -> Iterator[dict[str, Any]]:
    """Extract audio file links from a book page."""
    # Look for audio elements
    for audio in soup.find_all("audio"):
        source = audio.find("source")
        if source and source.get("src"):
            audio_url = source["src"]
            if not audio_url.startswith("http"):
                audio_url = f"{AZURE_BLOB_BASE}/{book_id}/{audio_url}"

            title = audio.get("title", "") or audio.parent.get_text(strip=True)[:100]

            yield {
                "audio_url": audio_url,
                "title": title,
                "format": "mp3",
            }

    # Look for direct audio links
    for link in soup.find_all("a", href=re.compile(r"\.(mp3|wav|m4a|ogg)$", re.I)):
        audio_url = link["href"]
        if not audio_url.startswith("http"):
            audio_url = f"{AZURE_BLOB_BASE}/{book_id}/{audio_url}"

        yield {
            "audio_url": audio_url,
            "title": link.get_text(strip=True),
            "format": audio_url.split(".")[-1].lower(),
        }


def _extract_transcript_links(
    soup: BeautifulSoup,
    book_id: str,
) -> Iterator[dict[str, Any]]:
    """Extract transcript/script PDF links from a book page."""
    for link in soup.find_all("a", href=re.compile(r"\.pdf$", re.I)):
        pdf_url = link["href"]
        if not pdf_url.startswith("http"):
            pdf_url = f"{AZURE_BLOB_BASE}/{book_id}/{pdf_url}"

        title = link.get_text(strip=True)

        # Check if this is a transcript/script
        is_transcript = any(
            keyword in title.lower()
            for keyword in ["script", "transcript", "text", "téacs", "scriopt"]
        )

        yield {
            "pdf_url": pdf_url,
            "title": title,
            "is_transcript": is_transcript,
            "format": "pdf",
        }


def _discover_exam_books(
    client: HttpClientFactory,
    cookies: dict[str, str],
    subject: ExamSubject,
    level: ExamLevel = ExamLevel.LEAVING_CERT,
) -> Iterator[dict[str, Any]]:
    """
    Discover available exam audio books for a subject.

    Yields dict with:
        - book_id: Book identifier
        - title: Book title
        - url: Book page URL
        - subject: Subject code
        - level: Exam level
    """
    with client.create_client() as http:
        # Navigate to exam audio section
        subject_paths = {
            ExamSubject.IRISH: "irish",
            ExamSubject.FRENCH: "french",
            ExamSubject.GERMAN: "german",
            ExamSubject.SPANISH: "spanish",
            ExamSubject.MUSIC: "music",
        }

        level_paths = {
            ExamLevel.LEAVING_CERT: "lc",
            ExamLevel.JUNIOR_CYCLE: "jc",
            ExamLevel.TRANSITION_YEAR: "ty",
        }

        # Try different URL patterns
        url_patterns = [
            f"/examaudio?subject={subject_paths[subject]}&level={level_paths[level]}",
            f"/examaudio/{subject_paths[subject]}/{level_paths[level]}",
            f"/exam-audio/{level_paths[level]}/{subject_paths[subject]}",
        ]

        for url in url_patterns:
            try:
                response = http.get(url, cookies=cookies)
                if response.status_code == 200:
                    break
            except Exception:
                continue
        else:
            # Fall back to main exam audio page
            response = http.get("/examaudio", cookies=cookies)

        if response.status_code != 200:
            logger.warning(
                "edcolearning_books_error",
                subject=subject.value,
                status=response.status_code,
            )
            return

        soup = BeautifulSoup(response.text, "html.parser")

        # Find book links
        for link in soup.find_all("a", href=re.compile(r"book\d+")):
            book_url = link["href"]
            book_id = _extract_book_id(book_url)

            if not book_id:
                continue

            if not book_url.startswith("http"):
                book_url = f"{EDCOLEARNING_BASE}{book_url}"

            title = link.get_text(strip=True) or f"{subject.value} Exam Audio"

            yield {
                "book_id": book_id,
                "title": title,
                "url": book_url,
                "subject": subject.value,
                "level": level.value,
            }


def _scrape_book_audio(
    client: HttpClientFactory,
    cookies: dict[str, str],
    book_id: str,
    book_url: str,
) -> Iterator[dict[str, Any]]:
    """
    Scrape audio files from a specific book.

    Yields dict with:
        - book_id: Book identifier
        - audio_url: Direct URL to audio file
        - title: Audio title
        - chapter_id: Chapter identifier if available
        - metadata: Parsed exam metadata
    """
    with client.create_client() as http:
        try:
            response = http.get(book_url, cookies=cookies)
            response.raise_for_status()
        except Exception as e:
            logger.warning("edcolearning_book_error", book_id=book_id, error=str(e))
            return

        soup = BeautifulSoup(response.text, "html.parser")

        # Extract audio links
        for audio_info in _extract_audio_links(soup, book_id):
            metadata = _parse_exam_metadata(audio_info["title"], audio_info["audio_url"])

            # Generate content hash for deduplication
            content_hash = hashlib.md5(audio_info["audio_url"].encode()).hexdigest()[:16]

            yield {
                "audio_id": f"{book_id}_{content_hash}",
                "book_id": book_id,
                "audio_url": audio_info["audio_url"],
                "title": audio_info["title"],
                "format": audio_info["format"],
                "year": metadata.get("year"),
                "level": metadata.get("level"),
                "paper_type": metadata.get("paper_type"),
                "language": metadata.get("language"),
                "source": "edcolearning",
                "scraped_at": datetime.now(UTC).isoformat(),
            }

        # Extract transcript links
        for pdf_info in _extract_transcript_links(soup, book_id):
            if pdf_info["is_transcript"]:
                content_hash = hashlib.md5(pdf_info["pdf_url"].encode()).hexdigest()[:16]

                yield {
                    "audio_id": None,
                    "book_id": book_id,
                    "transcript_url": pdf_info["pdf_url"],
                    "title": pdf_info["title"],
                    "format": "pdf",
                    "is_transcript": True,
                    "source": "edcolearning",
                    "scraped_at": datetime.now(UTC).isoformat(),
                }


@dlt.source(name="edcolearning")
def edcolearning_source(
    subjects: list[str] | None = None,
    level: str = "leaving_certificate",
    use_1password: bool = True,
) -> Iterator[DltResource]:
    """
    DLT source for EdcoLearning.ie exam audio resources.

    Args:
        subjects: List of subjects to scrape (default: all language subjects)
        level: Exam level ('leaving_certificate', 'junior_cycle', 'transition_year')
        use_1password: Load credentials from 1Password (default) or environment

    Yields:
        DLT resources for books, audio_files, and transcripts

    Examples:
        # All LC Irish and French exam audio
        pipeline.run(edcolearning_source(
            subjects=["irish", "french"],
            level="leaving_certificate",
        ))

        # All available subjects
        pipeline.run(edcolearning_source())
    """
    # Parse level
    try:
        exam_level = ExamLevel(level)
    except ValueError:
        exam_level = ExamLevel.LEAVING_CERT
        logger.warning("edcolearning_invalid_level", level=level, using=exam_level.value)

    # Parse subjects
    target_subjects = []
    if subjects:
        for s in subjects:
            try:
                target_subjects.append(ExamSubject(s.lower()))
            except ValueError:
                logger.warning("edcolearning_unknown_subject", subject=s)
    else:
        target_subjects = [ExamSubject.IRISH, ExamSubject.FRENCH, ExamSubject.GERMAN, ExamSubject.SPANISH]

    logger.info(
        "edcolearning_source_init",
        subjects=[s.value for s in target_subjects],
        level=exam_level.value,
    )

    # Load credentials
    try:
        if use_1password:
            credentials = EdcoCredentials.from_1password()
        else:
            credentials = EdcoCredentials.from_env()
    except ValueError as e:
        logger.error("edcolearning_credentials_error", error=str(e))

        @dlt.resource(name="audio_files", write_disposition="merge", primary_key=["audio_id"])
        def no_credentials():
            yield {
                "audio_id": "error_no_credentials",
                "status": "no_credentials",
                "error": str(e),
                "scraped_at": datetime.now(UTC).isoformat(),
            }

        return no_credentials

    # Create client and authenticate
    client = _edcolearning_client()
    try:
        session_cookies = _authenticate_session(client, credentials)
    except ValueError as e:
        logger.error("edcolearning_auth_error", error=str(e))

        @dlt.resource(name="audio_files", write_disposition="merge", primary_key=["audio_id"])
        def auth_failed():
            yield {
                "audio_id": "error_auth_failed",
                "status": "auth_failed",
                "error": str(e),
                "scraped_at": datetime.now(UTC).isoformat(),
            }

        return auth_failed

    @dlt.resource(
        name="books",
        write_disposition="merge",
        primary_key=["book_id"],
    )
    def books_resource() -> Iterator[dict[str, Any]]:
        """Extract available exam audio books."""
        for subject in target_subjects:
            try:
                yield from _discover_exam_books(client, session_cookies, subject, exam_level)
            except Exception as e:
                logger.warning(
                    "edcolearning_books_discovery_error",
                    subject=subject.value,
                    error=str(e),
                )

    @dlt.resource(
        name="audio_files",
        write_disposition="merge",
        primary_key=["audio_id"],
        columns={
            "audio_id": {"data_type": "text"},
            "book_id": {"data_type": "text"},
            "audio_url": {"data_type": "text"},
            "title": {"data_type": "text"},
            "format": {"data_type": "text"},
            "year": {"data_type": "bigint"},
            "level": {"data_type": "text"},
            "paper_type": {"data_type": "text"},
            "language": {"data_type": "text"},
            "source": {"data_type": "text"},
            "scraped_at": {"data_type": "timestamp"},
        },
    )
    def audio_files_resource() -> Iterator[dict[str, Any]]:
        """Extract audio files from all discovered books."""
        for subject in target_subjects:
            try:
                for book in _discover_exam_books(client, session_cookies, subject, exam_level):
                    try:
                        for audio in _scrape_book_audio(
                            client,
                            session_cookies,
                            book["book_id"],
                            book["url"],
                        ):
                            if audio.get("audio_url"):
                                # Add subject from book discovery
                                audio["subject"] = subject.value
                                yield audio
                    except Exception as e:
                        logger.warning(
                            "edcolearning_book_scrape_error",
                            book_id=book["book_id"],
                            error=str(e),
                        )
            except Exception as e:
                logger.warning(
                    "edcolearning_subject_error",
                    subject=subject.value,
                    error=str(e),
                )

    @dlt.resource(
        name="transcripts",
        write_disposition="merge",
        primary_key=["book_id", "title"],
    )
    def transcripts_resource() -> Iterator[dict[str, Any]]:
        """Extract transcript PDFs from all discovered books."""
        for subject in target_subjects:
            try:
                for book in _discover_exam_books(client, session_cookies, subject, exam_level):
                    try:
                        for item in _scrape_book_audio(
                            client,
                            session_cookies,
                            book["book_id"],
                            book["url"],
                        ):
                            if item.get("is_transcript") and item.get("transcript_url"):
                                item["subject"] = subject.value
                                yield item
                    except Exception as e:
                        logger.warning(
                            "edcolearning_transcript_error",
                            book_id=book["book_id"],
                            error=str(e),
                        )
            except Exception:
                pass

    return books_resource, audio_files_resource, transcripts_resource


# Convenience sources for specific subjects


def irish_lc_audio_source(use_1password: bool = True):
    """DLT source for Irish Leaving Certificate exam audio only."""
    return edcolearning_source(
        subjects=["irish"],
        level="leaving_certificate",
        use_1password=use_1password,
    )


def languages_lc_audio_source(use_1password: bool = True):
    """DLT source for all language subjects (Irish, French, German, Spanish)."""
    return edcolearning_source(
        subjects=["irish", "french", "german", "spanish"],
        level="leaving_certificate",
        use_1password=use_1password,
    )


def french_lc_audio_source(use_1password: bool = True):
    """DLT source for French Leaving Certificate exam audio only."""
    return edcolearning_source(
        subjects=["french"],
        level="leaving_certificate",
        use_1password=use_1password,
    )


def german_lc_audio_source(use_1password: bool = True):
    """DLT source for German Leaving Certificate exam audio only."""
    return edcolearning_source(
        subjects=["german"],
        level="leaving_certificate",
        use_1password=use_1password,
    )


def spanish_lc_audio_source(use_1password: bool = True):
    """DLT source for Spanish Leaving Certificate exam audio only."""
    return edcolearning_source(
        subjects=["spanish"],
        level="leaving_certificate",
        use_1password=use_1password,
    )
