#!/usr/bin/env python3
"""Fix broken dlt_sources.{nation}.X imports in dagster asset files.

The new canonical paths are cianfhoghlaim.dlt.british_isles.{full_name}.X.
The 2-letter code → full country name mapping:
  en  → england
  sct → scotland
  wls → wales
  ni  → northern_ireland
  iom → isle_of_man
  jey → jersey
  ggy → guernsey
"""
from __future__ import annotations
import re
from pathlib import Path

CODE_TO_NAME = {
    "en": "england",
    "sct": "scotland",
    "wls": "wales",
    "ni": "northern_ireland",
    "iom": "isle_of_man",
    "jey": "jersey",
    "ggy": "guernsey",
}

# Build the regex patterns
PATTERNS = []
for code, name in CODE_TO_NAME.items():
    # dlt_sources.{code}.X → cianfhoghlaim.dlt.british_isles.{name}.X
    PATTERNS.append((rf"\bdlt_sources\.{code}\.", f"cianfhoghlaim.dlt.british_isles.{name}."))


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
    root = Path("/Users/cianmacandeisigh/dev/kings_college_galway/cianfhoghlaim/dagster")
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