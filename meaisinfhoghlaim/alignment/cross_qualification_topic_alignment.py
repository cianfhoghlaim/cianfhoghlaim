"""Per-topic cross-qualification alignment (Plan 3 UC cross-qual).

Per the 2026-08-15-meaisinfoghlaim-ireland-england-roadmap (Plan 3).

Builds the canonical CrossQualificationTopicAlignment rows (1 row per
matching topic_id pair across 2 qualifications). Bridges:
  - ``qualification_a`` + ``topic_a`` (e.g. LC algebra)
  - ``qualification_b`` + ``topic_b`` (e.g. A-Level algebra)

Uses the bilingual_concept_registry (Plan 2 module 6) as the source of
common concept pairs to derive the alignment_score.

Generalisable: same aligner works for Scotland / Wales / NI rollouts.
"""

from __future__ import annotations

import logging
from typing import Any

from meaisinfhoghlaim.alignment.bilingual_concept_registry import BilingualConceptRegistry
from meaisinfhoghlaim.alignment.schema import (
    CrossQualificationTopicAlignment,
    QualificationLevel,
)

logger = logging.getLogger(__name__)


class CrossQualificationTopicAligner:
    """The canonical per-topic cross-qualification aligner."""

    def __init__(
        self,
        bilingual_registry: BilingualConceptRegistry | None = None,
    ) -> None:
        self.bilingual_registry = bilingual_registry or BilingualConceptRegistry()

    def align_one(
        self,
        topic_a: str,
        qualification_a: QualificationLevel,
        jurisdiction_a: str,
        topic_b: str,
        qualification_b: QualificationLevel,
        jurisdiction_b: str,
    ) -> CrossQualificationTopicAlignment | None:
        """Align a single topic pair across 2 qualifications.

        Uses the bilingual concept registry to find common concepts between
        topic_a + topic_b (via the bilingual_concept_registry entries that
        bridge them). Returns the alignment score (0.0-1.0).

        Returns None if no common concepts found.
        """
        import uuid as _uuid
        from datetime import datetime as _dt
        from datetime import timezone as _tz

        # 1. Find common concepts between topic_a + topic_b
        # by looking up the bilingual_registry for concepts in either topic.
        # (Simplified heuristic for Plan 3 v1; a real implementation would
        # use BAML ExtractCrossLinguisticConcept + topic embedding similarity.)
        concepts_a = self.bilingual_registry.get(jurisdiction_a, qualification_a.value)
        concepts_b = self.bilingual_registry.get(jurisdiction_b, qualification_b.value)
        common_pairs = []
        for ca in concepts_a:
            if ca.topic_id != topic_a:
                continue
            for cb in concepts_b:
                if cb.topic_id != topic_b:
                    continue
                # Same en_term or same ga_term => aligned
                if ca.en_term and ca.en_term == cb.en_term:
                    common_pairs.append(ca.pair_id)
                elif ca.ga_term and ca.ga_term == cb.ga_term:
                    common_pairs.append(ca.pair_id)

        if not common_pairs:
            return None

        # 2. Compute alignment score as a function of # common concepts
        # (cap at 1.0)
        score = min(1.0, len(common_pairs) * 0.25 + 0.25)
        return CrossQualificationTopicAlignment(
            alignment_id=str(_uuid.uuid4()),
            qualification_a=qualification_a,
            jurisdiction_a=jurisdiction_a,
            topic_a=topic_a,
            qualification_b=qualification_b,
            jurisdiction_b=jurisdiction_b,
            topic_b=topic_b,
            alignment_score=round(score, 4),
            common_concepts_json=str(common_pairs),
        )

    def align_all(
        self,
        qualification_a: QualificationLevel,
        jurisdiction_a: str,
        topics_a: list[str],
        qualification_b: QualificationLevel,
        jurisdiction_b: str,
        topics_b: list[str],
    ) -> list[CrossQualificationTopicAlignment]:
        """Align all topic pairs (cartesian product)."""
        out: list[CrossQualificationTopicAlignment] = []
        for ta in topics_a:
            for tb in topics_b:
                alignment = self.align_one(
                    ta, qualification_a, jurisdiction_a,
                    tb, qualification_b, jurisdiction_b,
                )
                if alignment is not None:
                    out.append(alignment)
        return out


__all__ = ["CrossQualificationTopicAligner", "CrossQualificationTopicAlignment", "QualificationLevel"]
