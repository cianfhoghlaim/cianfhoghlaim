"""UC cross-qual: CrossQualificationGapAnalyzerRuntime (Plan 3).

Per the 2026-08-15-meaisinfhoghlaim-ireland-england-roadmap (Plan 3).

The runtime gap analyzer. Given (qualification_a, jurisdiction_a, subject_a),
finds topics NOT covered by any equivalent (qualification_b, jurisdiction_b,
subject_b).

Generalisable: same analyzer works for Scotland / Wales / NI / Jersey /
Guernsey / IoM rollouts.

Output: list of CrossQualificationGap rows (one per gap topic).
"""

from __future__ import annotations

import logging
from typing import Any

from meaisinfhoghlaim.alignment.cross_qualification_subject_map import CrossQualificationSubjectMap
from meaisinfhoghlaim.alignment.cross_qualification_topic_alignment import (
    CrossQualificationTopicAligner,
)
from meaisinfhoghlaim.alignment.schema import (
    CrossQualificationGap,
    QualificationLevel,
)

logger = logging.getLogger(__name__)


class CrossQualificationGapAnalyzerRuntime:
    """The canonical runtime cross-qualification gap analyzer.

    Takes a (qualification_a, jurisdiction_a, subject_a, topics_a) tuple +
    queries the cross_qualification_subject_map + cross_qualification_topic_aligner
    + emits CrossQualificationGap rows for every gap topic.
    """

    def __init__(
        self,
        subject_map: CrossQualificationSubjectMap | None = None,
        topic_aligner: CrossQualificationTopicAligner | None = None,
    ) -> None:
        self.subject_map = subject_map or CrossQualificationSubjectMap()
        self.topic_aligner = topic_aligner or CrossQualificationTopicAligner()

    def analyze(
        self,
        qualification_a: QualificationLevel,
        jurisdiction_a: str,
        subject_a: str,
        topics_a: list[str],
    ) -> list[CrossQualificationGap]:
        """Find topics in qualification_a NOT covered by any equivalent.

        Args:
            qualification_a, jurisdiction_a, subject_a: the source cohort
            topics_a: the list of topic_ids in qualification_a

        Returns:
            list of CrossQualificationGap rows (1 per gap topic)
        """
        import uuid as _uuid
        from datetime import datetime as _dt
        from datetime import timezone as _tz

        # 1. Find all equivalences for this source cohort
        equivalences = self.subject_map.all()
        matching = [
            e for e in equivalences
            if e.qualification_a == qualification_a
            and e.jurisdiction_a == jurisdiction_a
            and e.subject_a == subject_a
            and e.equivalence_strength >= 0.5  # only count strong equivalences
        ]

        if not matching:
            # No equivalences -> all topics are gaps
            candidate_quals = [q.value for q in QualificationLevel]
            return [
                CrossQualificationGap(
                    gap_id=str(_uuid.uuid4()),
                    qualification_a=qualification_a,
                    jurisdiction_a=jurisdiction_a,
                    subject_a=subject_a,
                    topic_id=t,
                    candidate_qualifications=candidate_quals,
                    severity="high",
                )
                for t in topics_a
            ]

        # 2. For each topic, check if any equivalent covers it
        # (via cross_qualification_topic_aligner + subject_map)
        gaps: list[CrossQualificationGap] = []
        candidate_quals = sorted({e.qualification_b.value for e in matching})

        for topic_id in topics_a:
            covered = False
            for equiv in matching:
                # Check if this topic is aligned with any topic in qualification_b
                # For Plan 3 v1: heuristic via topic_aligner.align_one
                # (the aligner uses the bilingual_registry; we pass empty topics_b
                # because we don't have the equiv side's topics here; future v2
                # would inject them).
                try:
                    alignment = self.topic_aligner.align_one(
                        topic_id, qualification_a, jurisdiction_a,
                        f"placeholder_{equiv.subject_b}", equiv.qualification_b,
                        equiv.jurisdiction_b,
                    )
                    if alignment is not None and alignment.alignment_score > 0.5:
                        covered = True
                        break
                except Exception:
                    continue
            if not covered:
                # Infer severity by equivalence_strength
                max_strength = max(e.equivalence_strength for e in matching)
                severity = "high" if max_strength >= 0.8 else "medium" if max_strength >= 0.6 else "low"
                gaps.append(
                    CrossQualificationGap(
                        gap_id=str(_uuid.uuid4()),
                        qualification_a=qualification_a,
                        jurisdiction_a=jurisdiction_a,
                        subject_a=subject_a,
                        topic_id=topic_id,
                        candidate_qualifications=candidate_quals,
                        severity=severity,
                    )
                )

        logger.info(
            "Cross-qual gap analysis for %s/%s/%s: %d gaps found (out of %d topics)",
            jurisdiction_a, qualification_a.value, subject_a, len(gaps), len(topics_a),
        )
        return gaps


__all__ = ["CrossQualificationGapAnalyzerRuntime", "CrossQualificationGap", "QualificationLevel"]
