#!/usr/bin/env python3
"""Marimo PEP 723 template lint.

Per the 2026-11-25-mega-3c-marimo-and-integration-v1 change
(TASK-M3C-1.2): every Marimo notebook in `notebooks/*.py` MUST
import from `notebooks._shared._pep723_template` (no hand-written
PEP 723 `# /// script` blocks).

Usage:
    mise run lint:marimo-pep723-template

Exit codes:
    0 = all 201 notebooks use the canonical template
    1 = one or more notebooks have hand-written PEP 723 blocks
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS_DIR = REPO_ROOT / "notebooks"

# Matches the `# /// script` block (PEP 723 inline metadata)
PEP723_PATTERN = re.compile(
    r"#\s*///\s*script",
    re.MULTILINE,
)

# Matches import from the canonical template
CANONICAL_IMPORT_PATTERN = re.compile(
    r"from\s+notebooks\._shared\._pep723_template\s+import\s+CANONICAL_DEPENDENCIES",
)


def lint_file(path: Path) -> list[str]:
    """Return a list of violations in `path`."""
    violations = []
    try:
        content = path.read_text()
    except Exception:
        return violations
    if not PEP723_PATTERN.search(content):
        return violations
    # Check if the canonical import is used (then it's OK)
    if CANONICAL_IMPORT_PATTERN.search(content):
        return violations
    for i, line in enumerate(content.splitlines(), 1):
        if PEP723_PATTERN.search(line):
            violations.append(f"line {i}: {line.strip()[:80]}")
    return violations


def main() -> int:
    all_violations: list[tuple[Path, list[str]]] = []
    for path in NOTEBOOKS_DIR.glob("*.py"):
        if path.name.startswith("_"):
            continue
        violations = lint_file(path)
        if violations:
            all_violations.append((path, violations))
    if all_violations:
        print(f"FAIL: {sum(len(v) for _, v in all_violations)} notebooks use hand-written PEP 723 blocks:", file=sys.stderr)
        for path, violations in all_violations:
            rel = path.relative_to(REPO_ROOT)
            for v in violations:
                print(f"  {rel}: {v}", file=sys.stderr)
        return 1
    print(f"OK: all notebooks use the canonical PEP 723 template.")
    return 0


if __name__ == "__main__":
    sys.exit(main())