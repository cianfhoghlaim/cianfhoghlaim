"""spec_agents.py — the per-spec AGENTS.md generator.

Per the 2026-07-29-repo-hygiene-agent-routing-and-sync-wiring-v1 change
(see openspec/specs/repo-hygiene-agent-routing/spec.md).

Walks `openspec/specs/`, reads each `spec.md` first line (the one-line
purpose), and emits a sibling `AGENTS.md` at every spec, if missing or
older than its `spec.md`. The output uses the canonical 6-section
outline from `openspec/specs/repo-hygiene-agent-routing/templates/spec-AGENTS.md.tmpl`.

Usage:
    uv run python scripts/sync/spec_agents.py              # idempotent generator
    uv run python scripts/sync/spec_agents.py --dry-run    # print what would be emitted, no writes
    uv run python scripts/sync/spec_agents.py --force      # emit even if AGENTS.md is newer
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SPECS_ROOT = REPO_ROOT / "openspec" / "specs"
TEMPLATE = (
    REPO_ROOT
    / "openspec"
    / "specs"
    / "repo-hygiene-agent-routing"
    / "templates"
    / "spec-AGENTS.md.tmpl"
)


def derive_purpose(spec_md: Path) -> str:
    """Read the first line of the spec that looks like a purpose statement.

    Skips the H1 header (the spec name) and the first `## Purpose` heading,
    then pulls the first paragraph that follows (typically a `> ...` blockquote).
    Falls back to the first 100 chars of plain text if no blockquote is found.
    """
    text = spec_md.read_text()
    lines = text.splitlines()

    # Phase 1: skip the H1 header
    i = 0
    while i < len(lines) and not lines[i].lstrip().startswith("# "):
        i += 1
    i += 1  # past the H1

    # Phase 2: skip blanks + skip up to the first `## Purpose` (or any `##`) heading
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped.startswith("## "):
            # Skip the heading itself
            i += 1
            continue
        if stripped.startswith("#"):
            i += 1
            continue
        if not stripped:
            i += 1
            continue
        # First non-empty, non-heading line — should be the purpose blockquote
        if stripped.startswith(">"):
            # Collect all consecutive `>` lines into a single string
            purpose_lines = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                purpose_lines.append(lines[i].strip().lstrip("> ").strip())
                i += 1
            return " ".join(filter(None, purpose_lines))
        # If it's a plain paragraph, return the first 200 chars
        return stripped[:200] + ("..." if len(stripped) > 200 else "")
    # Fallback
    plain = re.sub(r"\s+", " ", text).strip()
    return plain[:100] + ("..." if len(plain) > 100 else "")


def infer_mise_tasks(spec_name: str) -> tuple[str, str, str, str]:
    """Infer the 2 most relevant mise tasks for the spec.

    Returns:
        (task_1, task_1_desc, task_2, task_2_desc)
    """
    # Canonical mapping (the 80% case)
    canonical = {
        "agent-memory-systems": (
            "agents:smoke",
            "Run the 3 agent-fleet smoke tests",
            "lint:registry",
            "Audit MODEL_REGISTRY hardcoded strings",
        ),
        "agent-observability": (
            "lint:registry",
            "Audit MODEL_REGISTRY",
            "agents:smoke",
            "Run smoke tests",
        ),
        "british-isles-education-pipeline-v3": (
            "sync:paths",
            "Layer 1: pre-v7 path drift",
            "biep:v3:gate",
            "BIEP v3 milestone gate",
        ),
        "centralized-model-registry": (
            "lint:registry",
            "Audit MODEL_REGISTRY",
            "models:list",
            "List all 52 MODEL_REGISTRY entries",
        ),
        "centralized-schema-registry": (
            "schema:generate",
            "Regenerate Zod + TanStack DB schemas",
            "schema:validate",
            "CI drift gate for generated Zod schemas",
        ),
        "deployment-control-panel": (
            "notebook:control-panel",
            "Open the 5-tab deployment control panel",
            "models:list",
            "List all MODEL_REGISTRY entries",
        ),
        "indexing-and-cognition": (
            "ccc:index",
            "Rebuild the CC semantic index",
            "ccc:v1:search",
            "Search the codebase_chunks LanceDB table",
        ),
        "knowledge-sync-loop": (
            "sync:all",
            "Run all 7 sync layers",
            "lint:drift-docs",
            "Validate every AGENTS.md number claim",
        ),
        "infrastructure-stacks": (
            "cic:stack-doctor",
            "Validate all 89 stacks against the 6-file GOLD_STANDARD",
            "stack-doctor:strict",
            "CI gate + grammar check",
        ),
    }
    if spec_name in canonical:
        return canonical[spec_name]
    # Fallback: the 2 most universal sync tasks
    return (
        "sync:all",
        "Run all 7 sync layers",
        "lint:drift-docs",
        "Validate every AGENTS.md number claim",
    )


def render_template(spec_name: str, purpose: str) -> str:
    """Render the template with the spec_name + purpose filled in."""
    task_1, desc_1, task_2, desc_2 = infer_mise_tasks(spec_name)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    template = TEMPLATE.read_text()
    return (
        template.replace("{{ spec_name }}", spec_name)
        .replace("{{ purpose_line }}", purpose)
        .replace("{{ mise_task_1 }}", task_1)
        .replace("{{ mise_task_1_desc }}", desc_1)
        .replace("{{ mise_task_2 }}", task_2)
        .replace("{{ mise_task_2_desc }}", desc_2)
        .replace("{{ date }}", today)
    )


def is_stale(spec_md: Path, agents_md: Path) -> bool:
    """Return True if `agents_md` is outdated (missing or older than `spec_md`)."""
    if not agents_md.exists():
        return True
    return spec_md.stat().st_mtime > agents_md.stat().st_mtime


def should_emit(spec_md: Path, agents_md: Path, force: bool) -> bool:
    """Decide whether to emit a fresh AGENTS.md for this spec."""
    if force:
        return True
    if not agents_md.exists():
        return True
    # If the existing AGENTS.md lacks the machine-readable footer, regenerate
    text = agents_md.read_text()
    if "<!-- generated:" not in text:
        return True
    return spec_md.stat().st_mtime > agents_md.stat().st_mtime


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate per-spec AGENTS.md files.")
    parser.add_argument(
        "--dry-run", action="store_true", help="Print what would be emitted, no writes"
    )
    parser.add_argument("--force", action="store_true", help="Emit even if AGENTS.md is newer")
    args = parser.parse_args()

    if not SPECS_ROOT.is_dir():
        print(f"ERROR: {SPECS_ROOT} not found", file=sys.stderr)
        return 1

    if not TEMPLATE.is_file():
        print(f"ERROR: template {TEMPLATE} not found", file=sys.stderr)
        return 1

    emitted: list[Path] = []
    skipped: list[Path] = []

    for spec_dir in sorted(SPECS_ROOT.iterdir()):
        if not spec_dir.is_dir():
            continue
        spec_md = spec_dir / "spec.md"
        if not spec_md.is_file():
            continue
        agents_md = spec_dir / "AGENTS.md"
        if not should_emit(spec_md, agents_md, force=args.force):
            skipped.append(agents_md)
            continue
        purpose = derive_purpose(spec_md)
        content = render_template(spec_dir.name, purpose)
        if args.dry_run:
            print(f"--- WOULD EMIT: {spec_dir.name}/AGENTS.md ---")
            print(content[:200] + "...")
        else:
            agents_md.write_text(content)
            emitted.append(agents_md)
            print(f"  + {spec_dir.name}/AGENTS.md")

    print()
    print(f"Emitted: {len(emitted)}")
    print(f"Skipped (already fresh): {len(skipped)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
