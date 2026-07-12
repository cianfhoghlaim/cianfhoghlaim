"""
Shared helpers split from ireland/pdf_downloader.py

Phase 3D of openspec change.
"""

import hashlib
import time
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx

DEFAULT_DOWNLOAD_DIR = Path("./downloads/curriculum_pdfs")

EXAM_DOWNLOAD_DIR = Path("./downloads/examinations")

MAX_FILE_SIZE_MB = 50

RATE_LIMIT_DELAY = 1.0  # Seconds between requests

REQUEST_TIMEOUT = 30  # Seconds

USER_AGENT = "Oideachais-Curriculum-Bot/1.0 (Educational Research; +https://cianfhoghlaim.ie)"

def _compute_content_hash(content: bytes) -> str:
    """Compute SHA-256 hash of content for deduplication."""
    return hashlib.sha256(content).hexdigest()

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

def _get_download_path(
    url: str,
    content_hash: str,
    cycle: str,
    subject: str,
    source: str,
    download_dir: Path,
    pdf_type: str | None = None,
    year: int | None = None,
    level: str | None = None,
) -> Path:
    """Build download path based on source type.

    Curriculum PDFs: download_dir/source/cycle/subject/filename.pdf
    Exam materials: download_dir/level/subject/year_level_paper_hash.pdf
    """
    if source == "examinations":
        # Exam materials use a different path structure:
        # downloads/examinations/{level}/{subject}/{year}_{level}_{paper}_{hash}.pdf
        filename = _safe_filename(url, content_hash, pdf_type, year, level, subject)
        path = download_dir / str(level or cycle) / subject / filename
    else:
        filename = _safe_filename(url, content_hash, pdf_type, year, level, subject)
        source_safe = source if source else "unknown_source"
        path = download_dir / source_safe / cycle / subject / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    return path

def _query_pending_pdfs(
    duckdb_path: str,
    cycle: str | None = None,
    subject: str | None = None,
    limit: int = 100,
) -> list[dict[str, Any]]:

    import duckdb

    try:
        conn = duckdb.connect(duckdb_path, read_only=True)

        # We might have tables in different schemas, let's look for them
        tables_query = conn.execute("SELECT table_schema, table_name FROM information_schema.tables WHERE table_name IN ('curriculum_pdfs', 'all_exam_materials')").fetchall()

        queries = []

        for schema, table in tables_query:
            if table == "curriculum_pdfs":
                columns_info = conn.execute(f"DESCRIBE {schema}.{table}").fetchall()
                column_names = [col[0] for col in columns_info]

                url_col = "url"
                cycle_col = "cycle"
                subject_col = "subject"
                lang_col = "language"
                type_col = "pdf_type"
                source_col = "source"

                year_col = "year" if "year" in column_names else "NULL AS year"
                level_col = "level" if "level" in column_names else "NULL AS level"

                queries.append(f"""
                    SELECT DISTINCT
                        {url_col} as url,
                        {cycle_col} as cycle,
                        {subject_col} as subject,
                        {lang_col} as language,
                        {type_col} as pdf_type,
                        {source_col} as source,
                        {year_col},
                        {level_col}
                    FROM {schema}.{table}
                """)
            elif table == "all_exam_materials":
                # For examinations.ie output
                queries.append(f"""
                    SELECT DISTINCT
                        pdf_url as url,
                        level as cycle,
                        subject as subject,
                        'en' as language,
                        'examinations' as source,
                        material_type as pdf_type,
                        year,
                        level
                    FROM {schema}.{table}
                    WHERE pdf_url IS NOT NULL AND pdf_url != ''
                """)

        if not queries:
            logger.warning("no_pdf_tables_found")
            return []

        base_query = " UNION ALL ".join(queries)

        query = f"""
            SELECT url, cycle, subject, language, pdf_type, source, year, level
            FROM ({base_query})
            WHERE 1=1
        """

        params = []
        if cycle:
            query += " AND cycle = ?"
            params.append(cycle)

        if subject:
            query += " AND subject = ?"
            params.append(subject)

        query += f" LIMIT {limit}"

        res = conn.execute(query, params).fetchall()

        pdfs = []
        for r in res:
            pdfs.append({
                "url": r[0],
                "cycle": r[1],
                "subject": r[2],
                "language": r[3],
                "pdf_type": r[4],
                "source": r[5],
                "year": r[6],
                "level": r[7],
            })

        return pdfs

    except Exception as e:
        logger.warning("query_pending_pdfs_failed", error=str(e))
        return []

