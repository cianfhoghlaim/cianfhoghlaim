"""
Research Knowledge Graph for bunchloch document collection.

Migrated from sruth.taighde.knowledge_graph.

Provides unified research retrieval combining:
- LightRAG: Dual retrieval (local + global) with entity extraction
- Cognee: AI memory and session context
- Memgraph: Cypher queries for structured relationships

Features:
- Dual retrieval modes (local=entity-focused, global=theme-focused)
- Session memory for agent context
- Learning path computation via prerequisite chains
- Federated search across all backends

Usage:
    from graph.research import ResearchGraph

    graph = ResearchGraph()
    await graph.initialize()
    results = await graph.search("Java OOP concepts", include=["lightrag", "memgraph"])
"""

import asyncio
import os
from pathlib import Path
from typing import Any, Literal

import structlog

from ._shared import MemgraphClient

logger = structlog.get_logger(__name__)

# Storage configuration
LIGHTRAG_WORKING_DIR = os.getenv(
    "LIGHTRAG_WORKING_DIR",
    str(Path(__file__).parent.parent.parent.parent / "storage" / "lightrag" / "research"),
)

COGNEE_DATA_DIR = os.getenv(
    "COGNEE_DATA_DIR",
    "./storage/cognee/research",
)

# Types
QueryMode = Literal["naive", "local", "global", "hybrid", "mix"]
BackendType = Literal["lightrag", "memgraph", "cognee"]


