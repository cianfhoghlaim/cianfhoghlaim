"""
Curriculum Specification Extraction Flow.

Extracts structured CurriculumSpecification objects from ingested curriculum pages
using BAML for type-safe LLM extraction.

Pipeline:
    DuckDB (curriculum_pages) → Filter (specifications) → BAML Extract → LanceDB + DuckDB

CRITICAL CONSTRAINTS:
    - BAML schema validation REQUIRED before LLM calls
    - DuckDB: Single-threaded only
    - LanceDB: MVCC safe, drop HNSW for bulk inserts

Usage:
    # Run extraction flow
    python -m sruth.oideachais.cocoindex_flows.curriculum_specification_extraction

    # Or import and run
    from sruth.oideachais.cocoindex_flows.curriculum_specification_extraction import (
        CurriculumSpecificationFlow,
    )
    flow = CurriculumSpecificationFlow()
    result = await flow.run(limit=10)
"""

from __future__ import annotations

import asyncio
import hashlib
import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Iterator

import structlog

logger = structlog.get_logger(__name__)

# Configuration
DEFAULT_DUCKDB_PATH = os.getenv(
    "OIDEACHAS_DUCKDB_PATH",
    "./storage/data/celtic_education.duckdb"
)
DEFAULT_LANCEDB_PATH = os.getenv(
    "OIDEACHAS_LANCEDB_PATH",
    "./storage/data/lancedb"
)


class DocumentType(str, Enum):
    """Types of curriculum documents."""
    SPECIFICATION = "specification"
    SYLLABUS = "syllabus"
    GUIDELINES = "guidelines"
    BRIEF = "brief"
    DRAFT = "draft_specification"
    OTHER = "other"


@dataclass
class ExtractionConfig:
    """Configuration for curriculum specification extraction."""

    # Source
    duckdb_path: str = DEFAULT_DUCKDB_PATH
    source_table: str = "education.curriculum_pages"

    # Filter
    document_types: list[str] = field(default_factory=lambda: [
        "specification", "syllabus"
    ])
    languages: list[str] = field(default_factory=lambda: ["en", "ga"])
    cycles: list[str] = field(default_factory=lambda: [
        "junior_cycle", "senior_cycle"
    ])

    # Extraction
    model: str = "claude-3-5-sonnet-20241022"
    max_content_length: int = 50000  # Max chars per document
    batch_size: int = 5  # Documents to process in parallel

    # Output
    lancedb_path: str = DEFAULT_LANCEDB_PATH
    output_table: str = "curriculum_specifications"
    outcomes_table: str = "learning_outcomes"

    # Embedding (for semantic search)
    embedding_model: str = "sentence-transformers/multilingual-e5-large"
    embedding_dim: int = 1024


# =============================================================================
# BAML Integration
# =============================================================================

