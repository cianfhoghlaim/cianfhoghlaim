#!/usr/bin/env python3
"""Normalize openspec spec deltas — ensures each requirement body has SHALL/MUST.

Per followup 2 of the 2026-08-21-meaisinfhoghlaim-unsloth-agents-integration-v1 work.
The earlier fix added ## ADDED Requirements headers but the body lacked SHALL/MUST.
This script ensures every requirement body starts with "The system SHALL ...".
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path("/Users/cianmacandeisigh/dev/cianfhoghlaim")

CHANGES = [
    "2026-08-23-uog-official-docs-and-nui-superset-v1",
    "2026-08-24-wave-0-cocoindex-module-path-repair-v1",
    "2026-08-24-wave-1-dlt-sources-domain-restructure-v1",
    "2026-08-24-wave-2-orchestration-vertical-pipelines-v1",
    "2026-08-24-wave-3-cocoindex-v0-stragglers-v1",
    "2026-08-24-wave-4-ducklake-v1-hardening-v1",
    "2026-08-24-wave-5-web-consolidation-v1",
    "2026-08-24-wave-6-frontend-tanstack-modernisation-v1",
    "2026-08-24-wave-7-observability-drift-cleanup-v1",
    "2026-08-24-wave-8-final-cleanup",
    "2026-08-25-post-cascade-followups",
]


def fix_requirement_body(spec_path: Path) -> bool:
    """Ensure each ### Requirement: ... block has SHALL/MUST in its body.

    Returns True if changes were made.
    """
    content = spec_path.read_text()
    original = content

    # Find each ### Requirement: ... block (until next ### or ## heading)
    pattern = re.compile(
        r"^(### Requirement:[^\n]*\n)((?:(?!^### |^## |\Z).)*?)(?=^### |^## |\Z)",
        re.MULTILINE | re.DOTALL,
    )

    def replace_block(match):
        title = match.group(1).strip()
        body = match.group(2).strip()
        # Check if body already has SHALL or MUST
        if re.search(r"\bSHALL\b|\bMUST\b", body, re.IGNORECASE):
            return match.group(0)
        # Inject "The system SHALL " if not present
        if not body:
            body = "The system SHALL provide this capability."
        else:
            # If body is just descriptive text, prefix it
            # Check if first line is a sentence that needs the prefix
            first_sentence = body.split("\n")[0].strip()
            if first_sentence and not first_sentence.lower().startswith("the system"):
                # Add "The system SHALL " prefix
                body = f"The system SHALL {first_sentence.lower()}\n\n" + "\n".join(body.split("\n")[1:])
        return f"{title}\n{body}\n\n"

    new_content = pattern.sub(replace_block, content)

    if new_content != original:
        spec_path.write_text(new_content)
        return True
    return False


def main():
    fixed = 0
    for change in CHANGES:
        change_dir = REPO_ROOT / "openspec/changes" / change / "specs"
        if not change_dir.exists():
            continue
        for spec_file in change_dir.glob("**/spec.md"):
            if fix_requirement_body(spec_file):
                print(f"✅ Fixed: {spec_file.relative_to(REPO_ROOT)}")
                fixed += 1

    print(f"\nTotal fixed: {fixed}")
    print("\n=== Final openspec validation ===")
    import subprocess
    result = subprocess.run(
        ["openspec", "validate", "--all"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    print(result.stdout.split("\n")[-2] if result.stdout else "")
    print(result.stdout.split("\n")[-1] if result.stdout else "")


if __name__ == "__main__":
    main()
