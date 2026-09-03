#!/usr/bin/env python3
"""DLT nested_hints path lint.

Per the 2026-08-17-hygiene-drift-cleanup-v1 change (P2.6): every
`nested_hints` (or `apply_hints(nested_hints=...)`) call in
dlt_sources/**/*.py MUST NOT contain path fragments with `__`.

The reason: per dlt-hub/dlt#4247 (introduced in dlt 1.28), path
fragments containing `__` are silently normalized away by
`DltResourceHints.get_nested_hints`. The hint targets a nonexistent
table and the user gets no warning. dlt-hub/dlt#4250 was the
proposed fix; this lint catches the regression risk before it ships.

The Cianfhoghlaim codebase was verified via grep to not have any
nested_hints with `__` path fragments (per the
2026-08-17-hygiene-drift-cleanup-v1 ccc audit), so this lint
should pass on first run.

Usage:
    mise run lint:dlt:nested-hints

Exit codes:
    0 = no nested_hints with `__` path fragments
    1 = one or more violations found
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DLT_SOURCES_DIR = REPO_ROOT / "dlt_sources"

# Match nested_hints(...) / apply_hints(nested_hints=...) calls and
# extract the path fragment. We do a multi-line regex to capture
# multi-arg call shapes.
NESTED_HINTS_RE = re.compile(
    r"nested_hints\s*=\s*\{([^}]+)\}",
    re.DOTALL,
)
# Within the captured dict, find path-like keys (e.g. "address__main_block")
# or values. The regression is about path FRAGMENTS, which can
# appear as either dict keys or values (dlt normalizes them).
PATH_FRAGMENT_RE = re.compile(r"""['"]([^'"]*?__[^'"]*?)['"]""")


def scan_dlt_sources() -> list[tuple[Path, str, str]]:
    """Scan dlt_sources/**/*.py for nested_hints calls with __ path fragments.

    Returns list of (file_path, matched_text, matched_fragment).
    """
    results: list[tuple[Path, str, str]] = []
    for py_file in DLT_SOURCES_DIR.glob("**/*.py"):
        if py_file.name == "__init__.py":
            continue
        text = py_file.read_text(encoding="utf-8")
        for nh_match in NESTED_HINTS_RE.finditer(text):
            dict_text = nh_match.group(1)
            for path_match in PATH_FRAGMENT_RE.finditer(dict_text):
                results.append((py_file, nh_match.group(0), path_match.group(1)))
    return results


def main() -> int:
    findings = scan_dlt_sources()
    if not findings:
        print("OK: no nested_hints calls with `__` path fragments found in dlt_sources/")
        return 0

    print(f"FAIL: {len(findings)} nested_hints call(s) contain `__` path fragments:", file=sys.stderr)
    for path, matched_text, fragment in findings:
        rel = path.relative_to(REPO_ROOT)
        print(f"  - {rel}: fragment={fragment!r}", file=sys.stderr)
        print(f"    matched: {matched_text[:200]!r}", file=sys.stderr)
    print(
        "\nFIX: per dlt-hub/dlt#4247 (fixed in #4250), path fragments containing\n"
        "`__` are silently normalized away in dlt 1.28+. Rename the path\n"
        "fragment to use single underscores or a different separator.\n"
        "See openspec/changes/2026-08-17-hygiene-drift-cleanup-v1/specs/cocoindex-v1-migration/spec.md\n"
        "for the regression context.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())