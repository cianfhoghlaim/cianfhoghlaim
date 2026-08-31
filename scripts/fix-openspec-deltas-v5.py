#!/usr/bin/env python3
"""Final fixup — puts SHALL/MUST on the FIRST LINE of every requirement body.

This is a more comprehensive version that handles the v0 stragglers / archive /
ducklake / wave-1 edge cases where the v3 script didn't fix.
"""
import re
from pathlib import Path

REPO_ROOT = Path("/Users/cianmacandeisigh/dev/cianfhoghlaim")

CHANGES = [
    "2026-08-22-archive-4-superseded-changes-v1",
    "2026-08-24-wave-1-dlt-sources-domain-restructure-v1",
    "2026-08-24-wave-3-cocoindex-v0-stragglers-v1",
    "2026-08-24-wave-4-ducklake-v1-hardening-v1",
]


def fix_first_line(spec_path: Path) -> bool:
    """Ensure first line of each requirement body has SHALL/MUST."""
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
        lines = body.split("\n")
        first_line = lines[0].strip()
        if re.search(r"\bSHALL\b|\bMUST\b", first_line, re.IGNORECASE):
            return match.group(0)
        # Find first line with SHALL/MUST
        for i, line in enumerate(lines):
            if re.search(r"\bSHALL\b|\bMUST\b", line, re.IGNORECASE):
                action = re.sub(r"^[^\n]*?\b(?:SHALL|MUST)\b\s*", "", line).strip()
                action = action.rstrip(".")
                first_clean = first_line.rstrip(".")
                new_first = f"The system SHALL {action}{'.' if not first_clean.endswith('.') else ''}"
                new_lines = [new_first] + lines[1:i] + lines[i + 1:]
                return f"{title}\n" + "\n".join(new_lines) + "\n\n"
        return match.group(0)

    new_content = pattern.sub(replace_block, content)

    if new_content != original:
        spec_path.write_text(new_content)
        return True
    return False


def add_scenario_if_missing(spec_path: Path) -> bool:
    """Add #### Scenario: if a requirement is missing one."""
    content = spec_path.read_text()
    original = content

    pattern = re.compile(
        r"^(### Requirement:[^\n]*\n)((?:(?!^### |^## |\Z).)*?)(?=^### |^## |\Z)",
        re.MULTILINE | re.DOTALL,
    )

    def replace_block(match):
        title = match.group(1).strip()
        body = match.group(2).strip()
        if "#### Scenario:" in body:
            return match.group(0)
        if not body:
            return match.group(0)
        # Wrap bullets in a scenario block
        when_idx = None
        for i, line in enumerate(body.split("\n")):
            if re.search(r"\*\*WHEN\*\*", line, re.IGNORECASE):
                when_idx = i
                break
        if when_idx is None:
            return match.group(0)
        lines = body.split("\n")
        pre = "\n".join(lines[:when_idx]).strip()
        bullets = "\n".join(lines[when_idx:]).strip()
        if pre:
            new_body = f"{pre}\n\n#### Scenario: Default scenario\n\n{bullets}\n\n"
        else:
            new_body = f"#### Scenario: Default scenario\n\n{bullets}\n\n"
        return f"{title}\n{new_body}"

    new_content = pattern.sub(replace_block, content)

    if new_content != original:
        spec_path.write_text(new_content)
        return True
    return False


def main():
    fixed1 = 0
    fixed2 = 0
    for change in CHANGES:
        change_dir = REPO_ROOT / "openspec/changes" / change / "specs"
        if not change_dir.exists():
            continue
        for spec_file in change_dir.glob("**/spec.md"):
            if fix_first_line(spec_file):
                print(f"✅ Fixed first line: {spec_file.relative_to(REPO_ROOT)}")
                fixed1 += 1
            if add_scenario_if_missing(spec_file):
                print(f"✅ Added scenario: {spec_file.relative_to(REPO_ROOT)}")
                fixed2 += 1

    print(f"\nFixed first line: {fixed1}, Added scenario: {fixed2}")
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
