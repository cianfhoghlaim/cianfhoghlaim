"""
DLT source for downloading curriculum PDFs from discovered URLs.

This source:
1. Queries PDF URLs from curriculum_pdfs table in DuckLake
2. Downloads PDFs with proper rate limiting
3. Stores them locally with hash-based deduplication
4. Tracks download status for incremental processing

Usage:
    from oideachais.data_platform.dlt_sources.ireland.pdf_downloader import pdf_download_source

    pipeline = dlt.pipeline(...)
    pipeline.run(pdf_download_source(
        duckdb_path="./curriculum_unified.duckdb",
        download_dir="./downloads/pdfs",
    ))
"""

import hashlib
import time
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import dlt
import httpx
import structlog

logger = structlog.get_logger(__name__)

# Download configuration
DEFAULT_DOWNLOAD_DIR = Path("./downloads/curriculum_pdfs")
MAX_FILE_SIZE_MB = 50
RATE_LIMIT_DELAY = 1.0  # Seconds between requests
REQUEST_TIMEOUT = 30  # Seconds
USER_AGENT = "Oideachais-Curriculum-Bot/1.0 (Educational Research; +https://cianfhoghlaim.ie)"


def _compute_content_hash(content: bytes) -> str:
    """Compute SHA-256 hash of content for deduplication."""
    return hashlib.sha256(content).hexdigest()


def _safe_filename(url: str, content_hash: str) -> str:
    """Generate a safe filename from URL and content hash."""
    parsed = urlparse(url)
    path_parts = parsed.path.strip("/").split("/")

    # Get the original filename from URL path
    if path_parts and path_parts[-1].endswith(".pdf"):
        original_name = path_parts[-1]
    else:
        original_name = "document.pdf"

    # Remove extension, add hash, add extension back
    name_without_ext = original_name.rsplit(".", 1)[0]
    # Truncate name if too long
    name_without_ext = name_without_ext[:50]

    return f"{name_without_ext}_{content_hash[:12]}.pdf"


def _get_download_path(
    url: str,
    content_hash: str,
    cycle: str,
    subject: str,
    download_dir: Path,
) -> Path:
    """Build download path: download_dir/cycle/subject/filename.pdf"""
    filename = _safe_filename(url, content_hash)
    path = download_dir / cycle / subject / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _download_pdf(
    url: str,
    client: httpx.Client,
    max_size_mb: int = MAX_FILE_SIZE_MB,
) -> tuple[bytes | None, dict[str, Any]]:
    """
    Download a PDF from URL with size limits.

    Returns:
        Tuple of (content_bytes, metadata_dict)
        content_bytes is None on error
    """
    metadata = {
        "url": url,
        "downloaded_at": datetime.now(UTC).isoformat(),
        "status": "pending",
    }

    try:
        # HEAD request to check size first
        head_response = client.head(url, follow_redirects=True)

        content_length = head_response.headers.get("content-length")
        if content_length:
            size_mb = int(content_length) / (1024 * 1024)
            if size_mb > max_size_mb:
                metadata["status"] = "skipped_too_large"
                metadata["size_mb"] = size_mb
                logger.info("pdf_too_large", url=url, size_mb=size_mb)
                return None, metadata

        # Check content type
        content_type = head_response.headers.get("content-type", "")
        if "pdf" not in content_type.lower() and not url.lower().endswith(".pdf"):
            metadata["status"] = "skipped_not_pdf"
            metadata["content_type"] = content_type
            return None, metadata

        # Download the file
        response = client.get(url, follow_redirects=True)
        response.raise_for_status()

        content = response.content
        metadata["status"] = "downloaded"
        metadata["size_bytes"] = len(content)
        metadata["content_type"] = response.headers.get("content-type", "")
        metadata["content_hash"] = _compute_content_hash(content)

        return content, metadata

    except httpx.TimeoutException:
        metadata["status"] = "error_timeout"
        logger.warning("pdf_download_timeout", url=url)
        return None, metadata

    except httpx.HTTPStatusError as e:
        metadata["status"] = f"error_http_{e.response.status_code}"
        logger.warning("pdf_download_http_error", url=url, status=e.response.status_code)
        return None, metadata

    except Exception as e:
        metadata["status"] = "error_unknown"
        metadata["error"] = str(e)
        logger.warning("pdf_download_error", url=url, error=str(e))
        return None, metadata


def _query_pending_pdfs(
    duckdb_path: str,
    cycle: str | None = None,
    subject: str | None = None,
    limit: int = 100,
) -> list[dict[str, Any]]:
    """
    Query PDF URLs from curriculum_pdfs table.

    Returns list of dicts with url, cycle, subject, language, pdf_type
    """
    import duckdb

    try:
        conn = duckdb.connect(duckdb_path, read_only=True)

        # Build query with optional filters
        query = """
            SELECT DISTINCT
                url,
                cycle,
                subject,
                language,
                pdf_type,
                source,
                discovered_at
            FROM curriculum_pdfs
            WHERE 1=1
        """
        params = []

        if cycle:
            query += " AND cycle = ?"
            params.append(cycle)

        if subject:
            query += " AND subject = ?"
            params.append(subject)

        query += " ORDER BY discovered_at DESC LIMIT ?"
        params.append(limit)

        result = conn.execute(query, params).fetchall()
        columns = ["url", "cycle", "subject", "language", "pdf_type", "source", "discovered_at"]

        return [dict(zip(columns, row)) for row in result]

    except Exception as e:
        logger.warning("pdf_query_error", error=str(e))
        return []


