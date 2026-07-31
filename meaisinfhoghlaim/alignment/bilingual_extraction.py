"""Bilingual extraction orchestrator (Plan 2 UC 7).

Per the 2026-08-15-meaisinfoghlaim-ireland-england-roadmap (Plan 2).
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from meaisinfoghlaim.alignment.bilingual_concept_registry import (
    BilingualConceptRegistry,
    LanguagePair,
)
from meaisinfoghlaim.alignment.cross_linguistic import (
    ExtractCrossLinguisticHandler,
)
from meaisinfoghlaim.alignment.schema import (
    BilingualConcept,
    Stage,
)

logger = logging.getLogger(__name__)


class BilingualExtractionOrchestrator:
    """The canonical bilingual EN<->GA extraction orchestrator."""

    def __init__(
        self,
        handler=None,
        registry=None,
    ):
        self.handler = handler or ExtractCrossLinguisticHandler()
        self.registry = registry or BilingualConceptRegistry()

    async def run_for_cohort(
        self,
        cohort_key: str,
        subject_id: str,
        stage: Stage,
        page_text: str,
        topic_id=None,
        language_pair=LanguagePair.EN_GA,
        operator_curated_pairs=None,
    ):
        """Run the bilingual extraction for one cohort."""
        baml_concepts = await self.handler.extract(
            page_text=page_text,
            subject=subject_id,
            topic_id=topic_id,
            language_pair=language_pair,
        )

        registry_rows = self.handler.merge_into_bilingual_registry(
            concepts=baml_concepts,
            cohort_key=cohort_key,
            subject_id=subject_id,
            stage=stage,
            topic_id=topic_id,
        )

        for row in registry_rows:
            try:
                concept = BilingualConcept(
                    pair_id=row["pair_id"],
                    en_term=row["en_term"],
                    ga_term=row["ga_term"],
                    definition_en=row.get("definition_en"),
                    definition_ga=row.get("definition_ga"),
                    language_pair=LanguagePair(row["language_pair"]),
                    subject_id=row["subject_id"],
                    stage=Stage(row["stage"]),
                    topic_id=row.get("topic_id"),
                    confidence=row["confidence"],
                    source_url=row.get("source_url"),
                    extraction_method="baml",
                )
                self.registry.upsert(concept, subject_id, stage.value)
            except Exception as exc:
                logger.warning(
                    "Skipping invalid bilingual concept %s/%s: %s",
                    row.get("en_term"), row.get("ga_term"), exc,
                )

        if operator_curated_pairs:
            self.registry.upsert_many(operator_curated_pairs, subject_id, stage.value)

        return self.registry.get(subject_id, stage.value, topic_id=topic_id)


__all__ = [
    "BilingualExtractionOrchestrator",
    "BilingualConcept",
    "LanguagePair",
    "Stage",
]
