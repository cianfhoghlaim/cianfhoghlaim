#!/usr/bin/env python3
"""BAML catch-coverage lint.

Per the 2026-08-26-mega-3a-baml-and-adk-v1 change (Phase 1: BAML
0.223.0 feature adoption): every `Extract*` function in
`baml_src/**/*.baml` MUST have a `catch_all (...)` block (or `catch (...)
...` for typed error catching). This prevents a single malformed
field from aborting the entire extraction workflow.

The lint uses regex-based AST matching on the BAML function bodies.
BAML has a Python-like syntax with `function <name>(...) { ... }`
blocks; we look for the `catch_all` or `catch` keyword inside each
function body.

Usage:
    mise run lint:baml-catch-coverage

Exit codes:
    0 = all Extract* functions have catch_all
    1 = one or more Extract* functions missing catch
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BAML_SRC = REPO_ROOT / "baml_src"

# Matches `function Extract*...(... ) { ... }` blocks (single-line or
# multi-line, including nested braces in prompts)
FUNCTION_PATTERN = re.compile(
    r"^function\s+(Extract\w+)\s*\([^)]*\)\s*(?:->\s*[^{]*)?\s*\{",
    re.MULTILINE,
)

# Matches `catch (...) { ... }` or `catch_all (...) { ... }`
CATCH_PATTERN = re.compile(
    r"\bcatch(?:_all)?\s*\(",
    re.MULTILINE,
)


def find_function_end(content: str, start: int) -> int:
    """Find the matching closing brace for the function starting at `start`.

    BAML uses Python-style braces; we count them.
    """
    depth = 0
    i = start
    while i < len(content):
        c = content[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return len(content)


def lint_file(path: Path) -> list[str]:
    """Return a list of function names in `path` missing catch blocks."""
    violations = []
    try:
        content = path.read_text()
    except Exception:
        return violations
    # Skip test fixtures
    if path.name.startswith("_test") or path.name.endswith("_test.baml"):
        return violations
    for match in FUNCTION_PATTERN.finditer(content):
        func_name = match.group(1)
        func_start = match.end() - 1  # position of the opening `{`
        func_end = find_function_end(content, func_start)
        func_body = content[func_start:func_end]
        if not CATCH_PATTERN.search(func_body):
            violations.append(func_name)
    return violations


def main() -> int:
    all_violations: list[tuple[Path, list[str]]] = []
    baml_files = list(BAML_SRC.rglob("*.baml"))
    for path in baml_files:
        violations = lint_file(path)
        if violations:
            all_violations.append((path, violations))
    if all_violations:
        print(f"FAIL: {sum(len(v) for _, v in all_violations)} Extract* functions missing catch:", file=sys.stderr)
        for path, violations in all_violations:
            rel = path.relative_to(REPO_ROOT)
            for v in violations:
                print(f"  {rel}: {v}", file=sys.stderr)
        return 1
    print(f"OK: all Extract* functions in {len(baml_files)} BAML files have catch blocks.")
    return 0


if __name__ == "__main__":
    sys.exit(main())