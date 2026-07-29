"""spec_agents.py — generates per-spec AGENTS.md files from the canonical template.

Per the 2026-07-29-repo-hygiene-agent-routing-and-sync-wiring-v1 change
(see openspec/changes/.../specs/repo-hygiene-agent-routing/spec.md).

Walks openspec/specs/, reads each spec.md first line (the one-line
purpose), and emits a sibling AGENTS.md per spec if missing or older
than its spec.md. Dry-run support via --dry-run flag.
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SPECS_DIR = REPO_ROOT / "openspec" / "specs"

TEMPLATE = """# `{slug}` — {title}

> {purpose}

## Routing

Load this AGENTS.md when working on the `{slug}` capability or any change that touches its spec.

For platform-wide context, load [`../../../AGENTS.md`](../../../AGENTS.md) and the openspec workflow at [`../../../openspec/AGENTS.md`](../../../openspec/AGENTS.md).

## Quick start

```bash
openspec validate <change-id> --strict   # MUST pass before commit
openspec list --specs | grep {slug}       # confirm the spec is registered
```

## Key sources

| Path | Why it matters |
|:--|:--|
| `openspec/specs/{slug}/spec.md` | The capability contract — every Requirement + Scenario lives here |
| `openspec/changes/<id>/specs/{slug}/spec.md` | The change delta where ADDED/MODIFIED/REMOVED Requirements are written |

## Adjacent specs

Inspect `openspec/specs/{slug}/spec.md` §Cross-references for the canonical adjacency list.

## DO NOT

- **Never** edit `openspec/specs/{slug}/spec.md` directly — only write deltas under `openspec/changes/<id>/specs/{slug}/spec.md`.

## Skill pointers

Consult the openspec skill (`.agents/skills/openspec/SKILL.md`) and any capability-specific skill referenced in the spec.

<!-- generated: {date}; do not hand-edit -->
"""


def slug_to_title(slug: str) -> str:
    return slug.replace("-", " ").title()


def first_purpose_line(spec_md: Path) -> str:
    text = spec_md.read_text()
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#"):
            continue
        return line
    return "Capability spec"


def emit(spec_dir: Path, *, dry_run: bool) -> tuple[Path, bool]:
    spec_md = spec_dir / "spec.md"
    agents_md = spec_dir / "AGENTS.md"
    if not spec_md.exists():
        return agents_md, False
    slug = spec_dir.name
    purpose = first_purpose_line(spec_md)
    title = slug_to_title(slug)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    rendered = TEMPLATE.format(slug=slug, title=title, purpose=purpose, date=today)
    if agents_md.exists() and agents_md.read_text() == rendered:
        return agents_md, False
    if not dry_run:
        agents_md.write_text(rendered)
    return agents_md, True


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate per-spec AGENTS.md siblings.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not SPECS_DIR.is_dir():
        print(f"ERROR: {SPECS_DIR} not found", file=sys.stderr)
        return 2

    written = 0
    skipped = 0
    for spec_dir in sorted(SPECS_DIR.iterdir()):
        if not spec_dir.is_dir():
            continue
        path, changed = emit(spec_dir, dry_run=args.dry_run)
        if changed:
            written += 1
            print(f"{'WOULD WRITE' if args.dry_run else 'WROTE'}: {path.relative_to(REPO_ROOT)}")
        else:
            skipped += 1
    print(f"DONE: {written} written, {skipped} unchanged ({len(list(SPECS_DIR.iterdir()))} specs scanned)")
    return 0


if __name__ == "__main__":
    sys.exit(main())