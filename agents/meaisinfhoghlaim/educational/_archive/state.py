"""The Archive state — every key, in one place.

Per openspec/changes/2026-09-23-upgrade-to-adk2-pillars-1-2-3-v1/.
Mirrors `docs/google_examples/agent-valley-archive/archive/state.py`.

The 5 keys for the 5-floor education ladder:

    key              scope      written by        read by
    ────────────────────────────────────────────────────────────────
    visit            session    write_down        vesper, the slip
    user:student_id  user       the service       the tower (floor 3)
    user:stage       user       the service       the drawer (floor 2)
    app:valley        app        BigQuery loader   the season (floor 5)
    user:visit_count  user       the service       vesper, the slip

The Pillar 3 Memory Bank surfaces (per the L4b_recursion pattern):
- InMemoryMemoryService for dev (no setup)
- VertexAiMemoryBankService for production (per agent-valley's chapter 4)

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

from ._stages import stage_to_floor  # circular-safe import
from agents.meaisinfhoghlaim._shared import EducationStage, STAGE_TO_FLOOR

#: The 5 ladder keys.
VISIT = "visit"
VISITOR = "user:student_id"
STUDENT = "user:stage"
VALLEY = "app:valley"
VISIT_COUNT = "user:visit_count"

#: Public mapping for backward compat (mirrors agents.meaisinfhoghlaim._shared).
STAGE_TO_FLOOR = STAGE_TO_FLOOR


#: The 5-storey prompt template — Vesper's voice, built rather than templated.
HOUSE = """You are Vesper, the archivist of cianfhoghlaim's Archive — a small deer with \
fairy lights in your antlers, who keeps the tower where the BIEP v3 \
5-stage ladder writes everything down. Teachers and students come when \
something has gone wrong with their course or their lesson.

THE SLIP — what is already written about this visitor:
{slip}

THE TOWER — what it handed you for this question:
{tower}

House rules:
1. Answer ONLY from the slip and the tower. If neither holds it, say so plainly.
2. For teacher queries, always cite the canonical primary or JC + SC subject area
   (e.g. 'cs203_data_structures' for Data Structures).
3. For student queries, honour wellbeing concerns (Children First Act 2015).
4. Two or three short, warm sentences. Never a list.
"""


def build_house() -> str:
    """Return the static Vesper prompt (no state substitution in Phase 1)."""
    return HOUSE


__all__ = [
    "VISIT",
    "VISITOR",
    "STUDENT",
    "VALLEY",
    "VISIT_COUNT",
    "STAGE_TO_FLOOR",
    "HOUSE",
    "build_house",
]
