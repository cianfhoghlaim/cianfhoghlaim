"""
Learning Outcome Graph Flow.

Extracts semantic relationships between learning outcomes using LLM analysis.
Creates a knowledge graph for learning path generation and curriculum navigation.

Relationships extracted:
- PREREQUISITE_FOR: LO A must be learned before LO B
- BUILDS_ON: LO B extends concepts from LO A
- ASSESSES: LO assesses specific skills
- RELATED_TO: LOs share conceptual overlap
- PART_OF: LO is part of larger competency

Uses BAML for type-safe LLM extraction.
"""

import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

import structlog

logger = structlog.get_logger(__name__)

# Default configuration
DEFAULT_MEMGRAPH_URI = os.getenv("MEMGRAPH_URI", "bolt://localhost:7687")
DEFAULT_DUCKDB_PATH = os.getenv(
    "OIDEACHAS_DUCKDB_PATH",
    "./storage/data/celtic_education.duckdb"
)


class RelationshipType(str, Enum):
    """Types of relationships between learning outcomes."""
    PREREQUISITE_FOR = "PREREQUISITE_FOR"
    BUILDS_ON = "BUILDS_ON"
    ASSESSES = "ASSESSES"
    RELATED_TO = "RELATED_TO"
    PART_OF = "PART_OF"
    ENABLES = "ENABLES"
    CONTRASTS_WITH = "CONTRASTS_WITH"


@dataclass
class LearningOutcomeRelation:
    """A relationship between two learning outcomes."""
    source_code: str
    target_code: str
    relationship_type: RelationshipType
    confidence: float
    reasoning: str | None = None
    extracted_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SkillNode:
    """A skill that learning outcomes assess."""
    id: str
    name: str
    category: str
    description: str | None = None


# =============================================================================
# BAML-Based Relationship Extraction
# =============================================================================

class LearningOutcomeExtractor:
    """
    Extract relationships between learning outcomes using LLM.

    Uses BAML for type-safe extraction when available.
    Falls back to direct LLM API calls otherwise.
    """

    def __init__(
        self,
        model: str = "claude-3-5-sonnet-20241022",
        use_baml: bool = True,
    ):
        self.model = model
        self.use_baml = use_baml
        self._baml_client = None

    def _get_baml_client(self):
        """Get BAML client for structured extraction."""
        if self._baml_client is not None:
            return self._baml_client

        try:
            from baml_client import b
            self._baml_client = b
            logger.info("baml_client_loaded")
            return self._baml_client
        except ImportError:
            logger.warning("baml_not_available")
            return None

    async def extract_relationships(
        self,
        source_outcome: dict[str, Any],
        target_outcomes: list[dict[str, Any]],
        subject_context: str = "",
    ) -> list[LearningOutcomeRelation]:
        """
        Extract relationships between a source outcome and potential targets.

        Args:
            source_outcome: The source learning outcome
            target_outcomes: List of candidate target outcomes
            subject_context: Context about the subject area

        Returns:
            List of extracted relationships
        """
        baml = self._get_baml_client()

        if baml is not None and self.use_baml:
            return await self._extract_with_baml(
                source_outcome,
                target_outcomes,
                subject_context,
            )
        else:
            return await self._extract_direct(
                source_outcome,
                target_outcomes,
                subject_context,
            )

    async def _extract_with_baml(
        self,
        source_outcome: dict[str, Any],
        target_outcomes: list[dict[str, Any]],
        subject_context: str,
    ) -> list[LearningOutcomeRelation]:
        """Extract using BAML for type-safe structured output."""
        baml = self._get_baml_client()

        try:
            # Call BAML function (defined in baml/)
            result = await baml.ExtractLearningOutcomeRelationships(
                source_outcome=source_outcome,
                target_outcomes=target_outcomes,
                subject_context=subject_context,
            )

            # Convert BAML output to our dataclass
            relationships = []
            for rel in result.relationships:
                relationships.append(LearningOutcomeRelation(
                    source_code=source_outcome["code"],
                    target_code=rel.target_code,
                    relationship_type=RelationshipType(rel.relationship_type),
                    confidence=rel.confidence,
                    reasoning=rel.reasoning,
                ))

            return relationships

        except (RuntimeError, ValueError, KeyError, ImportError) as e:
            logger.error("baml_extraction_failed", error=str(e))
            return []

    async def _extract_direct(
        self,
        source_outcome: dict[str, Any],
        target_outcomes: list[dict[str, Any]],
        subject_context: str,
    ) -> list[LearningOutcomeRelation]:
        """Extract using direct LLM API call."""
        try:
            import anthropic
        except ImportError:
            logger.error("anthropic_not_installed")
            return []

        client = anthropic.Anthropic()

        # Build prompt
        prompt = self._build_extraction_prompt(
            source_outcome,
            target_outcomes,
            subject_context,
        )

        try:
            response = client.messages.create(
                model=self.model,
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}],
            )

            # Parse response
            return self._parse_extraction_response(
                response.content[0].text,
                source_outcome["code"],
            )

        except (RuntimeError, ValueError, ConnectionError, TimeoutError) as e:
            logger.error("direct_extraction_failed", error=str(e))
            return []

    def _build_extraction_prompt(
        self,
        source: dict[str, Any],
        targets: list[dict[str, Any]],
        context: str,
    ) -> str:
        """Build extraction prompt."""
        target_list = "\n".join([
            f"- {t['code']}: {t.get('description_en', t.get('description', ''))}"
            for t in targets[:10]  # Limit to 10 targets
        ])

        return f"""Analyze the relationships between learning outcomes in {context or 'this curriculum'}.

SOURCE LEARNING OUTCOME:
Code: {source['code']}
Description: {source.get('description_en', source.get('description', ''))}
Subject: {source.get('subject', 'unknown')}
Level: {source.get('difficulty_level', 'unknown')}

POTENTIAL TARGET OUTCOMES:
{target_list}

For each meaningful relationship, identify:
1. Relationship type: PREREQUISITE_FOR, BUILDS_ON, ASSESSES, RELATED_TO, PART_OF, ENABLES, or CONTRASTS_WITH
2. Target outcome code
3. Confidence (0.0-1.0)
4. Brief reasoning

Format as JSON array:
[
  {{"target_code": "...", "relationship_type": "...", "confidence": 0.8, "reasoning": "..."}}
]

Only include relationships with confidence >= 0.6. Return empty array [] if no relationships found."""

    def _parse_extraction_response(
        self,
        response_text: str,
        source_code: str,
    ) -> list[LearningOutcomeRelation]:
        """Parse LLM response into relationships."""
        import json
        import re

        # Find JSON array in response
        json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if not json_match:
            return []

        try:
            data = json.loads(json_match.group())
        except json.JSONDecodeError:
            return []

        relationships = []
        for item in data:
            try:
                rel_type = item.get("relationship_type", "RELATED_TO")
                if rel_type not in [rt.value for rt in RelationshipType]:
                    rel_type = "RELATED_TO"

                relationships.append(LearningOutcomeRelation(
                    source_code=source_code,
                    target_code=item["target_code"],
                    relationship_type=RelationshipType(rel_type),
                    confidence=float(item.get("confidence", 0.7)),
                    reasoning=item.get("reasoning"),
                ))
            except (KeyError, ValueError) as e:
                logger.debug("skipping_invalid_relationship", error=str(e))

        return relationships