class BAMLExtractor:
    """
    BAML-based curriculum specification extractor.

    Uses ExtractCurriculumSpecification function from curriculum_extraction.baml
    """

    def __init__(self, model: str = "claude-3-5-sonnet-20241022"):
        self.model = model
        self._baml_client = None

    def _get_baml_client(self):
        """Lazy-load BAML client."""
        if self._baml_client is not None:
            return self._baml_client

        try:
            from baml_client import b
            self._baml_client = b
            logger.info("baml_client_loaded")
            return b
        except ImportError:
            logger.warning("baml_not_available")
            return None

    async def extract_specification(
        self,
        document_text: str,
        subject: str,
        cycle: str,
        language: str,
    ) -> dict[str, Any] | None:
        """
        Extract curriculum specification using BAML.

        Args:
            document_text: Full document content
            subject: Subject code
            cycle: Education cycle (junior_cycle, senior_cycle)
            language: Document language (en, ga)

        Returns:
            Extracted specification dict or None on failure
        """
        baml = self._get_baml_client()

        if baml is None:
            logger.warning("baml_not_available_falling_back")
            return await self._extract_fallback(document_text, subject, cycle, language)

        try:
            # Map cycle string to enum
            cycle_map = {
                "junior_cycle": "JUNIOR_CYCLE",
                "senior_cycle": "SENIOR_CYCLE",
                "primary": "PRIMARY",
            }
            baml_cycle = cycle_map.get(cycle, "JUNIOR_CYCLE")

            # Call BAML extraction function
            result = await baml.ExtractCurriculumSpecification(
                document_text=document_text[:50000],  # Limit length
                subject=subject,
                cycle=baml_cycle,
                language=language,
            )

            # Convert BAML result to dict
            return self._baml_to_dict(result)

        except Exception as e:
            logger.error("baml_extraction_failed", error=str(e), subject=subject)
            return None

    def _baml_to_dict(self, result: Any) -> dict[str, Any]:
        """Convert BAML result to dict."""
        # Handle BAML object with attributes
        if hasattr(result, "__dict__"):
            data = {}
            for key, value in result.__dict__.items():
                if key.startswith("_"):
                    continue
                if hasattr(value, "__dict__"):
                    data[key] = self._baml_to_dict(value)
                elif isinstance(value, list):
                    data[key] = [
                        self._baml_to_dict(v) if hasattr(v, "__dict__") else v
                        for v in value
                    ]
                elif hasattr(value, "value"):  # Enum
                    data[key] = value.value
                else:
                    data[key] = value
            return data
        return result

    async def _extract_fallback(
        self,
        document_text: str,
        subject: str,
        cycle: str,
        language: str,
    ) -> dict[str, Any] | None:
        """Fallback extraction without BAML."""
        try:
            import anthropic
        except ImportError:
            logger.error("anthropic_not_installed")
            return None

        client = anthropic.Anthropic()

        prompt = f"""Extract curriculum specification structure from this document.

Subject: {subject}
Cycle: {cycle}
Language: {language}

Document:
{document_text[:40000]}

Extract as JSON:
{{
  "title": "Full document title",
  "version_year": 2024,
  "strands": [
    {{
      "name": "Strand name",
      "learning_outcomes": [
        {{
          "outcome_code": "LO-SUBJECT-CYCLE-1.1",
          "text": "Outcome description",
          "action_verbs": ["apply", "analyse"]
        }}
      ]
    }}
  ],
  "assessment_info": {{
    "components": [
      {{"name": "Written Exam", "weighting": 80}}
    ]
  }}
}}"""

        try:
            response = client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
            )

            # Parse JSON from response
            import json
            import re

            text = response.content[0].text
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return None

        except Exception as e:
            logger.error("fallback_extraction_failed", error=str(e))
            return None


# =============================================================================
# Document Source
# =============================================================================

