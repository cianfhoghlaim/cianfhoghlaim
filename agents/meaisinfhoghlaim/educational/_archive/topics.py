"""Topics — what the cianfhoghlaim Archive is allowed to keep.

Per openspec/changes/2026-09-23-upgrade-to-adk2-pillars-1-2-3-v1/.
Mirrors `docs/google_examples/agent-valley-archive/archive/topics.py`.

The write policy (FILING) reads TOPICS — what topics the archive is
allowed to file. Per agent-valley: the model fills in the form; the
code moves the sparks.
"""
from __future__ import annotations

TOPICS: tuple[str, ...] = (
    "lesson_plan",
    "assessment",
    "sen_record",
    "parent_meeting",
    "professional_learning",
    "homework",
    "cba",
    "study_plan",
    "wellbeing",
    "exam",
    "timetable",
    "module",
    "programme",
    "college",
    "school",
    "subject",
    "syllabus",
    "marking_scheme",
    "past_paper",
)

__all__ = ["TOPICS"]
