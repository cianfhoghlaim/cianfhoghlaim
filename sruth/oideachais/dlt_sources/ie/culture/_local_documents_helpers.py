"""
Shared helpers split from ireland/local_documents.py

Phase 3D of openspec change.
"""

import hashlib
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
import dlt
import structlog
from dlt_sources.constants.local_sources import BUNCHLOCH_PATH, EXTRACTION_CONFIG, FILE_TYPE_EXTENSIONS, LOCAL_SUBJECT_PATHS, detect_language, get_document_metadata, get_file_type, should_process_file

def _compute_file_hash(path: Path, chunk_size: int = 8192) -> str:
    """Compute SHA-256 hash of file for change detection."""
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            sha256.update(chunk)
    return sha256.hexdigest()

def _extract_content(file_info: dict[str, Any]) -> dict[str, Any]:
    """Extract content from a file based on its type."""
    path = Path(file_info["path"])
    file_type = file_info.get("file_type", get_file_type(path))

    extraction_result: dict[str, Any]

    if file_type == "pdf":
        extraction_result = _extract_text_from_pdf(path)
    elif file_type == "word":
        extraction_result = _extract_text_from_word(path)
    elif file_type == "code":
        extraction_result = _extract_text_from_code(path)
    elif file_type == "text":
        try:
            with open(path, encoding="utf-8", errors="ignore") as f:
                content = f.read()
            extraction_result = {
                "status": "success",
                "total_chars": len(content),
                "full_text": content,
            }
        except (OSError, UnicodeDecodeError) as e:
            logger.warning("text_extraction_failed", path=str(path), error=str(e))
            extraction_result = {"status": "error", "error": str(e)}
    elif file_type == "image":
        # Images handled separately (OCR)
        extraction_result = {
            "status": "pending_ocr",
            "requires_ocr": True,
        }
    else:
        extraction_result = {
            "status": "unsupported",
            "file_type": file_type,
        }

    # Detect language from content if available
    if extraction_result.get("full_text"):
        extraction_result["detected_language"] = detect_language(
            extraction_result["full_text"]
        )

    return {
        **file_info,
        "extraction": extraction_result,
        "extracted_at": datetime.now(UTC).isoformat(),
    }

def _extract_text_from_code(path: Path) -> dict[str, Any]:
    """Extract content from code files."""
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # Detect programming language from extension
        ext_to_lang = {
            ".py": "python",
            ".ipynb": "jupyter",
            ".js": "javascript",
            ".ts": "typescript",
            ".sql": "sql",
            ".r": "r",
            ".R": "r",
        }
        language = ext_to_lang.get(path.suffix.lower(), "unknown")

        return {
            "status": "success",
            "language": language,
            "total_chars": len(content),
            "line_count": content.count("\n") + 1,
            "full_text": content,
        }

    except (OSError, UnicodeDecodeError) as e:
        logger.warning("code_extraction_failed", path=str(path), error=str(e))
        return {
            "status": "error",
            "error": str(e),
        }

def _extract_text_from_pdf(path: Path) -> dict[str, Any]:
    """Extract text content from PDF file."""
    config = EXTRACTION_CONFIG["pdf"]

    try:
        import pymupdf

        doc = pymupdf.open(str(path))
        pages = []
        total_chars = 0

        for page_num, page in enumerate(doc):
            if page_num >= config["max_pages"]:
                break

            text = page.get_text()
            pages.append({
                "page_number": page_num + 1,
                "text": text,
                "char_count": len(text),
            })
            total_chars += len(text)

        doc.close()

        return {
            "status": "success",
            "page_count": len(pages),
            "total_chars": total_chars,
            "pages": pages,
            "full_text": "\n\n".join(p["text"] for p in pages),
        }

    except ImportError:
        return {
            "status": "error",
            "error": "pymupdf not installed",
        }
    except (OSError, ValueError, RuntimeError) as e:
        logger.warning("pdf_extraction_failed", path=str(path), error=str(e))
        return {
            "status": "error",
            "error": str(e),
        }

def _extract_text_from_word(path: Path) -> dict[str, Any]:
    """Extract text content from Word document."""
    try:
        from docx import Document

        doc = Document(str(path))
        paragraphs = []

        for para in doc.paragraphs:
            if para.text.strip():
                paragraphs.append(para.text)

        full_text = "\n\n".join(paragraphs)

        return {
            "status": "success",
            "paragraph_count": len(paragraphs),
            "total_chars": len(full_text),
            "full_text": full_text,
        }

    except ImportError:
        return {
            "status": "error",
            "error": "python-docx not installed",
        }
    except (OSError, ValueError, KeyError) as e:
        logger.warning("word_extraction_failed", path=str(path), error=str(e))
        return {
            "status": "error",
            "error": str(e),
        }

def _scan_directory(
    base_path: Path,
    subject: str | None = None,
    file_types: list[str] | None = None,
    max_files: int | None = None,
) -> Iterator[dict[str, Any]]:
    """
    Scan directory for files to process.

    Args:
        base_path: Base directory to scan
        subject: Optional subject filter (comp_science, gaeilge, etc.)
        file_types: Optional list of file types to include
        max_files: Optional maximum number of files to yield
    """
    if not base_path.exists():
        return

    # Determine search paths
    if subject and subject in LOCAL_SUBJECT_PATHS:
        search_paths = [LOCAL_SUBJECT_PATHS[subject]]
    else:
        search_paths = [base_path]

    # Build extension set
    allowed_extensions: set[str] = set()
    if file_types:
        for ft in file_types:
            allowed_extensions.update(FILE_TYPE_EXTENSIONS.get(ft, []))
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

            if not should_process_file(path):
                continue

            if path.suffix.lower() not in allowed_extensions:
                continue

            try:
                stat = path.stat()
                file_hash = _compute_file_hash(path)

                metadata = get_document_metadata(path)

                yield {
                    "id": file_hash[:16],  # Short hash as ID
                    "path": str(path),
                    "filename": path.name,
                    "file_hash": file_hash,
                    "file_size": stat.st_size,
                    "modified_at": datetime.fromtimestamp(
                        stat.st_mtime, tz=UTC
                    ).isoformat(),
                    "created_at": datetime.fromtimestamp(
                        stat.st_ctime, tz=UTC
                    ).isoformat(),
                    "discovered_at": datetime.now(UTC).isoformat(),
                    **metadata,
                }
                count += 1

            except (OSError, PermissionError) as e:
                # Log but continue on file access errors
                yield {
                    "id": str(path),
                    "path": str(path),
                    "filename": path.name,
                    "error": str(e),
                    "status": "error",
                    "discovered_at": datetime.now(UTC).isoformat(),
                }
