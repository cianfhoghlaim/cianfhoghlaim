"""Cross-jurisdiction diff (Ireland <-> England).

Per the 2026-08-15-meaisinfoghlaim-ireland-england-roadmap (Plan 3, UC 4).

Compares a (qualification, jurisdiction, subject) tuple to the
equivalent (qualification, jurisdiction, subject) tuple and emits
structural diffs (topic-level alignment + equivalence_strength).

Generalisable to Scotland (Nat 5 / Higher / Adv Higher) + Wales (EN/CY) +
NI (CCEA) later.
"""

from __future__ import annotations

import logging
from typing import Any

from meaisinfoghlaim.alignment.cross_qualification_topic_alignment import (
    CrossQualificationTopicAligner,
)
from meaisinfoghlaim.alignment.qualification_normalizer import QualificationNormalizer
from meaisinfoghlaim.alignment.schema import (
    CrossJurisdictionDiff,
    QualificationLevel,
)

logger = logging.getLogger(__name__)


class CrossJurisdictionDiffer:
    """The canonical cross-jurisdiction differ."""

    def __init__(
        self,
        normalizer: QualificationNormalizer | None = None,
        topic_aligner: CrossQualificationTopicAligner | None = None,
    ) -> None:
        self.normalizer = normalizer or QualificationNormalizer()
        self.topic_aligner = topic_aligner or CrossQualificationTopicAligner()

    def diff(
        self,
        qualification_a: QualificationLevel,
        jurisdiction_a: str,
        subject_a: str,
        qualification_b: QualificationLevel,
        jurisdiction_b: str,
        subject_b: str,
        topics_a: list[str] | None = None,
        topics_b: list[str] | None = None,
    ) -> CrossJurisdictionDiff:
        """Diff 2 (qualification, jurisdiction, subject) tuples.

        Args:
            qualification_a, jurisdiction_a, subject_a: the first cohort
            qualification_b, jurisdiction_b, subject_b: the second cohort
            topics_a: the list of topic_ids for cohort_a (optional; uses placeholder if None)
            topics_b: the list of topic_ids for cohort_b (optional; uses placeholder if None)

        Returns:
            CrossJurisdictionDiff with alignment_pct + equivalence_id
        """
        import uuid as _uuid
        from datetime import datetime as _dt
        from datetime import timezone as _tz

        # 1. Find the equivalence
        equivalences = self.normalizer.normalize(qualification_a, jurisdiction_a, subject_a)
        matched_equiv = None
        for equiv in equivalences:
            if (
                equiv.qualification_b == qualification_b
                and equiv.jurisdiction_b == jurisdiction_b
                and equiv.subject_b == subject_b
            ):
                matched_equiv = equiv
                break

        # 2. Use placeholder topics if not provided
        if topics_a is None:
            topics_a = [f"placeholder_topic_a_{i}" for i in range(5)]
        if topics_b is None:
            topics_b = [f"placeholder_topic_b_{i}" for i in range(5)]

        # 3. Compute per-topic alignment (using topic_aligner)
        aligned_count = 0
        for topic_a in topics_a:
            for topic_b in topics_b:
                alignment = self.topic_aligner.align_one(
                    topic_a, qualification_a, jurisdiction_a,
                    topic_b, qualification_b, jurisdiction_b,
                )
                if alignment is not None and alignment.alignment_score > 0.5:
                    aligned_count += 1
                    break  # one matched alignment is enough per topic_a
        total_a = len(topics_a)
        total_b = len(topics_b)
        max_total = max(total_a, total_b)
        alignment_pct = aligned_count / max_total if max_total > 0 else 0.0

        return CrossJurisdictionDiff(
            diff_id=str(_uuid.uuid4()),
            qualification_a=qualification_a,
            jurisdiction_a=jurisdiction_a,
            subject_a=subject_a,
            qualification_b=qualification_b,
            jurisdiction_b=jurisdiction_b,
            subject_b=subject_b,
            equivalence_id=matched_equiv.map_id if matched_equiv else None,
            topic_count_a=total_a,
            topic_count_b=total_b,
            aligned_topic_count=aligned_count,
            alignment_pct=round(alignment_pct, 4),
        )


__all__ = ["CrossJurisdictionDiffer", "CrossJurisdictionDiff", "QualificationLevel"]
