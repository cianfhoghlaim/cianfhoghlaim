"""
LightRAG Integration for Curriculum Knowledge Graph.

Provides dual-level knowledge graph retrieval alongside the canonical
Cognee + FalkorDB infrastructure (the agent-observability spec removed
Memgraph + Neo4j from the production stack lineup). LightRAG offers:
- Hybrid graph-vector retrieval
- Entity-relationship extraction
- Citation tracking for academic integrity

The Cognee code-side backend defaults to FalkorDB; Memgraph is the
legacy fallback (set CIANFHOGHLAIM_COGNEE_BACKEND=memgraph to override).

Based on /taighde/teanga/LightRAG/ reference implementation.

Usage:
    from graph.lightrag_curriculum import CurriculumLightRAG

    rag = CurriculumLightRAG()
    await rag.insert("Learning outcome text...")
    results = await rag.query("What are the math learning outcomes?")
"""

from __future__ import annotations

import asyncio
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

logger = logging.getLogger(__name__)

# Default working directory for LightRAG data
DEFAULT_WORKING_DIR = Path(__file__).parents[2] / "storage" / "data" / "lightrag"


@dataclass
class LightRAGConfig:
    """Configuration for LightRAG curriculum integration."""

    working_dir: Path = field(default_factory=lambda: DEFAULT_WORKING_DIR)
    # The Cognee code-side backend defaults to FalkorDB (per
    # CIANFHOGHLAIM_COGNEE_BACKEND). Memgraph remains as a legacy
    # fallback for operators who need it.
    graph_storage: str = "falkordb"
    vector_storage: str = "lancedb"  # Use existing LanceDB
    llm_provider: str = "litellm"
    llm_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    chunk_size: int = 1000
    chunk_overlap: int = 100
    entity_types: list[str] = field(
        default_factory=lambda: [
            "Subject",
            "Strand",
            "StrandUnit",
            "LearningOutcome",
            "Skill",
            "Concept",
            "Topic",
            "Level",
        ]
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "working_dir": str(self.working_dir),
            "graph_storage": self.graph_storage,
            "vector_storage": self.vector_storage,
            "llm_provider": self.llm_provider,
            "llm_model": self.llm_model,
            "embedding_model": self.embedding_model,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "entity_types": self.entity_types,
        }


@dataclass
class QueryResult:
    """Result from a LightRAG query."""

    query: str
    mode: str
    response: str
    sources: list[dict[str, Any]] = field(default_factory=list)
    entities: list[dict[str, Any]] = field(default_factory=list)
    relations: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "query": self.query,
            "mode": self.mode,
            "response": self.response,
            "source_count": len(self.sources),
            "entity_count": len(self.entities),
            "relation_count": len(self.relations),
            "metadata": self.metadata,
        }


