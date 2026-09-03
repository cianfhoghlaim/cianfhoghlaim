#!/usr/bin/env python3
"""Sweep ie -> ireland within the dlt/ tree itself (for files that import from the old ie/ path)."""
from __future__ import annotations
import re
from pathlib import Path

MAPPINGS = [
    (r"british_isles\.ie\b", "british_isles.ireland"),
    (r"british_isles\.en\b", "british_isles.england"),
]


def sweep_file(path: Path) -> int:
    text = path.read_text()
    original = text
    n = 0
    for pattern, replacement in MAPPINGS:
        text, c = re.subn(pattern, replacement, text)
        n += c
    if text != original:
        path.write_text(text)
    return n


def main() -> None:
    # Find all .py files under cianfhoghlaim/ that still reference british_isles.ie or british_isles.en
    root = Path("/Users/cianmacandeisigh/dev/kings_college_galway/cianfhoghlaim")
    total = 0
    files_changed = 0
    for py in root.rglob("*.py"):
        text = py.read_text()
        if "british_isles.ie" in text or "british_isles.en" in text:
            n = sweep_file(py)
            if n > 0:
                total += n
                files_changed += 1
                print(f"[OK] {py.relative_to(root.parent)}: {n}")
    print(f"\nTotal: {total} replacements in {files_changed} files")


if __name__ == "__main__":
    main()