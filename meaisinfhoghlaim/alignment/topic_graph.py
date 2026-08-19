"""UC 3: TopicGraph + BilingualTopicEdge builder.

Per the 2026-08-15-meaisinfoghlaim-ireland-england-roadmap (Plan 2, UC 3 +
UC 7 bilingual extension).

Builds:
  - TopicGraphEdge: per-subject topic graph edges (UC 3)
  - BilingualTopicEdge: per-subject topic graph edges with the language_pair
    dimension + anchored_pair_id bridge to the bilingual_concept_registry
    (UC 7)

Generalisable: same edge-builder works for any (jurisdiction, stage,
subject, board) cohort. The bilingual_topic_edges table is consumed by
Plan 5's notebooks/64_meaisin_bilingual_curriculum.py + the
meaisin_bilingual_coverage Dagster asset.

Architecture:
  - TopicGraphBuilder builds the monolingual topic graph (UC 3) from a
    cohort's syllabus documents + BAML ExtractCurriculumSyllabus output
  - BilingualTopicGraphBuilder extends the monolingual builder with the
    language_pair dimension + the bilingual_concept_registry anchors
    (UC 7 + Plan 2)
"""

from __future__ import annotations

import logging
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Iterable

from meaisinfhoghlaim.alignment.schema import (
    BilingualTopicEdge,
    LanguagePair,
    TopicGraphEdge,
)

logger = logging.getLogger(__name__)


class TopicGraphBuilder:
    """The canonical per-subject topic graph builder.

    Stateless beyond an internal cache; reuse across cohorts.
    """

    def __init__(self) -> None:
        self._cache: dict[str, list[TopicGraphEdge]] = {}

    async def build(
        self,
        cohort_key: str,
        syllabus_doc: dict[str, Any],
    ) -> list[TopicGraphEdge]:
        """Build the topic graph edges from a BAML ExtractCurriculumSyllabus output.

        Args:
            cohort_key: the canonical cohort key
            syllabus_doc: the BAML ExtractCurriculumSyllabus output dict
                (has module_topics array)

        Returns:
            list of TopicGraphEdge (1 per (topic_a, topic_b, weight) tuple)
        """
        if cohort_key in self._cache:
            return self._cache[cohort_key]

        # Extract the topics from the syllabus doc
        topics = syllabus_doc.get("module_topics", [])
        topic_ids = [t.get("topic_id") for t in topics if t.get("topic_id")]

        # Build edges: connect each topic to its prerequisites (per the
        # syllabus's prerequisites array), with weight = 1.0 for hard
        # prerequisites + 0.5 for soft prerequisites.
        edges: list[TopicGraphEdge] = []
        idx = 0
        for topic in topics:
            topic_id = topic.get("topic_id")
            if not topic_id:
                continue
            for prereq in topic.get("prerequisites", []):
                prereq_id = prereq.get("topic_id")
                if not prereq_id:
                    continue
                idx += 1
                weight = 1.0 if prereq.get("type") == "hard" else 0.5
                edge_type = (
                    "prerequisite" if prereq.get("type") == "hard"
                    else prereq.get("type", "related")
                )
                try:
                    edge = TopicGraphEdge(
                        edge_id=f"edge-{cohort_key}-{idx}",
                        cohort_key=cohort_key,
                        topic_a=prereq_id,
                        topic_b=topic_id,
                        weight=weight,
                        edge_type=edge_type if edge_type in ("prerequisite", "related", "extension") else "related",
                    )
                    edges.append(edge)
                except Exception as exc:
                    logger.warning(
                        "Skipping invalid topic edge (%s -> %s): %s",
                        prereq_id, topic_id, exc,
                    )

        # Also build edges between consecutive topics within a module
        # (treated as "extension" edges with weight 0.4)
        topics_by_module = defaultdict(list)
        for topic in topics:
            mod = topic.get("module_id")
            if mod:
                topics_by_module[mod].append(topic.get("topic_id"))
        for mod_id, mod_topics in topics_by_module.items():
            for i in range(len(mod_topics) - 1):
                idx += 1
                try:
                    edge = TopicGraphEdge(
                        edge_id=f"edge-{cohort_key}-{idx}",
                        cohort_key=cohort_key,
                        topic_a=mod_topics[i],
                        topic_b=mod_topics[i + 1],
                        weight=0.4,
                        edge_type="extension",
                    )
                    edges.append(edge)
                except Exception as exc:
                    logger.warning(
                        "Skipping extension edge (%s -> %s): %s",
                        mod_topics[i], mod_topics[i + 1], exc,
                    )

        self._cache[cohort_key] = edges
        logger.info(
            "Built %d topic graph edges for cohort=%s", len(edges), cohort_key
        )
        return edges


