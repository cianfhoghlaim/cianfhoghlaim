"""Bilingual EN<->GA coverage audit (Plan 2, UC 7 + UC 10).

Per the 2026-08-15-meaisinfoghlaim-ireland-england-roadmap (Plan 2).

The canonical per-cohort bilingual coverage audit. Gates at >= 95%
bilingual coverage per the locked BIEP v3 threshold.

Computes the canonical BilingualCoverageAudit (Pydantic v2) for a cohort:
  - en_topic_count / en_topic_total / en_coverage_pct
  - ga_topic_count / ga_topic_total / ga_coverage_pct
  - bilingual_pairs_found (count from bilingual_concept_registry)
  - gap_topics (topics missing EN or GA coverage)
  - passed_threshold (True iff BOTH en_pct and ga_pct >= 0.95)

Generalisable: same audit works for Wales (EN/CY) + Scotland (EN/GD)
via the LanguagePair enum.

Consumed by:
  - notebooks/64_meaisin_bilingual_curriculum.py (the bilingual ops dashboard)
  - Plan 5's meaisin_bilingual_coverage Dagster asset
"""

from __future__ import annotations

import logging
from typing import Any

from meaisinfoghlaim.alignment.bilingual_concept_registry import BilingualConceptRegistry
from meaisinfoghlaim.alignment.schema import (
    BilingualCoverageAudit,
    LanguagePair,
    Stage,
)

logger = logging.getLogger(__name__)


class BilingualCoverageAuditor:
    """The canonical bilingual coverage auditor.

    Reads the bilingual_concept_registry + the cohort topic inventory
    + emits the canonical BilingualCoverageAudit row.
    """

    THRESHOLD = 0.95  # BIEP v3 gate (locked 2026-08-15)

    def __init__(self, registry: BilingualConceptRegistry | None = None) -> None:
        self.registry = registry or BilingualConceptRegistry()

    def audit(
        self,
        cohort_key: str,
        subject_id: str,
        stage: Stage,
        topic_ids: list[str],
        language_pair: LanguagePair = LanguagePair.EN_GA,
    ) -> BilingualCoverageAudit:
        """Run the bilingual coverage audit for a cohort.

        Args:
            cohort_key: the canonical cohort key (e.g. 'ireland/lc/mathematics/en')
            subject_id: the canonical subject ID
            stage: the canonical Stage enum value
            topic_ids: the list of topic_ids in the cohort (the syllabus's
                module_topics array)
            language_pair: default en-ga

        Returns:
            BilingualCoverageAudit with computed en_pct + ga_pct + passed_threshold
        """
        import uuid as _uuid
        from datetime import datetime as _dt
        from datetime import timezone as _tz

        # 1. Look up the bilingual pairs for this (subject, stage)
        concepts = self.registry.get(subject_id, stage.value, language_pair=language_pair)
        concept_index = {c.topic_id: c for c in concepts if c.topic_id}

        # 2. Count bilingual coverage per topic
        en_covered: set[str] = set()
        ga_covered: set[str] = set()
        bilingual_pairs = 0
        for topic_id in topic_ids:
            pair = concept_index.get(topic_id)
            if pair is None:
                continue
            if pair.en_term:
                en_covered.add(topic_id)
            if pair.ga_term:
                ga_covered.add(topic_id)
            bilingual_pairs += 1

        # 3. Identify gap topics (missing either EN or GA coverage)
        gap_topics = [
            t for t in topic_ids
            if t in concept_index and (t not in en_covered or t not in ga_covered)
        ]

        # 4. Build the audit
        audit = BilingualCoverageAudit(
            audit_id=str(_uuid.uuid4()),
            cohort_key=cohort_key,
            language_pair=language_pair,
            en_topic_count=len(en_covered),
            en_topic_total=len(topic_ids),
            ga_topic_count=len(ga_covered),
            ga_topic_total=len(topic_ids),
            bilingual_pairs_found=bilingual_pairs,
            gap_topics=gap_topics,
        )
        logger.info(
            "Bilingual coverage for %s (%s): en=%.1f%%, ga=%.1f%%, pairs=%d, gaps=%d, passed=%s",
            cohort_key, language_pair.value,
            audit.en_coverage_pct * 100,
            audit.ga_coverage_pct * 100,
            audit.bilingual_pairs_found,
            len(audit.gap_topics),
            audit.passed_threshold,
        )
        return audit


__all__ = ["BilingualCoverageAuditor", "BilingualCoverageAudit"]
