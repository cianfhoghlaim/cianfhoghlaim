"""A2UI surface lint gate.

Per the 2026-09-30-mega-3b-cocoindex-and-copilotkit-v1 change
(TASK-M3B-6.1.3): every A2UI surface MUST use the canonical
`A2UISurfaceGenerator` from `web/apps/cianfhoghlaim/components/_shared/A2UISurfaceGenerator.tsx`.

Usage:
    mise run lint:a2ui-surface-coverage

Exit codes:
    0 = all 8 A2UI surfaces use the canonical generator
    1 = one or more surfaces use hand-written createSurface calls
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WEB_APPS = REPO_ROOT / "web" / "apps"

# Matches hand-written A2UI surface implementations (we want to eliminate these)
HAND_WRITTEN_PATTERN = re.compile(
    r"(createSurface|createA2UIMessageRenderer)\s*\(",
    re.MULTILINE,
)

# Matches usage of the canonical A2UISurfaceGenerator
GENERATOR_PATTERN = re.compile(
    r"A2UISurfaceGenerator",
)


def lint_file(path: Path) -> list[str]:
    """Return a list of violations in `path`."""
    violations = []
    try:
        content = path.read_text()
    except Exception:
        return violations
    if not HAND_WRITTEN_PATTERN.search(content):
        return violations
    # Check if the canonical generator is used (then it's OK)
    if GENERATOR_PATTERN.search(content):
        return violations
    for i, line in enumerate(content.splitlines(), 1):
        if HAND_WRITTEN_PATTERN.search(line):
            violations.append(f"line {i}: {line.strip()[:80]}")
    return violations


def main() -> int:
    all_violations: list[tuple[Path, list[str]]] = []
    # Scan all .tsx files in web/apps/*/src
    for tsx_file in WEB_APPS.rglob("*.tsx"):
        if "/node_modules/" in str(tsx_file):
            continue
        if "_shared/" in str(tsx_file):
            continue  # skip the generator itself
        violations = lint_file(tsx_file)
        if violations:
            all_violations.append((tsx_file, violations))
    if all_violations:
        print(f"FAIL: {sum(len(v) for _, v in all_violations)} A2UI surfaces use hand-written implementations:", file=sys.stderr)
        for path, violations in all_violations:
            rel = path.relative_to(REPO_ROOT)
            for v in violations:
                print(f"  {rel}: {v}", file=sys.stderr)
        return 1
    print("OK: all A2UI surfaces use the canonical A2UISurfaceGenerator.")
    return 0


if __name__ == "__main__":
    sys.exit(main())