class CurriculumLightRAG:
    """
    LightRAG wrapper for curriculum knowledge graph operations.

    Provides dual-level retrieval:
    - Graph queries: Navigate curriculum hierarchy
    - Vector queries: Semantic similarity search
    - Hybrid queries: Combine both approaches

    Integrates with existing Memgraph for graph storage and
    LanceDB for vector storage.
    """

    def __init__(self, config: LightRAGConfig | None = None):
        """
        Initialize LightRAG for curriculum.

        Args:
            config: LightRAG configuration
        """
        self.config = config or LightRAGConfig()
        self._rag = None
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize LightRAG instance."""
        if self._initialized:
            return

        # Ensure working directory exists
        self.config.working_dir.mkdir(parents=True, exist_ok=True)

        try:
            from lightrag import LightRAG, QueryParam
            from lightrag.llm import (
                gpt_4o_mini_complete,
                openai_embedding,
            )

            # Configure LightRAG with LiteLLM for model flexibility
            self._rag = LightRAG(
                working_dir=str(self.config.working_dir),
                llm_model_func=self._get_llm_func(),
                embedding_func=self._get_embedding_func(),
                chunk_token_size=self.config.chunk_size,
                chunk_overlap_token_size=self.config.chunk_overlap,
            )

            self._initialized = True
            logger.info("LightRAG initialized successfully")

        except ImportError as e:
            logger.warning(f"LightRAG not installed: {e}")
            self._initialized = False

    def _get_llm_func(self):
        """Get LLM function based on config."""
        try:
            import litellm

            async def litellm_complete(prompt: str, **kwargs) -> str:
                response = await litellm.acompletion(
                    model=self.config.llm_model,
                    messages=[{"role": "user", "content": prompt}],
                    **kwargs,
                )
                return response.choices[0].message.content

            return litellm_complete

        except ImportError:
            # Fallback to OpenAI direct
            from lightrag.llm import gpt_4o_mini_complete
            return gpt_4o_mini_complete

    def _get_embedding_func(self):
        """Get embedding function based on config."""
        try:
            import litellm

            async def litellm_embedding(texts: list[str]) -> list[list[float]]:
                response = await litellm.aembedding(
                    model=self.config.embedding_model,
                    input=texts,
                )
                return [item["embedding"] for item in response.data]

            return litellm_embedding

        except ImportError:
            from lightrag.llm import openai_embedding
            return openai_embedding

    async def insert(
        self,
        text: str,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """
        Insert curriculum text into the knowledge graph.

        Args:
            text: Curriculum content to insert
            metadata: Optional metadata (subject, level, etc.)

        Returns:
            True if insertion successful
        """
        await self.initialize()

        if not self._rag:
            logger.error("LightRAG not initialized")
            return False

        try:
            # Add metadata as context if provided
            if metadata:
                context = f"[Subject: {metadata.get('subject', 'Unknown')}] "
                context += f"[Level: {metadata.get('level', 'Unknown')}] "
                text = context + text

            await self._rag.ainsert(text)
            logger.info(f"Inserted {len(text)} chars into LightRAG")
            return True

        except Exception as e:
            logger.error(f"LightRAG insert failed: {e}")
            return False

    async def batch_insert(
        self,
        texts: list[str],
        metadata_list: list[dict[str, Any]] | None = None,
    ) -> int:
        """
        Insert multiple curriculum texts.

        Args:
            texts: List of curriculum content
            metadata_list: Optional list of metadata dicts

        Returns:
            Number of successful insertions
        """
        await self.initialize()

        if not self._rag:
            return 0

        metadata_list = metadata_list or [{}] * len(texts)
        success_count = 0

        for text, metadata in zip(texts, metadata_list, strict=False):
            if await self.insert(text, metadata):
                success_count += 1

        logger.info(f"Batch inserted {success_count}/{len(texts)} texts")
        return success_count

    async def query(
        self,
        query: str,
        mode: Literal["naive", "local", "global", "hybrid"] = "hybrid",
        only_need_context: bool = False,
    ) -> QueryResult:
        """
        Query the curriculum knowledge graph.

        Args:
            query: Natural language query
            mode: Query mode:
                - naive: Simple vector search
                - local: Entity-focused search
                - global: Relationship traversal
                - hybrid: Combine all approaches
            only_need_context: Return only context, not generated answer

        Returns:
            QueryResult with response and sources
        """
        await self.initialize()

        if not self._rag:
            return QueryResult(
                query=query,
                mode=mode,
                response="LightRAG not initialized",
            )

        try:
            from lightrag import QueryParam

            param = QueryParam(
                mode=mode,
                only_need_context=only_need_context,
            )

            response = await self._rag.aquery(query, param=param)

            return QueryResult(
                query=query,
                mode=mode,
                response=response if isinstance(response, str) else str(response),
                metadata={"only_context": only_need_context},
            )

        except Exception as e:
            logger.error(f"LightRAG query failed: {e}")
            return QueryResult(
                query=query,
                mode=mode,
                response=f"Query failed: {e}",
            )

    async def get_entities(self, entity_type: str | None = None) -> list[dict[str, Any]]:
        """
        Get extracted entities from the knowledge graph.

        Args:
            entity_type: Optional filter by entity type

        Returns:
            List of entity dictionaries
        """
        await self.initialize()

        if not self._rag:
            return []

        try:
            # Access internal graph storage
            entities = []
            # Note: Implementation depends on LightRAG internals
            # This is a placeholder for the actual entity retrieval
            return entities

        except Exception as e:
            logger.error(f"Failed to get entities: {e}")
            return []

    async def get_relations(
        self,
        source_entity: str | None = None,
        relation_type: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Get extracted relations from the knowledge graph.

        Args:
            source_entity: Optional filter by source entity
            relation_type: Optional filter by relation type

        Returns:
            List of relation dictionaries
        """
        await self.initialize()

        if not self._rag:
            return []

        try:
            relations = []
            # Placeholder for actual relation retrieval
            return relations

        except Exception as e:
            logger.error(f"Failed to get relations: {e}")
            return []


