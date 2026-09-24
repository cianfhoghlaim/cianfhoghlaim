"""cianfhoghlaim — Class Rep feedback theme aggregator.

Per openspec/changes/2026-09-23-consolidate-uog-tertiary-pipeline-v1/, Case Study 3.

Aggregates Class Rep reports across multiple modules to surface themes
(assessment, content, lecturer, accessibility, welfare, logistics) for
the SU Education Officer.

Pure-Python, deterministic. Below the configured minimum
(default 3) class reps per theme, no aggregation is performed (avoids
over-extrapolating from 1 or 2 voices).

The theme taxonomy is the canonical SU Education Council taxonomy
(2025/26). Each theme has a keyword list + a "priority weight"
(assessment = 1.0, welfare = 0.8, etc.) so the output is sorted by
weighted volume.

**Phase 2 — UoG tertiary pipeline real-data upgrade:**
Each `ClassRepReport.module_code` is resolved via
`config.module_full_names` to its snake_case full-name form
(e.g. "CS203" → "cs203_data_structures") so the aggregation JOINs
the 4-tier tertiary Module schema at
`dlt_sources/british_isles/ireland/tertiary/uog/modules.py`.

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md at the cianfhoghlaim repo root).
"""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field

from ..config import config as _config


@dataclass(frozen=True)
class ClassRepReport:
    """A single Class Rep's weekly/monthly feedback report."""
    rep_id: str
    module_code: str  # bare code, e.g. "CS203"
    module_title: str
    report_text: str
    semester: str  # e.g. "2025/26 S1"
    submitted_at_iso: str

    @property
    def module_id(self) -> str:
        """The snake_case full-name FK to the 4-tier Module schema.

        Returns the canonical module_id (e.g. "cs203_data_structures")
        that JOINs with `dlt_sources/.../tertiary/uog/modules.py`.
        """
        from ..config import module_full_name
        return module_full_name(self.module_code) or self.module_code.lower()


@dataclass(frozen=True)
class ThemeAggregation:
    """Aggregated themes across many ClassRepReport rows."""
    total_reports: int
    total_modules: int
    themes: dict[str, int]  # theme_name -> weighted_count
    top_concerns: tuple[str, ...]  # sorted by weighted_count desc
    modules_with_multiple_concerns: tuple[str, ...]  # modules that flagged ≥ 3 themes
    insufficient_data: bool  # True if total_reports < min_class_reps_for_aggregation


# Canonical SU Education Council theme taxonomy (2025/26).
# (theme_name, priority_weight, keyword_regex)
_THEME_TAXONOMY: tuple[tuple[str, float, str], ...] = (
    ("ASSESSMENT", 1.0, r"\bassessment|\bexam|\bgrade|\bmark|\bplagiarism|\bdeadline|\bsubmission"),
    ("CONTENT", 0.7, r"\bcontent|\bcurriculum|\bmaterial|\bsyllabus|\breadings?\b|\bslides?\b"),
    ("LECTURER", 0.9, r"\blecturer|\bprofessor|\bteaching|\bdelivery|\bunclear|\bunresponsive"),
    ("ACCESSIBILITY", 1.0, r"\baccessib|\bdisability|\breasonable\s+accommodation|\bcaption|\bscreen\s+reader"),
    ("WELFARE", 0.8, r"\bwelfare|\bmental\s+health|\bstress|\bburnout|\bisolation"),
    ("LOGISTICS", 0.5, r"\btimetable|\broom|\bvenue|\bschedule|\bconflict|\bclash"),
    ("INCLUSION", 0.9, r"\binclusion|\bdiversity|\benglish\s+as\s+a\s+second|\bESL|\binternational"),
)


def aggregate_class_rep_themes(reports: list[ClassRepReport]) -> ThemeAggregation:
    """Aggregate class rep feedback into theme counts (weighted by priority)."""
    total_reports = len(reports)
    total_modules = len({r.module_code for r in reports})

    # Per-module theme tally (for the "modules with multiple concerns" output)
    per_module_themes: dict[str, set[str]] = {}

    # Per-theme weighted total
    theme_counts: Counter[str] = Counter()

    for r in reports:
        text = r.report_text.lower()
        module_themes: set[str] = set()
        for theme_name, weight, pattern in _THEME_TAXONOMY:
            matches = re.findall(pattern, text, flags=re.IGNORECASE)
            if matches:
                # Count each match + apply the priority weight
                theme_counts[theme_name] += int(len(matches) * weight)
                module_themes.add(theme_name)
        per_module_themes[r.module_code] = module_themes

    # Modules that flagged ≥ 3 themes (cross-cutting concern)
    modules_with_multiple_concerns = tuple(
        sorted(m for m, themes in per_module_themes.items() if len(themes) >= 3)
    )

    # Top concerns = themes sorted by weighted count desc
    top_concerns = tuple(name for name, _ in theme_counts.most_common())

    insufficient_data = total_reports < _config.min_class_reps_for_aggregation

    return ThemeAggregation(
        total_reports=total_reports,
        total_modules=total_modules,
        themes=dict(theme_counts),
        top_concerns=top_concerns,
        modules_with_multiple_concerns=modules_with_multiple_concerns,
        insufficient_data=insufficient_data,
    )


# Re-export config so callers can introspect
config = _config
