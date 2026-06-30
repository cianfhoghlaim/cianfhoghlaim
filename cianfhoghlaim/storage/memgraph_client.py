"""
Memgraph Graph Database Client.

Primary knowledge graph client for:
- Curriculum hierarchy (Subject -> Strand -> Unit -> Learning Outcome)
- Document relationships
- Temporal versioning (tracking curriculum changes by year)
- MAGE algorithm integration
"""

import logging
from collections.abc import Generator
from contextlib import contextmanager, suppress
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from ..storage.config import MemgraphConfig, get_config

logger = logging.getLogger(__name__)


@dataclass
class CurriculumNode:
    """Base class for curriculum graph nodes."""

    id: str
    name_en: str
    name_ga: str | None = None
    properties: dict[str, Any] | None = None


@dataclass
class Subject(CurriculumNode):
    """Subject node (e.g., Irish, Mathematics)."""

    code: str = ""
    education_level: str = ""
    syllabus_url: str | None = None


@dataclass
class Strand(CurriculumNode):
    """Strand within a subject."""

    subject_code: str = ""
    sequence: int = 0
    description: str | None = None


@dataclass
class StrandUnit(CurriculumNode):
    """Unit within a strand."""

    strand_id: str = ""
    sequence: int = 0
    description: str | None = None


@dataclass
class LearningOutcome(CurriculumNode):
    """Specific learning outcome."""

    code: str = ""
    strand_unit_id: str = ""
    description_en: str = ""
    description_ga: str | None = None
    difficulty_level: str = ""
    curriculum_year: int = 2024
    key_skills: list[str] | None = None


