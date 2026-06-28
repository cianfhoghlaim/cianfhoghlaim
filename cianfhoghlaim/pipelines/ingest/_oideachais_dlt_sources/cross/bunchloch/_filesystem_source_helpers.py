"""
Shared helpers split from bunchloch/filesystem_source.py

Phase 3D of openspec change.
"""

import hashlib
import re
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import dlt

BUNCHLOCH_PATH = Path("/Users/cliste/dev/cianfhoghlaim/taighde/bunchloch")

COURSE_CODE_PATTERN = re.compile(r"([A-Z]{2,3})(\d{3,4})")

FILE_TYPE_EXTENSIONS = {
    "pdf": {".pdf"},
    "word": {".doc", ".docx"},
    "code": {".py", ".java", ".js", ".ts", ".sql", ".r", ".R", ".class"},
    "presentation": {".ppt", ".pptx", ".key"},
    "image": {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff"},
    "text": {".txt", ".md", ".rst", ".log"},
    "data": {".csv", ".json", ".xml", ".dat"},
}

SKIP_PATTERNS = {
    ".DS_Store",
    ".gitignore",
    "Thumbs.db",
    "__MACOSX",
    ".idea",
}

SUBJECT_PATHS = {
    "comp_science": BUNCHLOCH_PATH / "comp_science",
    "gaeilge": BUNCHLOCH_PATH / "gaeilge",
    "mata": BUNCHLOCH_PATH / "mata",
    "oideachas": BUNCHLOCH_PATH / "oideachas",
}

def compute_file_hash(path: Path, chunk_size: int = 8192) -> str:
    """Compute SHA-256 hash of file for change detection."""
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            sha256.update(chunk)
    return sha256.hexdigest()

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

def detect_subject(path: Path) -> str:
    """Detect subject from directory structure."""
    path_str = str(path).lower()
    for subject, subject_path in SUBJECT_PATHS.items():
        if str(subject_path).lower() in path_str:
            return subject
    return "unknown"

def extract_course_code(path: Path) -> str | None:
    """Extract course code from file path (e.g., CT511, GA101)."""
    path_str = str(path)
    match = COURSE_CODE_PATTERN.search(path_str)
    if match:
        return f"{match.group(1)}{match.group(2)}"
    return None

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

def get_file_type(path: Path) -> str:
    """Determine file type from extension."""
    ext = path.suffix.lower()
    for file_type, extensions in FILE_TYPE_EXTENSIONS.items():
        if ext in extensions:
            return file_type
    return "unknown"

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
    search_paths = [SUBJECT_PATHS[subject]] if subject and subject in SUBJECT_PATHS else [base_path]

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

def should_skip_file(path: Path) -> bool:
    """Check if file should be skipped."""
    name = path.name
    for pattern in SKIP_PATTERNS:
        if pattern in str(path):
            return True
    return bool(name.startswith("."))
