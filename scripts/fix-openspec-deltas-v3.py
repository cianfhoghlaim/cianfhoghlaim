#!/usr/bin/env python3
"""Fix requirement body structure — puts SHALL/MUST on the first line.

Per followup 2 of the 2026-08-21-meaisinfhoghlaim-unsloth-agents-integration-v1 work.
The openspec parser only looks at the first line of the requirement body for
SHALL/MUST keywords. This script restructures requirements so the first line
contains SHALL/MUST, then the descriptive text follows.
"""
import re
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


def restructure_requirement_body(spec_path: Path) -> bool:
    """Restructure each ### Requirement: body so the first line has SHALL/MUST.

    Pattern transformation:
      Before:
        ### Requirement: <title>

        <descriptive text>.
        SHALL <statement>...

      After:
        ### Requirement: <title>

        The system SHALL <descriptive text stripped of trailing period>.
        <statement>...
    """
    content = spec_path.read_text()
    original = content

    # Find each ### Requirement: block
    pattern = re.compile(
        r"^(### Requirement:[^\n]*\n)((?:(?!^### |^## |\Z).)*?)(?=^### |^## |\Z)",
        re.MULTILINE | re.DOTALL,
    )

    def replace_block(match):
        title = match.group(1).strip()
        body = match.group(2).strip()
        if not body:
            return match.group(0)
        # Split into lines
        lines = body.split("\n")
        first_line = lines[0].strip()
        # If first line already has SHALL/MUST, skip
        if re.search(r"\bSHALL\b|\bMUST\b", first_line, re.IGNORECASE):
            return match.group(0)
        # Find which line has SHALL/MUST and merge it with the first line
        shall_line_idx = None
        shall_line = None
        for i, line in enumerate(lines):
            if re.search(r"\bSHALL\b|\bMUST\b", line, re.IGNORECASE):
                shall_line_idx = i
                shall_line = line.strip()
                break
        if shall_line_idx is None:
            return match.group(0)
        # Extract the action part from the SHALL line (the text after SHALL/MUST)
        action = re.sub(r"^[^\n]*?\b(?:SHALL|MUST)\b\s*", "", shall_line).strip()
        if not action:
            return match.group(0)
        # Strip trailing period from first line if present
        first_line_clean = first_line.rstrip(".")
        # Build the new first line: "The system SHALL <action>.<rest_of_first_line>"
        new_first_line = f"The system SHALL {action}{'.' if not first_line_clean.endswith('.') else ''}"
        # Replace first line + remove the SHALL line
        new_lines = [new_first_line] + lines[1:shall_line_idx] + lines[shall_line_idx + 1:]
        # Remove any leading blank lines
        while new_lines and not new_lines[0].strip():
            new_lines = new_lines[1:]
        return f"{title}\n" + "\n".join(new_lines) + "\n\n"

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
            if restructure_requirement_body(spec_file):
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
    lines = result.stdout.strip().split("\n")
    for line in lines[-3:]:
        print(line)


if __name__ == "__main__":
    main()
