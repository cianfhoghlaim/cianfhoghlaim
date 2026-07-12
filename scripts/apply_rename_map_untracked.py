#!/usr/bin/env python3
"""Apply a rename map (old → new paths) via plain mv + git add, only for paths that exist."""
import json
import os
import shutil
import subprocess
import sys


def move_and_add(old: str, new: str) -> bool:
    """mv a single path; git add the destination."""
    if not os.path.exists(old):
        return False
    parent = os.path.dirname(new)
    if parent:
        os.makedirs(parent, exist_ok=True)
    shutil.move(old, new)
    # Stage the new path; if anything was already tracked it'll be re-added
    subprocess.run(
        ["git", "add", new],
        capture_output=True,
        text=True,
    )
    return True


def apply_map(maps: dict[str, str], label: str) -> tuple[int, int, int]:
    success = 0
    skipped = 0
    failed = 0
    # Sort by depth descending so deepest paths come first
    items = sorted(maps.items(), key=lambda kv: kv[0].count("/"), reverse=True)
    for old, new in items:
        if not os.path.exists(old):
            skipped += 1
            continue
        if move_and_add(old, new):
            success += 1
        else:
            failed += 1
    print(f"{label}: {success} moved, {skipped} not-found, {failed} failed")
    return success, skipped, failed


if __name__ == "__main__":
    label = sys.argv[1]
    maps_json = sys.argv[2]
    maps = json.loads(maps_json)
    apply_map(maps, label)