class ResearchLightRAG:
    """
    LightRAG client for research document knowledge graph.

    Provides dual retrieval capabilities:
    - Local: Entity-focused queries (who, what, where)
    - Global: Theme-focused queries (why, how, trends)
    - Hybrid: Combines both for comprehensive results
    """

    def __init__(
        self,
        working_dir: str | Path | None = None,
        model: str = "claude-sonnet-4-20250514",
        embedding_model: str = "BAAI/bge-m3",
    ):
        self.working_dir = Path(working_dir or LIGHTRAG_WORKING_DIR)
        self.model = model
        self.embedding_model = embedding_model
        self._rag = None
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize LightRAG instance and storage."""
        if self._initialized:
            return

        try:
            import litellm
            from lightrag import LightRAG

            self.working_dir.mkdir(parents=True, exist_ok=True)

            async def llm_func(prompt: str, **kwargs) -> str:
                response = await litellm.acompletion(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    **kwargs,
                )
                return response.choices[0].message.content

            async def embed_func(texts: list[str]) -> Any:
                import numpy as np
                from sentence_transformers import SentenceTransformer

                model = SentenceTransformer(self.embedding_model)
                embeddings = model.encode(texts, normalize_embeddings=True)
                return np.array(embeddings)

            self._rag = LightRAG(
                working_dir=str(self.working_dir),
                llm_model_func=llm_func,
                embedding_func=embed_func,
                chunk_token_size=1200,
                chunk_overlap_token_size=100,
                kv_storage="JsonKVStorage",
                vector_storage="NanoVectorDBStorage",
                graph_storage="NetworkXStorage",
            )

            await self._rag.initialize_storages()
            self._initialized = True
            logger.info("research_lightrag_initialized", working_dir=str(self.working_dir))

        except ImportError as e:
            logger.error("lightrag_import_error", error=str(e))
            raise RuntimeError("LightRAG not installed. Install with: pip install lightrag-hku") from e

    async def close(self) -> None:
        """Finalize and close LightRAG storage."""
        if self._rag and self._initialized:
            await self._rag.finalize_storages()
            self._initialized = False
            logger.info("research_lightrag_closed")

    async def insert_documents(
        self,
        documents: list[str],
        batch_size: int = 10,
    ) -> dict[str, Any]:
        """Insert documents into LightRAG knowledge graph."""
        if not self._initialized:
            await self.initialize()

        inserted = 0
        failed = 0

        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            try:
                text = "\n\n---\n\n".join(batch)
                await self._rag.ainsert(text)
                inserted += len(batch)
            except Exception as e:
                failed += len(batch)
                logger.error("lightrag_insert_error", error=str(e))

        logger.info("lightrag_insert_complete", inserted=inserted, failed=failed)
        return {"inserted": inserted, "failed": failed, "total": len(documents)}

    async def query(
        self,
        question: str,
        mode: QueryMode = "hybrid",
        top_k: int = 10,
    ) -> str:
        """Query the knowledge graph."""
        if not self._initialized:
            await self.initialize()

        try:
            from lightrag import QueryParam

            result = await self._rag.aquery(
                question,
                param=QueryParam(mode=mode, top_k=top_k),
            )
            logger.debug("lightrag_query", question=question[:100], mode=mode)
            return result

        except Exception as e:
            logger.error("lightrag_query_error", error=str(e))
            return f"Error querying LightRAG: {e}"

    async def query_local(self, question: str, top_k: int = 10) -> str:
        """Local query: Entity-focused retrieval."""
        return await self.query(question, mode="local", top_k=top_k)

    async def query_global(self, question: str, top_k: int = 10) -> str:
        """Global query: Theme-focused retrieval."""
        return await self.query(question, mode="global", top_k=top_k)

    async def query_hybrid(self, question: str, top_k: int = 10) -> str:
        """Hybrid query: Combines local and global."""
        return await self.query(question, mode="hybrid", top_k=top_k)

    async def get_entities(self) -> list[dict[str, Any]]:
        """Get all extracted entities from the knowledge graph."""
        if not self._initialized:
            await self.initialize()

        try:
            if hasattr(self._rag, "_graph"):
                entities = []
                for node_id, node_data in self._rag._graph.nodes(data=True):
                    entities.append({
                        "id": node_id,
                        "type": node_data.get("type", "unknown"),
                        "description": node_data.get("description", ""),
                    })
                return entities
        except Exception as e:
            logger.error("lightrag_get_entities_error", error=str(e))
        return []

    async def get_relationships(self) -> list[dict[str, Any]]:
        """Get all extracted relationships from the knowledge graph."""
        if not self._initialized:
            await self.initialize()

        try:
            if hasattr(self._rag, "_graph"):
                relationships = []
                for source, target, edge_data in self._rag._graph.edges(data=True):
                    relationships.append({
                        "source": source,
                        "target": target,
                        "type": edge_data.get("type", "related_to"),
                        "description": edge_data.get("description", ""),
                    })
                return relationships
        except Exception as e:
            logger.error("lightrag_get_relationships_error", error=str(e))
        return []

    @property
    def is_initialized(self) -> bool:
        return self._initialized


class ResearchMemory:
    """
    Cognee memory client for AI agent memory.

    Provides persistent memory with:
    - Knowledge graph construction from documents
    - Semantic search with graph traversal
    - Session context management
    - Multi-hop reasoning
    """

    def __init__(
        self,
        data_dir: str = COGNEE_DATA_DIR,
        llm_model: str = "claude-sonnet-4-20250514",
        embedding_model: str = "BAAI/bge-m3",
    ):
        self.data_dir = data_dir
        self.llm_model = llm_model
        self.embedding_model = embedding_model
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize Cognee with configuration."""
        if self._initialized:
            return

        try:
            import cognee

            cognee.config.set_data_directory(self.data_dir)
            cognee.config.set_llm_model(self.llm_model)
            os.makedirs(self.data_dir, exist_ok=True)

            self._initialized = True
            logger.info("research_memory_initialized", data_dir=self.data_dir)

        except ImportError as e:
            logger.error("cognee_import_error", error=str(e))
            raise RuntimeError("Cognee not installed. Install with: pip install cognee") from e

    async def add_to_memory(
        self,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Add content to Cognee memory."""
        if not self._initialized:
            await self.initialize()

        try:
            import cognee

            await cognee.add(content, metadata=metadata or {})
            await cognee.cognify()

            logger.debug("memory_content_added", content_length=len(content))
            return {"success": True, "content_length": len(content), "metadata": metadata}

        except Exception as e:
            logger.error("cognee_add_error", error=str(e))
            return {"success": False, "error": str(e)}

    async def search(
        self,
        query: str,
        limit: int = 10,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Search memory with semantic + graph retrieval."""
        if not self._initialized:
            await self.initialize()

        try:
            import cognee

            results = await cognee.search(query, limit=limit)

            if filters:
                results = [
                    r for r in results
                    if all(r.get("metadata", {}).get(k) == v for k, v in filters.items())
                ]

            logger.debug("memory_search", query=query[:50], result_count=len(results))
            return results

        except Exception as e:
            logger.error("cognee_search_error", error=str(e))
            return []

    async def get_session_context(
        self,
        session_id: str,
        max_entries: int = 20,
    ) -> str:
        """Get formatted context for a session."""
        entries = await self.search(f"session:{session_id}", limit=max_entries)

        if not entries:
            return "No previous context for this session."

        context_parts = []
        for entry in entries:
            content = entry.get("content", "")[:500]
            source = entry.get("metadata", {}).get("source", "unknown")
            context_parts.append(f"[{source}] {content}")

        return "\n\n".join(context_parts)

    async def add_session_entry(
        self,
        session_id: str,
        content: str,
        entry_type: str = "observation",
        source: str | None = None,
    ) -> dict[str, Any]:
        """Add an entry to session memory."""
        metadata = {"session_id": session_id, "entry_type": entry_type}
        if source:
            metadata["source"] = source
        return await self.add_to_memory(content, metadata)

    async def get_related_concepts(
        self,
        concept: str,
        depth: int = 2,
    ) -> list[dict[str, Any]]:
        """Get concepts related to a given concept via graph traversal."""
        if not self._initialized:
            await self.initialize()

        try:
            import cognee

            results = await cognee.search(f"concepts related to {concept}", limit=20)

            related = []
            for r in results:
                if r.get("type") == "entity" or r.get("type") == "concept":
                    related.append({
                        "concept": r.get("content", r.get("name", "")),
                        "relationship": r.get("relationship", "related_to"),
                        "score": r.get("score", 0),
                    })

            return related[:depth * 5]

        except Exception as e:
            logger.error("cognee_related_error", error=str(e))
            return []

    @property
    def is_initialized(self) -> bool:
        return self._initialized


class ResearchMemgraph:
    """
    Memgraph client for structured curriculum relationships.

    Uses shared MemgraphClient interface.

    Graph Schema:
    - (Document) -[:BELONGS_TO]-> (Course)
    - (Document) -[:COVERS]-> (Topic)
    - (Topic) -[:PREREQUISITE_FOR]-> (Topic)
    - (Course) -[:PART_OF]-> (Subject)
    """

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
    ):
        self._client = MemgraphClient(
            host=host or os.getenv("MEMGRAPH_HOST", "localhost"),
            port=port or int(os.getenv("MEMGRAPH_PORT", "7687")),
        )
        self._initialized = False

    def initialize_schema(self) -> None:
        """Create schema constraints and indexes."""
        self._client.connect()
        self._initialized = True
        logger.info("research_memgraph_initialized")

    def close(self) -> None:
        """Close the database connection."""
        self._client.close()
        self._initialized = False

    def query(self, cypher: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Execute Cypher query and return results."""
        result = self._client.query(cypher, params or {})
        return result.raw_result

    def create_document(
        self,
        file_hash: str,
        file_name: str,
        file_path: str,
        subject: str,
        course_code: str | None = None,
        topics: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create or update a document node with relationships."""
        result = self.query(
            """
            MERGE (d:Document {file_hash: $file_hash})
            SET d.file_name = $file_name,
                d.file_path = $file_path,
                d.subject = $subject
            RETURN d
            """,
            {"file_hash": file_hash, "file_name": file_name, "file_path": file_path, "subject": subject},
        )

        if course_code:
            self.query(
                """
                MATCH (d:Document {file_hash: $file_hash})
                MERGE (c:Course {code: $course_code})
                MERGE (d)-[:BELONGS_TO]->(c)
                """,
                {"file_hash": file_hash, "course_code": course_code},
            )

        if topics:
            for topic in topics:
                self.query(
                    """
                    MATCH (d:Document {file_hash: $file_hash})
                    MERGE (t:Topic {name: $topic})
                    MERGE (d)-[:COVERS]->(t)
                    """,
                    {"file_hash": file_hash, "topic": topic},
                )

        return result[0] if result else {}

    def get_documents_by_course(self, course_code: str) -> list[dict[str, Any]]:
        """Get all documents for a course."""
        return self.query(
            """
            MATCH (d:Document)-[:BELONGS_TO]->(c:Course {code: $course_code})
            RETURN d.file_hash as file_hash, d.file_name as file_name
            """,
            {"course_code": course_code},
        )

    def get_documents_by_topic(self, topic: str) -> list[dict[str, Any]]:
        """Get all documents covering a topic."""
        return self.query(
            """
            MATCH (d:Document)-[:COVERS]->(t:Topic {name: $topic})
            RETURN d.file_hash as file_hash, d.file_name as file_name
            """,
            {"topic": topic},
        )

    def get_prerequisites(self, topic: str, depth: int = 3) -> list[dict[str, Any]]:
        """Get prerequisites for a topic."""
        return self.query(
            f"""
            MATCH path = (p:Topic)-[:PREREQUISITE_FOR*1..{depth}]->(t:Topic {{name: $topic}})
            RETURN p.name as prerequisite, length(path) as depth
            ORDER BY depth, p.name
            """,
            {"topic": topic},
        )

    def get_learning_path(self, topic: str) -> list[str]:
        """Get ordered learning path to a topic."""
        prerequisites = self.get_prerequisites(topic, depth=5)
        sorted_prereqs = sorted(prerequisites, key=lambda x: -x["depth"])
        path = [p["prerequisite"] for p in sorted_prereqs]
        path.append(topic)
        return path

    def get_topic_coverage(self) -> list[dict[str, Any]]:
        """Get document count per topic."""
        return self.query(
            """
            MATCH (d:Document)-[:COVERS]->(t:Topic)
            RETURN t.name as topic, count(d) as document_count
            ORDER BY document_count DESC
            """
        )

    def find_related_documents(self, file_hash: str, limit: int = 10) -> list[dict[str, Any]]:
        """Find documents related to a given document."""
        return self.query(
            """
            MATCH (d1:Document {file_hash: $file_hash})-[:COVERS]->(t:Topic)<-[:COVERS]-(d2:Document)
            WHERE d1 <> d2
            RETURN d2.file_hash as file_hash, d2.file_name as file_name, count(t) as shared_topics
            ORDER BY shared_topics DESC
            LIMIT $limit
            """,
            {"file_hash": file_hash, "limit": limit},
        )


class ResearchGraph:
    """
    Unified interface for federated knowledge graph queries.

    Combines results from:
    - LightRAG: Semantic + entity-based retrieval
    - Memgraph: Structured relationship queries
    - Cognee: AI memory and session context
    """

    def __init__(self):
        self.lightrag = ResearchLightRAG()
        self.memgraph = ResearchMemgraph()
        self.cognee = ResearchMemory()
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize all graph backends."""
        if self._initialized:
            return

        await asyncio.gather(
            self.lightrag.initialize(),
            self.cognee.initialize(),
        )

        try:
            self.memgraph.initialize_schema()
        except Exception as e:
            logger.warning("memgraph_init_failed", error=str(e))

        self._initialized = True
        logger.info("research_graph_initialized")

    async def close(self) -> None:
        """Close all graph backend connections."""
        await self.lightrag.close()
        self.memgraph.close()
        self._initialized = False

    async def search(
        self,
        query: str,
        include: list[BackendType] | None = None,
        limit: int = 10,
    ) -> dict[str, Any]:
        """Search across all graph backends."""
        if not self._initialized:
            await self.initialize()

        include = include or ["lightrag", "memgraph", "cognee"]
        results: dict[str, Any] = {}

        if "lightrag" in include:
            try:
                answer = await self.lightrag.query(query, mode="hybrid", top_k=limit)
                results["lightrag"] = {"type": "lightrag", "answer": answer, "mode": "hybrid"}
            except Exception as e:
                results["lightrag"] = {"error": str(e)}

        if "memgraph" in include:
            try:
                import re
                words = query.lower().split()
                topic_results = []
                for word in words:
                    if len(word) > 3:
                        docs = self.memgraph.get_documents_by_topic(word.capitalize())
                        topic_results.extend(docs[:limit // 2])

                course_match = re.search(r"([A-Z]{2,3}\d{3,4})", query.upper())
                if course_match:
                    course_docs = self.memgraph.get_documents_by_course(course_match.group(1))
                    topic_results.extend(course_docs)

                results["memgraph"] = {"type": "memgraph", "documents": topic_results[:limit]}
            except Exception as e:
                results["memgraph"] = {"error": str(e)}

        if "cognee" in include:
            try:
                cognee_results = await self.cognee.search(query, limit=limit)
                results["cognee"] = {"type": "cognee", "results": cognee_results}
            except Exception as e:
                results["cognee"] = {"error": str(e)}

        results["merged"] = self._merge_results(results, limit)
        return results

    def _merge_results(self, results: dict[str, Any], limit: int) -> list[dict[str, Any]]:
        """Merge and rank results from all backends."""
        merged = []

        if "lightrag" in results and not results["lightrag"].get("error"):
            merged.append({
                "source": "lightrag",
                "type": "answer",
                "content": results["lightrag"].get("answer", ""),
                "score": 1.0,
            })

        if "memgraph" in results and not results["memgraph"].get("error"):
            for doc in results["memgraph"].get("documents", []):
                merged.append({
                    "source": "memgraph",
                    "type": "document",
                    "content": doc.get("file_name", ""),
                    "file_hash": doc.get("file_hash", ""),
                    "score": 0.8,
                })

        if "cognee" in results and not results["cognee"].get("error"):
            for result in results["cognee"].get("results", []):
                merged.append({
                    "source": "cognee",
                    "type": "memory",
                    "content": result.get("content", "")[:200],
                    "score": result.get("score", 0.5),
                })

        merged.sort(key=lambda x: x.get("score", 0), reverse=True)
        return merged[:limit]

    async def add_document(
        self,
        file_hash: str,
        file_name: str,
        file_path: str,
        subject: str,
        content: str,
        course_code: str | None = None,
        topics: list[str] | None = None,
    ) -> dict[str, Any]:
        """Add document to all graph backends."""
        if not self._initialized:
            await self.initialize()

        results = {}

        try:
            results["lightrag"] = await self.lightrag.insert_documents([content])
        except Exception as e:
            results["lightrag"] = {"error": str(e)}

        try:
            self.memgraph.create_document(
                file_hash=file_hash,
                file_name=file_name,
                file_path=file_path,
                subject=subject,
                course_code=course_code,
                topics=topics,
            )
            results["memgraph"] = {"success": True}
        except Exception as e:
            results["memgraph"] = {"error": str(e)}

        try:
            results["cognee"] = await self.cognee.add_to_memory(
                content=content,
                metadata={
                    "file_hash": file_hash,
                    "file_name": file_name,
                    "subject": subject,
                    "course_code": course_code,
                },
            )
        except Exception as e:
            results["cognee"] = {"error": str(e)}

        return results

    async def get_learning_path(self, topic: str) -> list[str]:
        """Get ordered learning path for a topic."""
        return self.memgraph.get_learning_path(topic)

    async def get_session_context(self, session_id: str, max_entries: int = 20) -> str:
        """Get formatted session context from Cognee."""
        return await self.cognee.get_session_context(session_id, max_entries)

    async def get_graph_stats(self) -> dict[str, Any]:
        """Get statistics from all graph backends."""
        stats = {}

        try:
            entities = await self.lightrag.get_entities()
            relationships = await self.lightrag.get_relationships()
            stats["lightrag"] = {"entities": len(entities), "relationships": len(relationships)}
        except Exception:
            stats["lightrag"] = {"error": "unavailable"}

        try:
            topic_coverage = self.memgraph.get_topic_coverage()
            stats["memgraph"] = {"topics": len(topic_coverage), "top_topics": topic_coverage[:5]}
        except Exception:
            stats["memgraph"] = {"error": "unavailable"}

        stats["cognee"] = {"initialized": self.cognee.is_initialized}

        return stats

    @property
    def is_initialized(self) -> bool:
        return self._initialized


__all__ = [
    "ResearchLightRAG",
    "ResearchMemory",
    "ResearchMemgraph",
    "ResearchGraph",
    "QueryMode",
    "BackendType",
]
