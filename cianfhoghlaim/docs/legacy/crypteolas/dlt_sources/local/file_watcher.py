"""
DLT source for local file processing.

Watches local directories for documentation and code files.
Supports:
- Markdown documentation
- PDF files (with text extraction)
- Source code (Python, TypeScript, Rust, Go, Solidity)

Features:
- Content hashing for change detection
- Tree-sitter language detection
- Garage S3 backup for files
"""

import hashlib
import mimetypes
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

import dlt


# File type configurations
SUPPORTED_EXTENSIONS = {
    # Documentation
    ".md": {"type": "markdown", "category": "docs"},
    ".mdx": {"type": "markdown", "category": "docs"},
    ".rst": {"type": "restructuredtext", "category": "docs"},
    ".txt": {"type": "text", "category": "docs"},
    ".pdf": {"type": "pdf", "category": "docs"},
    # Code
    ".py": {"type": "python", "category": "code"},
    ".ts": {"type": "typescript", "category": "code"},
    ".tsx": {"type": "typescript", "category": "code"},
    ".js": {"type": "javascript", "category": "code"},
    ".jsx": {"type": "javascript", "category": "code"},
    ".rs": {"type": "rust", "category": "code"},
    ".go": {"type": "go", "category": "code"},
    ".sol": {"type": "solidity", "category": "code"},
    ".vy": {"type": "vyper", "category": "code"},
    ".move": {"type": "move", "category": "code"},
    # Config
    ".json": {"type": "json", "category": "config"},
    ".yaml": {"type": "yaml", "category": "config"},
    ".yml": {"type": "yaml", "category": "config"},
    ".toml": {"type": "toml", "category": "config"},
}


