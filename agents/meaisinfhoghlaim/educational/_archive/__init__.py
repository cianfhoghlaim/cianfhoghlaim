"""agents.meaisinfhoghlaim.educational._archive — the education twin of agent-valley.

Per openspec/changes/2026-09-23-upgrade-to-adk2-pillars-1-2-3-v1/.

Five floors of memory, mapped to the 5 BIEP v3 stages:

    floor 5   the valley        the whole BIEP      DuckLake + MotherDuck   (cross-8-nation + 5-stage)
    floor 4   the season       the whole BIEP      BQ + Vertex AI Memory Bank  (cross-8-nation)
    floor 3   the tower        what was said       Vertex AI Memory Bank     (per-visit, per-stage)
    floor 2   the drawer       this visitor        user: prefix               (cross-visit per student)
    floor 1   the books        every visit         SqliteSessionService      (per-session, per-stage)

Mirrors agent-valley-archive exactly — the only difference is the
DOMAIN: agent-valley serves visitors with broken devices; cianfhoghlaim's
_archive serves teachers + students across the 5 BIEP v3 stages.
"""
from __future__ import annotations

from .agent import build_archive_agent
from .state import (
    VISIT,
    VISITOR,
    STUDENT,
    VALLEY,
    VISIT_COUNT,
    STAGE_TO_FLOOR,
    build_house,
)
from .memory import burn, list_floor, archive_today
from .topics import TOPICS

__all__ = [
    "build_archive_agent",
    "VISIT",
    "VISITOR",
    "STUDENT",
    "VALLEY",
    "VISIT_COUNT",
    "STAGE_TO_FLOOR",
    "TOPICS",
    "build_house",
    "burn",
    "list_floor",
    "archive_today",
]
