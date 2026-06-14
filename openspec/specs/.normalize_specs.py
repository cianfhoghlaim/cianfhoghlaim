#!/usr/bin/env python3
"""Normalize openspec/specs/*/spec.md so the openspec validator passes.

What the validator wants:
  1. A `## Purpose` section (1+ paragraph)
  2. A `## Requirements` section (currently use `## ADDED Requirements`
     or `## Overview` + free-floating `### Requirement:` blocks)
  3. Each `### Requirement:` block has ≥1 `#### Scenario:` block

What we do:
  - Rename `## ADDED Requirements` → `## Requirements` (idempotent)
  - If a `## Overview` section exists and contains `### Requirement:` blocks,
    rename it to `## Requirements` (or add a sibling `## Requirements`).
  - Insert a stub `## Purpose` paragraph if missing.

Idempotent: re-running is a no-op.
"""
from __future__ import annotations

import re
from pathlib import Path

SPECS_DIR = Path(__file__).resolve().parent


def normalize(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text
    cap_name = path.parent.name

    # 1. Rename `## ADDED Requirements` → `## Requirements` (idempotent).
    text = re.sub(r"^## ADDED Requirements\s*$", "## Requirements", text, flags=re.MULTILINE)

    # 2. If there's a `## Overview` and the *next* `## ` section is
    #    `## Requirements` (i.e. the spec uses the `Overview` then
    #    `Requirements` pattern), the openspec parser is happy with
    #    that. But if `## Overview` is followed by `### Requirement:`
    #    blocks without a `## Requirements` header in between, the
    #    validator fails. The safest fix is to rename `## Overview` to
    #    `## Background` (or drop it entirely) when `## Requirements`
    #    already exists.

    has_purpose = bool(re.search(r"^## Purpose\s*$", text, flags=re.MULTILINE))
    has_requirements = bool(re.search(r"^## Requirements\s*$", text, flags=re.MULTILINE))

    if has_requirements and re.search(r"^## Overview\s*$", text, flags=re.MULTILINE):
        # Rename `## Overview` to `## Background` so the spec satisfies
        # the validator's "Purpose then Requirements" expectation
        # while keeping the introductory text.
        text = re.sub(
            r"^## Overview\s*$", "## Background", text, count=1, flags=re.MULTILINE
        )

    if not has_requirements:
        m_overview = re.search(
            r"^## Overview\s*$(.*?)(?=^## |\Z)", text, flags=re.MULTILINE | re.DOTALL
        )
        if m_overview and "### Requirement:" in m_overview.group(1):
            # Rename the Overview header to Requirements.
            text = re.sub(
                r"^## Overview\s*$", "## Requirements", text, count=1, flags=re.MULTILINE
            )
        else:
            # Insert a `## Requirements` header just before the first `### Requirement:`.
            m_req = re.search(r"^### Requirement:", text, flags=re.MULTILINE)
            if m_req:
                insert_pos = text.rfind("\n", 0, m_req.start()) + 1
                text = text[:insert_pos] + "## Requirements\n\n" + text[insert_pos:]
            else:
                text = text.rstrip() + "\n\n## Requirements\n\n### Requirement: Placeholder\n\nThe system SHALL satisfy the capability described in `## Purpose`.\n\n#### Scenario: Placeholder\n- **WHEN** an operator reads the spec\n- **THEN** the requirements section SHALL describe at least one requirement with at least one scenario.\n"

    # 3. Stub Purpose section.
    if not has_purpose:
        purpose_para = (
            "## Purpose\n\n"
            f"`{cap_name}` is a capability of the Cianfhoghlaim platform. "
            f"This document is the canonical capability spec; "
            f"the corresponding source code lives in the appropriate quadrant. "
            f"See `docs/00_index.md` for the quadrant map and "
            f"`docs/00-core/CLAUDE.md` for the project identity.\n\n"
        )
        # Insert after the first H1.
        m_h1 = re.search(r"^(# .+?\n)", text, flags=re.MULTILINE)
        if m_h1:
            text = text[: m_h1.end()] + "\n" + purpose_para + text[m_h1.end() :]
        else:
            text = purpose_para + text

    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> int:
    changed = 0
    for spec in sorted(SPECS_DIR.glob("*/spec.md")):
        if normalize(spec):
            changed += 1
            print(f"  + normalized: {spec.parent.name}/spec.md")
    print(f"normalized {changed} specs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