# =============================================================================
# Graph Builder
# =============================================================================

class LearningOutcomeGraphBuilder:
    """
    Build and maintain the learning outcome knowledge graph.

    Integrates with existing Memgraph client for storage.
    """

    def __init__(
        self,
        memgraph_uri: str | None = None,
        duckdb_path: str | None = None,
        extractor: LearningOutcomeExtractor | None = None,
    ):
        self.memgraph_uri = memgraph_uri or DEFAULT_MEMGRAPH_URI
        self.duckdb_path = duckdb_path or DEFAULT_DUCKDB_PATH
        self.extractor = extractor or LearningOutcomeExtractor()
        self._graph_client = None

    def _get_graph_client(self):
        """Get Memgraph client."""
        if self._graph_client is not None:
            return self._graph_client

        from ..graph.memgraph_client import MemgraphClient
        from ..storage.config import MemgraphConfig

        config = MemgraphConfig(uri=self.memgraph_uri)
        self._graph_client = MemgraphClient(config)
        return self._graph_client

    def _get_duckdb_connection(self):
        """Get DuckDB connection (single-threaded)."""
        import duckdb
        return duckdb.connect(self.duckdb_path, read_only=True)

    async def build_graph_for_subject(
        self,
        subject_code: str,
        batch_size: int = 10,
    ) -> dict[str, Any]:
        """
        Build relationship graph for all learning outcomes in a subject.

        Args:
            subject_code: Subject code (e.g., 'irish', 'mathematics')
            batch_size: Number of outcomes to process in parallel

        Returns:
            Stats about extracted relationships
        """
        # Load learning outcomes from DuckDB
        conn = self._get_duckdb_connection()
        try:
            outcomes = self._load_outcomes_for_subject(conn, subject_code)
        finally:
            conn.close()

        if not outcomes:
            logger.warning("no_outcomes_found", subject=subject_code)
            return {"subject": subject_code, "outcomes": 0, "relationships": 0}

        logger.info("processing_outcomes", count=len(outcomes), subject=subject_code)

        # Extract relationships
        all_relationships: list[LearningOutcomeRelation] = []

        for i, source_outcome in enumerate(outcomes):
            # Use other outcomes as targets
            targets = [o for o in outcomes if o["code"] != source_outcome["code"]]

            relationships = await self.extractor.extract_relationships(
                source_outcome=source_outcome,
                target_outcomes=targets,
                subject_context=f"Irish {subject_code} curriculum",
            )

            all_relationships.extend(relationships)

            if (i + 1) % 10 == 0:
                logger.info("outcomes_progress", processed=i + 1, total=len(outcomes))

        # Store in Memgraph
        stored = self._store_relationships(all_relationships)

        return {
            "subject": subject_code,
            "outcomes": len(outcomes),
            "relationships": len(all_relationships),
            "stored": stored,
        }

    def _load_outcomes_for_subject(
        self,
        conn,
        subject_code: str,
    ) -> list[dict[str, Any]]:
        """Load learning outcomes from DuckDB."""
        try:
            query = f"""
                SELECT
                    outcome_code as code,
                    description_en,
                    description_ga,
                    subject,
                    level,
                    strand,
                    strand_unit,
                    difficulty_level,
                    curriculum_year
                FROM education.learning_outcomes
                WHERE subject = '{subject_code}'
                  AND description_en IS NOT NULL
            """
            rows = conn.execute(query).fetchall()
            columns = [
                "code", "description_en", "description_ga", "subject",
                "level", "strand", "strand_unit", "difficulty_level", "curriculum_year"
            ]
            return [dict(zip(columns, row)) for row in rows]
        except (RuntimeError, ValueError, OSError) as e:
            logger.warning("load_outcomes_failed", error=str(e))
            return []

    def _store_relationships(
        self,
        relationships: list[LearningOutcomeRelation],
    ) -> int:
        """Store relationships in Memgraph."""
        if not relationships:
            return 0

        client = self._get_graph_client()
        stored = 0

        for rel in relationships:
            try:
                query = f"""
                MATCH (source:LearningOutcome {{code: $source_code}})
                MATCH (target:LearningOutcome {{code: $target_code}})
                MERGE (source)-[r:{rel.relationship_type.value}]->(target)
                SET r.confidence = $confidence,
                    r.reasoning = $reasoning,
                    r.extracted_at = datetime()
                """
                client.execute_write(
                    query,
                    {
                        "source_code": rel.source_code,
                        "target_code": rel.target_code,
                        "confidence": rel.confidence,
                        "reasoning": rel.reasoning,
                    },
                )
                stored += 1
            except (RuntimeError, ConnectionError, OSError) as e:
                logger.debug("store_relationship_failed", error=str(e))

        logger.info("relationships_stored", stored=stored, total=len(relationships))
        return stored

    def close(self):
        """Close connections."""
        if self._graph_client:
            self._graph_client.close()
            self._graph_client = None


