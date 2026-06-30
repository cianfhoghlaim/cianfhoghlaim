#!/usr/bin/env python3
"""Fix broken imports in dlt/british_isles/ files. Convert legacy paths to canonical cianfhoghlaim.dlt.* paths."""
from __future__ import annotations
import re
from pathlib import Path

# Mapping: (old_pattern, new_replacement)
# These are the 4 legacy patterns found across the 8 nations
MAPPINGS = [
    # Law sources use the canonical legislation helper
    (r"from dlt_sources\.law\._legislation_helper import _crawl_legislation",
     "from cianfhoghlaim.dlt.law._legislation_helper import _crawl_legislation"),
    # Firecrawl: ..common -> ....common (need 4 levels to reach dlt/common from a nested file)
    # But actually we need to compute the right relative path
    # The .archive files use ...common (3 dots) which is WRONG
    # From dlt/british_isles/sct/law/X.py, dlt/common is at .... (4 dots)
    (r"from \.\.\.common\.firecrawl_source import (\w+(?:, \w+)*)",
     r"from cianfhoghlaim.dlt.common.firecrawl_source import \1"),
    (r"from \.\.\.common\.incremental import (\w+(?:, \w+)*)",
     r"from cianfhoghlaim.dlt.common.incremental import \1"),
    (r"from \.\.\.common\.http_client import (\w+(?:, \w+)*)",
     r"from cianfhoghlaim.dlt.common.http_client import \1"),
    (r"from \.\.\.common\.incremental import _crawl_source",
     "from cianfhoghlaim.dlt.common.incremental import crawl_source"),  # sct/jersey/ggy used wrong function
    # The old ireland.curriculum_source._crawl_source was moved to cianfhoghlaim.dlt.common.incremental.crawl_source
    (r"from \.\.\.\.ireland\.curriculum_source import _crawl_source",
     "from cianfhoghlaim.dlt.common.incremental import crawl_source"),
    # shared.http - the england/education/school_info.py uses shared.http.get_info_schools_client
    (r"from shared\.http import (\w+(?:, \w+)*)",
     r"from cianfhoghlaim.dlt.common.http_client import \1"),
    # dlt_sources.ie.X for the moved files
    (r"from dlt_sources\.ie\.education\.curriculum_source import (\w+(?:, \w+)*)",
     r"from cianfhoghlaim.dlt.british_isles.ireland.education.curriculum_source import \1"),
    (r"from dlt_sources\.ie\.culture\.duchas import (\w+(?:, \w+)*)",
     r"from cianfhoghlaim.dlt.british_isles.ireland.culture.duchas import \1"),
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
    root = Path("/Users/cianmacandeisigh/dev/kings_college_galway/cianfhoghlaim/dlt/british_isles")
    total = 0
    files_changed = 0
    for py in root.rglob("*.py"):
        text = py.read_text()
        n = sweep_file(py)
        if n > 0:
            total += n
            files_changed += 1
            print(f"[OK] {py.relative_to(root.parent)}: {n}")
    print(f"\nTotal: {total} replacements in {files_changed} files")


if __name__ == "__main__":
    main()