class BilingualTopicGraphBuilder:
    """The bilingual extension of TopicGraphBuilder (UC 3 + UC 7).

    Takes a TopicGraphBuilder + a bilingual_concept_registry + a cohort,
    and emits BilingualTopicEdge rows with the language_pair dimension.
    """

    def __init__(self) -> None:
        self._cache: dict[str, list[BilingualTopicEdge]] = {}

    async def build(
        self,
        cohort_key: str,
        topic_edges: list[TopicGraphEdge],
        concept_pairs: list,  # list[BilingualConcept] from bilingual_concept_registry
        language_pair: LanguagePair = LanguagePair.EN_GA,
    ) -> list[BilingualTopicEdge]:
        """Build the bilingual topic graph edges.

        For each TopicGraphEdge in topic_edges:
          - Look up concept pairs in concept_pairs whose en_term or
            ga_term matches the topic_id of either endpoint
          - If found, emit a BilingualTopicEdge anchored by the pair_id

        Args:
            cohort_key: the canonical cohort key
            topic_edges: the output of TopicGraphBuilder.build(cohort_key, ...)
            concept_pairs: list of BilingualConcept (from bilingual_concept_registry)
            language_pair: the language pair dimension (default en-ga)

        Returns:
            list of BilingualTopicEdge (1 per matching concept pair per topic edge)
        """
        if cohort_key in self._cache:
            return self._cache[cohort_key]

        # Build an index: topic_id (lower-cased term) -> BilingualConcept
        concept_index: dict[str, Any] = {}
        for pair in concept_pairs:
            if pair.en_term:
                concept_index[pair.en_term.lower()] = pair
            if pair.ga_term:
                concept_index[pair.ga_term.lower()] = pair

        edges: list[BilingualTopicEdge] = []
        idx = 0
        for topic_edge in topic_edges:
            pair_a = concept_index.get(topic_edge.topic_a.lower())
            pair_b = concept_index.get(topic_edge.topic_b.lower())
            if pair_a is None and pair_b is None:
                continue  # no concept anchor; emit nothing
            anchored_pair = pair_a or pair_b
            idx += 1
            try:
                edge = BilingualTopicEdge(
                    edge_id=f"biedge-{cohort_key}-{idx}",
                    cohort_key=cohort_key,
                    topic_a=topic_edge.topic_a,
                    topic_b=topic_edge.topic_b,
                    weight=topic_edge.weight,
                    language_pair=language_pair,
                    anchored_pair_id=anchored_pair.pair_id if anchored_pair else None,
                    edge_type=topic_edge.edge_type,
                )
                edges.append(edge)
            except Exception as exc:
                logger.warning(
                    "Skipping invalid bilingual topic edge (%s <-> %s): %s",
                    topic_edge.topic_a, topic_edge.topic_b, exc,
                )

        self._cache[cohort_key] = edges
        logger.info(
            "Built %d bilingual topic graph edges for cohort=%s (language_pair=%s)",
            len(edges), cohort_key, language_pair.value,
        )
        return edges


__all__ = [
    "TopicGraphBuilder",
    "BilingualTopicGraphBuilder",
    "TopicGraphEdge",
    "BilingualTopicEdge",
]
