#!/usr/bin/env python3
"""baml_audit_fallbacks.py — CI gate for the per-function fallback chain pattern.

Per the 2026-08-31-baml-primary-alias-and-fallback-v1 change. Fails if any
BAML function in `baml_src/**` (excluding the documented exception list)
is missing a `fallback` block.

Usage:
    uv run python scripts/baml_audit_fallbacks.py --strict

Exit codes:
    0 — 0 drift (all non-exception functions have a fallback chain)
    1 — at least one function missing a fallback chain
    2 — usage error
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BAML_ROOT = REPO_ROOT / "baml_src"

# Functions exempt from the fallback-chain requirement (the canonical exception list).
EXCEPTION_FUNCTIONS: set[str] = {
    # Test-only deterministic client (no network).
    "TestMock",
    # GaeilgeLC helper (the Modern Irish-language path uses the per-function
    # `client "GaeilgeLCClient"` override instead).
    "GaeilgeLCClient",
    # The 5 tuatha_media_intel helpers (separate openspec change covers them).
    "ExtractMediaIntelFrame",
    "ExtractMediaIntelAsset",
    "ExtractMediaIntelNPC",
    "ExtractMediaIntelStory",
    "ExtractMediaIntelParticle",
}

# Pattern: extract all `function NAME(...) -> ... { ... }` blocks
FUNCTION_PATTERN = re.compile(
    r"function\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*\([^)]*\)[^{]*\{",
    re.MULTILINE,
)
FALLBACK_PATTERN = re.compile(r"\bfallback\b\s+[\"']", re.MULTILINE)


def find_functions(path: Path) -> list[tuple[str, str, int]]:
    """Yield (file_path, function_name, line_number) tuples."""
    try:
        content = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []
    matches: list[tuple[str, str, int]] = []
    for m in FUNCTION_PATTERN.finditer(content):
        name = m.group("name")
        if name in EXCEPTION_FUNCTIONS:
            continue
        # Compute 1-indexed line number
        line_no = content[: m.start()].count("\n") + 1
        matches.append((str(path.relative_to(REPO_ROOT)), name, line_no))
    return matches


def find_missing_fallbacks() -> list[tuple[str, str, int]]:
    """Return the list of (file, function, line) tuples that lack a fallback."""
    missing: list[tuple[str, str, int]] = []
    for baml_file in sorted(BAML_ROOT.rglob("*.baml")):
        for file, name, line_no in find_functions(baml_file):
            try:
                content = baml_file.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            # Read from function start to the next top-level `function` or `client` or EOF.
            start = content.find(f"function {name}")
            if start < 0:
                continue
            # Find the end of the function body — next function/class/client at column 0
            tail = content[start:]
            end_match = re.search(r"\n(?:function|client<|class)\s", tail[len(f"function {name}"):])
            body = tail[: end_match.start() + len(f"function {name}")] if end_match else tail
            if not FALLBACK_PATTERN.search(body):
                missing.append((file, name, line_no))
    return missing


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit BAML functions for missing fallback chains (per the v5 BAML switching strategy)"
    )
    parser.add_argument("--strict", action="store_true", help="Exit 1 on drift")
    args = parser.parse_args()

    missing = find_missing_fallbacks()
    if not missing:
        print(f"Found 0 missing fallback chains in {sum(1 for _ in BAML_ROOT.rglob('*.baml'))} BAML files")
        return 0

    print(f"Found {len(missing)} BAML functions missing fallback chains:")
    for file, name, line in missing:
        print(f"  {file}:{line}: '{name}' missing fallback chain")
    if args.strict:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())