#!/usr/bin/env python3
"""Apply a rename map (old → new paths) via git mv, only for paths that exist."""
import json
import os
import subprocess
import sys


def git_mv(old: str, new: str) -> bool:
    """git mv a single path; returns True if it succeeded."""
    if not os.path.exists(old):
        return False
    # Make the parent dir of the new path
    parent = os.path.dirname(new)
    if parent:
        os.makedirs(parent, exist_ok=True)
    result = subprocess.run(
        ["git", "mv", old, new],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"  FAIL: {old} -> {new}: {result.stderr.strip()}")
        return False
    return True


def apply_map(maps: dict[str, str], label: str) -> tuple[int, int, int]:
    success = 0
    skipped = 0
    failed = 0
    # Two-pass: do leaf moves first (so parent moves don't conflict)
    # Sort by depth descending so deepest paths come first
    items = sorted(maps.items(), key=lambda kv: kv[0].count("/"), reverse=True)
    for old, new in items:
        if not os.path.exists(old):
            skipped += 1
            continue
        if git_mv(old, new):
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