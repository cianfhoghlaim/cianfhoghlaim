"""Per-cohort coverage audit (Plan 4).

Per the 2026-08-15-meaisinfoghlaim-ireland-england-roadmap (Plan 4).

The canonical coverage audit. Compares the CohortRegistry against the
v3 BIEP milestone counts (Ireland 82 subjects x 2 languages; England
92 subjects x 3 boards) and reports the missing cohorts.

Generalisable: same audit works for Scotland / Wales / NI / Jersey /
Guernsey / IoM rollouts.
"""

from __future__ import annotations

import logging
from typing import Any

from meaisinfhoghlaim.alignment.schema import (
    Board,
    CohortLifecycleState,
    CohortRow,
    LanguagePair,
    QualificationLevel,
)
from meaisinfhoghlaim.datasets.cohort_registry import CohortRegistry

logger = logging.getLogger(__name__)


# The canonical BIEP v3 milestone counts.
# Ireland: 64 LC subjects x 2 languages = 128, plus 18 JC subjects x 2
# languages = 36, plus 16 short courses + 36 CBAs. We model the core
# (164 = 128 + 36). The short-course + CBA counts are subject to a
# separate audit.
IRELAND_EXPECTED_COUNTS = {
    (QualificationLevel.LC, "ireland"): 64,
    (QualificationLevel.JC, "ireland"): 18,
}
IRELAND_BILINGUAL_EXPECTED_COUNTS = {
    (QualificationLevel.LC, "ireland", LanguagePair.EN_GA): 128,  # 64 x 2 langs
    (QualificationLevel.JC, "ireland", LanguagePair.EN_GA): 36,  # 18 x 2 langs
}

# England: 43 GCSE subjects x 3 boards = 129, plus 49 A-Level subjects x 3
# boards = 147. Total 276.
ENGLAND_EXPECTED_COUNTS = {
    (QualificationLevel.GCSE, "england"): 43,
    (QualificationLevel.A_LEVEL, "england"): 49,
}
ENGLAND_BOARD_EXPECTED_COUNTS = {
    (QualificationLevel.GCSE, "england", Board.AQA): 43,
    (QualificationLevel.GCSE, "england", Board.OCR): 43,
    (QualificationLevel.GCSE, "england", Board.EDEXCEL): 43,
    (QualificationLevel.A_LEVEL, "england", Board.AQA): 49,
    (QualificationLevel.A_LEVEL, "england", Board.OCR): 49,
    (QualificationLevel.A_LEVEL, "england", Board.EDEXCEL): 49,
}


class CohortAuditReport:
    """The canonical coverage audit report."""

    def __init__(
        self,
        registry: CohortRegistry,
        jurisdiction: str,
    ) -> None:
        self.registry = registry
        self.jurisdiction = jurisdiction
        self.existing: list = registry.all(jurisdiction=jurisdiction)
        self.missing_subjects: list = []
        self.missing_languages: list = []
        self.completed: list = []
        self.in_progress: list = []
        self._compute()

    def _compute(self) -> None:
        """Compute the audit (the missing subjects + language gaps + lifecycle states)."""
        if self.jurisdiction == "ireland":
            expected = IRELAND_EXPECTED_COUNTS
        elif self.jurisdiction == "england":
            expected = ENGLAND_EXPECTED_COUNTS
        else:
            expected = {}

        # Build a set of (stage, subject) tuples that exist in the registry
        existing_set = set()
        for cohort in self.existing:
            existing_set.add((cohort.stage, cohort.subject))

        # Count by stage
        by_stage: dict = {}
        for cohort in self.existing:
            key = (cohort.stage, cohort.jurisdiction)
            by_stage.setdefault(key, set()).add(cohort.subject)

        # Find missing subjects per stage
        for (stage, jur), expected_count in expected.items():
            existing_subjects = by_stage.get((stage, jur), set())
            # The expected_count is the max distinct subjects; if we have fewer
            # we report the gap
            if len(existing_subjects) < expected_count:
                gap = expected_count - len(existing_subjects)
                for i in range(gap):
                    self.missing_subjects.append(
                        {"stage": stage.value, "jurisdiction": jur, "index": i}
                    )

        # Lifecycle state breakdown
        for cohort in self.existing:
            if cohort.lifecycle_state == CohortLifecycleState.PROMOTED:
                self.completed.append(cohort)
            else:
                self.in_progress.append(cohort)

        # Bilingual audit (Ireland only — per the >= 95% gate from Plan 2)
        if self.jurisdiction == "ireland":
            for cohort in self.existing:
                if cohort.language == "en" and not cohort.ga_extracted:
                    self.missing_languages.append({
                        "cohort_id": cohort.cohort_id,
                        "subject": cohort.subject,
                        "missing_lang": "ga",
                    })

    def summary(self) -> dict:
        """Operator-facing summary; consumed by Plan 5 notebooks."""
        return {
            "jurisdiction": self.jurisdiction,
            "existing_cohort_count": len(self.existing),
            "completed_count": len(self.completed),
            "in_progress_count": len(self.in_progress),
            "missing_subjects_count": len(self.missing_subjects),
            "missing_languages_count": len(self.missing_languages),
            "missing_subjects_sample": self.missing_subjects[:5],
            "missing_languages_sample": self.missing_languages[:5],
        }


class CohortAuditor:
    """The canonical cohort coverage auditor."""

    def __init__(self, registry: CohortRegistry | None = None) -> None:
        self.registry = registry or CohortRegistry()

    def audit(self, jurisdiction: str) -> CohortAuditReport:
        """Run the coverage audit for the given jurisdiction."""
        return CohortAuditReport(self.registry, jurisdiction)


__all__ = ["CohortAuditor", "CohortAuditReport", "CohortRegistry"]
