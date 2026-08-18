#!/usr/bin/env python3
"""BAML stub-prompt lint.

Per the 2026-08-17-biep-v3-bring-up-v1 change (P2.16): every BAML
function in baml_src/**/*.baml MUST NOT have the literal body
`"Auto-generated extraction prompt."`. This was the 832-of-838 stub
class per the `centralized-schema-registry` spec.

The lint scans `baml_src/**/*.baml` for the literal substring
`Auto-generated extraction prompt` in any prompt body. Test-only
fixtures matching `_test*.baml` are exempt.

Usage:
    mise run lint:baml-stub-prompts

Exit codes:
    0 = no stub prompts remain
    1 = one or more stub prompts found
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BAML_SRC = REPO_ROOT / "baml_src"

STUB_PROMPT_LITERAL = "Auto-generated extraction prompt"

# Match the prompt body. BAML prompt blocks use `prompt #"..."` or
# `prompt #"""..."""`. We scan for the literal substring.
prompt_block_re = re.compile(
    r'prompt\s*#(?:"""|"|\'\')(.+?)(?:"""|"|\'\')',
    re.DOTALL,
)


def scan_baml_files() -> list[tuple[Path, int, str]]:
    """Scan baml_src/**/*.baml for stub prompts. Returns list of (file, line, snippet)."""
    findings: list[tuple[Path, int, str]] = []
    if not BAML_SRC.exists():
        return findings

    for py_file in sorted(BAML_SRC.glob("**/*.baml")):
        # Test fixtures are exempt
        if py_file.name.startswith("_test"):
            continue
        text = py_file.read_text(encoding="utf-8")
        for line_no, line in enumerate(text.splitlines(), start=1):
            if STUB_PROMPT_LITERAL in line:
                # Use the line content as the snippet (truncated)
                snippet = line.strip()[:100]
                findings.append((py_file, line_no, snippet))

    return findings


def main() -> int:
    findings = scan_baml_files()
    if not findings:
        print("OK: no BAML stub prompts found in baml_src/")
        return 0

    print(f"FAIL: {len(findings)} BAML stub prompt(s) found:", file=sys.stderr)
    for path, lineno, snippet in findings:
        rel = path.relative_to(REPO_ROOT)
        print(f"  - {rel}:{lineno}: {snippet!r}", file=sys.stderr)
    print(
        "\nFIX: replace the literal `\"Auto-generated extraction prompt.\"` "
        "string with a real prompt body (per the "
        "`centralized-schema-registry` spec and the "
        "`2026-08-10-baml-extraction-completion-v1` change).",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())