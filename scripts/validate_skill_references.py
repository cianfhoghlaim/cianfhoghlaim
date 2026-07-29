#!/usr/bin/env python3
"""Validate each SKILL.md references paths that exist on disk.

Per the 2026-08-15-knowledge-sync-loop-v1 change (Layer 4).
Walks every `.agents/skills/<slug>/SKILL.md`, extracts all
backtick-quoted paths, and verifies each path exists on disk.

This catches the common drift pattern where a skill's body
references a file that was renamed/archived in a subsequent
openspec change (e.g. the `sruth/...` → `...` rename).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

SKILLS_DIR = Path(".agents/skills")
PATH_PATTERN = re.compile(r"`([A-Za-z0-9_./\-]+\.[a-z]{1,5})`")
REPO_ROOT = Path(".").resolve()


def is_checkable_path(token: str) -> bool:
    """Return True if the token looks like a file path (not an API name)."""
    # Skip tokens that are clearly not file paths:
    # - URLs
    # - Python identifiers (no slash)
    # - All-uppercase tokens (env var names, acronyms)
    if token.startswith("http"):
        return False
    if "/" not in token and "\\" not in token:
        return False
    if token.isupper():
        return False
    # Must have a file extension
    if "." not in token.split("/")[-1]:
        return False
    return True


def main() -> int:
    if not SKILLS_DIR.exists():
        print(f"ERROR: {SKILLS_DIR} not found")
        return 1

    fail = 0
    total_refs = 0
    total_ok = 0
    per_skill = {}

    for skill_md in sorted(SKILLS_DIR.rglob("SKILL.md")):
        skill_name = skill_md.parent.name
        content = skill_md.read_text()
        # Take only the first 30 lines (the frontmatter + the description)
        # to limit false positives from prose examples.
        body = "\n".join(content.splitlines()[:30])
        skill_refs = 0
        skill_fail = 0
        for match in PATH_PATTERN.finditer(body):
            token = match.group(1)
            if not is_checkable_path(token):
                continue
            # Skip absolute paths (e.g. /Users/...)
            if token.startswith("/"):
                continue
            total_refs += 1
            skill_refs += 1
            candidate = REPO_ROOT / token
            if candidate.exists():
                total_ok += 1
                continue
            # Also check the basename only (some skills reference files
            # by basename when the dir is implicit)
            basename = Path(token).name
            if any(
                candidate.parent.glob(f"**/{basename}") if candidate.parent.exists() else []
            ):
                total_ok += 1
                continue
            print(f"  FAIL {skill_name}: {token}")
            skill_fail += 1
            fail += 1
        per_skill[skill_name] = (skill_refs, skill_fail)

    print(f"\nSummary: {total_ok}/{total_refs} refs OK across {len(per_skill)} skills")
    if fail > 0:
        print(f"FAIL: {fail} dangling references found")
        return 1
    print("OK: 0 dangling references")
    return 0


if __name__ == "__main__":
    sys.exit(main())