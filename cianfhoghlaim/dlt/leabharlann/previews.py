"""
Preview pairing helper for the leabharlann_books dlt source.

Pairs `<book>.pdf` with `<book>_preview.png` in a sibling `previews/`
directory and returns the matched preview path. The preview is recorded
as a column on the parent book's row, not indexed as a separate document.

Pattern: `<book>.pdf` → `<subject>/previews/<book>_preview.png`
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


def find_preview_for(
    book_path: Path,
    previews_dir: Path,
) -> str | None:
    """
    Return the path to the preview image for `book_path`, or None.

    Tries in order:
    1. `<book_stem>_preview.png` (canonical Zotero/lit-catalog pattern)
    2. `<book_stem>.png`
    3. `<book_stem>.jpg`
    """
    stem = book_path.stem
    for suffix in ("_preview.png", ".png", ".jpg", ".jpeg"):
        candidate = previews_dir / f"{stem}{suffix}"
        if candidate.exists():
            return str(candidate)
    return None


def iter_books_with_previews(
    books_dir: Path,
    file_types: tuple[str, ...] = ("pdf",),
) -> Iterator[dict[str, Any]]:
    """
    Yield `{book_path, preview_path}` dicts for every supported book file
    in `books_dir`. The preview_path may be None.

    This is a pure function over the filesystem; the dlt resource calls it
    per subject directory.
    """
    if not books_dir.exists():
        return
    previews_dir = books_dir / "previews"
    for path in books_dir.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower().lstrip(".") not in file_types:
            continue
        if path.parent.name == "previews":
            # Skip preview files themselves.
            continue
        yield {
            "book_path": path,
            "preview_path": find_preview_for(path, previews_dir),
        }


__all__ = ["find_preview_for", "iter_books_with_previews"]
