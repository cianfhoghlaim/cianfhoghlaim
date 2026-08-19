#!/usr/bin/env python3
"""CocoIndex → BAML coverage lint.

Per the 2026-08-18-mega-3-fast-follow-v1 change (FF.6) + the
2026-08-26-mega-3a-baml-and-adk-v1 change: every BIEP CocoIndex App in
`cocoindex_flows/biep_parity/*.py` MUST import at least 1 BAML function
via `from baml_client.async_client import b` (or the typed
`from baml_client.types import ...`).

The reason: BAML is the single source of truth for the BIEP
extraction. CocoIndex Apps that don't call BAML duplicate the LLM
call logic.

Usage:
    mise run lint:cocoindex-baml-coverage

Exit codes:
    0 = all 47 BIEP CocoIndex Apps import BAML
    1 = one or more Apps missing BAML
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BIE_PARITY = REPO_ROOT / "cocoindex_flows" / "biep_parity"

# Matches `from baml_client... import b` or `from baml_client.types import ...`
BAML_IMPORT_PATTERN = re.compile(
    r"^\s*from\s+baml_client(?:\.\w+)*\s+import\s+",
    re.MULTILINE,
)


def lint_file(path: Path) -> bool:
    """Return True if the file imports at least 1 BAML symbol."""
    try:
        content = path.read_text()
    except Exception:
        return False
    return bool(BAML_IMPORT_PATTERN.search(content))


def main() -> int:
    violations: list[Path] = []
    for path in BIE_PARITY.rglob("*.py"):
        # Skip __init__.py
        if path.name == "__init__.py":
            continue
        # Skip pure factory config (LC_SUBJECT_CONFIG etc.)
        if path.name.endswith("_config.py"):
            continue
        if not lint_file(path):
            violations.append(path)
    if violations:
        print(f"FAIL: {len(violations)} CocoIndex files missing BAML import:", file=sys.stderr)
        for path in violations:
            rel = path.relative_to(REPO_ROOT)
            print(f"  {rel}", file=sys.stderr)
        return 1
    print(f"OK: all CocoIndex files in {BIE_PARITY.relative_to(REPO_ROOT)} import BAML.")
    return 0


if __name__ == "__main__":
    sys.exit(main())