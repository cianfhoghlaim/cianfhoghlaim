"""
Curriculum Query Engine.

Executes queries across 6 modes with knowledge graph integration,
vector search, and curriculum-specific retrieval strategies.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from .query_modes import CurriculumQueryMode, CurriculumQueryParam

logger = logging.getLogger(__name__)


@dataclass
class RetrievedChunk:
    """A retrieved document chunk with metadata."""

    chunk_id: str
    content: str
    score: float

    # Source information
    doc_id: str
    doc_title: str
    source_type: str  # ncca, sec, circular

    # Curriculum metadata
    subject: Optional[str] = None
    level: Optional[str] = None
    strand: Optional[str] = None
    learning_outcome_codes: list[str] = field(default_factory=list)

    # Retrieval metadata
    retrieval_method: str = ""  # vector, keyword, graph
    graph_distance: Optional[int] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "content": self.content,
            "score": self.score,
            "doc_id": self.doc_id,
            "doc_title": self.doc_title,
            "source_type": self.source_type,
            "subject": self.subject,
            "level": self.level,
            "strand": self.strand,
            "learning_outcome_codes": self.learning_outcome_codes,
            "retrieval_method": self.retrieval_method,
            "graph_distance": self.graph_distance,
        }


@dataclass
class QueryResult:
    """Result of a curriculum query."""

    query: str
    mode: CurriculumQueryMode
    chunks: list[RetrievedChunk]

    # Execution metadata
    total_chunks_found: int = 0
    execution_time_ms: float = 0.0
    cache_hit: bool = False

    # Graph context (for LOCAL/GLOBAL/HYBRID modes)
    entities_found: list[dict[str, Any]] = field(default_factory=list)
    relations_found: list[dict[str, Any]] = field(default_factory=list)

    # Keywords extracted
    keywords: list[str] = field(default_factory=list)

    # Prerequisite chain (for PREREQUISITE mode)
    prerequisite_chain: list[dict[str, Any]] = field(default_factory=list)

    # Assessment alignment (for ASSESSMENT mode)
    aligned_questions: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "mode": self.mode.value,
            "chunks": [c.to_dict() for c in self.chunks],
            "total_chunks_found": self.total_chunks_found,
            "execution_time_ms": self.execution_time_ms,
            "cache_hit": self.cache_hit,
            "entities_found": self.entities_found,
            "relations_found": self.relations_found,
            "keywords": self.keywords,
            "prerequisite_chain": self.prerequisite_chain,
            "aligned_questions": self.aligned_questions,
        }


class CurriculumQueryEngine:
    """
    Execute queries across 6 modes.

    Based on LightRAG operate.py patterns with curriculum-specific extensions.
    """

    def __init__(
        self,
        vector_store: Any = None,
        graph_store: Any = None,
        text_store: Any = None,
        cache_manager: Any = None,
        reranker: Any = None,
        llm_client: Any = None,
    ):
        """
        Initialize query engine.

        Args:
            vector_store: Vector database (LanceDB/Qdrant)
            graph_store: Graph database (Memgraph/FalkorDB)
            text_store: Text search (Elasticsearch)
            cache_manager: Multi-level cache
            reranker: Reranking pipeline
            llm_client: LLM for keyword extraction
        """
        self.vector_store = vector_store
        self.graph_store = graph_store
        self.text_store = text_store
        self.cache_manager = cache_manager
        self.reranker = reranker
        self.llm_client = llm_client

    async def query(
        self,
        query_text: str,
        params: Optional[CurriculumQueryParam] = None,
    ) -> QueryResult:
        """
        Execute a query using the specified mode.

        Args:
            query_text: The query string
            params: Query parameters (default: MIX mode)

        Returns:
            QueryResult with retrieved chunks and metadata
        """
        import time

        start_time = time.time()
        params = params or CurriculumQueryParam()

        # Check cache first
        if params.use_cache and self.cache_manager:
            cached = await self.cache_manager.get_query(
                query_text, params.mode.value, params.to_dict()
            )
            if cached:
                cached.cache_hit = True
                return cached

        # Extract keywords for graph queries
        keywords = await self._extract_keywords(query_text, params)

        # Execute query based on mode
        match params.mode:
            case CurriculumQueryMode.LOCAL:
                result = await self._local_query(query_text, keywords, params)
            case CurriculumQueryMode.GLOBAL:
                result = await self._global_query(query_text, keywords, params)
            case CurriculumQueryMode.HYBRID:
                result = await self._hybrid_query(query_text, keywords, params)
            case CurriculumQueryMode.NAIVE:
                result = await self._naive_vector_query(query_text, params)
            case CurriculumQueryMode.MIX:
                result = await self._mix_query(query_text, keywords, params)
            case CurriculumQueryMode.PREREQUISITE:
                result = await self._prerequisite_chain_query(query_text, params)
            case CurriculumQueryMode.ASSESSMENT:
                result = await self._assessment_aligned_query(query_text, params)
            case _:
                result = await self._mix_query(query_text, keywords, params)

        # Apply reranking
        if params.apply_reranking and self.reranker:
            result.chunks = await self.reranker.rerank(
                query_text, result.chunks, params, top_k=params.top_k
            )

        result.execution_time_ms = (time.time() - start_time) * 1000
        result.keywords = keywords

        # Cache result
        if params.use_cache and self.cache_manager:
            await self.cache_manager.set_query(
                query_text, params.mode.value, params.to_dict(), result
            )

        return result

    async def _extract_keywords(
        self,
        query_text: str,
        params: CurriculumQueryParam,
    ) -> list[str]:
        """Extract keywords for graph queries using LLM."""
        if not self.llm_client:
            # Fallback to simple extraction
            import re

            words = re.findall(r"\b[A-Za-z]{4,}\b", query_text)
            return list(set(words))[:10]

        try:
            # Use LLM for smarter extraction
            response = await self.llm_client.acompletion(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Extract key curriculum concepts from the query. "
                            "Return only a JSON array of strings. "
                            "Focus on educational terms, subjects, topics."
                        ),
                    },
                    {"role": "user", "content": query_text},
                ],
                response_format={"type": "json_object"},
            )
            import json

            data = json.loads(response.choices[0].message.content)
            return data.get("keywords", [])[:15]

        except Exception as e:
            logger.warning(f"Keyword extraction failed: {e}")
            return []

    async def _local_query(
        self,
        query_text: str,
        keywords: list[str],
        params: CurriculumQueryParam,
    ) -> QueryResult:
        """
        LOCAL mode: Entity-focused retrieval.

        Finds entities matching keywords and retrieves their descriptions.
        Best for specific concept lookups.
        """
        chunks = []
        entities = []

        if self.graph_store:
            # Query graph for matching entities
            for keyword in keywords:
                entity_results = await self.graph_store.find_entities(
                    keyword,
                    limit=params.top_k,
                    filters={
                        "subject": params.subject_filter,
                        "level": params.level_filter,
                    },
                )
                entities.extend(entity_results)

            # Convert entities to chunks
            for entity in entities[: params.top_k]:
                chunks.append(
                    RetrievedChunk(
                        chunk_id=entity.get("id", ""),
                        content=entity.get("description", ""),
                        score=entity.get("score", 0.5),
                        doc_id=entity.get("doc_id", ""),
                        doc_title=entity.get("name", ""),
                        source_type=entity.get("source_type", "unknown"),
                        subject=entity.get("subject"),
                        retrieval_method="graph_entity",
                    )
                )

        return QueryResult(
            query=query_text,
            mode=CurriculumQueryMode.LOCAL,
            chunks=chunks,
            total_chunks_found=len(chunks),
            entities_found=entities,
        )

    async def _global_query(
        self,
        query_text: str,
        keywords: list[str],
        params: CurriculumQueryParam,
    ) -> QueryResult:
        """
        GLOBAL mode: Relationship-focused retrieval.

        Explores relationships between concepts.
        Best for understanding connections and prerequisites.
        """
        chunks = []
        relations = []

        if self.graph_store:
            # Query graph for relationships
            for keyword in keywords:
                relation_results = await self.graph_store.find_relations(
                    keyword,
                    limit=params.top_k,
                    max_hops=2,
                )
                relations.extend(relation_results)

            # Convert relations to chunks
            for rel in relations[: params.top_k]:
                content = f"{rel.get('source_name')} → {rel.get('relation_type')} → {rel.get('target_name')}"
                if rel.get("description"):
                    content += f"\n{rel.get('description')}"

                chunks.append(
                    RetrievedChunk(
                        chunk_id=rel.get("id", ""),
                        content=content,
                        score=rel.get("score", 0.5),
                        doc_id=rel.get("doc_id", ""),
                        doc_title=rel.get("source_name", ""),
                        source_type=rel.get("source_type", "unknown"),
                        retrieval_method="graph_relation",
                        graph_distance=rel.get("hops", 1),
                    )
                )

        return QueryResult(
            query=query_text,
            mode=CurriculumQueryMode.GLOBAL,
            chunks=chunks,
            total_chunks_found=len(chunks),
            relations_found=relations,
        )

    async def _hybrid_query(
        self,
        query_text: str,
        keywords: list[str],
        params: CurriculumQueryParam,
    ) -> QueryResult:
        """
        HYBRID mode: Combined LOCAL + GLOBAL.

        Merges entity and relationship results.
        """
        local_result, global_result = await asyncio.gather(
            self._local_query(query_text, keywords, params),
            self._global_query(query_text, keywords, params),
        )

        # Merge and deduplicate
        seen_ids = set()
        merged_chunks = []

        for chunk in local_result.chunks + global_result.chunks:
            if chunk.chunk_id not in seen_ids:
                seen_ids.add(chunk.chunk_id)
                merged_chunks.append(chunk)

        # Sort by score
        merged_chunks.sort(key=lambda x: x.score, reverse=True)

        return QueryResult(
            query=query_text,
            mode=CurriculumQueryMode.HYBRID,
            chunks=merged_chunks[: params.top_k],
            total_chunks_found=len(merged_chunks),
            entities_found=local_result.entities_found,
            relations_found=global_result.relations_found,
        )

    async def _naive_vector_query(
        self,
        query_text: str,
        params: CurriculumQueryParam,
    ) -> QueryResult:
        """
        NAIVE mode: Pure vector search.

        Simple semantic search without graph augmentation.
        """
        chunks = []

        if self.vector_store:
            # Build filters
            filters = {}
            if params.subject_filter:
                filters["subject"] = params.subject_filter
            if params.level_filter:
                filters["level"] = params.level_filter

            results = await self.vector_store.search(
                query_text,
                top_k=params.top_k,
                filters=filters,
            )

            for r in results:
                chunks.append(
                    RetrievedChunk(
                        chunk_id=r.get("id", ""),
                        content=r.get("content", ""),
                        score=r.get("score", 0.0),
                        doc_id=r.get("doc_id", ""),
                        doc_title=r.get("title", ""),
                        source_type=r.get("source_type", "unknown"),
                        subject=r.get("subject"),
                        level=r.get("level"),
                        retrieval_method="vector",
                    )
                )

        return QueryResult(
            query=query_text,
            mode=CurriculumQueryMode.NAIVE,
            chunks=chunks,
            total_chunks_found=len(chunks),
        )

    async def _mix_query(
        self,
        query_text: str,
        keywords: list[str],
        params: CurriculumQueryParam,
    ) -> QueryResult:
        """
        MIX mode: Knowledge graph + vector chunks (default).

        Combines graph context with vector retrieval.
        """
        # Run graph and vector queries in parallel
        graph_result, vector_result = await asyncio.gather(
            self._hybrid_query(query_text, keywords, params),
            self._naive_vector_query(query_text, params),
        )

        # Weighted merge
        merged_chunks = []
        seen_ids = set()

        # Graph results with boost
        for chunk in graph_result.chunks:
            if chunk.chunk_id not in seen_ids:
                chunk.score *= 1.2  # Boost graph results
                merged_chunks.append(chunk)
                seen_ids.add(chunk.chunk_id)

        # Vector results
        for chunk in vector_result.chunks:
            if chunk.chunk_id not in seen_ids:
                merged_chunks.append(chunk)
                seen_ids.add(chunk.chunk_id)

        merged_chunks.sort(key=lambda x: x.score, reverse=True)

        return QueryResult(
            query=query_text,
            mode=CurriculumQueryMode.MIX,
            chunks=merged_chunks[: params.top_k],
            total_chunks_found=len(merged_chunks),
            entities_found=graph_result.entities_found,
            relations_found=graph_result.relations_found,
        )

    async def _prerequisite_chain_query(
        self,
        query_text: str,
        params: CurriculumQueryParam,
    ) -> QueryResult:
        """
        PREREQUISITE mode: Follow prerequisite chains.

        Traverses REQUIRES_PREREQUISITE edges in the knowledge graph.
        """
        chunks = []
        prerequisite_chain = []

        if self.graph_store:
            # Find the starting concept
            start_entities = await self.graph_store.find_entities(
                query_text,
                limit=1,
                filters={"subject": params.subject_filter},
            )

            if start_entities:
                start_entity = start_entities[0]

                # Traverse prerequisite chain
                chain = await self.graph_store.traverse_prerequisites(
                    start_entity["id"],
                    max_depth=params.max_hop_depth,
                )

                for i, node in enumerate(chain):
                    prerequisite_chain.append(
                        {
                            "order": i,
                            "concept": node.get("name"),
                            "description": node.get("description"),
                            "level": node.get("level"),
                        }
                    )

                    chunks.append(
                        RetrievedChunk(
                            chunk_id=node.get("id", ""),
                            content=node.get("description", ""),
                            score=1.0 - (i * 0.1),  # Earlier in chain = higher score
                            doc_id=node.get("doc_id", ""),
                            doc_title=node.get("name", ""),
                            source_type=node.get("source_type", "unknown"),
                            subject=params.subject_filter,
                            retrieval_method="prerequisite_chain",
                            graph_distance=i,
                        )
                    )

        return QueryResult(
            query=query_text,
            mode=CurriculumQueryMode.PREREQUISITE,
            chunks=chunks,
            total_chunks_found=len(chunks),
            prerequisite_chain=prerequisite_chain,
        )

    async def _assessment_aligned_query(
        self,
        query_text: str,
        params: CurriculumQueryParam,
    ) -> QueryResult:
        """
        ASSESSMENT mode: Learning outcome → exam question mapping.

        Finds SEC exam questions aligned to curriculum learning outcomes.
        """
        chunks = []
        aligned_questions = []

        # First find relevant learning outcomes
        lo_results = await self._naive_vector_query(query_text, params)

        if self.graph_store:
            for chunk in lo_results.chunks[:5]:
                # Find exam questions linked to this learning outcome
                questions = await self.graph_store.find_aligned_questions(
                    learning_outcome_id=chunk.chunk_id,
                    exam_years=params.exam_years,
                    include_marking_schemes=params.include_marking_schemes,
                )

                for q in questions:
                    aligned_questions.append(
                        {
                            "learning_outcome": chunk.doc_title,
                            "question_id": q.get("id"),
                            "question_text": q.get("text"),
                            "exam_year": q.get("year"),
                            "marks": q.get("marks"),
                            "has_marking_scheme": q.get("has_marking_scheme", False),
                        }
                    )

                    chunks.append(
                        RetrievedChunk(
                            chunk_id=q.get("id", ""),
                            content=q.get("text", ""),
                            score=q.get("alignment_score", 0.8),
                            doc_id=q.get("doc_id", ""),
                            doc_title=f"SEC {q.get('year')} Q{q.get('number')}",
                            source_type="sec",
                            subject=params.subject_filter,
                            level=params.level_filter,
                            learning_outcome_codes=[chunk.chunk_id],
                            retrieval_method="assessment_alignment",
                        )
                    )

        return QueryResult(
            query=query_text,
            mode=CurriculumQueryMode.ASSESSMENT,
            chunks=chunks[: params.top_k],
            total_chunks_found=len(chunks),
            aligned_questions=aligned_questions,
        )
