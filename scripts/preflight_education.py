#!/usr/bin/env python3
"""scripts/preflight_education.py — the ADK 2 + Memory Bank + BQ preflight for cianfhoghlaim.

Per openspec/changes/2026-09-23-upgrade-to-adk2-pillars-1-2-3-v1/.
Mirrors `docs/google_examples/agent-valley-archive/scripts/preflight.py` — every
assertion is a sentence the codelab makes to the operator.

Run:
    uv run python scripts/preflight_education.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

TICK, BOX = "\033[32m✓\033[0m", "\033[90m▢\033[0m"
DIM, OFF = "\033[90m", "\033[0m"


def main() -> int:
    print()
    rows = []

    # 1) google-adk >= 2.5.0?
    try:
        import google.adk

        adk_version = getattr(google.adk, "__version__", "unknown")
        ok = adk_version.startswith("2.")
        rows.append((ok, f"google-adk version", f"{DIM}{adk_version}{OFF}"))
    except Exception as exc:
        rows.append((False, "google-adk importable", str(exc)))

    # 2) The 5-floor archive state keys are reachable
    try:
        from agents.meaisinfhoghlaim.educational._archive.state import (
            VISIT, VISITOR, STUDENT, VALLEY, VISIT_COUNT, STAGE_TO_FLOOR,
        )
        for key in (VISIT, VISITOR, STUDENT, VALLEY, VISIT_COUNT):
            assert key
        rows.append((True, "Archive 5 keys reachable", f"{VISIT}, {VISITOR}, {STUDENT}, {VALLEY}, {VISIT_COUNT}"))
    except Exception as exc:
        rows.append((False, "Archive 5 keys", str(exc)))

    # 3) The 3 Pillar-1 workflow graphs are registered
    try:
        from agents.workflows import (
            teacher_daily_workflow, student_secondary_workflow, tertiary_personal_workflow,
        )
        rows.append((True, "Pillar 1 workflows", "teacher + student + tertiary"))
    except Exception as exc:
        rows.append((False, "Pillar 1 workflows", str(exc)))

    # 4) The 5 Pillar-3 deep-research pipelines are registered
    try:
        from agents.workflows import (
            aistear_deep_research, primary_deep_research, jc_deep_research,
            sc_deep_research, tertiary_deep_research,
        )
        rows.append((True, "Pillar 3 deep-research", "aistear + primary + jc + sc + tertiary"))
    except Exception as exc:
        rows.append((False, "Pillar 3 deep-research", str(exc)))

    # 5) The 3 root orchestrators (tertiary SU + K-12 teacher + K-12 student) are registered
    try:
        from agents.meaisinfhoghlaim.educational.students_union.root_agent import root_agent
        from agents.meaisinfhoghlaim.educational.teachers._root import teacher_root
        from agents.meaisinfhoghlaim.educational.students_jc._root import student_root
        rows.append((True, "3 root orchestrators", "SU + teacher + student"))
    except Exception as exc:
        rows.append((False, "3 root orchestrators", str(exc)))

    print(f"  {DIM}cianfhoghlaim ADK 2 + education archive preflight{OFF}")
    for ok, what, detail in rows:
        print(f"  {TICK if ok else BOX} {what:<32} {DIM}· {detail}{OFF}")
        if not ok:
            return 1
    print()
    print(f"  {TICK} ready for `python scripts/walk_education.py`")
    return 0


if __name__ == "__main__":
    sys.exit(main())
