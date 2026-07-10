"""
BIEP v1 MotherDuck Dives — 4-dive registry.

Imports + re-exports the 4 BIEP v1 Dives for the MotherDuck
workspace. The motherduck-cli loads these via
``mcp-server-motherduck``'s `save_dive` tool.

The 4 Dives are:

1. ``lc_syllabus_topics`` — topic frequency per LC subject per year
2. ``lc_exam_difficulty`` — per-subject per-year per-paper difficulty score
3. ``lc_marking_complexity`` — per-subject per-topic average descriptor count
4. ``gov_circulars_archive`` — `gov.ie` circulars by dept + year + subject area

Reference: openspec/changes/2026-07-06-british-isles-education-pipeline-v1/
openspec/specs/british-isles-education-pipeline/spec.md
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# Re-export the 4 Dive specs.
from .gov_circulars_archive import GOV_CIRCULARS_ARCHIVE_DIVE
from .lc_exam_difficulty import LC_EXAM_DIFFICULTY_DIVE
from .lc_marking_complexity import LC_MARKING_COMPLEXITY_DIVE
from .lc_syllabus_topics import LC_SYLLABUS_TOPICS_DIVE


# The 4 BIEP v1 Dives (registry order = display order).
BIEP_DIVES: tuple[Any, ...] = (
    LC_SYLLABUS_TOPICS_DIVE,
    LC_EXAM_DIFFICULTY_DIVE,
    LC_MARKING_COMPLEXITY_DIVE,
    GOV_CIRCULARS_ARCHIVE_DIVE,
)


@dataclass
class DiveRegistry:
    """The 4 BIEP v1 Dives ready for save_dive() calls."""

    dives: tuple[Any, ...] = BIEP_DIVES

    def to_dicts(self) -> list[dict[str, Any]]:
        return [dive.to_dict() for dive in self.dives]

    def save_all(self) -> int:
        """Save all 4 Dives to the MotherDuck workspace.

        Returns the count of Dives successfully saved.
        """
        try:
            from motherduck.dives import save_dive  # type: ignore[import-not-found]
        except ImportError:
            print("ERROR: `motherduck` package not installed.")
            return 0
        saved = 0
        for dive in self.dives:
            try:
                save_dive(
                    name=dive.name,
                    sql=dive.sql,
                    description=dive.description,
                    charts=dive.charts,
                    filters=dive.filters,
                )
                saved += 1
                print(f"  [OK]   {dive.name}")
            except Exception as e:  # pragma: no cover
                print(f"  [FAIL] {dive.name}: {e}")
        return saved


__all__ = [
    "BIEP_DIVES",
    "DiveRegistry",
    "LC_SYLLABUS_TOPICS_DIVE",
    "LC_EXAM_DIFFICULTY_DIVE",
    "LC_MARKING_COMPLEXITY_DIVE",
    "GOV_CIRCULARS_ARCHIVE_DIVE",
]


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--save":
        registry = DiveRegistry()
        n = registry.save_all()
        print(f"Saved {n}/{len(BIEP_DIVES)} Dives")
        sys.exit(0 if n == len(BIEP_DIVES) else 1)
    else:
        for dive in BIEP_DIVES:
            print(f"  {dive.name}: {len(dive.charts)} charts, {len(dive.filters)} filters")
