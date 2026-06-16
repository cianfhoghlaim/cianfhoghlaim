"""
Author Archive filesystem scanner.

Generic, path-parameterised, multi-account scanner used by:
- `oideachais/dlt_sources/author_archive/university_of_galway.py`
- `oideachais/dlt_sources/author_archive/gemini_deep_research.py`
- `oideachais/dlt_sources/author_archive/google_takeout.py`

Refactored from:
- `oideachais/dlt_sources/bunchloch/filesystem_source.py:1`
- `oideachais/dlt_sources/ireland/local_documents.py:1`

Key design points:
- `PathGrammar` carries the per-archive rules (allowed extensions, skip patterns,
  subject detection, course-code regex, "requires handwriting OCR" detection) so
  the scanner is shared by all three sources.
- `FileHashTracker` is hoisted here from `oideachais.dlt_sources.ireland.local_documents`.
  The old import path keeps working via a re-export shim in
  `oideachais/dlt_sources/ireland/local_documents.py`.
- LBYL exception handling per `oideachais/.agents/skills/dignified-python/`.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


# ============================================================================
# Configuration dataclasses
# ============================================================================


DEFAULT_FILE_TYPE_EXTENSIONS: dict[str, set[str]] = {
    "pdf": {".pdf"},
    "word": {".doc", ".docx"},
    "code": {".py", ".ipynb", ".js", ".ts", ".java", ".class"},
    "presentation": {".ppt", ".pptx", ".key"},
    "image": {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".heic"},
    "pages": {".pages"},
    "spreadsheet": {".xls", ".xlsx", ".csv"},
    "text": {".txt", ".md", ".rst", ".log"},
    "data": {".json", ".xml", ".dat"},
    "epub": {".epub"},
    "tsv": {".tsv"},
}

DEFAULT_SKIP_PATTERNS: set[str] = {
    ".DS_Store",
    ".gitignore",
    "Thumbs.db",
    "__MACOSX",
    ".idea",
    ".vscode",
    ".venv",
    "__pycache__",
}


@dataclass(frozen=True)
class PathGrammar:
    """
    Per-archive rules for scanning.

    The same scanner iterates three different trees (UoG, Gemini, Takeout);
    this dataclass holds the differences.
    """

    # Subject detection: list of (label, path_prefix) tuples. First match wins.
    # Path matching is case-insensitive and matches if the lowercased subject
    # path appears anywhere in the lowercased file path.
    subject_paths: dict[str, Path] = field(default_factory=dict)

    # Regex pattern to extract a course code from the path. Default matches
    # `CT511`, `GA101`, `ed305` (case-insensitive). Set to None to disable.
    course_code_pattern: re.Pattern[str] | None = field(
        default_factory=lambda: re.compile(r"([A-Za-z]{2,3})(\d{3,4})")
    )

    # File extensions considered "handwriting candidates" — these will have
    # `requires_handwriting_ocr=True` in the output row.
    handwriting_extensions: set[str] = field(
        default_factory=lambda: {".pages", ".heic"}
    )

    # Subdirectory names whose contents are *always* handwriting candidates,
    # regardless of file extension. Used for UoG `mata/`, `past/`.
    handwriting_subdirs: set[str] = field(default_factory=set)

    # Subdirectory names whose PDF files are *likely* scanned (image-only),
    # e.g. `gemini_deep_research/<domain>/` is born-digital so empty by default.
    scanned_pdf_subdirs: set[str] = field(default_factory=set)

    # Allowed file extensions per category.
    file_type_extensions: dict[str, set[str]] = field(
        default_factory=lambda: DEFAULT_FILE_TYPE_EXTENSIONS.copy()
    )

    # Patterns to skip outright (matched anywhere in the path).
    skip_patterns: set[str] = field(
        default_factory=lambda: set(DEFAULT_SKIP_PATTERNS)
    )


# ============================================================================
# Utility functions
# ============================================================================


def compute_file_hash(path: Path, chunk_size: int = 8192) -> str:
    """Compute SHA-256 hash of a file for change detection."""
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            sha256.update(chunk)
    return sha256.hexdigest()


def get_file_type(path: Path, grammar: PathGrammar) -> str:
    """Determine the file type label from the extension (per grammar)."""
    ext = path.suffix.lower()
    for file_type, extensions in grammar.file_type_extensions.items():
        if ext in extensions:
            return file_type
    return "unknown"


def extract_course_code(path: Path, grammar: PathGrammar) -> str | None:
    """Extract a course code (e.g. `CT511`, `GA101`, `ed305`) from the path."""
    if grammar.course_code_pattern is None:
        return None
    match = grammar.course_code_pattern.search(str(path))
    if match:
        return f"{match.group(1).upper()}{match.group(2)}"
    return None


def detect_subject(path: Path, grammar: PathGrammar) -> str:
    """Detect a subject label from the file path (case-insensitive substring)."""
    path_lower = str(path).lower()
    for subject, subject_path in grammar.subject_paths.items():
        if str(subject_path).lower() in path_lower:
            return subject
    return "unknown"


def detect_domain(path: Path, base_path: Path) -> str:
    """
    Detect the top-level subdirectory (relative to `base_path`) as a domain label.

    `gemini_deep_research/law/foo.pdf` → "law"
    `university_of_galway/mata/foo.pages` → "mata"
    """
    try:
        rel = path.relative_to(base_path)
    except ValueError:
        return "unknown"
    parts = rel.parts
    if len(parts) <= 1:
        return "root"
    return parts[0]


def requires_handwriting_ocr(path: Path, grammar: PathGrammar) -> bool:
    """Heuristic: does this file likely need OCR / HTR?"""
    if path.suffix.lower() in grammar.handwriting_extensions:
        return True
    for part in path.parts:
        if part in grammar.handwriting_subdirs:
            return True
    return False


def should_skip_file(path: Path, grammar: PathGrammar) -> bool:
    """Return True if this file should be skipped."""
    name = path.name
    if name.startswith("."):
        return True
    path_str = str(path)
    for pattern in grammar.skip_patterns:
        if pattern in path_str:
            return True
    return False


def detect_language(text: str) -> str:
    """
    Trivial language detector. Returns "en" (English-only for this change).

    Placeholder for the canonical Irish detector at
    `oideachais/dlt_sources/ireland/local_documents.py:detect_language`.
    """
    if not text:
        return "unknown"
    return "en"


def get_document_metadata(
    path: Path, base_path: Path, grammar: PathGrammar
) -> dict[str, Any]:
    """Build the metadata dict for a single file."""
    if base_path in path.parents:
        rel_path = path.relative_to(base_path)
    else:
        rel_path = path

    stat = path.stat()
    return {
        "file_path": str(path),
        "relative_path": str(rel_path),
        "file_name": path.name,
        "file_stem": path.stem,
        "file_extension": path.suffix.lower(),
        "file_type": get_file_type(path, grammar),
        "file_size": stat.st_size,
        "subject": detect_subject(path, grammar),
        "domain": detect_domain(path, base_path),
        "course_code": extract_course_code(path, grammar),
        "parent_dir": path.parent.name,
        "requires_handwriting_ocr": requires_handwriting_ocr(path, grammar),
        "modified_at": datetime.fromtimestamp(stat.st_mtime, tz=UTC).isoformat(),
        "created_at": datetime.fromtimestamp(stat.st_ctime, tz=UTC).isoformat(),
    }


# ============================================================================
# PDF / DOCX / text extraction
# ============================================================================


def _extract_text_from_pdf(path: Path, max_pages: int = 500) -> dict[str, Any]:
    """Extract text content from a PDF file via pymupdf."""
    try:
        import pymupdf  # type: ignore[import-untyped]
    except ImportError:
        return {"status": "error", "error": "pymupdf not installed"}

    try:
        doc = pymupdf.open(str(path))
        pages: list[dict[str, Any]] = []
        total_chars = 0
        for page_num, page in enumerate(doc):
            if page_num >= max_pages:
                break
            text = page.get_text()
            pages.append(
                {
                    "page_number": page_num + 1,
                    "text": text,
                    "char_count": len(text),
                }
            )
            total_chars += len(text)
        doc.close()
        return {
            "status": "success",
            "page_count": len(pages),
            "total_chars": total_chars,
            "full_text": "\n\n".join(p["text"] for p in pages),
            "pages": pages,
        }
    except (OSError, ValueError, RuntimeError) as e:
        logger.warning("pdf_extraction_failed", path=str(path), error=str(e))
        return {"status": "error", "error": str(e)}


def _extract_text_from_word(path: Path) -> dict[str, Any]:
    """Extract text content from a Word document via python-docx."""
    try:
        from docx import Document  # type: ignore[import-untyped]
    except ImportError:
        return {"status": "error", "error": "python-docx not installed"}

    try:
        doc = Document(str(path))
        paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
        full_text = "\n\n".join(paragraphs)
        return {
            "status": "success",
            "paragraph_count": len(paragraphs),
            "total_chars": len(full_text),
            "full_text": full_text,
        }
    except (OSError, ValueError, KeyError) as e:
        logger.warning("word_extraction_failed", path=str(path), error=str(e))
        return {"status": "error", "error": str(e)}


def _extract_text_from_code(path: Path) -> dict[str, Any]:
    """Read a plain-text code file."""
    ext_to_lang = {
        ".py": "python",
        ".ipynb": "jupyter",
        ".js": "javascript",
        ".ts": "typescript",
        ".java": "java",
        ".sql": "sql",
        ".r": "r",
        ".R": "r",
    }
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            content = f.read()
        return {
            "status": "success",
            "language": ext_to_lang.get(path.suffix.lower(), "unknown"),
            "total_chars": len(content),
            "line_count": content.count("\n") + 1,
            "full_text": content,
        }
    except (OSError, UnicodeDecodeError) as e:
        logger.warning("code_extraction_failed", path=str(path), error=str(e))
        return {"status": "error", "error": str(e)}


def extract_content(
    file_info: dict[str, Any], base_path: Path, grammar: PathGrammar
) -> dict[str, Any]:
    """Extract text from a single file based on its `file_type`."""
    path = Path(file_info["file_path"])
    file_type = file_info.get("file_type") or get_file_type(path, grammar)

    if file_type == "pdf":
        extraction_result = _extract_text_from_pdf(path)
    elif file_type == "word":
        extraction_result = _extract_text_from_word(path)
    elif file_type == "code":
        extraction_result = _extract_text_from_code(path)
    elif file_type in {"text", "data"}:
        extraction_result = _extract_text_from_code(path)
    else:
        extraction_result = {
            "status": "unsupported",
            "file_type": file_type,
        }

    if extraction_result.get("full_text"):
        extraction_result["detected_language"] = detect_language(
            extraction_result["full_text"]
        )

    return {
        **file_info,
        "extraction": extraction_result,
        "extracted_at": datetime.now(UTC).isoformat(),
    }


# ============================================================================
# Directory scanning
# ============================================================================


def scan_directory(
    base_path: Path,
    grammar: PathGrammar,
    account: str,
    file_types: list[str] | None = None,
    max_files: int | None = None,
    include_extraction: bool = False,
) -> Iterator[dict[str, Any]]:
    """
    Scan a directory and yield one dict per discovered file.

    Args:
        base_path: Root directory to walk.
        grammar: Per-archive rules.
        account: The `account` label stamped on every row (e.g. "university_of_galway").
        file_types: If set, restrict to these file_type labels.
        max_files: Optional cap on the number of rows yielded.
        include_extraction: If True, extract text content (slower).

    Yields:
        One row per file (merged by `file_hash` downstream).
    """
    if not base_path.exists():
        logger.warning("directory_not_found", path=str(base_path), account=account)
        return

    if file_types is not None:
        allowed_extensions: set[str] = set()
        for ft in file_types:
            allowed_extensions.update(grammar.file_type_extensions.get(ft, set()))
    else:
        allowed_extensions = {
            ext for exts in grammar.file_type_extensions.values() for ext in exts
        }

    count = 0
    for path in base_path.rglob("*"):
        if max_files is not None and count >= max_files:
            return
        if not path.is_file():
            continue
        if should_skip_file(path, grammar):
            continue
        if path.suffix.lower() not in allowed_extensions:
            continue

        try:
            file_hash = compute_file_hash(path)
            metadata = get_document_metadata(path, base_path, grammar)
            row: dict[str, Any] = {
                "id": file_hash[:16],
                "file_hash": file_hash,
                "account": account,
                "discovered_at": datetime.now(UTC).isoformat(),
                **metadata,
            }
            if include_extraction:
                row = extract_content(row, base_path, grammar)
            yield row
            count += 1
        except (OSError, PermissionError) as e:
            logger.warning("file_scan_error", path=str(path), error=str(e))
            yield {
                "id": str(path),
                "file_path": str(path),
                "file_name": path.name,
                "account": account,
                "error": str(e),
                "status": "error",
                "discovered_at": datetime.now(UTC).isoformat(),
            }


# ============================================================================
# File hash tracker (hoisted from local_documents.py)
# ============================================================================


class FileHashTracker:
    """
    Track file hashes for incremental processing.

    Uses DuckDB for persistent hash storage. Hoisted from
    `oideachais/dlt_sources/ireland/local_documents.py:420` to
    `oideachais/dlt_sources/author_archive/_scanner.py`. The old import
    path is preserved by a re-export shim.
    """

    def __init__(self, db_path: str | Path | None = None) -> None:
        self.db_path = (
            Path(db_path)
            if db_path
            else Path("./.dlt/author_archive_file_hashes.duckdb")
        )
        self._ensure_table()

    def _ensure_table(self) -> None:
        try:
            import duckdb
        except ImportError:
            logger.warning("duckdb_not_available_hash_tracker_no_op")
            return

        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            conn = duckdb.connect(str(self.db_path))
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS file_hashes (
                    path VARCHAR PRIMARY KEY,
                    file_hash VARCHAR,
                    last_processed TIMESTAMP,
                    status VARCHAR
                )
                """
            )
            conn.close()
        except (OSError, RuntimeError) as e:
            logger.debug("hash_tracker_init_failed", error=str(e))

    def get_hash(self, path: str) -> str | None:
        try:
            import duckdb

            conn = duckdb.connect(str(self.db_path))
            result = conn.execute(
                "SELECT file_hash FROM file_hashes WHERE path = ?", [path]
            ).fetchone()
            conn.close()
            return result[0] if result else None
        except (ImportError, OSError, RuntimeError) as e:
            logger.debug("hash_lookup_failed", path=path, error=str(e))
            return None

    def set_hash(self, path: str, file_hash: str, status: str = "processed") -> None:
        try:
            import duckdb

            conn = duckdb.connect(str(self.db_path))
            conn.execute(
                """
                INSERT OR REPLACE INTO file_hashes (path, file_hash, last_processed, status)
                VALUES (?, ?, CURRENT_TIMESTAMP, ?)
                """,
                [path, file_hash, status],
            )
            conn.close()
        except (ImportError, OSError, RuntimeError) as e:
            logger.debug("hash_store_failed", path=path, error=str(e))

    def has_changed(self, path: str, current_hash: str) -> bool:
        stored_hash = self.get_hash(path)
        return stored_hash != current_hash

    def get_changed_files(
        self, files: Iterator[dict[str, Any]]
    ) -> Iterator[dict[str, Any]]:
        for file_info in files:
            current_hash = file_info.get("file_hash")
            path = file_info.get("file_path")
            if current_hash and path:
                if self.has_changed(path, current_hash):
                    file_info["is_new_or_changed"] = True
                    yield file_info
            else:
                yield file_info


__all__ = [
    "DEFAULT_FILE_TYPE_EXTENSIONS",
    "DEFAULT_SKIP_PATTERNS",
    "PathGrammar",
    "FileHashTracker",
    "compute_file_hash",
    "get_file_type",
    "extract_course_code",
    "detect_subject",
    "detect_domain",
    "requires_handwriting_ocr",
    "should_skip_file",
    "detect_language",
    "get_document_metadata",
    "extract_content",
    "scan_directory",
]
