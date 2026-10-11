#!/usr/bin/env python3
"""scripts/lint_baml_frontmatter.py — BAML frontmatter + class-field alignment lint.

Per the 2026-10-30-biep-tertiary-baml-repair-v1 umbrella of
openspec/plans/2026-10-30-platform-reset-saga-v1.md. The lint enforces:

  1. NO `__all__ = [...]` at the top level (Python-specific, not BAML).
  2. NO `client "openai/..."` or `client "<model>"` string-literal clients
     in function bodies (use the named `Primary` client from clients.baml).
  3. NO multi-space alignment in class field declarations
     (the `name   type   @description(...)` style that baml-cli 0.226.1
     rejects with "This line is invalid").
  4. NO inline string-literal unions in class field declarations
     (e.g. `element "earth" | "air" | ...` — use a named enum).

The lint prints a summary + exit code 1 on any failure. Integrated as
`mise run core:lint:baml` (added 2026-10-30). Wired into the
`core:lint` aggregate task.

Usage:
  python scripts/lint_baml_frontmatter.py                    # all files
  python scripts/lint_baml_frontmatter.py --strict           # warnings as errors
  python scripts/lint_baml_frontmatter.py --limit 10         # first 10 files
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path("/Users/cianmacandeisigh/dev/cianfhoghlaim")
BAML_SRC = ROOT / "baml_src"

# Rule 1: top-level __all__ is a Python idiom, not BAML.
RE_TOP_LEVEL_ALL = re.compile(r"^__all__\s*=\s*\[[^\]]*\]", re.MULTILINE)

# Rule 2: string-literal client (not the named `Primary` / `BIEPV3Extract` / etc.).
RE_STRING_LITERAL_CLIENT = re.compile(
    r'^\s*client\s+"(?:openai|anthropic|minimax|gemini|gpt-4|gpt-3\.5|claude|minimax-m3)[^"]*"',
    re.MULTILINE,
)

# Rule 3: multi-space between a class field type and its @description attribute
# (only matters for class bodies, not function parameter lists).
RE_CLASS_FIELD_MULTI_SPACE = re.compile(
    r"^\s+[A-Za-z_][A-Za-z0-9_]*\s+\S*\s{2,}\s*@description",
    re.MULTILINE,
)

# Rule 4: inline string-literal union as a class field type
# (the `name "a" | "b" | "c"` pattern; use a named enum instead).
RE_INLINE_STRING_UNION = re.compile(
    r'^\s+[A-Za-z_][A-Za-z0-9_]*\s+"[^"]+"\s*\|',
    re.MULTILINE,
)


def lint_file(path: Path) -> list[str]:
    """Return a list of human-readable violations for the file (empty = pass)."""
    try:
        text = path.read_text()
    except (OSError, UnicodeDecodeError) as exc:
        return [f"  {path}: cannot read ({exc})"]

    violations: list[str] = []

    for m in RE_TOP_LEVEL_ALL.finditer(text):
        line_no = text[: m.start()].count("\n") + 1
        violations.append(
            f"  {path}:{line_no}: top-level `__all__` is not BAML (use a class or enum instead)"
        )

    for m in RE_STRING_LITERAL_CLIENT.finditer(text):
        line_no = text[: m.start()].count("\n") + 1
        snippet = m.group(0).strip()
        violations.append(
            f"  {path}:{line_no}: string-literal client `{snippet[:80]}...` is not BAML (use the named `Primary` client from clients.baml)"
        )

    for m in RE_CLASS_FIELD_MULTI_SPACE.finditer(text):
        line_no = text[: m.start()].count("\n") + 1
        violations.append(
            f"  {path}:{line_no}: multi-space alignment in class field (use single space between type and @description)"
        )

    for m in RE_INLINE_STRING_UNION.finditer(text):
        line_no = text[: m.start()].count("\n") + 1
        violations.append(
            f"  {path}:{line_no}: inline string-literal union as class field type (use a named enum instead)"
        )

    return violations


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--strict", action="store_true", help="warnings as errors")
    parser.add_argument(
        "--limit", type=int, default=0, help="limit to first N files (0 = all)"
    )
    parser.add_argument(
        "--root", type=Path, default=BAML_SRC, help="BAML root directory"
    )
    args = parser.parse_args(argv)

    files = sorted(args.root.rglob("*.baml"))
    if args.limit > 0:
        files = files[: args.limit]

    all_violations: list[str] = []
    files_with_violations = 0
    for f in files:
        v = lint_file(f)
        if v:
            files_with_violations += 1
            all_violations.extend(v)

    print(f"=== BAML frontmatter lint: checked {len(files)} files, {files_with_violations} with violations ===")
    for line in all_violations:
        print(line)
    if all_violations:
        print(f"\nFAILED: {len(all_violations)} violation(s) in {files_with_violations} file(s)")
        return 1
    print("\nOK: 0 violations")
    return 0


if __name__ == "__main__":
    sys.exit(main())
