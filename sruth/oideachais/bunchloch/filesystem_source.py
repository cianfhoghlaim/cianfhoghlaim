"""
DLT source for bunchloch research document filesystem ingestion.

Processes local files from:
- comp_science/  (CT###: CT874, CT545, CT511 - CS courses)
- gaeilge/       (GA###/GF###: GA101, GA201 - Irish language)
- mata/          (Applied Statistics, Networks - Mathematics)
- oideachas/     (ED###, lesson plans - Education)

Features:
- Incremental processing via file hash tracking
- Course code extraction from paths
- Subject detection from directory structure
- File type routing (PDF, DOCX, code)
- DuckLake-ready schema with partitioning

Document Counts (1,251 files, 3.4GB):
- PDFs: 843
- DOCX: 407
- Code: 42 (Java)
- Other: Keynote, text, images

Migrated from sruth.taighde.dlt_sources.filesystem_source.
"""

import hashlib
import re
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import dlt
import structlog

logger = structlog.get_logger(__name__)

# ============================================================================
# Configuration
# ============================================================================

BUNCHLOCH_PATH = Path("/Users/cliste/dev/cianfhoghlaim/taighde/bunchloch")

SUBJECT_PATHS = {
    "comp_science": BUNCHLOCH_PATH / "comp_science",
    "gaeilge": BUNCHLOCH_PATH / "gaeilge",
    "mata": BUNCHLOCH_PATH / "mata",
    "oideachas": BUNCHLOCH_PATH / "oideachas",
}

