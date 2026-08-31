#!/usr/bin/env python3
"""Fix requirement body structure — wraps body in #### Scenario: blocks if missing.

Per followup 2 of the 2026-08-21-meaisinfhoghlaim-unsloth-agents-integration-v1 work.
The earlier v3 fix removed #### Scenario: lines. This v4 fix adds them back.
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


def add_scenario_blocks(spec_path: Path) -> bool:
    """Ensure each ### Requirement: block has at least one #### Scenario: block.

    The openspec parser requires a #### Scenario: subsection under each requirement.
    If missing, wrap any subsequent bullet points in a Scenario block.
    """
    content = spec_path.read_text()
    original = content

    # Pattern: ### Requirement: ... block
    pattern = re.compile(
        r"^(### Requirement:[^\n]*\n)((?:(?!^### |^## |\Z).)*?)(?=^### |^## |\Z)",
        re.MULTILINE | re.DOTALL,
    )

    def replace_block(match):
        title = match.group(1).strip()
        body = match.group(2).strip()
        if not body:
            return match.group(0)
        # Check if body already has a #### Scenario: subsection
        if "#### Scenario:" in body:
            return match.group(0)
        # Check if body has bullet points (#### Scenario candidates)
        lines = body.split("\n")
        # Find the first non-empty line that looks like a bullet
        # A scenario is a series of " - **WHEN** ... / - **THEN** ..." bullets
        # If body has - **WHEN** anywhere, wrap the rest in a Scenario block
        when_idx = None
        for i, line in enumerate(lines):
            if re.search(r"\*\*WHEN\*\*", line, re.IGNORECASE):
                when_idx = i
                break
        if when_idx is None:
            return match.group(0)
        # Split body into pre-scenario text + scenario bullets
        pre_scenario = "\n".join(lines[:when_idx]).strip()
        scenario_bullets = "\n".join(lines[when_idx:]).strip()
        # Build new body with the scenario wrapped
        if pre_scenario:
            new_body = f"{pre_scenario}\n\n#### Scenario: Default scenario\n\n{scenario_bullets}\n\n"
        else:
            new_body = f"#### Scenario: Default scenario\n\n{scenario_bullets}\n\n"
        return f"{title}\n{new_body}"

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
            if add_scenario_blocks(spec_file):
                print(f"✅ Added Scenario: {spec_file.relative_to(REPO_ROOT)}")
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
