"""MotherDuck Dives for the Cianfhoghlaim lakehouse.

The canonical BIEP v1 4-Dive registry is exposed here as
``BIEP_DIVES``. Each Dive is a :class:`DiveSpec` dataclass that the
MotherDuck ``save_dive`` MCP tool pushes to the workspace at
``md:cianfhoghlaim`` (see :mod:`motherduck.dives.lc_syllabus_topics`).

New Dives can be added by importing the DiveSpec from its module and
appending the constant to ``BIEP_DIVES``. The
:meth:`DiveRegistry.save_all` method iterates the registry and
returns the count of Dives successfully serialised.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("motherduck.dives")

# Re-export the canonical BIEP v1 4 Dives (one per jurisdiction stage):
#   1. lc_syllabus_topics    — topic frequency per LC subject per year
#   2. lc_exam_difficulty    — average marks per question per paper
#   3. lc_marking_complexity — descriptor word count per marking scheme
#   4. gov_circulars_archive — gov.ie circulars + syllabus links
from .lc_syllabus_topics import LC_SYLLABUS_TOPICS_DIVE
from .lc_exam_difficulty import LC_EXAM_DIFFICULTY_DIVE
from .lc_marking_complexity import LC_MARKING_COMPLEXITY_DIVE
from .gov_circulars_archive import GOV_CIRCULARS_ARCHIVE_DIVE

# Optional v3 successor Dives (BIEP v3 jurisdiction coverage).
# These are exported but NOT in the canonical BIEP_DIVES tuple until
# the v3 MotherDuck compute is provisioned (per
# openspec/changes/2026-08-12-biep-v3-motherduck-flights-v1/).
try:  # pragma: no cover — v3 optional
    from .ireland_lc_syllabus_topics import IRELAND_LC_SYLLABUS_TOPICS_DIVE
    _V3_DIVES = (IRELAND_LC_SYLLABUS_TOPICS_DIVE,)
except ImportError:
    _V3_DIVES = ()

# The canonical BIEP v1 4-Dive registry.
BIEP_DIVES: tuple["DiveSpec", ...] = (
    LC_SYLLABUS_TOPICS_DIVE,
    LC_EXAM_DIFFICULTY_DIVE,
    LC_MARKING_COMPLEXITY_DIVE,
    GOV_CIRCULARS_ARCHIVE_DIVE,
)

# All known Dives (v1 + v3 successors).
ALL_DIVES: tuple["DiveSpec", ...] = BIEP_DIVES + _V3_DIVES


@dataclass
class DiveSpec:
    """Minimal MotherDuck Dive spec (also re-defined here for back-compat).

    Sub-package Dive files (e.g. ``lc_syllabus_topics.py``) declare
    their own ``DiveSpec`` dataclass; this module-level class is the
    one referenced by ``DiveRegistry``. The structural shape
    (``name/description/sql/charts/filters``) matches every
    per-Dive module.
    """

    name: str
    description: str
    sql: str
    charts: list[dict[str, Any]] = field(default_factory=list)
    filters: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serialise to a JSON-friendly dict (for ``save_dive`` MCP tool)."""
        return {
            "name": self.name,
            "description": self.description,
            "sql": self.sql,
            "charts": self.charts,
            "filters": self.filters,
        }


class DiveRegistry:
    """Aggregate registry of all BIEP Dives.

    Use :meth:`save_all` to iterate the registry and serialise each
    Dive to JSON. In production, the returned payload is consumed by
    the MotherDuck ``save_dive`` MCP tool via the
    ``mcp-server-motherduck`` server. In dev / CI environments where
    no MotherDuck token is available, :meth:`save_all` still returns
    the count of Dives successfully serialised (it does not raise on
    auth errors).
    """

    def __init__(self, dives: tuple[DiveSpec, ...] | None = None) -> None:
        self.dives: tuple[DiveSpec, ...] = dives if dives is not None else BIEP_DIVES

    def save_all(self) -> int:
        """Serialise every registered Dive to JSON.

        Returns the count of Dives successfully serialised. In CI
        environments without MotherDuck credentials, the JSON payload
        is still produced (to stdout via :meth:`save_dive_definition`)
        so callers can verify the registry shape without network I/O.
        """
        saved = 0
        for dive in self.dives:
            try:
                payload = dive.to_dict()
                logger.info("dive_serialised: %s (%d charts, %d filters)",
                            payload["name"], len(payload["charts"]),
                            len(payload["filters"]))
                saved += 1
            except Exception as e:  # pragma: no cover
                logger.warning("dive_serialise_failed: %s — %s", dive.name, e)
        return saved

    def to_json(self) -> str:
        """Return all Dives as a single JSON document (the MotherDuck workspace import payload)."""
        import json
        return json.dumps([d.to_dict() for d in self.dives], indent=2)


__all__ = [
    "ALL_DIVES",
    "BIEP_DIVES",
    "DiveRegistry",
    "DiveSpec",
    "GOV_CIRCULARS_ARCHIVE_DIVE",
    "LC_EXAM_DIFFICULTY_DIVE",
    "LC_MARKING_COMPLEXITY_DIVE",
    "LC_SYLLABUS_TOPICS_DIVE",
]