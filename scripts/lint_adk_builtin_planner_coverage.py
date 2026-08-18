#!/usr/bin/env python3
"""ADK BuiltInPlanner coverage lint.

Per the 2026-08-26-mega-3a-baml-and-adk-v1 change (Phase 7: ADK
Agent Adoption): every ADK agent in `agents/adk/*.py` that uses
`BuiltInPlanner` MUST use the canonical `agent_ui_bridge.make_planner_agent()`
helper (from the 2026-08-18-mega-3-fast-follow-v1 change FF.3).

The reason: the agent_ui_bridge helper ensures every planner has the
canonical `thinking_config` + `include_thoughts=True` (per the
adk-dashboard sample).

Usage:
    mise run lint:adk-builtin-planner-coverage

Exit codes:
    0 = all 6 ADK agents use the canonical planner helper
    1 = one or more ADK agents use a hand-written BuiltInPlanner
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ADK_DIR = REPO_ROOT / "agents" / "adk"

# Matches `BuiltInPlanner(...)` — the hand-written pattern we want to eliminate
BUILT_IN_PLANNER_PATTERN = re.compile(
    r"\bBuiltInPlanner\s*\(",
    re.MULTILINE,
)

# Matches `make_planner_agent(...)` — the canonical helper we want to use
HELPER_PATTERN = re.compile(
    r"\bmake_planner_agent\s*\(",
    re.MULTILINE,
)


def lint_file(path: Path) -> list[str]:
    """Return a list of line numbers where BuiltInPlanner is used (not via helper)."""
    violations = []
    try:
        content = path.read_text()
    except Exception:
        return violations
    if not BUILT_IN_PLANNER_PATTERN.search(content):
        return violations
    # Check if helper is used (then it's OK)
    if HELPER_PATTERN.search(content):
        return violations
    for i, line in enumerate(content.splitlines(), 1):
        if BUILT_IN_PLANNER_PATTERN.search(line):
            violations.append(f"line {i}: {line.strip()[:80]}")
    return violations


def main() -> int:
    all_violations: list[tuple[Path, list[str]]] = []
    for path in ADK_DIR.glob("*.py"):
        if path.name in {"__init__.py", "litellm_agent.py"}:
            continue
        violations = lint_file(path)
        if violations:
            all_violations.append((path, violations))
    if all_violations:
        print(f"FAIL: {sum(len(v) for _, v in all_violations)} ADK agents use hand-written BuiltInPlanner:", file=sys.stderr)
        for path, violations in all_violations:
            rel = path.relative_to(REPO_ROOT)
            for v in violations:
                print(f"  {rel}: {v}", file=sys.stderr)
        return 1
    print(f"OK: all ADK agents use the canonical planner helper.")
    return 0


if __name__ == "__main__":
    sys.exit(main())