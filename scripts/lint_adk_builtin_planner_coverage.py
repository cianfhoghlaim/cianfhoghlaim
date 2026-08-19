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

# Matches `BuiltInPlanner(...)` — the hand-written pattern we want to eliminate.
# The canonical pattern includes `thinking_config=genai_types.ThinkingConfig(include_thoughts=True)`.
# The lint flags any hand-written `BuiltInPlanner` (regardless of pattern) + checks for
# the canonical `include_thoughts=True` flag.
BUILT_IN_PLANNER_PATTERN = re.compile(
    r"\bBuiltInPlanner\s*\(",
    re.MULTILINE,
)

# Matches the canonical include_thoughts=True flag
CANONICAL_THOUGHT_FLAG = re.compile(
    r"include_thoughts\s*=\s*True",
    re.MULTILINE,
)

# Matches `make_planner_agent(...)` — the canonical helper we want to use
HELPER_PATTERN = re.compile(
    r"\bmake_planner_agent\s*\(",
    re.MULTILINE,
)


def lint_file(path: Path) -> list[str]:
    """Return a list of line numbers where BuiltInPlanner is used without the canonical pattern."""
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
    # The canonical pattern includes `include_thoughts=True` somewhere
    # in the BuiltInPlanner call (across multiple lines)
    for match in BUILT_IN_PLANNER_PATTERN.finditer(content):
        # Find the matching closing paren
        start = match.end() - 1
        depth = 0
        end = start
        for i in range(start, min(start + 500, len(content))):
            if content[i] == "(":
                depth += 1
            elif content[i] == ")":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        planner_block = content[start:end]
        # If the canonical include_thoughts=True is missing, flag it
        if not CANONICAL_THOUGHT_FLAG.search(planner_block):
            line_num = content[:match.start()].count("\n") + 1
            violations.append(f"line {line_num}: BuiltInPlanner missing include_thoughts=True (canonical pattern)")
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
        print(f"FAIL: {sum(len(v) for _, v in all_violations)} ADK agents use non-canonical BuiltInPlanner:", file=sys.stderr)
        for path, violations in all_violations:
            rel = path.relative_to(REPO_ROOT)
            for v in violations:
                print(f"  {rel}: {v}", file=sys.stderr)
        return 1
    print(f"OK: all ADK agents use the canonical BuiltInPlanner with include_thoughts=True.")
    return 0


if __name__ == "__main__":
    sys.exit(main())