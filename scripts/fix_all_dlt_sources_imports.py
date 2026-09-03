#!/usr/bin/env python3
"""Deep sweep: fix ALL remaining dlt_sources.* imports to canonical cianfhoghlaim.dlt.* paths."""
from __future__ import annotations
import re
from pathlib import Path

# Mapping of known broken imports
PATTERNS = [
    # dlt_sources.official_media.X → cianfhoghlaim.dlt.official_media.X
    (r"\bdlt_sources\.official_media\b", "cianfhoghlaim.dlt.official_media"),
    # dlt_sources.cross.X → cianfhoghlaim.dlt.cross.X
    (r"\bdlt_sources\.cross\b", "cianfhoghlaim.dlt.cross"),
    # dlt_sources.ie.X → cianfhoghlaim.dlt.british_isles.ireland.X
    (r"\bdlt_sources\.ie\b", "cianfhoghlaim.dlt.british_isles.ireland"),
    # dlt_sources.en.X → cianfhoghlaim.dlt.british_isles.england.X
    (r"\bdlt_sources\.en\b", "cianfhoghlaim.dlt.british_isles.england"),
    # dlt_sources.sct.X → cianfhoghlaim.dlt.british_isles.scotland.X
    (r"\bdlt_sources\.sct\b", "cianfhoghlaim.dlt.british_isles.scotland"),
    # dlt_sources.wls.X → cianfhoghlaim.dlt.british_isles.wales.X
    (r"\bdlt_sources\.wls\b", "cianfhoghlaim.dlt.british_isles.wales"),
    # dlt_sources.ni.X → cianfhoghlaim.dlt.british_isles.northern_ireland.X
    (r"\bdlt_sources\.ni\b", "cianfhoghlaim.dlt.british_isles.northern_ireland"),
    # dlt_sources.iom.X → cianfhoghlaim.dlt.british_isles.isle_of_man.X
    (r"\bdlt_sources\.iom\b", "cianfhoghlaim.dlt.british_isles.isle_of_man"),
    # dlt_sources.jey.X → cianfhoghlaim.dlt.british_isles.jersey.X
    (r"\bdlt_sources\.jey\b", "cianfhoghlaim.dlt.british_isles.jersey"),
    # dlt_sources.ggy.X → cianfhoghlaim.dlt.british_isles.guernsey.X
    (r"\bdlt_sources\.ggy\b", "cianfhoghlaim.dlt.british_isles.guernsey"),
    # dlt_sources.leabharlann.X → cianfhoghlaim.dlt.leabharlann.X
    (r"\bdlt_sources\.leabharlann\b", "cianfhoghlaim.dlt.leabharlann"),
    # dlt_sources.law.X → cianfhoghlaim.dlt.law.X
    (r"\bdlt_sources\.law\b", "cianfhoghlaim.dlt.law"),
    # dlt_sources.common.X → cianfhoghlaim.dlt.common.X
    (r"\bdlt_sources\.common\b", "cianfhoghlaim.dlt.common"),
    # dlt_sources.subjects.X → cianfhoghlaim.dlt.british_isles.ireland.education.subjects.X
    (r"\bdlt_sources\.subjects\b", "cianfhoghlaim.dlt.british_isles.ireland.education.subjects"),
    # dlt_sources._university_deep_factory → cianfhoghlaim.dlt._university_deep_factory
    (r"\bdlt_sources\._university_deep_factory\b", "cianfhoghlaim.dlt._university_deep_factory"),
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