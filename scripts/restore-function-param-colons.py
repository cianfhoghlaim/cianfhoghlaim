#!/usr/bin/env python3
"""
restore-function-param-colons.py — Re-add colons after function parameter
names that were over-zealously rewritten by migrate-baml-syntax.py.

In BAML v0.212+, function parameters REQUIRE `param: type` (colon syntax),
but class fields use `field type` (whitespace syntax). The migration script
mistakenly converted function parameters to the class-field syntax.

This script walks all .baml files under cianfhoghlaim/baml/, detects
function parameter contexts (indented lines between `function Name(` and
the closing `)` on its own line), and re-adds the colons.

Usage:
    uv run python scripts/restore-function-param-colons.py --dry-run
    uv run python scripts/restore-function-param-colons.py --apply
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from dataclasses import dataclass, field

REPO_ROOT = Path(__file__).resolve().parent.parent
BAML_ROOT = REPO_ROOT / "cianfhoghlaim" / "baml"

# Regex for matching a single function parameter line.
# Captures: leading whitespace, param name, type (possibly followed by comma)
_PARAM_LINE_RE = re.compile(
    r"^(?P<indent>\s+)"           # leading indent
    r"(?P<param>[a-z_][a-zA-Z0-9_]*)"   # parameter name
    r"\s+"                        # space (was originally colon+space)
    r"(?P<type>"                  # type
    r"string(?:\[\])?(?:\?)?"
    r"|int(?:\[\])?(?:\?)?"
    r"|float(?:\[\])?(?:\?)?"
    r"|bool(?:\[\])?(?:\?)?"
    r"|image(?:\[\])?(?:\?)?"
    r"|[A-Z][a-zA-Z0-9_]*(?:\[\])?(?:\?)?"
    r"|list<[^>]+>(?:\?)?"
    r"|map<[^,]+,\s*[^>]+>(?:\?)?"
    r"|class\s+[a-zA-Z0-9_]+"
    r"|enum\s+[a-zA-Z0-9_]+"
    r"|optional\s+[a-zA-Z<>,\s\[\]]+"
    r")"
    r"(?P<comma>,?)"
    r"(?P<rest>.*)$"
)

# Matches a function declaration opener.
_FUNCTION_OPENER_RE = re.compile(r"^\s*function\s+\w+\(")
# Matches the function arg list closer (paren on its own line, indented).
_FUNCTION_CLOSER_RE = re.compile(r"^\s*\)\s*->")


@dataclass
class FileResult:
    path: Path
    changes: list[tuple[int, str, str]] = field(default_factory=list)

    @property
    def num_changed(self) -> int:
        return len(self.changes)


def process_file(path: Path, apply: bool) -> FileResult:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    result = FileResult(path=path)

    in_function_args = False
    paren_depth = 0

    for idx, raw_line in enumerate(lines, start=1):
        line = raw_line.rstrip("\n")

        if not in_function_args:
            # Look for a function opener. The function opener may have its
            # closing paren on the same line OR on a later line.
            if _FUNCTION_OPENER_RE.match(line):
                # Count parens on this line. If balanced (open and close on
                # same line), no multi-line arg list. Otherwise, enter
                # function-arg mode.
                opens = line.count("(")
                closes = line.count(")")
                paren_depth = opens - closes
                if paren_depth > 0:
                    in_function_args = True
                continue
        else:
            # In function arg list. Count parens to know when we exit.
            opens = line.count("(")
            closes = line.count(")")
            paren_depth += opens - closes

            # Try to match a parameter line and rewrite it.
            m = _PARAM_LINE_RE.match(line)
            if m and not line.lstrip().startswith("//"):
                # Re-add the colon after the parameter name.
                indent = m.group("indent")
                param = m.group("param")
                type_ = m.group("type")
                comma = m.group("comma")
                rest = m.group("rest")
                # Preserve original indentation
                new_line = f"{indent}{param}: {type_}{comma}{rest}"
                if new_line != line:
                    if raw_line.endswith("\r\n"):
                        new_line_with_eol = new_line + "\r\n"
                    else:
                        new_line_with_eol = new_line + "\n"
                    result.changes.append((idx, line, new_line))
                    lines[idx - 1] = new_line_with_eol

            # Exit when paren depth returns to 0.
            if paren_depth <= 0:
                in_function_args = False
                paren_depth = 0

    if apply and result.num_changed > 0:
        path.write_text("".join(lines), encoding="utf-8")

    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Restore colons in function parameter definitions"
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    if not args.dry_run and not args.apply:
        args.dry_run = True

    targets = sorted(BAML_ROOT.rglob("*.baml"))
    grand_changes = 0
    for path in targets:
        result = process_file(path, apply=args.apply)
        if result.num_changed == 0:
            continue
        rel = path.relative_to(REPO_ROOT)
        print(f"[{'APPLIED' if args.apply else 'CHG'}] {rel} — {result.num_changed} lines")
        for idx, before, after in result.changes[:5]:
            print(f"  L{idx}: {before.strip()!r}  →  {after.strip()!r}")
        if result.num_changed > 5:
            print(f"  ... +{result.num_changed - 5} more")
        grand_changes += result.num_changed

    print(f"\n[SUMMARY] {grand_changes} parameter lines {'rewritten' if args.apply else 'pending'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())