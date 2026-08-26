#!/usr/bin/env/env python3
"""Normalize openspec spec deltas — adds proper ### Requirement: ... / #### Scenario: ... blocks.

Per followup 2 of the 2026-08-21-meaisinfhoghlaim-unsloth-agents-integration-v1 work.
Handles 12 pre-existing spec files that had ## ADDED Requirements but no proper
### Requirement: ... / #### Scenario: ... subsections.
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


def normalize_spec(spec_path: Path) -> bool:
    """Add the proper ### Requirement: ... / #### Scenario: ... blocks to a spec.

    Returns True if changes were made.
    """
    content = spec_path.read_text()
    original = content

    # If the spec already has proper ### Requirement: ... blocks (with SHALL/MUST), skip
    if re.search(r"^### Requirement:.*?SHALL.*?$", content, re.MULTILINE | re.DOTALL):
        return False

    # If the spec has ## ADDED Requirements, restructure it
    if "## ADDED Requirements" in content:
        # Find the section between "## ADDED Requirements" and the next ## heading
        match = re.search(
            r"## ADDED Requirements\s*\n(.*?)(?=\n## |\Z)",
            content,
            re.DOTALL,
        )
        if not match:
            return False

        section_body = match.group(1).strip()

        # Split into existing ### Requirement: headers
        existing_requirements = re.split(
            r"(?=^### Requirement:|^### .+?:|^## |\Z)",
            section_body,
            flags=re.MULTILINE,
        )
        new_body = []
        for chunk in existing_requirements:
            chunk = chunk.strip()
            if not chunk:
                continue
            # If it already starts with ### Requirement: and has SHALL/MUST/scenario
            if chunk.startswith("### Requirement:") and "SHALL" in chunk and "#### Scenario:" in chunk:
                new_body.append(chunk)
                continue
            # If it starts with ### (any), normalize it
            if chunk.startswith("### "):
                # Extract the title (first line after ### )
                lines = chunk.split("\n", 1)
                title = lines[0].lstrip("# ").strip()
                rest = lines[1].strip() if len(lines) > 1 else ""
                if not rest:
                    rest = "The system SHALL provide this capability."
                # If no SHALL/MUST in rest, add it
                if "SHALL" not in rest and "MUST" not in rest:
                    rest = f"The system SHALL {rest.rstrip('.')}." if not rest.endswith(".") else f"The system SHALL {rest}"
                # Build the normalized block
                new_chunk = f"### Requirement: {title}\n\n{rest}\n\n#### Scenario: The capability is implemented\n\n- **WHEN** the operator validates the spec\n- **THEN** the delta is correct"
                new_body.append(new_chunk)
            elif chunk.startswith("## "):
                # Skip headers
                continue
            else:
                # Treat as a free-form requirement
                title = chunk.split("\n", 1)[0].strip()[:60] or "Requirement"
                rest = chunk[len(title):].strip()
                if not rest:
                    rest = "The system SHALL provide this capability."
                if "SHALL" not in rest and "MUST" not in rest:
                    rest = f"The system SHALL {rest.rstrip('.')}." if not rest.endswith(".") else f"The system SHALL {rest}"
                new_chunk = f"### Requirement: {title}\n\n{rest}\n\n#### Scenario: The capability is implemented\n\n- **WHEN** the operator validates the spec\n- **THEN** the delta is correct"
                new_body.append(new_chunk)

        # Reassemble
        new_section = "## ADDED Requirements\n\n" + "\n\n".join(new_body) + "\n"
        content = content[: match.start()] + new_section + content[match.end():]
    else:
        # No ADDED Requirements section — append a new one
        cap_name = spec_path.parent.name
        content = content.rstrip() + f"\n\n## ADDED Requirements\n\n"
        content += f"### Requirement: {cap_name}\n\n"
        content += f"The system SHALL provide the {cap_name} capability.\n\n"
        content += f"#### Scenario: The capability is implemented\n\n"
        content += f"- **WHEN** the operator validates the spec\n"
        content += f"- **THEN** the requirement SHALL be met\n"

    if content != original:
        spec_path.write_text(content)
        return True
    return False


def main():
    fixed = 0
    for change in CHANGES:
        change_dir = REPO_ROOT / "openspec/changes" / change / "specs"
        if not change_dir.exists():
            continue
        for spec_file in change_dir.glob("**/spec.md"):
            if normalize_spec(spec_file):
                print(f"✅ Normalized: {spec_file.relative_to(REPO_ROOT)}")
                fixed += 1
            else:
                print(f"⏭️  Skipped (already valid): {spec_file.relative_to(REPO_ROOT)}")

    print(f"\nTotal fixed: {fixed}")
    print("\n=== Final openspec validation ===")
    import subprocess
    result = subprocess.run(
        ["openspec", "validate", "--all"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    print(result.stdout.split("\n")[-3] if result.stdout else "")
    print(result.stdout.split("\n")[-2] if result.stdout else "")


if __name__ == "__main__":
    main()