class MemgraphClient:
    """
    Client for Memgraph graph database operations.

    Uses the neo4j driver (Memgraph is Bolt-compatible).
    """

    def __init__(self, config: MemgraphConfig | None = None):
        self.config = config or get_config().memgraph
        self._driver = None

    def _get_driver(self):
        """Get or create the Neo4j/Memgraph driver."""
        if self._driver is None:
            try:
                from neo4j import GraphDatabase
            except ImportError:
                raise ImportError(
                    "neo4j driver is not installed. Run: pip install neo4j"
                )

            if self.config.username and self.config.password:
                self._driver = GraphDatabase.driver(
                    self.config.uri,
                    auth=(self.config.username, self.config.password),
                )
            else:
                self._driver = GraphDatabase.driver(self.config.uri)

            logger.info(f"Connected to Memgraph at {self.config.uri}")

        return self._driver

    @property
    def driver(self):
        """Get the database driver."""
        return self._get_driver()

    def close(self) -> None:
        """Close the driver connection."""
        if self._driver:
            self._driver.close()
            self._driver = None

    @contextmanager
    def session(self) -> Generator[Any]:
        """Get a database session."""
        session = self.driver.session()
        try:
            yield session
        finally:
            session.close()

    def health_check(self) -> bool:
        """Check Memgraph connectivity."""
        try:
            with self.session() as session:
                session.run("RETURN 1").single()
            return True
        except Exception as e:
            logger.error(f"Memgraph health check failed: {e}")
            return False

    # =========================================================================
    # Generic Operations
    # =========================================================================

    def execute(self, query: str, params: dict | None = None) -> list[dict]:
        """Execute a Cypher query and return results."""
        with self.session() as session:
            result = session.run(query, params or {})
            return [dict(record) for record in result]

    def execute_write(self, query: str, params: dict | None = None) -> dict:
        """Execute a write query and return summary."""
        with self.session() as session:
            result = session.run(query, params or {})
            summary = result.consume()
            return {
                "nodes_created": summary.counters.nodes_created,
                "relationships_created": summary.counters.relationships_created,
                "properties_set": summary.counters.properties_set,
            }

    # =========================================================================
    # Curriculum Hierarchy
    # =========================================================================

    def add_subject(
        self,
        code: str,
        name_en: str,
        name_ga: str,
        education_level: str,
        syllabus_url: str | None = None,
        valid_from: datetime | None = None,
    ) -> dict:
        """Add or update a subject node."""
        query = """
        MERGE (s:Subject {code: $code})
        SET s.name_en = $name_en,
            s.name_ga = $name_ga,
            s.education_level = $education_level,
            s.syllabus_url = $syllabus_url,
            s.valid_from = $valid_from,
            s.updated_at = datetime()
        RETURN s
        """
        return self.execute_write(
            query,
            {
                "code": code,
                "name_en": name_en,
                "name_ga": name_ga,
                "education_level": education_level,
                "syllabus_url": syllabus_url,
                "valid_from": (valid_from or datetime.now()).isoformat(),
            },
        )

    def add_strand(
        self,
        id: str,
        subject_code: str,
        name_en: str,
        name_ga: str | None = None,
        sequence: int = 0,
        description: str | None = None,
    ) -> dict:
        """Add a strand and link to subject."""
        query = """
        MATCH (sub:Subject {code: $subject_code})
        MERGE (st:Strand {id: $id})
        SET st.name_en = $name_en,
            st.name_ga = $name_ga,
            st.subject_code = $subject_code,
            st.sequence = $sequence,
            st.description = $description,
            st.updated_at = datetime()
        MERGE (sub)-[:HAS_STRAND {sequence: $sequence}]->(st)
        RETURN st
        """
        return self.execute_write(
            query,
            {
                "id": id,
                "subject_code": subject_code,
                "name_en": name_en,
                "name_ga": name_ga,
                "sequence": sequence,
                "description": description,
            },
        )

    def add_strand_unit(
        self,
        id: str,
        strand_id: str,
        name_en: str,
        name_ga: str | None = None,
        sequence: int = 0,
        description: str | None = None,
    ) -> dict:
        """Add a strand unit and link to strand."""
        query = """
        MATCH (st:Strand {id: $strand_id})
        MERGE (su:StrandUnit {id: $id})
        SET su.name_en = $name_en,
            su.name_ga = $name_ga,
            su.strand_id = $strand_id,
            su.sequence = $sequence,
            su.description = $description,
            su.updated_at = datetime()
        MERGE (st)-[:HAS_UNIT {sequence: $sequence}]->(su)
        RETURN su
        """
        return self.execute_write(
            query,
            {
                "id": id,
                "strand_id": strand_id,
                "name_en": name_en,
                "name_ga": name_ga,
                "sequence": sequence,
                "description": description,
            },
        )

    def add_learning_outcome(
        self,
        code: str,
        strand_unit_id: str,
        description_en: str,
        description_ga: str | None = None,
        difficulty_level: str = "ordinary",
        curriculum_year: int = 2024,
        key_skills: list[str] | None = None,
    ) -> dict:
        """Add a learning outcome and link to strand unit."""
        query = """
        MATCH (su:StrandUnit {id: $strand_unit_id})
        MERGE (lo:LearningOutcome {code: $code})
        SET lo.description_en = $description_en,
            lo.description_ga = $description_ga,
            lo.difficulty_level = $difficulty_level,
            lo.curriculum_year = $curriculum_year,
            lo.key_skills = $key_skills,
            lo.valid_from = datetime(),
            lo.updated_at = datetime()
        MERGE (su)-[:HAS_OUTCOME]->(lo)
        RETURN lo
        """
        return self.execute_write(
            query,
            {
                "code": code,
                "strand_unit_id": strand_unit_id,
                "description_en": description_en,
                "description_ga": description_ga,
                "difficulty_level": difficulty_level,
                "curriculum_year": curriculum_year,
                "key_skills": key_skills or [],
            },
        )

    # =========================================================================
    # Document Relationships
    # =========================================================================

    def add_document(
        self,
        id: str,
        title: str,
        document_type: str,
        education_level: str,
        subject: str,
        year: int | None = None,
        source_url: str | None = None,
        lancedb_table: str | None = None,
    ) -> dict:
        """Add a curriculum document node."""
        query = """
        MERGE (d:Document {id: $id})
        SET d.title = $title,
            d.document_type = $document_type,
            d.education_level = $education_level,
            d.subject = $subject,
            d.year = $year,
            d.source_url = $source_url,
            d.lancedb_table = $lancedb_table,
            d.created_at = datetime()
        RETURN d
        """
        return self.execute_write(
            query,
            {
                "id": id,
                "title": title,
                "document_type": document_type,
                "education_level": education_level,
                "subject": subject,
                "year": year,
                "source_url": source_url,
                "lancedb_table": lancedb_table,
            },
        )

    def link_document_to_subject(
        self,
        document_id: str,
        subject_code: str,
        is_primary: bool = True,
    ) -> dict:
        """Create relationship between document and subject."""
        query = """
        MATCH (d:Document {id: $document_id})
        MATCH (s:Subject {code: $subject_code})
        MERGE (d)-[r:COVERS_SUBJECT]->(s)
        SET r.primary = $is_primary
        RETURN d, s
        """
        return self.execute_write(
            query,
            {
                "document_id": document_id,
                "subject_code": subject_code,
                "is_primary": is_primary,
            },
        )

    def link_document_to_outcome(
        self,
        document_id: str,
        outcome_code: str,
        relevance_score: float = 1.0,
        section: str | None = None,
    ) -> dict:
        """Link document to learning outcome."""
        query = """
        MATCH (d:Document {id: $document_id})
        MATCH (lo:LearningOutcome {code: $outcome_code})
        MERGE (d)-[r:ADDRESSES_OUTCOME]->(lo)
        SET r.relevance_score = $relevance_score,
            r.section = $section
        RETURN d, lo
        """
        return self.execute_write(
            query,
            {
                "document_id": document_id,
                "outcome_code": outcome_code,
                "relevance_score": relevance_score,
                "section": section,
            },
        )

    # =========================================================================
    # Query Methods
    # =========================================================================

    def get_subject(self, code: str) -> dict | None:
        """Get a subject by code."""
        results = self.execute(
            "MATCH (s:Subject {code: $code}) RETURN s",
            {"code": code},
        )
        if results:
            return dict(results[0]["s"])
        return None

    def get_curriculum_tree(self, subject_code: str) -> list[dict]:
        """Get full curriculum tree for a subject."""
        query = """
        MATCH (sub:Subject {code: $subject_code})
        OPTIONAL MATCH (sub)-[:HAS_STRAND]->(st:Strand)
        OPTIONAL MATCH (st)-[:HAS_UNIT]->(su:StrandUnit)
        OPTIONAL MATCH (su)-[:HAS_OUTCOME]->(lo:LearningOutcome)
        RETURN sub, collect(DISTINCT st) as strands,
               collect(DISTINCT su) as units,
               collect(DISTINCT lo) as outcomes
        """
        return self.execute(query, {"subject_code": subject_code})

    def find_related_outcomes(
        self,
        outcome_code: str,
        depth: int = 2,
    ) -> list[dict]:
        """Find learning outcomes related to the given one."""
        query = """
        MATCH (lo:LearningOutcome {code: $outcome_code})
        MATCH path = (lo)-[:RELATED_TO|PREREQUISITE_OF*1..$depth]-(related:LearningOutcome)
        RETURN DISTINCT related.code as code,
               related.description_en as description,
               length(path) as distance
        ORDER BY distance
        """
        return self.execute(
            query.replace("$depth", str(depth)),
            {"outcome_code": outcome_code},
        )

    def get_documents_for_outcome(
        self,
        outcome_code: str,
        document_type: str | None = None,
    ) -> list[dict]:
        """Get documents that address a learning outcome."""
        query = """
        MATCH (d:Document)-[r:ADDRESSES_OUTCOME]->(lo:LearningOutcome {code: $outcome_code})
        """
        if document_type:
            query += " WHERE d.document_type = $document_type"

        query += """
        RETURN d.id as id, d.title as title, d.document_type as type,
               r.relevance_score as relevance
        ORDER BY r.relevance_score DESC
        """
        return self.execute(
            query,
            {"outcome_code": outcome_code, "document_type": document_type},
        )

    # =========================================================================
    # Temporal Queries
    # =========================================================================

    def track_curriculum_changes(
        self,
        subject_code: str,
        from_year: int,
        to_year: int,
    ) -> list[dict]:
        """Find curriculum changes between years."""
        query = """
        MATCH (lo:LearningOutcome)
        WHERE lo.curriculum_year >= $from_year
        AND lo.curriculum_year <= $to_year
        MATCH (lo)<-[:HAS_OUTCOME]-(su)<-[:HAS_UNIT]-(st)<-[:HAS_STRAND]-(sub:Subject {code: $subject_code})
        RETURN lo.code as code,
               lo.description_en as description,
               lo.curriculum_year as year,
               lo.valid_from as valid_from,
               lo.valid_to as valid_to
        ORDER BY lo.curriculum_year, lo.code
        """
        return self.execute(
            query,
            {
                "subject_code": subject_code,
                "from_year": from_year,
                "to_year": to_year,
            },
        )

    def get_outcomes_by_year(self, curriculum_year: int) -> list[dict]:
        """Get all learning outcomes introduced in a specific year."""
        query = """
        MATCH (lo:LearningOutcome {curriculum_year: $year})
        RETURN lo.code as code,
               lo.description_en as description,
               lo.difficulty_level as difficulty
        ORDER BY lo.code
        """
        return self.execute(query, {"year": curriculum_year})

    # =========================================================================
    # MAGE Algorithm Helpers
    # =========================================================================

    def run_pagerank(self, node_label: str = "LearningOutcome") -> list[dict]:
        """Run PageRank algorithm on nodes."""
        query = f"""
        CALL pagerank.get()
        YIELD node, rank
        WHERE node:{node_label}
        RETURN node.code as code, rank
        ORDER BY rank DESC
        LIMIT 20
        """
        return self.execute(query)

    def run_community_detection(
        self,
        node_label: str = "LearningOutcome",
    ) -> list[dict]:
        """Run Louvain community detection."""
        query = f"""
        CALL community_detection.louvain()
        YIELD node, community_id
        WHERE node:{node_label}
        RETURN community_id, collect(node.code) as members
        ORDER BY size(members) DESC
        """
        return self.execute(query)

    def find_shortest_path(
        self,
        start_code: str,
        end_code: str,
        relationship_types: list[str] | None = None,
    ) -> list[dict]:
        """Find shortest path between two learning outcomes."""
        rel_pattern = (
            "|".join(relationship_types)
            if relationship_types
            else "PREREQUISITE_OF|RELATED_TO"
        )
        query = f"""
        MATCH (start:LearningOutcome {{code: $start_code}})
        MATCH (end:LearningOutcome {{code: $end_code}})
        MATCH path = shortestPath((start)-[:{rel_pattern}*]-(end))
        RETURN [n in nodes(path) | n.code] as path_codes,
               length(path) as distance
        """
        return self.execute(
            query,
            {"start_code": start_code, "end_code": end_code},
        )

    # =========================================================================
    # PDF Document Integration
    # =========================================================================

    def add_pdf_document(
        self,
        document_id: str,
        title: str,
        pdf_type: str,
        cycle: str,
        subject: str,
        source_url: str | None = None,
        local_path: str | None = None,
        lancedb_table: str = "oideachas.curriculum_pdfs",
        page_count: int = 1,
        ocr_confidence: float = 0.0,
        ocr_backend: str | None = None,
    ) -> dict:
        """
        Add a PDF document node with PDF-specific metadata.

        Creates a Document:PDF node linked to the LanceDB vector store.

        Args:
            document_id: Unique identifier for the PDF
            title: Document title
            pdf_type: Type (specification, marking_scheme, sample_paper, etc.)
            cycle: Education cycle (junior_cycle, senior_cycle, etc.)
            subject: Subject slug
            source_url: Original URL where PDF was discovered
            local_path: Local file path after download
            lancedb_table: LanceDB table for vector embeddings
            page_count: Number of pages in PDF
            ocr_confidence: OCR extraction confidence score
            ocr_backend: OCR backend used (docling, paddleocr, etc.)

        Returns:
            Created node dict
        """
        query = """
        MERGE (d:Document:PDF {id: $id})
        SET d.title = $title,
            d.document_type = 'pdf',
            d.pdf_type = $pdf_type,
            d.education_level = $cycle,
            d.subject = $subject,
            d.source_url = $source_url,
            d.local_path = $local_path,
            d.lancedb_table = $lancedb_table,
            d.page_count = $page_count,
            d.ocr_confidence = $ocr_confidence,
            d.ocr_backend = $ocr_backend,
            d.created_at = datetime()
        RETURN d
        """
        return self.execute_write(
            query,
            {
                "id": document_id,
                "title": title,
                "pdf_type": pdf_type,
                "cycle": cycle,
                "subject": subject,
                "source_url": source_url,
                "local_path": local_path,
                "lancedb_table": lancedb_table,
                "page_count": page_count,
                "ocr_confidence": ocr_confidence,
                "ocr_backend": ocr_backend,
            },
        )

    def get_pdf_documents_for_subject(
        self,
        subject: str,
        cycle: str | None = None,
        pdf_type: str | None = None,
    ) -> list[dict]:
        """
        Get PDF documents for a subject with optional filters.

        Args:
            subject: Subject slug
            cycle: Optional education cycle filter
            pdf_type: Optional PDF type filter

        Returns:
            List of PDF document dicts
        """
        query = """
        MATCH (d:Document:PDF {subject: $subject})
        """
        params = {"subject": subject}

        conditions = []
        if cycle:
            conditions.append("d.education_level = $cycle")
            params["cycle"] = cycle
        if pdf_type:
            conditions.append("d.pdf_type = $pdf_type")
            params["pdf_type"] = pdf_type

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += """
        RETURN d.id as id,
               d.title as title,
               d.pdf_type as pdf_type,
               d.education_level as cycle,
               d.source_url as source_url,
               d.local_path as local_path,
               d.lancedb_table as lancedb_table,
               d.page_count as page_count,
               d.ocr_confidence as ocr_confidence
        ORDER BY d.created_at DESC
        """
        return self.execute(query, params)

    def link_pdf_to_outcomes(
        self,
        document_id: str,
        outcome_codes: list[str],
        relevance_scores: list[float] | None = None,
    ) -> int:
        """
        Link a PDF document to multiple learning outcomes.

        Args:
            document_id: PDF document ID
            outcome_codes: List of learning outcome codes
            relevance_scores: Optional relevance scores (1.0 if not provided)

        Returns:
            Number of relationships created
        """
        if relevance_scores is None:
            relevance_scores = [1.0] * len(outcome_codes)

        count = 0
        for code, score in zip(outcome_codes, relevance_scores, strict=False):
            try:
                self.link_document_to_outcome(
                    document_id=document_id,
                    outcome_code=code,
                    relevance_score=score,
                )
                count += 1
            except Exception:
                pass  # Outcome might not exist

        return count


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

    def load_learning_outcomes(self, subject_code: str | None = None) -> int:
        """
        Load learning outcomes from DuckDB into Memgraph.

        Args:
            subject_code: Optional filter for specific subject
        """
        conn = self._connect_duckdb()

        try:
            query = """
                SELECT
                    id,
                    subject,
                    level,
                    strand,
                    strand_unit,
                    outcome_code,
                    description_en,
                    description_ga,
                    difficulty_level,
                    curriculum_year
                FROM education.learning_outcomes
            """
            if subject_code:
                query += f" WHERE subject = '{subject_code}'"

            try:
                rows = conn.execute(query).fetchall()
            except Exception:
                logger.warning("learning_outcomes table not found, skipping")
                return 0

            count = 0
            for row in rows:
                (
                    lo_id, subject, level, strand, strand_unit,
                    outcome_code, desc_en, desc_ga, difficulty, year
                ) = row

                # Ensure strand exists
                strand_id = f"{subject}_{level}_{strand}" if strand else f"{subject}_{level}_default"
                self.graph.client.add_strand(
                    id=strand_id,
                    subject_code=subject,
                    name_en=strand or "Default Strand",
                )

                # Ensure strand unit exists
                unit_id = f"{strand_id}_{strand_unit or 'default'}"
                self.graph.client.add_strand_unit(
                    id=unit_id,
                    strand_id=strand_id,
                    name_en=strand_unit or "Default Unit",
                )

                # Add learning outcome
                self.graph.client.add_learning_outcome(
                    code=outcome_code or f"LO_{lo_id}",
                    strand_unit_id=unit_id,
                    description_en=desc_en or "",
                    description_ga=desc_ga,
                    difficulty_level=difficulty or "ordinary",
                    curriculum_year=year or 2024,
                )
                count += 1

            logger.info(f"Loaded {count} learning outcomes")
            return count

        finally:
            conn.close()

    def load_documents(self) -> int:
        """Load curriculum documents from DuckDB into Memgraph."""
        conn = self._connect_duckdb()

        try:
            query = """
                SELECT
                    id,
                    title,
                    document_type,
                    subject,
                    level as education_level,
                    source_url,
                    curriculum_year
                FROM education.curriculum_documents
            """

            try:
                rows = conn.execute(query).fetchall()
            except Exception:
                # Fallback: use curriculum_pages
                query = """
                    SELECT DISTINCT
                        page_url as id,
                        title,
                        'specification' as document_type,
                        subject,
                        level as education_level,
                        page_url as source_url,
                        2024 as curriculum_year
                    FROM education.curriculum_pages
                    WHERE title IS NOT NULL
                    LIMIT 100
                """
                try:
                    rows = conn.execute(query).fetchall()
                except Exception:
                    logger.warning("No document tables found, skipping")
                    return 0

            count = 0
            for row in rows:
                doc_id, title, doc_type, subject, level, url, year = row[:7]

                if doc_id:
                    self.graph.client.add_document(
                        id=str(doc_id)[:100],
                        title=str(title or "Untitled")[:200],
                        document_type=str(doc_type or "specification"),
                        education_level=str(level or ""),
                        subject=str(subject or ""),
                        year=int(year) if year else 2024,
                        source_url=str(url)[:500] if url else None,
                    )

                    # Link to subject
                    if subject:
                        with suppress(Exception):
                            self.graph.client.link_document_to_subject(
                                str(doc_id)[:100],
                                str(subject),
                            )

                    count += 1

            logger.info(f"Loaded {count} documents")
            return count

        finally:
            conn.close()

    def load_all(self) -> dict[str, int]:
        """
        Load all curriculum data into Memgraph.

        Returns count of loaded items by type.
        """
        results = {}

        # Initialize schema first
        self.initialize_schema()

        # Load in order (subjects -> outcomes -> documents)
        results["subjects"] = self.load_subjects()
        results["learning_outcomes"] = self.load_learning_outcomes()
        results["documents"] = self.load_documents()

        total = sum(results.values())
        logger.info(f"Loaded {total} total items into Memgraph")

        return results