@dlt.resource(
    name="pdf_downloads",
    write_disposition="merge",
    primary_key=["content_hash"],
)
def pdf_downloads(
    duckdb_path: str,
    download_dir: Path | str = DEFAULT_DOWNLOAD_DIR,
    cycle: str | None = None,
    subject: str | None = None,
    max_files: int = 100,
    max_size_mb: int = MAX_FILE_SIZE_MB,
    rate_limit_delay: float = RATE_LIMIT_DELAY,
) -> Iterator[dict[str, Any]]:
    """
    Download PDFs from curriculum_pdfs table URLs.

    Args:
        duckdb_path: Path to DuckDB database with curriculum_pdfs table
        download_dir: Directory to save downloaded PDFs
        cycle: Optional cycle filter (junior_cycle, senior_cycle)
        subject: Optional subject filter
        max_files: Maximum number of PDFs to download
        max_size_mb: Maximum file size in MB
        rate_limit_delay: Delay between downloads in seconds

    Yields:
        Dict with download metadata for each PDF
    """
    download_dir = Path(download_dir)
    download_dir.mkdir(parents=True, exist_ok=True)

    # Query pending PDFs
    pending_pdfs = _query_pending_pdfs(
        duckdb_path=duckdb_path,
        cycle=cycle,
        subject=subject,
        limit=max_files,
    )

    logger.info("pdf_download_starting", count=len(pending_pdfs))

    # Create HTTP client with proper headers
    with httpx.Client(
        timeout=REQUEST_TIMEOUT,
        headers={"User-Agent": USER_AGENT},
        follow_redirects=True,
    ) as client:
        for pdf_info in pending_pdfs:
            url = pdf_info["url"]
            pdf_cycle = pdf_info["cycle"]
            pdf_subject = pdf_info["subject"]

            # Download the PDF
            content, metadata = _download_pdf(url, client, max_size_mb)

            # Merge PDF info with download metadata
            record = {
                **pdf_info,
                **metadata,
            }

            # Save file if download succeeded
            if content and metadata.get("content_hash"):
                file_path = _get_download_path(
                    url=url,
                    content_hash=metadata["content_hash"],
                    cycle=pdf_cycle,
                    subject=pdf_subject,
                    download_dir=download_dir,
                )

                # Only write if file doesn't exist (hash-based dedup)
                if not file_path.exists():
                    file_path.write_bytes(content)
                    record["local_path"] = str(file_path)
                    record["is_new"] = True
                    logger.info("pdf_saved", path=str(file_path))
                else:
                    record["local_path"] = str(file_path)
                    record["is_new"] = False
                    record["status"] = "already_exists"

            yield record

            # Rate limiting
            time.sleep(rate_limit_delay)


@dlt.resource(
    name="pdf_download_errors",
    write_disposition="append",
)
def pdf_download_errors(
    downloads_resource: Iterator[dict[str, Any]],
) -> Iterator[dict[str, Any]]:
    """
    Filter and yield only failed downloads for retry tracking.

    Args:
        downloads_resource: Output from pdf_downloads resource

    Yields:
        Dict with error metadata for failed downloads
    """
    for record in downloads_resource:
        if record.get("status", "").startswith("error_"):
            yield record


@dlt.source(name="curriculum_pdf_downloads")
def pdf_download_source(
    duckdb_path: str,
    download_dir: Path | str = DEFAULT_DOWNLOAD_DIR,
    cycle: str | None = None,
    subject: str | None = None,
    max_files: int = 100,
    max_size_mb: int = MAX_FILE_SIZE_MB,
    rate_limit_delay: float = RATE_LIMIT_DELAY,
):
    """
    DLT source for downloading curriculum PDFs.

    Resources:
    - pdf_downloads: All download records (success and failure)
    - pdf_download_errors: Failed downloads for retry

    Usage:
        pipeline = dlt.pipeline(...)
        pipeline.run(pdf_download_source(
            duckdb_path="./curriculum_unified.duckdb",
            download_dir="./downloads/pdfs",
            cycle="senior_cycle",
            subject="mathematics",
        ))
    """
    yield pdf_downloads(
        duckdb_path=duckdb_path,
        download_dir=download_dir,
        cycle=cycle,
        subject=subject,
        max_files=max_files,
        max_size_mb=max_size_mb,
        rate_limit_delay=rate_limit_delay,
    )


__all__ = [
    "pdf_download_source",
    "pdf_downloads",
    "pdf_download_errors",
]