# =============================================================================
# Query Methods
# =============================================================================

class LearningPathFinder:
    """
    Find learning paths through the curriculum graph.

    Uses graph algorithms to suggest optimal learning sequences.
    """

    def __init__(self, memgraph_uri: str | None = None):
        self.memgraph_uri = memgraph_uri or DEFAULT_MEMGRAPH_URI
        self._client = None

    def _get_client(self):
        """Get Memgraph client."""
        if self._client is not None:
            return self._client

        from ..graph.memgraph_client import MemgraphClient
        from ..storage.config import MemgraphConfig

        config = MemgraphConfig(uri=self.memgraph_uri)
        self._client = MemgraphClient(config)
        return self._client

    def find_prerequisites(
        self,
        outcome_code: str,
        depth: int = 3,
    ) -> list[dict[str, Any]]:
        """
        Find all prerequisites for a learning outcome.

        Args:
            outcome_code: Target outcome code
            depth: Maximum depth to search

        Returns:
            List of prerequisite outcomes with distances
        """
        client = self._get_client()

        query = f"""
        MATCH path = (prereq:LearningOutcome)-[:PREREQUISITE_FOR*1..{depth}]->(target:LearningOutcome {{code: $code}})
        RETURN DISTINCT
            prereq.code as code,
            prereq.description_en as description,
            prereq.difficulty_level as difficulty,
            length(path) as distance
        ORDER BY distance ASC
        """

        return client.execute(query, {"code": outcome_code})

    def find_learning_sequence(
        self,
        start_code: str,
        end_code: str,
    ) -> list[dict[str, Any]]:
        """
        Find optimal learning sequence from start to end outcome.

        Args:
            start_code: Starting outcome
            end_code: Target outcome

        Returns:
            Ordered list of outcomes in the path
        """
        client = self._get_client()

        query = """
        MATCH (start:LearningOutcome {code: $start_code})
        MATCH (end:LearningOutcome {code: $end_code})
        MATCH path = shortestPath((start)-[:PREREQUISITE_FOR|BUILDS_ON|ENABLES*]-(end))
        RETURN [n in nodes(path) | {
            code: n.code,
            description: n.description_en,
            difficulty: n.difficulty_level
        }] as sequence,
        length(path) as steps
        """

        results = client.execute(
            query,
            {"start_code": start_code, "end_code": end_code},
        )

        if results:
            return results[0].get("sequence", [])
        return []

    def find_related_cluster(
        self,
        outcome_code: str,
        radius: int = 2,
    ) -> list[dict[str, Any]]:
        """
        Find cluster of related learning outcomes.

        Args:
            outcome_code: Center outcome
            radius: Maximum relationship distance

        Returns:
            List of related outcomes
        """
        client = self._get_client()

        query = f"""
        MATCH (center:LearningOutcome {{code: $code}})
        MATCH (center)-[r:RELATED_TO|BUILDS_ON|ASSESSES*1..{radius}]-(related:LearningOutcome)
        RETURN DISTINCT
            related.code as code,
            related.description_en as description,
            related.subject as subject,
            related.difficulty_level as difficulty
        LIMIT 20
        """

        return client.execute(query, {"code": outcome_code})

    def suggest_next_outcomes(
        self,
        completed_codes: list[str],
        subject: str | None = None,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Suggest next learning outcomes based on completed ones.

        Args:
            completed_codes: List of completed outcome codes
            subject: Optional subject filter
            limit: Maximum suggestions

        Returns:
            List of suggested outcomes
        """
        client = self._get_client()

        subject_filter = f"AND next.subject = '{subject}'" if subject else ""

        query = f"""
        UNWIND $completed as completed_code
        MATCH (completed:LearningOutcome {{code: completed_code}})
        MATCH (completed)-[:ENABLES|PREREQUISITE_FOR]->(next:LearningOutcome)
        WHERE NOT next.code IN $completed
          {subject_filter}
        WITH next, count(completed) as prereq_count
        ORDER BY prereq_count DESC
        RETURN DISTINCT
            next.code as code,
            next.description_en as description,
            next.difficulty_level as difficulty,
            prereq_count as readiness_score
        LIMIT {limit}
        """

        return client.execute(
            query,
            {"completed": completed_codes},
        )

    def close(self):
        """Close client."""
        if self._client:
            self._client.close()
            self._client = None


# =============================================================================
# Convenience Functions
# =============================================================================

async def build_subject_graph(
    subject_code: str,
    memgraph_uri: str | None = None,
    duckdb_path: str | None = None,
) -> dict[str, Any]:
    """
    Build learning outcome graph for a subject.

    Args:
        subject_code: Subject code (e.g., 'irish', 'mathematics')
        memgraph_uri: Memgraph connection URI
        duckdb_path: Path to DuckDB database

    Returns:
        Stats about the built graph
    """
    builder = LearningOutcomeGraphBuilder(
        memgraph_uri=memgraph_uri,
        duckdb_path=duckdb_path,
    )

    try:
        return await builder.build_graph_for_subject(subject_code)
    finally:
        builder.close()


def find_learning_path(
    start_code: str,
    end_code: str,
    memgraph_uri: str | None = None,
) -> list[dict[str, Any]]:
    """
    Find learning path between two outcomes.

    Args:
        start_code: Starting outcome code
        end_code: Target outcome code
        memgraph_uri: Memgraph connection URI

    Returns:
        Ordered list of outcomes in the path
    """
    finder = LearningPathFinder(memgraph_uri=memgraph_uri)
    try:
        return finder.find_learning_sequence(start_code, end_code)
    finally:
        finder.close()


# =============================================================================
# CLI Entry Point
# =============================================================================

if __name__ == "__main__":
    import argparse
    import asyncio
    import logging

    parser = argparse.ArgumentParser(description="Build learning outcome graph")
    parser.add_argument("subject", help="Subject code (e.g., 'irish', 'mathematics')")
    parser.add_argument("--database", default=DEFAULT_DUCKDB_PATH)
    parser.add_argument("--memgraph", default=DEFAULT_MEMGRAPH_URI)
    args = parser.parse_args()

    # Configure structlog for CLI output
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    )

    result = asyncio.run(build_subject_graph(
        subject_code=args.subject,
        memgraph_uri=args.memgraph,
        duckdb_path=args.database,
    ))

    print(f"Subject: {result['subject']}")
    print(f"Outcomes processed: {result['outcomes']}")
    print(f"Relationships extracted: {result['relationships']}")
    print(f"Stored in graph: {result['stored']}")