def load_curriculum_to_graph(
    duckdb_path: str = "./storage/data/celtic_education.duckdb",
) -> dict[str, int]:
    """
    Convenience function to load curriculum data into Memgraph.

    Args:
        duckdb_path: Path to DuckDB database

    Returns:
        Dictionary with counts of loaded items
    """
    loader = CurriculumDataLoader(duckdb_path=duckdb_path)
    try:
        return loader.load_all()
    finally:
        loader.graph.close()


# Singleton instance
_curriculum_graph: CurriculumGraph | None = None


def get_curriculum_graph() -> CurriculumGraph:
    """Get the curriculum graph singleton."""
    global _curriculum_graph
    if _curriculum_graph is None:
        _curriculum_graph = CurriculumGraph()
    return _curriculum_graph


# =========================================================================
# CLI Entry Point
# =========================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Load curriculum data into Memgraph")
    parser.add_argument("--database", default="./storage/data/celtic_education.duckdb")
    parser.add_argument("--subjects-only", action="store_true", help="Only load subjects")
    args = parser.parse_args()

    if args.subjects_only:
        loader = CurriculumDataLoader(duckdb_path=args.database)
        count = loader.load_subjects()
        print(f"Loaded {count} subjects")
        loader.graph.close()
    else:
        results = load_curriculum_to_graph(duckdb_path=args.database)
        for item_type, count in results.items():
            print(f"{item_type}: {count}")