def _compute_file_hash(file_path: Path) -> str:
    """Compute SHA-256 hash of file content."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _read_file_content(file_path: Path) -> str | None:
    """Read file content as text."""
    try:
        # Handle binary files
        ext = file_path.suffix.lower()
        if ext == ".pdf":
            return _extract_pdf_text(file_path)

        # Text files
        encodings = ["utf-8", "latin-1", "cp1252"]
        for encoding in encodings:
            try:
                return file_path.read_text(encoding=encoding)
            except UnicodeDecodeError:
                continue

        return None
    except Exception:
        return None


def _extract_pdf_text(file_path: Path) -> str | None:
    """Extract text from PDF file."""
    try:
        # Try pypdf first
        try:
            from pypdf import PdfReader

            reader = PdfReader(str(file_path))
            text_parts = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            return "\n\n".join(text_parts) if text_parts else None
        except ImportError:
            pass

        # Fallback to pdfplumber
        try:
            import pdfplumber

            with pdfplumber.open(file_path) as pdf:
                text_parts = []
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
                return "\n\n".join(text_parts) if text_parts else None
        except ImportError:
            pass

        return None
    except Exception:
        return None


def _detect_language(file_path: Path, content: str | None) -> str | None:
    """Detect programming language from file."""
    ext = file_path.suffix.lower()
    config = SUPPORTED_EXTENSIONS.get(ext, {})
    return config.get("type")


def _get_file_metadata(file_path: Path) -> dict[str, Any]:
    """Get file metadata."""
    stat = file_path.stat()
    return {
        "size": stat.st_size,
        "created_at": datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc).isoformat(),
        "modified_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
        "permissions": oct(stat.st_mode)[-3:],
    }


def _process_file(file_path: Path, base_path: Path) -> dict[str, Any]:
    """Process a single file."""
    ext = file_path.suffix.lower()
    config = SUPPORTED_EXTENSIONS.get(ext, {"type": "unknown", "category": "other"})

    content = _read_file_content(file_path)
    content_hash = _compute_file_hash(file_path)
    metadata = _get_file_metadata(file_path)

    relative_path = str(file_path.relative_to(base_path))

    return {
        "path": str(file_path),
        "relative_path": relative_path,
        "filename": file_path.name,
        "extension": ext,
        "file_type": config["type"],
        "category": config["category"],
        "content": content,
        "content_hash": content_hash,
        "size": metadata["size"],
        "created_at": metadata["created_at"],
        "modified_at": metadata["modified_at"],
        "source_type": "local",
        "indexed_at": datetime.now(timezone.utc).isoformat(),
    }


def _should_ignore(path: Path, ignore_patterns: list[str]) -> bool:
    """Check if path should be ignored."""
    path_str = str(path)

    # Default ignores
    default_ignores = [
        "__pycache__",
        ".git",
        ".venv",
        "venv",
        "node_modules",
        ".next",
        "dist",
        "build",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "target",  # Rust
        ".cargo",
    ]

    for pattern in default_ignores + ignore_patterns:
        if pattern in path_str:
            return True

    return False


@dlt.source(name="local_files")
def local_files_source(
    watch_paths: list[str],
    file_types: list[str] | None = None,
    ignore_patterns: list[str] | None = None,
    include_hidden: bool = False,
    max_file_size_mb: float = 10.0,
):
    """
    DLT source for local file processing.

    Args:
        watch_paths: List of directory paths to watch
        file_types: File extensions to include (e.g., [".md", ".py"])
        ignore_patterns: Patterns to ignore
        include_hidden: Whether to include hidden files
        max_file_size_mb: Maximum file size in MB

    Returns:
        DLT source with local file content
    """
    file_types = file_types or list(SUPPORTED_EXTENSIONS.keys())
    ignore_patterns = ignore_patterns or []
    max_size_bytes = int(max_file_size_mb * 1024 * 1024)

    @dlt.resource(
        name="local_documents",
        write_disposition="merge",
        primary_key=["path"],
    )
    def local_documents() -> Iterator[dict[str, Any]]:
        """Local document files."""
        for path_str in watch_paths:
            base_path = Path(path_str).resolve()
            if not base_path.exists():
                continue

            for file_path in base_path.rglob("*"):
                # Skip directories
                if file_path.is_dir():
                    continue

                # Check extension
                if file_path.suffix.lower() not in file_types:
                    continue

                # Check hidden files
                if not include_hidden and file_path.name.startswith("."):
                    continue

                # Check ignore patterns
                if _should_ignore(file_path, ignore_patterns):
                    continue

                # Check file size
                try:
                    if file_path.stat().st_size > max_size_bytes:
                        continue
                except OSError:
                    continue

                # Process file
                try:
                    yield _process_file(file_path, base_path)
                except Exception as e:
                    yield {
                        "path": str(file_path),
                        "error": str(e),
                        "status": "error",
                        "indexed_at": datetime.now(timezone.utc).isoformat(),
                    }

    return local_documents


@dlt.source(name="workspace")
def workspace_source(
    workspace_path: str,
    project_name: str | None = None,
    include_code: bool = True,
    include_docs: bool = True,
):
    """
    DLT source for a workspace/project directory.

    Intelligently processes:
    - Documentation (README, docs/, *.md)
    - Source code (with language detection)
    - Configuration files

    Args:
        workspace_path: Path to the workspace root
        project_name: Optional project name
        include_code: Whether to include source code
        include_docs: Whether to include documentation

    Returns:
        DLT source with workspace content
    """
    base_path = Path(workspace_path).resolve()
    project_name = project_name or base_path.name

    def _get_file_types() -> list[str]:
        """Get file types based on flags."""
        types = []
        if include_docs:
            types.extend([".md", ".mdx", ".rst", ".txt", ".pdf"])
        if include_code:
            types.extend([".py", ".ts", ".tsx", ".js", ".jsx", ".rs", ".go", ".sol", ".vy"])
        return types

    @dlt.resource(
        name="workspace_files",
        write_disposition="merge",
        primary_key=["path"],
    )
    def workspace_files() -> Iterator[dict[str, Any]]:
        """Workspace files."""
        file_types = _get_file_types()

        for file_path in base_path.rglob("*"):
            if file_path.is_dir():
                continue

            if file_path.suffix.lower() not in file_types:
                continue

            if _should_ignore(file_path, []):
                continue

            try:
                result = _process_file(file_path, base_path)
                result["project"] = project_name
                yield result
            except Exception:
                continue

    @dlt.resource(
        name="workspace_readme",
        write_disposition="merge",
        primary_key=["path"],
    )
    def workspace_readme() -> Iterator[dict[str, Any]]:
        """Workspace README files."""
        readme_patterns = ["README.md", "README", "readme.md", "Readme.md"]

        for pattern in readme_patterns:
            readme_path = base_path / pattern
            if readme_path.exists():
                result = _process_file(readme_path, base_path)
                result["project"] = project_name
                result["is_readme"] = True
                yield result
                break

    return workspace_files, workspace_readme


@dlt.source(name="code_files")
def code_files_source(
    paths: list[str],
    languages: list[str] | None = None,
    include_tests: bool = False,
):
    """
    DLT source for code files with language filtering.

    Args:
        paths: List of directory paths
        languages: Languages to include (python, typescript, rust, go, solidity)
        include_tests: Whether to include test files

    Returns:
        DLT source with code files
    """
    # Map languages to extensions
    language_extensions = {
        "python": [".py"],
        "typescript": [".ts", ".tsx"],
        "javascript": [".js", ".jsx"],
        "rust": [".rs"],
        "go": [".go"],
        "solidity": [".sol"],
        "vyper": [".vy"],
        "move": [".move"],
    }

    # Determine extensions to include
    if languages:
        extensions = []
        for lang in languages:
            extensions.extend(language_extensions.get(lang.lower(), []))
    else:
        extensions = [ext for exts in language_extensions.values() for ext in exts]

    # Test file patterns
    test_patterns = ["test_", "_test", "tests/", "test/", "__tests__", ".test.", ".spec."]

    def _is_test_file(path: Path) -> bool:
        """Check if file is a test file."""
        path_str = str(path).lower()
        return any(pattern in path_str for pattern in test_patterns)

    @dlt.resource(
        name="code_files",
        write_disposition="merge",
        primary_key=["path"],
    )
    def code_files() -> Iterator[dict[str, Any]]:
        """Code files with language detection."""
        for path_str in paths:
            base_path = Path(path_str).resolve()
            if not base_path.exists():
                continue

            for file_path in base_path.rglob("*"):
                if file_path.is_dir():
                    continue

                if file_path.suffix.lower() not in extensions:
                    continue

                if _should_ignore(file_path, []):
                    continue

                # Check test files
                if not include_tests and _is_test_file(file_path):
                    continue

                try:
                    result = _process_file(file_path, base_path)
                    result["language"] = _detect_language(file_path, result.get("content"))
                    result["is_test"] = _is_test_file(file_path)
                    yield result
                except Exception:
                    continue

    return code_files


# =========================================================================
# Utility Functions
# =========================================================================

def get_changed_files(
    watch_path: str,
    since: datetime | None = None,
    hash_cache: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    """
    Get files that have changed since a given time or hash cache.

    Args:
        watch_path: Directory to watch
        since: Only include files modified after this time
        hash_cache: Previous hash cache for comparison

    Returns:
        List of changed files with their details
    """
    base_path = Path(watch_path).resolve()
    hash_cache = hash_cache or {}
    changed = []

    for file_path in base_path.rglob("*"):
        if file_path.is_dir():
            continue

        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        if _should_ignore(file_path, []):
            continue

        try:
            stat = file_path.stat()
            modified_at = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)

            # Check modification time
            if since and modified_at <= since:
                continue

            # Check hash
            current_hash = _compute_file_hash(file_path)
            path_str = str(file_path)

            if path_str in hash_cache and hash_cache[path_str] == current_hash:
                continue

            changed.append({
                "path": path_str,
                "hash": current_hash,
                "modified_at": modified_at.isoformat(),
                "change_type": "new" if path_str not in hash_cache else "modified",
            })

        except Exception:
            continue

    return changed


def backup_files_to_garage(
    watch_path: str,
    file_types: list[str] | None = None,
) -> list[dict[str, Any]]:
    """
    Backup local files to Garage S3.

    Args:
        watch_path: Directory to backup
        file_types: File extensions to include

    Returns:
        List of backup results
    """
    try:
        from tuatha.crypteolas.storage.garage_client import get_garage_client
    except ImportError:
        return []

    file_types = file_types or list(SUPPORTED_EXTENSIONS.keys())
    base_path = Path(watch_path).resolve()
    garage = get_garage_client()
    results = []

    for file_path in base_path.rglob("*"):
        if file_path.is_dir():
            continue

        if file_path.suffix.lower() not in file_types:
            continue

        if _should_ignore(file_path, []):
            continue

        try:
            stored = garage.store_local_file(file_path, source_type="local")
            results.append({
                "path": str(file_path),
                "s3_key": stored.key,
                "s3_bucket": stored.bucket,
                "size": stored.size,
                "status": "success",
            })
        except Exception as e:
            results.append({
                "path": str(file_path),
                "error": str(e),
                "status": "error",
            })

    return results
