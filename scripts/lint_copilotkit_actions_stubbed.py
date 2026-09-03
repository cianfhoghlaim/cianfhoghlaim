#!/usr/bin/env python3
"""CopilotKit actions-stubbed lint.

Per the 2026-08-17-biep-v3-bring-up-v1 change (P2.17): every
CopilotKit action in `web/apps/cianfhoghlaim-leaving-cert/apps/api/src/copilotkit/actions.ts`
MUST NOT return the literal string `"TBD"` placeholder. This was the
12-of-14 stub class per the `agentic-frontend-frameworks` spec.

The lint scans actions.ts for the literal substring `"TBD"` in any
return-statement that includes a placeholder-looking string literal
(test fixtures ending in `.test.ts` are exempt).

Usage:
    mise run lint:copilotkit-actions-stubbed

Exit codes:
    0 = no stub actions found
    1 = one or more stub actions found
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ACTIONS_TS = (
    REPO_ROOT
    / "web"
    / "apps"
    / "cianfhoghlaim-leaving-cert"
    / "apps"
    / "api"
    / "src"
    / "copilotkit"
    / "actions.ts"
)

# Match return statements that contain `"TBD"` (the literal stub marker).
# Exclude comments + console.log lines.
RETURN_TBD_RE = re.compile(
    r'return\s*\{[^}]*[\'"]TBD[\'"][^}]*\}',
    re.MULTILINE,
)


def main() -> int:
    if not ACTIONS_TS.exists():
        print(f"FAIL: {ACTIONS_TS} does not exist", file=sys.stderr)
        return 1

    text = ACTIONS_TS.read_text(encoding="utf-8")

    findings: list[tuple[int, str]] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        if "TBD" in line and "return" in line:
            # Strip comments and console.log noise
            stripped = line.split("//")[0].strip()
            if "return" in stripped and "TBD" in stripped:
                findings.append((lineno, stripped[:120]))

    if not findings:
        print("OK: no CopilotKit stub actions found.")
        return 0

    print(f"FAIL: {len(findings)} CopilotKit stub action(s) found:", file=sys.stderr)
    for lineno, content in findings:
        print(f"  - line {lineno}: {content}", file=sys.stderr)
    print(
        "\nFIX: wire to real handlers per the "
        "`agentic-frontend-frameworks` spec. The 5 real handlers are at "
        "`web/apps/cianfhoghlaim-leaving-cert/apps/api/src/copilotkit/handlers/`\n"
        "(syllabus, marking, ocr, learning_outcome, student_progress).",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())