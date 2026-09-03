#!/usr/bin/env python3
"""Sweep consumer files: replace british_isles.ie → british_isles.ireland and british_isles.en → british_isles.england.

Usage: python scripts/sweep_british_isles_names.py
"""
from __future__ import annotations
import re
from pathlib import Path

# Two mappings
MAPPINGS = [
    (r"british_isles\.ie\b", "british_isles.ireland"),
    (r"british_isles\.ie/", "british_isles/ireland/"),
    (r"british_isles/en/", "british_isles/england/"),
    (r"british_isles\.en\b", "british_isles.england"),
]

# Consumer files to sweep
CONSUMER_FILES = [
    "cianfhoghlaim/dagster/assets/uk_education_assets.py",
    "cianfhoghlaim/dagster/assets/wire_unwired_dlt_sources.py",
    "cianfhoghlaim/dagster/assets/multi_nation_curriculum_assets.py",
    "cianfhoghlaim/dagster/assets/celtic_language_assets.py",
    "cianfhoghlaim/dagster/assets/unified_audio_dataset_assets.py",
    "cianfhoghlaim/dagster/assets/ie/education/aistear_dlt_assets.py",
    "cianfhoghlaim/dagster/factories.py",
    "cianfhoghlaim/dlt/gaois.py",
    "cianfhoghlaim/dlt/duchas.py",
    "cianfhoghlaim/notebooks/mission_control.py",
    "cianfhoghlaim/tests/_oideachais/dlt_sources/ie/education/test_curriculum_source_local_cache.py",
]


def sweep_file(path: Path) -> tuple[int, list[str]]:
    text = path.read_text()
    original = text
    replacements = 0
    for pattern, replacement in MAPPINGS:
        text, n = re.subn(pattern, replacement, text)
        replacements += n
    if text != original:
        path.write_text(text)
    return replacements


def main() -> None:
    total = 0
    files_changed = 0
    for relpath in CONSUMER_FILES:
        path = Path("/Users/cianmacandeisigh/dev/kings_college_galway") / relpath
        if not path.exists():
            print(f"[SKIP] {relpath}")
            continue
        n = sweep_file(path)
        if n > 0:
            files_changed += 1
            total += n
            print(f"[OK] {relpath}: {n}")
    print(f"\nTotal: {total} replacements in {files_changed} files")


if __name__ == "__main__":
    main()