def _safe_filename(url: str, content_hash: str, pdf_type: str | None = None, year: int | None = None, level: str | None = None, subject: str | None = None) -> str:
    """Generate a normalized filename incorporating metadata if available, but preserving the original filename."""
    parsed = urlparse(url)
    path_parts = parsed.path.strip("/").split("/")
    original_name = path_parts[-1] if (path_parts and path_parts[-1].lower().endswith(".pdf")) else "document.pdf"

    name_without_ext = original_name.rsplit(".", 1)[0][:50]

    parts = []
    if year:
        parts.append(str(year))
    if level:
        parts.append(str(level).replace(" ", "").title())
    if pdf_type:
        parts.append(str(pdf_type).replace(" ", "").title())

    if parts:
        prefix = "_".join(parts)
        return f"{prefix}_{name_without_ext}_{content_hash[:6]}.pdf"

    return f"{name_without_ext}_{content_hash[:6]}.pdf"

def exam_pdf_downloads(
    duckdb_path: str,
    download_dir: Path | str = EXAM_DOWNLOAD_DIR,
    level: str | None = None,
    subject: str | None = None,
    max_files: int = 500,
    max_size_mb: int = MAX_FILE_SIZE_MB,
    rate_limit_delay: float = RATE_LIMIT_DELAY,
) -> Iterator[dict[str, Any]]:
    """
    Download exam material PDFs from all_exam_materials table.

    Uses examinations-specific path structure:
        downloads/examinations/{level}/{subject}/{year}_{level}_{paper}_{hash}.pdf

    Args:
        duckdb_path: Path to DuckDB database with all_exam_materials table
        download_dir: Directory to save downloaded exam PDFs
        level: Optional level filter (leaving_certificate, junior_cycle, leaving_certificate_applied)
        subject: Optional subject filter
        max_files: Maximum number of PDFs to download
        max_size_mb: Maximum file size in Manitoba
        rate_limit_delay: Delay between downloads in seconds
    """
    download_dir = Path(download_dir)
    download_dir.mkdir(parents=True, exist_ok=True)

    pending_pdfs = _query_pending_pdfs(
        duckdb_path=duckdb_path,
        cycle=level,
        subject=subject,
        limit=max_files,
    )

    # Filter to only exam materials
    exam_pdfs = [p for p in pending_pdfs if p.get("source") == "examinations" or p.get("level")]

    logger.info("exam_pdf_download_starting", count=len(exam_pdfs))

    with httpx.Client(
        timeout=REQUEST_TIMEOUT,
        headers={"User-Agent": USER_AGENT},
        follow_redirects=True,
    ) as client:
        for pdf_info in exam_pdfs:
            url = pdf_info["url"]
            pdf_level = pdf_info.get("level") or pdf_info.get("cycle", "leaving_certificate")
            pdf_subject = pdf_info["subject"]

            content, metadata = _download_pdf(url, client, max_size_mb)

            record = {**pdf_info, **metadata}

            if content and metadata.get("content_hash"):
                file_path = _get_download_path(
                    url=url,
                    content_hash=metadata["content_hash"],
                    cycle=pdf_level,
                    subject=pdf_subject,
                    source="examinations",
                    download_dir=download_dir,
                    pdf_type=pdf_info.get("pdf_type"),
                    year=pdf_info.get("year"),
                    level=pdf_level,
                )

                if not file_path.exists():
                    file_path.write_bytes(content)
                    record["local_path"] = str(file_path)
                    record["is_new"] = True
                    logger.info("exam_pdf_saved", path=str(file_path))
                else:
                    record["local_path"] = str(file_path)
                    record["is_new"] = False
                    record["status"] = "already_exists"

            yield record
            time.sleep(rate_limit_delay)

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
        max_size_mb: Maximum file size in Manitoba
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
                    source=pdf_info.get("source"),
                    download_dir=download_dir,
                    pdf_type=pdf_info.get("pdf_type"),
                    year=pdf_info.get("year"),
                    level=pdf_info.get("level"),
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