class CurriculumPageSource:
    """
    Source for curriculum pages from DuckDB.

    Filters for specification/syllabus documents.
    """

    def __init__(self, config: ExtractionConfig):
        self.config = config

    def read_documents(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """
        Read curriculum documents from DuckDB.

        CONSTRAINT: Single-threaded access only.
        """
        import duckdb

        conn = duckdb.connect(self.config.duckdb_path, read_only=True)

        try:
            # Build document type filter
            doc_types = ", ".join([f"'{dt}'" for dt in self.config.document_types])
            lang_filter = ", ".join([f"'{l}'" for l in self.config.languages])
            cycle_filter = ", ".join([f"'{c}'" for c in self.config.cycles])

            query = f"""
                SELECT
                    url,
                    title,
                    content,
                    content_hash,
                    subject,
                    cycle,
                    language,
                    document_type,
                    source,
                    crawled_at
                FROM {self.config.source_table}
                WHERE content IS NOT NULL
                  AND LENGTH(content) > 1000
                  AND document_type IN ({doc_types})
                  AND language IN ({lang_filter})
                  AND cycle IN ({cycle_filter})
                ORDER BY crawled_at DESC
                LIMIT {limit}
                OFFSET {offset}
            """

            rows = conn.execute(query).fetchall()
            columns = [
                "url", "title", "content", "content_hash", "subject",
                "cycle", "language", "document_type", "source", "crawled_at"
            ]

            documents = [dict(zip(columns, row)) for row in rows]
            logger.info("documents_loaded", count=len(documents))
            return documents

        except Exception as e:
            logger.warning("document_load_failed", error=str(e))
            return []

        finally:
            conn.close()


# =============================================================================
# Specification Sink
# =============================================================================

class SpecificationSink:
    """
    Sink for extracted curriculum specifications.

    Stores in:
    - LanceDB: Vector embeddings of learning outcomes
    - DuckDB: Structured specification data
    """

    def __init__(self, config: ExtractionConfig):
        self.config = config
        self._embedder = None

    def _get_embedder(self):
        """Lazy-load embedding model."""
        if self._embedder is not None:
            return self._embedder

        from sentence_transformers import SentenceTransformer
        self._embedder = SentenceTransformer(self.config.embedding_model)
        return self._embedder

    def store_specification(
        self,
        specification: dict[str, Any],
        source_url: str,
    ) -> dict[str, int]:
        """
        Store extracted specification.

        Returns counts of stored items.
        """
        import duckdb
        import lancedb

        stored = {"specifications": 0, "outcomes": 0, "embeddings": 0}

        # Generate document ID
        doc_id = hashlib.sha256(source_url.encode()).hexdigest()[:16]

        # 1. Store specification metadata in DuckDB
        conn = duckdb.connect(self.config.duckdb_path)
        try:
            self._store_specification_metadata(conn, specification, doc_id, source_url)
            stored["specifications"] = 1
        finally:
            conn.close()

        # 2. Extract and embed learning outcomes
        outcomes = self._flatten_outcomes(specification, doc_id)
        if outcomes:
            # Embed outcomes
            embedder = self._get_embedder()
            texts = [o["text"] for o in outcomes]
            embeddings = embedder.encode(texts, batch_size=100, normalize_embeddings=True)

            # Add embeddings to outcomes
            for i, outcome in enumerate(outcomes):
                outcome["vector"] = embeddings[i].tolist()

            # Store in LanceDB
            db = lancedb.connect(self.config.lancedb_path)
            table_name = self.config.outcomes_table

            if table_name in db.table_names():
                table = db.open_table(table_name)
                # Drop index for bulk insert
                if len(outcomes) > 50:
                    try:
                        table.drop_index("vector_idx")
                    except (ValueError, RuntimeError):
                        pass
                table.add(outcomes)
            else:
                table = db.create_table(table_name, data=outcomes)

            # Recreate index
            if len(outcomes) > 50:
                table.create_index(
                    "vector_idx",
                    index_type="IVF_HNSW",
                    metric="cosine",
                )

            stored["outcomes"] = len(outcomes)
            stored["embeddings"] = len(outcomes)

        return stored

    def _store_specification_metadata(
        self,
        conn,
        specification: dict[str, Any],
        doc_id: str,
        source_url: str,
    ):
        """Store specification metadata in DuckDB."""
        # Create table if not exists
        conn.execute("""
            CREATE TABLE IF NOT EXISTS education.curriculum_specifications (
                doc_id VARCHAR PRIMARY KEY,
                source_url VARCHAR,
                title VARCHAR,
                subject VARCHAR,
                cycle VARCHAR,
                language VARCHAR,
                version_year INTEGER,
                specification_type VARCHAR,
                strand_count INTEGER,
                outcome_count INTEGER,
                extracted_at TIMESTAMP,
                raw_data JSON
            )
        """)

        # Count outcomes
        outcome_count = sum(
            len(strand.get("learning_outcomes", []))
            for strand in specification.get("strands", [])
        )

        import json

        conn.execute("""
            INSERT OR REPLACE INTO education.curriculum_specifications
            (doc_id, source_url, title, subject, cycle, language, version_year,
             specification_type, strand_count, outcome_count, extracted_at, raw_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            doc_id,
            source_url,
            specification.get("title"),
            specification.get("subject"),
            specification.get("cycle"),
            specification.get("language"),
            specification.get("version_year"),
            specification.get("specification_type"),
            len(specification.get("strands", [])),
            outcome_count,
            datetime.utcnow(),
            json.dumps(specification),
        ))

    def _flatten_outcomes(
        self,
        specification: dict[str, Any],
        doc_id: str,
    ) -> list[dict[str, Any]]:
        """Flatten learning outcomes from specification."""
        outcomes = []

        subject = specification.get("subject", "unknown")
        cycle = specification.get("cycle", "unknown")
        language = specification.get("language", "en")

        for strand in specification.get("strands", []):
            strand_name = strand.get("name", "")

            for outcome in strand.get("learning_outcomes", []):
                outcomes.append({
                    "outcome_id": f"{doc_id}_{outcome.get('outcome_code', '')}",
                    "doc_id": doc_id,
                    "outcome_code": outcome.get("outcome_code", ""),
                    "text": outcome.get("text", ""),
                    "text_ga": outcome.get("text_ga", ""),
                    "subject": subject,
                    "cycle": cycle,
                    "language": language,
                    "strand": strand_name,
                    "strand_unit": outcome.get("strand_unit", ""),
                    "level": outcome.get("level", ""),
                    "action_verbs": outcome.get("action_verbs", []),
                    "key_skills": outcome.get("key_skills", []),
                    "cross_curricular": outcome.get("cross_curricular", False),
                    "extracted_at": datetime.utcnow().isoformat(),
                })

        return outcomes


# =============================================================================
# Extraction Flow
# =============================================================================

class CurriculumSpecificationFlow:
    """
    Flow for extracting curriculum specifications.

    Pipeline:
        1. Read curriculum pages from DuckDB
        2. Filter for specification documents
        3. Extract using BAML
        4. Store in LanceDB + DuckDB
    """

    def __init__(self, config: ExtractionConfig | None = None):
        self.config = config or ExtractionConfig()
        self.source = CurriculumPageSource(self.config)
        self.extractor = BAMLExtractor(model=self.config.model)
        self.sink = SpecificationSink(self.config)

    async def process_document(
        self,
        document: dict[str, Any],
    ) -> dict[str, Any] | None:
        """Process a single document."""
        content = document.get("content", "")
        if not content or len(content) < 1000:
            return None

        # Truncate if too long
        if len(content) > self.config.max_content_length:
            content = content[:self.config.max_content_length]

        specification = await self.extractor.extract_specification(
            document_text=content,
            subject=document.get("subject", "unknown"),
            cycle=document.get("cycle", "junior_cycle"),
            language=document.get("language", "en"),
        )

        if specification:
            # Add source metadata
            specification["source_url"] = document.get("url")
            specification["source"] = document.get("source")
            specification["crawled_at"] = document.get("crawled_at")

        return specification

    async def run(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> dict[str, Any]:
        """
        Run the extraction flow.

        Args:
            limit: Maximum documents to process
            offset: Starting offset

        Returns:
            Stats about the extraction
        """
        import time

        start_time = time.time()

        # 1. Load documents
        documents = self.source.read_documents(limit=limit, offset=offset)
        if not documents:
            return {
                "documents": 0,
                "specifications": 0,
                "outcomes": 0,
                "errors": 0,
                "elapsed_s": time.time() - start_time,
            }

        logger.info("extraction_starting", document_count=len(documents))

        # 2. Process documents
        specifications = []
        errors = 0

        # Process in batches
        for i in range(0, len(documents), self.config.batch_size):
            batch = documents[i:i + self.config.batch_size]

            # Process batch concurrently
            tasks = [self.process_document(doc) for doc in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for j, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error("document_failed", error=str(result))
                    errors += 1
                elif result is not None:
                    specifications.append((result, batch[j].get("url")))

            logger.info(
                "batch_complete",
                batch=i // self.config.batch_size + 1,
                processed=len(batch),
                extracted=sum(1 for r in results if r is not None and not isinstance(r, Exception)),
            )

        # 3. Store specifications
        total_outcomes = 0
        for spec, url in specifications:
            stored = self.sink.store_specification(spec, url)
            total_outcomes += stored.get("outcomes", 0)

        elapsed = time.time() - start_time

        stats = {
            "documents": len(documents),
            "specifications": len(specifications),
            "outcomes": total_outcomes,
            "errors": errors,
            "elapsed_s": elapsed,
            "throughput_docs_per_min": len(documents) / (elapsed / 60) if elapsed > 0 else 0,
        }

        logger.info("extraction_complete", **stats)
        return stats


# =============================================================================
# Exam Paper Extraction Flow
# =============================================================================

class ExamPaperExtractionFlow:
    """
    Flow for extracting exam paper structure.

    Pipeline:
        1. Read exam PDFs from DLT-ingested data
        2. Extract using BAML (ExamPaper, MarkingScheme, ExaminerReport)
        3. Store in LanceDB for question search
    """

    def __init__(self, config: ExtractionConfig | None = None):
        self.config = config or ExtractionConfig()
        self.extractor = BAMLExtractor(model=self.config.model)

    async def extract_exam_paper(
        self,
        document_text: str,
        subject: str,
        year: int,
        level: str,
        paper_number: int = 1,
    ) -> dict[str, Any] | None:
        """Extract exam paper structure using BAML."""
        baml = self.extractor._get_baml_client()

        if baml is None:
            return None

        try:
            # Map level string to enum
            level_map = {
                "higher": "HIGHER",
                "ordinary": "ORDINARY",
                "foundation": "FOUNDATION",
                "common": "COMMON",
            }
            baml_level = level_map.get(level.lower(), "ORDINARY")

            result = await baml.ExtractExamPaperStructure(
                document_text=document_text[:50000],
                subject=subject,
                year=year,
                level=baml_level,
                paper_number=paper_number,
            )

            return self.extractor._baml_to_dict(result)

        except Exception as e:
            logger.error("exam_paper_extraction_failed", error=str(e))
            return None

    async def extract_marking_scheme(
        self,
        document_text: str,
        subject: str,
        year: int,
        level: str,
    ) -> dict[str, Any] | None:
        """Extract marking scheme using BAML."""
        baml = self.extractor._get_baml_client()

        if baml is None:
            return None

        try:
            level_map = {
                "higher": "HIGHER",
                "ordinary": "ORDINARY",
                "foundation": "FOUNDATION",
            }
            baml_level = level_map.get(level.lower(), "ORDINARY")

            result = await baml.ExtractMarkingScheme(
                document_text=document_text[:50000],
                subject=subject,
                year=year,
                level=baml_level,
            )

            return self.extractor._baml_to_dict(result)

        except Exception as e:
            logger.error("marking_scheme_extraction_failed", error=str(e))
            return None

    async def extract_examiner_report(
        self,
        document_text: str,
        subject: str,
        year: int,
        level: str,
    ) -> dict[str, Any] | None:
        """Extract examiner report insights using BAML."""
        baml = self.extractor._get_baml_client()

        if baml is None:
            return None

        try:
            level_map = {
                "higher": "HIGHER",
                "ordinary": "ORDINARY",
                "foundation": "FOUNDATION",
            }
            baml_level = level_map.get(level.lower(), "ORDINARY")

            result = await baml.ExtractExaminerReportInsights(
                document_text=document_text[:50000],
                subject=subject,
                year=year,
                level=baml_level,
            )

            return self.extractor._baml_to_dict(result)

        except Exception as e:
            logger.error("examiner_report_extraction_failed", error=str(e))
            return None


# =============================================================================
# Convenience Functions
# =============================================================================

async def run_specification_extraction(
    limit: int = 100,
    config: ExtractionConfig | None = None,
) -> dict[str, Any]:
    """
    Run curriculum specification extraction.

    Args:
        limit: Maximum documents to process
        config: Optional configuration

    Returns:
        Extraction statistics
    """
    flow = CurriculumSpecificationFlow(config)
    return await flow.run(limit=limit)


async def extract_single_specification(
    document_text: str,
    subject: str,
    cycle: str = "junior_cycle",
    language: str = "en",
) -> dict[str, Any] | None:
    """
    Extract specification from a single document.

    Args:
        document_text: Document content
        subject: Subject code
        cycle: Education cycle
        language: Document language

    Returns:
        Extracted specification or None
    """
    extractor = BAMLExtractor()
    return await extractor.extract_specification(
        document_text=document_text,
        subject=subject,
        cycle=cycle,
        language=language,
    )


# =============================================================================
# CLI Entry Point
# =============================================================================

if __name__ == "__main__":
    import argparse
    import logging

    parser = argparse.ArgumentParser(description="Extract curriculum specifications")
    parser.add_argument("--database", default=DEFAULT_DUCKDB_PATH)
    parser.add_argument("--lancedb", default=DEFAULT_LANCEDB_PATH)
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--model", default="claude-3-5-sonnet-20241022")
    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    )

    config = ExtractionConfig(
        duckdb_path=args.database,
        lancedb_path=args.lancedb,
        model=args.model,
    )

    result = asyncio.run(run_specification_extraction(limit=args.limit, config=config))

    print(f"Documents processed: {result['documents']}")
    print(f"Specifications extracted: {result['specifications']}")
    print(f"Learning outcomes: {result['outcomes']}")
    print(f"Errors: {result['errors']}")
    print(f"Time: {result['elapsed_s']:.2f}s")