class CurriculumRAGProvider:
    """
    Unified RAG provider combining LightRAG with existing graph infrastructure.

    Provides a single interface for:
    - LightRAG: Entity extraction and hybrid retrieval
    - Cognee: AI memory and contextual understanding
    - Memgraph: Direct Cypher queries for structured data
    """

    def __init__(
        self,
        lightrag_config: LightRAGConfig | None = None,
        memgraph_uri: str | None = None,
    ):
        """
        Initialize unified RAG provider.

        Args:
            lightrag_config: Configuration for LightRAG
            memgraph_uri: Memgraph connection URI (legacy fallback;
                default is `bolt://memgraph:7687`. The Cognee code-side
                default backend is FalkorDB per CIANFHOGHLAIM_COGNEE_BACKEND.)
        """
        self.lightrag = CurriculumLightRAG(lightrag_config)
        self.memgraph_uri = memgraph_uri or os.getenv(
            "MEMGRAPH_URI", "bolt://memgraph:7687"
        )

    async def initialize(self) -> None:
        """Initialize all components."""
        await self.lightrag.initialize()
        # Initialize Memgraph connection if needed

    async def hybrid_query(
        self,
        query: str,
        use_lightrag: bool = True,
        use_memgraph: bool = True,
    ) -> dict[str, Any]:
        """
        Execute hybrid query across all RAG systems.

        Args:
            query: Natural language query
            use_lightrag: Include LightRAG results
            use_memgraph: Include Memgraph graph traversal

        Returns:
            Combined results from all systems
        """
        results: dict[str, Any] = {"query": query}

        if use_lightrag:
            lightrag_result = await self.lightrag.query(query, mode="hybrid")
            results["lightrag"] = lightrag_result.to_dict()

        if use_memgraph:
            # Execute Memgraph query for structured curriculum data
            # This would use the existing MemgraphClient
            results["memgraph"] = {"status": "available"}

        return results


# =============================================================================
# Factory Function
# =============================================================================

def create_curriculum_lightrag(
    working_dir: str | Path | None = None,
    llm_model: str = "gpt-4o-mini",
    embedding_model: str = "text-embedding-3-small",
) -> CurriculumLightRAG:
    """
    Create a configured CurriculumLightRAG instance.

    Args:
        working_dir: Storage directory
        llm_model: LLM model identifier
        embedding_model: Embedding model identifier

    Returns:
        Configured CurriculumLightRAG instance
    """
    config = LightRAGConfig(
        working_dir=Path(working_dir) if working_dir else DEFAULT_WORKING_DIR,
        llm_model=llm_model,
        embedding_model=embedding_model,
    )
    return CurriculumLightRAG(config)


# =============================================================================
# CLI Entry Point
# =============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="LightRAG Curriculum Knowledge Graph")
    subparsers = parser.add_subparsers(dest="command")

    # Insert command
    insert_parser = subparsers.add_parser("insert", help="Insert text into graph")
    insert_parser.add_argument("text", help="Text to insert")
    insert_parser.add_argument("--subject", help="Subject metadata")

    # Query command
    query_parser = subparsers.add_parser("query", help="Query the graph")
    query_parser.add_argument("query", help="Query text")
    query_parser.add_argument(
        "--mode",
        default="hybrid",
        choices=["naive", "local", "global", "hybrid"],
    )

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    rag = CurriculumLightRAG()

    if args.command == "insert":
        metadata = {"subject": args.subject} if args.subject else None
        success = asyncio.run(rag.insert(args.text, metadata))
        print("Inserted" if success else "Failed")

    elif args.command == "query":
        result = asyncio.run(rag.query(args.query, mode=args.mode))
        print(f"Mode: {result.mode}")
        print(f"Response: {result.response}")