FILE_TYPE_EXTENSIONS = {
    "pdf": {".pdf"},
    "word": {".doc", ".docx"},
    "code": {".py", ".java", ".js", ".ts", ".sql", ".r", ".R", ".class"},
    "presentation": {".ppt", ".pptx", ".key"},
    "image": {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff"},
    "text": {".txt", ".md", ".rst", ".log"},
    "data": {".csv", ".json", ".xml", ".dat"},
}

# Course code patterns (e.g., CT511, GA101, GF107)
COURSE_CODE_PATTERN = re.compile(r"([A-Z]{2,3})(\d{3,4})")

# Files to skip
SKIP_PATTERNS = {
    ".DS_Store",
    ".gitignore",
    "Thumbs.db",
    "__MACOSX",
    ".idea",
}


# ============================================================================
# Utility Functions
# ============================================================================


def compute_file_hash(path: Path, chunk_size: int = 8192) -> str:
    """Compute SHA-256 hash of file for change detection."""
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            sha256.update(chunk)
    return sha256.hexdigest()


def get_file_type(path: Path) -> str:
    """Determine file type from extension."""
    ext = path.suffix.lower()
    for file_type, extensions in FILE_TYPE_EXTENSIONS.items():
        if ext in extensions:
            return file_type
    return "unknown"


def extract_course_code(path: Path) -> str | None:
    """Extract course code from file path (e.g., CT511, GA101)."""
    path_str = str(path)
    match = COURSE_CODE_PATTERN.search(path_str)
    if match:
        return f"{match.group(1)}{match.group(2)}"
    return None


def detect_subject(path: Path) -> str:
    """Detect subject from directory structure."""
    path_str = str(path).lower()
    for subject, subject_path in SUBJECT_PATHS.items():
        if str(subject_path).lower() in path_str:
            return subject
    return "unknown"


def should_skip_file(path: Path) -> bool:
    """Check if file should be skipped."""
    name = path.name
    for pattern in SKIP_PATTERNS:
        if pattern in str(path):
            return True
    if name.startswith("."):
        return True
    return False


def get_file_metadata(path: Path) -> dict[str, Any]:
    """Extract metadata from file path and attributes."""
    stat = path.stat()
    rel_path = path.relative_to(BUNCHLOCH_PATH) if BUNCHLOCH_PATH in path.parents else path

    return {
        "file_path": str(path),
        "relative_path": str(rel_path),
        "file_name": path.name,
        "file_stem": path.stem,
        "file_extension": path.suffix.lower(),
        "file_type": get_file_type(path),
        "file_size": stat.st_size,
        "subject": detect_subject(path),
        "course_code": extract_course_code(path),
        "parent_dir": path.parent.name,
        "modified_at": datetime.fromtimestamp(stat.st_mtime, tz=UTC).isoformat(),
        "created_at": datetime.fromtimestamp(stat.st_ctime, tz=UTC).isoformat(),
    }


# ============================================================================
# Directory Scanning
# ============================================================================


def scan_directory(
    base_path: Path,
    subject: str | None = None,
    file_types: list[str] | None = None,
    max_files: int | None = None,
) -> Iterator[dict[str, Any]]:
    """
    Scan directory for files to process.

    Args:
        base_path: Base directory to scan
        subject: Optional subject filter (comp_science, gaeilge, mata, oideachas)
        file_types: Optional list of file types to include
        max_files: Optional maximum number of files to yield
    """
    if not base_path.exists():
        logger.warning("directory_not_found", path=str(base_path))
        return

    # Determine search paths
    if subject and subject in SUBJECT_PATHS:
        search_paths = [SUBJECT_PATHS[subject]]
    else:
        search_paths = [base_path]

    # Build extension set
    allowed_extensions: set[str] = set()
    if file_types:
        for ft in file_types:
            allowed_extensions.update(FILE_TYPE_EXTENSIONS.get(ft, set()))
    else:
        for exts in FILE_TYPE_EXTENSIONS.values():
            allowed_extensions.update(exts)

    count = 0
    for search_path in search_paths:
        if not search_path.exists():
            continue

        for path in search_path.rglob("*"):
            if max_files and count >= max_files:
                return

            if not path.is_file():
                continue

            if should_skip_file(path):
                continue

            if path.suffix.lower() not in allowed_extensions:
                continue

            try:
                file_hash = compute_file_hash(path)
                metadata = get_file_metadata(path)

                yield {
                    "id": file_hash[:16],
                    "file_hash": file_hash,
                    "discovered_at": datetime.now(UTC).isoformat(),
                    **metadata,
                }
                count += 1

            except (OSError, PermissionError) as e:
                logger.warning("file_scan_error", path=str(path), error=str(e))
                yield {
                    "id": str(path),
                    "file_path": str(path),
                    "file_name": path.name,
                    "error": str(e),
                    "status": "error",
                    "discovered_at": datetime.now(UTC).isoformat(),
                }


# ============================================================================
# DLT Source Definition
# ============================================================================


@dlt.source(name="bunchloch")
def bunchloch_source(
    base_path: str | Path = BUNCHLOCH_PATH,
    subject: str | None = None,
    max_files: int | None = None,
):
    """
    DLT source for bunchloch research documents.

    Args:
        base_path: Base directory (default: taighde/bunchloch)
        subject: Optional subject filter (comp_science, gaeilge, mata, oideachas)
        max_files: Optional limit on files to process

    Returns:
        DLT resources for each document type
    """
    base_path = Path(base_path)

    @dlt.resource(
        name="documents",
        write_disposition="merge",
        primary_key=["file_hash"],
        columns={
            "subject": {"partition": True},  # Partition by subject for DuckLake
        },
    )
    def all_documents() -> Iterator[dict[str, Any]]:
        """All discovered documents with metadata."""
        yield from scan_directory(base_path, subject, None, max_files)

    @dlt.resource(
        name="pdf_documents",
        write_disposition="merge",
        primary_key=["file_hash"],
    )
    def pdf_documents() -> Iterator[dict[str, Any]]:
        """PDF documents only (843 files)."""
        yield from scan_directory(base_path, subject, ["pdf"], max_files)

    @dlt.resource(
        name="word_documents",
        write_disposition="merge",
        primary_key=["file_hash"],
    )
    def word_documents() -> Iterator[dict[str, Any]]:
        """Word documents only (407 files)."""
        yield from scan_directory(base_path, subject, ["word"], max_files)

    @dlt.resource(
        name="code_files",
        write_disposition="merge",
        primary_key=["file_hash"],
    )
    def code_files() -> Iterator[dict[str, Any]]:
        """Code files only (42 Java files)."""
        yield from scan_directory(base_path, subject, ["code"], max_files)

    @dlt.resource(
        name="presentations",
        write_disposition="merge",
        primary_key=["file_hash"],
    )
    def presentations() -> Iterator[dict[str, Any]]:
        """Presentation files (Keynote, PowerPoint)."""
        yield from scan_directory(base_path, subject, ["presentation"], max_files)

    return all_documents, pdf_documents, word_documents, code_files, presentations


@dlt.source(name="bunchloch_by_subject")
def bunchloch_by_subject_source(
    subject: str,
    max_files: int | None = None,
):
    """
    DLT source for documents from a specific subject.

    Args:
        subject: Subject to process (comp_science, gaeilge, mata, oideachas)
        max_files: Optional maximum number of files

    Returns:
        DLT resource with subject-specific documents
    """
    if subject not in SUBJECT_PATHS:
        raise ValueError(f"Unknown subject: {subject}. Valid: {list(SUBJECT_PATHS.keys())}")

    @dlt.resource(
        name=f"{subject}_documents",
        write_disposition="merge",
        primary_key=["file_hash"],
    )
    def subject_documents() -> Iterator[dict[str, Any]]:
        """Documents from the specified subject."""
        yield from scan_directory(BUNCHLOCH_PATH, subject, None, max_files)

    return subject_documents


# ============================================================================
# Pipeline Utilities
# ============================================================================


def create_bunchloch_pipeline(
    destination: str = "duckdb",
    dataset_name: str = "research_bunchloch",  # Changed from "bunchloch" to namespace under research
) -> dlt.Pipeline:
    """
    Create DLT pipeline for bunchloch ingestion.

    Args:
        destination: DLT destination (duckdb, postgres, etc.)
        dataset_name: Dataset name in destination

    Returns:
        Configured DLT pipeline
    """
    return dlt.pipeline(
        pipeline_name="bunchloch_pipeline",
        destination=destination,
        dataset_name=dataset_name,
    )


def run_full_ingestion(
    destination: str = "duckdb",
    max_files: int | None = None,
) -> Any:
    """
    Run full bunchloch ingestion.

    Args:
        destination: DLT destination
        max_files: Optional limit for testing

    Returns:
        DLT load info
    """
    pipeline = create_bunchloch_pipeline(destination=destination)
    source = bunchloch_source(max_files=max_files)
    load_info = pipeline.run(source)

    logger.info(
        "bunchloch_ingestion_complete",
        load_info=str(load_info),
        destination=destination,
    )

    return load_info


if __name__ == "__main__":
    # Quick test
    load_info = run_full_ingestion(max_files=10)
    print(load_info)
