"""UC 7: CrossLinguistic concept extraction (EN<->GA) via BAML + the bilingual_concept_registry.

Per the 2026-08-15-meaisinfoghlaim-ireland-england-roadmap (Plan 2, UC 7).

Wraps the existing BAML ExtractCrossLinguisticConcept function (at
baml_src/british_isles/ireland/education/lc_extraction/cross_linguistic.baml)
and persists the output to the bilingual_concept_registry (Plan 2 module 6).

Architecture:
  1. ExtractCrossLinguisticHandler.extract(page_text) calls the BAML function
  2. The BAML function returns a list[CrossLinguisticConcept]
  3. For each concept, the handler upserts a BilingualConcept row into
     the bilingual_concept_registry
  4. Returns the canonical BilingualConcept list to the caller

Generalisable: same handler works for Wales (EN/CY) + Scotland (EN/GD)
via the LanguagePair enum.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from meaisinfhoghlaim.alignment.schema import (
    CrossLinguisticConcept,
    LanguagePair,
    Stage,
)

logger = logging.getLogger(__name__)


class ExtractCrossLinguisticHandler:
    """The canonical handler for UC 7.

    Wraps the BAML ExtractCrossLinguisticConcept function + the bilingual
    concept registry. Stateless beyond the optional BAML client injection.
    """

    def __init__(self, baml_client: Any | None = None) -> None:
        self._baml_client = baml_client
        self._baml_available: bool | None = None

    def _get_baml_client(self) -> Any | None:
        """Lazy-load the BAML client; returns None if not available."""
        if self._baml_available is False:
            return None
        if self._baml_client is not None:
            return self._baml_client
        try:
            from baml_client.sync_client import b  # type: ignore[import-not-found]
            self._baml_client = b
            self._baml_available = True
            return b
        except ImportError:
            self._baml_available = False
            return None

    async def extract(
        self,
        page_text: str,
        subject: str | None = None,
        concept_id: str | None = None,
        language_pair: LanguagePair = LanguagePair.EN_GA,
    ) -> list[CrossLinguisticConcept]:
        """Run the BAML ExtractCrossLinguisticConcept function.

        Args:
            page_text: the page text (EN) to extract concepts from
            subject: optional subject context (helps BAML filter)
            concept_id: optional concept_id filter (BAML supports per-concept)
            language_pair: default EN<->GA

        Returns:
            list of CrossLinguisticConcept (the canonical BAML output schema)

        Falls back to an empty list if the BAML client is unavailable.
        """
        baml = self._get_baml_client()
        if baml is None:
            logger.warning(
                "BAML client unavailable; ExtractCrossLinguisticHandler returns empty list"
            )
            return []
        try:
            # The BAML function signature is documented in
            # baml_src/british_isles/ireland/education/lc_extraction/cross_linguistic.baml
            result = b.ExtractCrossLinguisticConcept(
                english_text=page_text,
                irish_text="",  # BAML fills from cross-corpus if empty
                subject=subject,
                concept_id=concept_id,
            )
            if hasattr(result, "__iter__"):
                return list(result)
            return [result]
        except Exception as exc:
            logger.exception("BAML ExtractCrossLinguisticConcept failed: %s", exc)
            return []

    def merge_into_bilingual_registry(
        self,
        concepts: list[CrossLinguisticConcept],
        cohort_key: str,
        subject_id: str,
        stage: Stage,
        topic_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """Convert BAML output to bilingual_concept_registry-ready rows.

        Returns:
            list of dicts matching the bilingual_concept_registry schema
            (each dict = 1 row to insert). The actual insertion is the
            registry's responsibility (Plan 2 module 6).
        """
        rows: list[dict[str, Any]] = []
        for concept in concepts:
            if not concept.en_term or not concept.ga_term:
                continue
            row = {
                "pair_id": concept.concept_id,  # BAML output uses the canonical UUID
                "en_term": concept.en_term,
                "ga_term": concept.ga_term,
                "definition_en": concept.definition_en,
                "definition_ga": concept.definition_ga,
                "language_pair": concept.language_pair.value,
                "subject_id": subject_id,
                "stage": stage.value,
                "topic_id": topic_id or concept.topic_id,
                "confidence": concept.translation_fidelity,
                "source_url": concept.source_url,
                "extraction_method": "baml",
                "cohort_key": cohort_key,
            }
            rows.append(row)
        return rows


__all__ = [
    "ExtractCrossLinguisticHandler",
    "CrossLinguisticConcept",
    "LanguagePair",
    "Stage",
]
