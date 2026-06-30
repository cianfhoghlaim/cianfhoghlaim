#!/usr/bin/env python3
"""Fix remaining dlt_sources.constants imports."""
from __future__ import annotations
import re
from pathlib import Path

PATTERNS = [
    (r"\bdlt_sources\.constants\.local_sources\b", "cianfhoghlaim.dlt.constants.local_sources"),
]


def sweep_file(path: Path) -> int:
    text = path.read_text()
    original = text
    n = 0
    for pattern, replacement in PATTERNS:
        text, c = re.subn(pattern, replacement, text)
        n += c
    if text != original:
        path.write_text(text)
    return n


def main() -> None:
    root = Path("/Users/cianmacandeisigh/dev/kings_college_galway/cianfhoghlaim")
    total = 0
    files_changed = 0
    for py in root.rglob("*.py"):
        text = py.read_text()
        if "dlt_sources." in text:
            n = sweep_file(py)
            if n > 0:
                total += n
                files_changed += 1
                print(f"[OK] {py.relative_to(root.parent)}: {n}")
    print(f"\nTotal: {total} replacements in {files_changed} files")


if __name__ == "__main__":
    main()