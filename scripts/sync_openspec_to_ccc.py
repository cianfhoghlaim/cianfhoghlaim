#!/usr/bin/env python3
"""Append the 20th concept guide to .cocoindex_code/guides.yml.

Per the 2026-08-15-knowledge-sync-loop-v1 change (Layer 2).
This is idempotent — running multiple times is safe.
"""

from __future__ import annotations

import sys
from pathlib import Path

GUIDE_PATH = Path(".cocoindex_code/guides.yml")
GUIDE_ENTRY = """- title: "openspec archive search"
  description: |
    How to find any openspec change (pending or archived) by keyword,
    spec, or implementation status. Use when the user asks "what
    changes have we made for X", "is there a spec for Y", or "where
    is the BIEP v3 Ireland full coverage spec". 14 pending + 303
    archived.
  files:
    - openspec/changes/2026-08-15-knowledge-sync-loop-v1/proposal.md
    - openspec/changes/2026-07-28-biep-v3-ireland-full-coverage-v1/proposal.md
    - openspec/specs/knowledge-sync-loop/spec.md
    - openspec/specs/agent-platform-cluster/spec.md
    - openspec/AGENTS.md
  tags: [openspec, changes, specs, archive, knowledge]
  domain: "00-openspec"
"""


def main() -> int:
    if not GUIDE_PATH.exists():
        # CCC index not yet initialized; create the directory + file
        GUIDE_PATH.parent.mkdir(parents=True, exist_ok=True)
        GUIDE_PATH.write_text(
            "# ccc guides.yml — concept guides for Cianfhoghlaim monorepo\n"
            "# (auto-generated on first sync)\n\n" + GUIDE_ENTRY
        )
        print(f"Created {GUIDE_PATH} with the 20th concept guide")
        return 0

    content = GUIDE_PATH.read_text()
    if "openspec archive search" in content:
        print(f"20th concept guide already present in {GUIDE_PATH}")
        return 0

    # Append the new guide
    if not content.endswith("\n"):
        content += "\n"
    content += "\n" + GUIDE_ENTRY
    GUIDE_PATH.write_text(content)
    print(f"Appended 20th concept guide to {GUIDE_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
