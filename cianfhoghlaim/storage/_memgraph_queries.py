"""Memgraph query helpers — `CurriculumGraph` + `CurriculumDataLoader`
(split from `memgraph_client.py` per T4).

Per the `2026-07-09-agent-fleet-and-observability-facade-v1` change,
the 1124-LOC `cianfhoghlaim/storage/memgraph_client.py` monolith is
split into 3 files:

- `_memgraph_protocol.py` — Protocol + dataclasses
- `_memgraph_client.py` — concrete `MemgraphClient`
- `_memgraph_queries.py` — `CurriculumGraph` + `CurriculumDataLoader`
  (this file)

The body of every helper is preserved verbatim from the legacy
monolith so the public API is byte-identical.
"""
from __future__ import annotations

import logging

from ._memgraph_client import MemgraphClient
from ._memgraph_protocol import (
    LearningOutcome,
    MemgraphConfig,
    get_config,
)

logger = logging.getLogger(__name__)


class CurriculumGraph:
    """
    High-level interface for curriculum knowledge graph operations.

    Provides semantic methods for common curriculum operations.
    """

    def __init__(self, config: MemgraphConfig | None = None):
        self.client = MemgraphClient(config)

    def close(self) -> None:
        """Close the client."""
        self.client.close()

    def add_curriculum_document(
        self,
        doc: dict,
        year: int,
        learning_outcomes: list[str] | None = None,
    ) -> None:
        """
        Add a curriculum document and link to outcomes.

        Args:
            doc: Document metadata dict
            year: Curriculum year
            learning_outcomes: List of outcome codes the document addresses
        """
        self.client.add_document(
            id=doc["id"],
            title=doc["title"],
            document_type=doc.get("document_type", "specification"),
            education_level=doc.get("education_level", ""),
            subject=doc.get("subject", ""),
            year=year,
            source_url=doc.get("source_url"),
            lancedb_table=doc.get("lancedb_table"),
        )

        # Link to subject
        if doc.get("subject"):
            self.client.link_document_to_subject(doc["id"], doc["subject"])

        # Link to learning outcomes
        if learning_outcomes:
            for outcome_code in learning_outcomes:
                self.client.link_document_to_outcome(doc["id"], outcome_code)

    def add_learning_outcome(
        self,
        lo: LearningOutcome,
        strand_id: str,
        year: int,
    ) -> None:
        """Add a learning outcome with temporal tracking."""
        self.client.add_learning_outcome(
            code=lo.code,
            strand_unit_id=strand_id,
            description_en=lo.description_en,
            description_ga=lo.description_ga,
            difficulty_level=lo.difficulty_level,
            curriculum_year=year,
            key_skills=lo.key_skills,
        )

    def find_related_outcomes(
        self,
        lo_code: str,
        depth: int = 2,
    ) -> list[dict]:
        """Find related learning outcomes."""
        return self.client.find_related_outcomes(lo_code, depth)

    def track_curriculum_changes(
        self,
        subject: str,
        from_year: int,
        to_year: int,
    ) -> list[dict]:
        """Track curriculum changes between years."""
        return self.client.track_curriculum_changes(subject, from_year, to_year)

    def get_important_outcomes(self) -> list[dict]:
        """Get most important learning outcomes by PageRank."""
        return self.client.run_pagerank()

    def get_outcome_clusters(self) -> list[dict]:
        """Get clusters of related learning outcomes."""
        return self.client.run_community_detection()


# =========================================================================
# Data Loading
# =========================================================================


class CurriculumDataLoader:
    """
    Load curriculum data from DuckDB into Memgraph.

    Reads curriculum structure from DuckDB tables and creates
    the knowledge graph in Memgraph.
    """

    def __init__(
        self,
        duckdb_path: str = "./storage/data/celtic_education.duckdb",
        memgraph_config: MemgraphConfig | None = None,
    ):
        self.duckdb_path = duckdb_path
        self.graph = CurriculumGraph(memgraph_config)

    def _connect_duckdb(self):
        """Get DuckDB connection (single-threaded)."""
        import duckdb
        return duckdb.connect(self.duckdb_path, read_only=True)

    def initialize_schema(self) -> dict:
        """
        Create indexes and constraints in Memgraph.

        Returns summary of created indexes/constraints.
        """
        schema_queries = [
            # Indexes
            "CREATE INDEX ON :Subject(code)",
            "CREATE INDEX ON :Strand(id)",
            "CREATE INDEX ON :StrandUnit(id)",
            "CREATE INDEX ON :LearningOutcome(code)",
            "CREATE INDEX ON :Document(id)",
            # Constraints
            "CREATE CONSTRAINT ON (s:Subject) ASSERT s.code IS UNIQUE",
            "CREATE CONSTRAINT ON (lo:LearningOutcome) ASSERT lo.code IS UNIQUE",
        ]

        results = {"indexes_created": 0, "errors": []}

        for query in schema_queries:
            try:
                self.graph.client.execute_write(query)
                results["indexes_created"] += 1
            except Exception as e:
                if "already exists" not in str(e).lower():
                    results["errors"].append(str(e))

        logger.info(f"Schema initialized: {results['indexes_created']} indexes")
        return results

    def load_subjects(self) -> int:
        """Load subjects from DuckDB into Memgraph."""
        conn = self._connect_duckdb()

        try:
            # Try to read from subjects table or curriculum_pages
            try:
                query = """
                    SELECT DISTINCT
                        subject as code,
                        subject as name_en,
                        NULL as name_ga,
                        level as education_level,
                        source as syllabus_url
                    FROM education.curriculum_pages
                    WHERE subject IS NOT NULL
                """
                rows = conn.execute(query).fetchall()
            except Exception:
                # Fallback: hardcoded Irish curriculum subjects
                rows = [
                    ("irish", "Irish", "Gaeilge", "all", None),
                    ("english", "English", "Béarla", "all", None),
                    ("mathematics", "Mathematics", "Matamaitic", "all", None),
                    ("history", "History", "Stair", "post_primary", None),
                    ("geography", "Geography", "Tíreolaíocht", "post_primary", None),
                    ("science", "Science", "Eolaíocht", "post_primary", None),
                    ("biology", "Biology", "Bitheolaíocht", "senior_cycle", None),
                    ("chemistry", "Chemistry", "Ceimic", "senior_cycle", None),
                    ("physics", "Physics", "Fisic", "senior_cycle", None),
                ]

            count = 0
            for row in rows:
                code, name_en, name_ga, level, url = row[:5] if len(row) >= 5 else (row + (None,) * 5)[:5]
                if code:
                    self.graph.client.add_subject(
                        code=str(code),
                        name_en=str(name_en or code),
                        name_ga=str(name_ga or ""),
                        education_level=str(level or "all"),
                        syllabus_url=url,
                    )
                    count += 1

            logger.info(f"Loaded {count} subjects")
            return count

        finally:
            conn.close()

    def load_curriculum(self) -> dict:
        """Load all curriculum data."""
        return {
            "subjects": self.load_subjects(),
        }


# =========================================================================
# Convenience functions
# =========================================================================


def load_curriculum_to_graph(
    memgraph_config: MemgraphConfig | None = None,
    duckdb_path: str = "./storage/data/celtic_education.duckdb",
) -> dict:
    """
    Helper to load curriculum data into a fresh graph.

    Args:
        memgraph_config: Memgraph connection config
        duckdb_path: Path to DuckDB curriculum database

    Returns:
        Load summary dict
    """
    loader = CurriculumDataLoader(
        duckdb_path=duckdb_path,
        memgraph_config=memgraph_config,
    )

    loader.initialize_schema()
    summary = loader.load_curriculum()
    loader.graph.close()

    return summary


_curriculum_graph: CurriculumGraph | None = None


def get_curriculum_graph() -> CurriculumGraph:
    """Singleton curriculum graph accessor."""
    global _curriculum_graph
    if _curriculum_graph is None:
        _curriculum_graph = CurriculumGraph()
    return _curriculum_graph


__all__ = [
    "CurriculumDataLoader",
    "CurriculumGraph",
    "get_curriculum_graph",
    "load_curriculum_to_graph",
]
