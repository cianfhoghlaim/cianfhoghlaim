"""
Cognee integration for crypto knowledge graph construction.

Uses ECL (Extract-Cognify-Load) pipeline to:
1. Extract entities and relationships from documents
2. Cognify with LLM-powered entity resolution
3. Load into dual-graph architecture (Memgraph + FalkorDB)

The dual-graph approach:
- Memgraph: Static knowledge (protocols, tokens, relationships)
- FalkorDB: Temporal knowledge (events, price movements, agent memory)
"""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator, Optional

import cognee
from cognee.api.v1.cognify import cognify
from cognee.api.v1.search import SearchType


from crypteolas.pipelines.knowledge.graph_schema import (
    CryptoEntitySchema,
    EntityType,
    RelationshipType,
    ETHENA_ONTOLOGY,
)
from crypteolas.config.llm import get_model_id, LITELLM_BASE_URL


# =============================================================================
# Configuration
# =============================================================================


class CogneeConfig:
    """Cognee configuration for crypto domain."""

    # LLM settings (use central config)
    LLM_PROVIDER = "litellm"  # Use LiteLLM proxy
    LLM_MODEL = get_model_id()  # From central config

    # Graph backends
    MEMGRAPH_URI = "bolt://localhost:7687"
    FALKORDB_HOST = "localhost"
    FALKORDB_PORT = 6379

    # Vector store
    LANCEDB_URI = "data/crypto_vectors"

    # Processing
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200


def configure_cognee(
    graph_backend: str = "memgraph",
    vector_backend: str = "lancedb",
    llm_provider: str = "litellm",
    llm_model: Optional[str] = None,
) -> None:
    """
    Configure Cognee for crypto knowledge processing.

    Args:
        graph_backend: Graph database (memgraph, falkordb)
        vector_backend: Vector store (lancedb, qdrant)
        llm_provider: LLM provider
        llm_model: Model identifier
    """
    import os

    # Set LLM configuration
    cognee.config.llm_provider = llm_provider
    cognee.config.llm_model = llm_model or CogneeConfig.LLM_MODEL

    # Set LiteLLM API base if using proxy (use central config)
    if llm_provider == "litellm":
        os.environ["LITELLM_API_BASE"] = LITELLM_BASE_URL

    # Configure graph backend
    if graph_backend == "memgraph":
        cognee.config.graph_database_provider = "memgraph"
        cognee.config.graph_database_url = CogneeConfig.MEMGRAPH_URI
    elif graph_backend == "falkordb":
        cognee.config.graph_database_provider = "falkordb"
        cognee.config.graph_database_url = (
            f"redis://{CogneeConfig.FALKORDB_HOST}:{CogneeConfig.FALKORDB_PORT}"
        )

    # Configure vector backend
    if vector_backend == "lancedb":
        cognee.config.vector_db_provider = "lancedb"
        cognee.config.vector_db_url = CogneeConfig.LANCEDB_URI


# =============================================================================
# Pipeline
# =============================================================================


class CryptoCogneePipeline:
    """
    Cognee pipeline for crypto knowledge extraction.

    Processes documents through:
    1. Chunking with crypto-aware splitting
    2. Entity extraction (protocols, tokens, strategies)
    3. Relationship inference
    4. Graph construction
    """

    def __init__(
        self,
        graph_backend: str = "memgraph",
        vector_backend: str = "lancedb",
    ):
        self.graph_backend = graph_backend
        self.vector_backend = vector_backend

        # Configure Cognee
        configure_cognee(
            graph_backend=graph_backend,
            vector_backend=vector_backend,
        )

        # Initialize seed ontology
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the pipeline with seed ontology."""
        if self._initialized:
            return

        # Reset to clean state (optional)
        # await cognee.prune.prune_data()
        # await cognee.prune.prune_system(metadata=True)

        # Add seed ontology
        await self._seed_ontology()

        self._initialized = True

    async def _seed_ontology(self) -> None:
        """Seed knowledge graph with crypto domain ontology."""
        # Add Ethena ecosystem as seed data
        seed_text = self._generate_seed_text()

        await cognee.add(seed_text, dataset_name="crypto_ontology")
        await cognify(dataset_name="crypto_ontology")

    def _generate_seed_text(self) -> str:
        """Generate seed text from ontology."""
        parts = ["# Crypto DeFi Ontology\n"]

        # Protocols
        parts.append("\n## Protocols\n")
        for protocol in ETHENA_ONTOLOGY.get("protocols", []):
            parts.append(f"- {protocol['name']}: {protocol.get('description', '')}\n")

        # Tokens
        parts.append("\n## Tokens\n")
        for token in ETHENA_ONTOLOGY.get("tokens", []):
            parts.append(
                f"- {token['name']} ({token['symbol']}): "
                f"{token.get('description', '')}\n"
            )

        # Strategies
        parts.append("\n## Yield Strategies\n")
        for strategy in ETHENA_ONTOLOGY.get("yield_strategies", []):
            parts.append(
                f"- {strategy['name']}: {strategy.get('description', '')}\n"
            )

        # Risks
        parts.append("\n## Risk Factors\n")
        for risk in ETHENA_ONTOLOGY.get("risk_factors", []):
            parts.append(f"- {risk['name']}: {risk.get('description', '')}\n")

        return "".join(parts)

    async def add_documents(
        self,
        documents: list[dict[str, Any]],
        dataset_name: str = "crypto_docs",
    ) -> None:
        """
        Add documents to Cognee for processing.

        Args:
            documents: List of document dicts with 'content' and metadata
            dataset_name: Dataset identifier
        """
        for doc in documents:
            content = doc.get("content", "")
            if not content:
                continue

            # Add metadata as prefix
            metadata_prefix = ""
            if doc.get("title"):
                metadata_prefix += f"# {doc['title']}\n\n"
            if doc.get("protocol"):
                metadata_prefix += f"Protocol: {doc['protocol']}\n"
            if doc.get("url"):
                metadata_prefix += f"Source: {doc['url']}\n"

            full_content = metadata_prefix + "\n" + content

            await cognee.add(full_content, dataset_name=dataset_name)

    async def cognify(
        self,
        dataset_name: str = "crypto_docs",
    ) -> dict[str, Any]:
        """
        Run cognification on added documents.

        Extracts entities and relationships into knowledge graph.

        Args:
            dataset_name: Dataset to process

        Returns:
            Processing results
        """
        result = await cognify(dataset_name=dataset_name)
        return {"status": "completed", "dataset": dataset_name, "result": result}

    async def search(
        self,
        query: str,
        search_type: str = "insights",
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Search the knowledge graph.

        Args:
            query: Search query
            search_type: Type of search (insights, chunks, graph_completion)
            limit: Max results

        Returns:
            Search results
        """
        type_map = {
            "insights": SearchType.INSIGHTS,
            "chunks": SearchType.CHUNKS,
            "graph": SearchType.GRAPH_COMPLETION,
        }

        search_type_enum = type_map.get(search_type, SearchType.INSIGHTS)

        results = await cognee.search(
            query_text=query,
            search_type=search_type_enum,
        )

        return results[:limit]

    async def get_graph_context(
        self,
        entity_id: str,
        depth: int = 2,
    ) -> dict[str, Any]:
        """
        Get graph neighborhood for an entity.

        Args:
            entity_id: Entity identifier
            depth: Traversal depth

        Returns:
            Subgraph around entity
        """
        # Use graph completion search
        query = f"What is related to {entity_id}?"
        results = await cognee.search(
            query_text=query,
            search_type=SearchType.GRAPH_COMPLETION,
        )

        return {"entity": entity_id, "context": results}


# =============================================================================
# Graph Operations
# =============================================================================


async def create_entity_node(
    entity_type: EntityType,
    entity_id: str,
    properties: dict[str, Any],
    backend: str = "memgraph",
) -> str:
    """
    Create entity node directly in graph.

    Args:
        entity_type: Type of entity
        entity_id: Unique identifier
        properties: Node properties
        backend: Graph backend

    Returns:
        Node ID
    """
    if backend == "memgraph":
        return await _create_memgraph_node(entity_type.value, entity_id, properties)
    elif backend == "falkordb":
        return await _create_falkordb_node(entity_type.value, entity_id, properties)
    else:
        raise ValueError(f"Unknown backend: {backend}")


async def _create_memgraph_node(
    label: str,
    entity_id: str,
    properties: dict[str, Any],
) -> str:
    """Create node in Memgraph."""
    from neo4j import AsyncGraphDatabase

    driver = AsyncGraphDatabase.driver(CogneeConfig.MEMGRAPH_URI)

    async with driver.session() as session:
        props = {**properties, "id": entity_id}
        prop_str = ", ".join(f"{k}: ${k}" for k in props.keys())

        query = f"CREATE (n:{label} {{{prop_str}}}) RETURN n.id"
        result = await session.run(query, props)
        record = await result.single()

    await driver.close()
    return record["n.id"]


async def _create_falkordb_node(
    label: str,
    entity_id: str,
    properties: dict[str, Any],
) -> str:
    """Create node in FalkorDB."""
    from falkordb import FalkorDB

    db = FalkorDB(
        host=CogneeConfig.FALKORDB_HOST,
        port=CogneeConfig.FALKORDB_PORT,
    )
    graph = db.select_graph("crypto_temporal")

    props = {**properties, "id": entity_id}
    prop_str = ", ".join(f"{k}: '{v}'" for k, v in props.items() if isinstance(v, str))

    query = f"CREATE (n:{label} {{{prop_str}}}) RETURN n.id"
    result = graph.query(query)

    return entity_id


async def create_relationship(
    from_id: str,
    to_id: str,
    relationship_type: RelationshipType,
    properties: Optional[dict[str, Any]] = None,
    backend: str = "memgraph",
) -> bool:
    """
    Create relationship between entities.

    Args:
        from_id: Source entity ID
        to_id: Target entity ID
        relationship_type: Type of relationship
        properties: Relationship properties
        backend: Graph backend

    Returns:
        Success status
    """
    if backend == "memgraph":
        return await _create_memgraph_relationship(
            from_id, to_id, relationship_type.value, properties
        )
    elif backend == "falkordb":
        return await _create_falkordb_relationship(
            from_id, to_id, relationship_type.value, properties
        )
    else:
        raise ValueError(f"Unknown backend: {backend}")


async def _create_memgraph_relationship(
    from_id: str,
    to_id: str,
    rel_type: str,
    properties: Optional[dict[str, Any]] = None,
) -> bool:
    """Create relationship in Memgraph."""
    from neo4j import AsyncGraphDatabase

    driver = AsyncGraphDatabase.driver(CogneeConfig.MEMGRAPH_URI)

    async with driver.session() as session:
        props = properties or {}
        prop_str = ", ".join(f"{k}: ${k}" for k in props.keys()) if props else ""

        query = f"""
        MATCH (a {{id: $from_id}}), (b {{id: $to_id}})
        CREATE (a)-[r:{rel_type} {{{prop_str}}}]->(b)
        RETURN type(r)
        """
        params = {"from_id": from_id, "to_id": to_id, **props}
        result = await session.run(query, params)
        record = await result.single()

    await driver.close()
    return record is not None


async def _create_falkordb_relationship(
    from_id: str,
    to_id: str,
    rel_type: str,
    properties: Optional[dict[str, Any]] = None,
) -> bool:
    """Create relationship in FalkorDB."""
    from falkordb import FalkorDB

    db = FalkorDB(
        host=CogneeConfig.FALKORDB_HOST,
        port=CogneeConfig.FALKORDB_PORT,
    )
    graph = db.select_graph("crypto_temporal")

    query = f"""
    MATCH (a {{id: '{from_id}'}}), (b {{id: '{to_id}'}})
    CREATE (a)-[r:{rel_type}]->(b)
    RETURN type(r)
    """
    result = graph.query(query)

    return len(result.result_set) > 0


# =============================================================================
# Convenience Functions
# =============================================================================


async def cognify_crypto_docs(
    documents: list[dict[str, Any]],
    dataset_name: str = "crypto_docs",
    graph_backend: str = "memgraph",
) -> dict[str, Any]:
    """
    Process crypto documents through Cognee pipeline.

    Args:
        documents: Documents with 'content' field
        dataset_name: Dataset identifier
        graph_backend: Target graph database

    Returns:
        Processing results
    """
    pipeline = CryptoCogneePipeline(graph_backend=graph_backend)
    await pipeline.initialize()
    await pipeline.add_documents(documents, dataset_name)
    result = await pipeline.cognify(dataset_name)

    return result


async def query_knowledge_graph(
    query: str,
    search_type: str = "insights",
    graph_backend: str = "memgraph",
    limit: int = 10,
) -> list[dict[str, Any]]:
    """
    Query crypto knowledge graph.

    Args:
        query: Search query
        search_type: Type of search
        graph_backend: Graph backend
        limit: Max results

    Returns:
        Search results
    """
    pipeline = CryptoCogneePipeline(graph_backend=graph_backend)
    results = await pipeline.search(query, search_type, limit)

    return results


def sync_cognify_docs(
    documents: list[dict[str, Any]],
    dataset_name: str = "crypto_docs",
) -> dict[str, Any]:
    """Synchronous wrapper for cognify_crypto_docs."""
    return asyncio.run(cognify_crypto_docs(documents, dataset_name))


def sync_query(
    query: str,
    search_type: str = "insights",
) -> list[dict[str, Any]]:
    """Synchronous wrapper for query_knowledge_graph."""
    return asyncio.run(query_knowledge_graph(query, search_type))


# =============================================================================
# Integration with DLT Pipeline
# =============================================================================


def load_from_duckdb(
    db_path: str = "data/crypto_analytics.duckdb",
    table_name: str = "firecrawl_crawl",
    protocol_filter: Optional[str] = None,
) -> list[dict[str, Any]]:
    """
    Load documents from DuckDB for Cognee processing.

    Args:
        db_path: DuckDB database path
        table_name: Source table
        protocol_filter: Optional protocol filter

    Returns:
        List of document dicts
    """
    import duckdb

    con = duckdb.connect(db_path)

    query = f"""
        SELECT
            url,
            title,
            markdown as content,
            start_url,
            metadata
        FROM {table_name}
        WHERE markdown IS NOT NULL
    """

    if protocol_filter:
        query += f" AND start_url LIKE '%{protocol_filter}%'"

    results = con.execute(query).fetchall()
    con.close()

    documents = []
    for row in results:
        url, title, content, start_url, metadata = row
        protocol = _extract_protocol(start_url)

        documents.append({
            "url": url,
            "title": title,
            "content": content,
            "protocol": protocol,
            "metadata": metadata or {},
        })

    return documents


def _extract_protocol(url: str) -> str:
    """Extract protocol name from URL."""
    url_lower = url.lower() if url else ""

    protocols = ["ethena", "aave", "pendle", "lido", "eigenlayer", "curve"]
    for p in protocols:
        if p in url_lower:
            return p
    return "unknown"


# =============================================================================
# CLI Runner
# =============================================================================


def run_cognee_pipeline(
    source: str = "duckdb",
    db_path: str = "data/crypto_analytics.duckdb",
    table_name: str = "firecrawl_crawl",
    protocol_filter: Optional[str] = None,
    graph_backend: str = "memgraph",
):
    """
    Run Cognee knowledge graph pipeline.

    Args:
        source: Data source (duckdb, r2)
        db_path: DuckDB path
        table_name: Source table
        protocol_filter: Filter by protocol
        graph_backend: Target graph
    """
    print(f"Loading documents from {source}...")

    if source == "duckdb":
        documents = load_from_duckdb(db_path, table_name, protocol_filter)
    else:
        raise ValueError(f"Unknown source: {source}")

    print(f"Found {len(documents)} documents")

    if not documents:
        print("No documents to process")
        return

    print("Running Cognee pipeline...")
    result = sync_cognify_docs(documents)
    print(f"Pipeline result: {result}")

    # Test query
    print("\nTesting search...")
    results = sync_query("How does Ethena generate yield?")
    for r in results[:3]:
        print(f"- {r}")

    return result


if __name__ == "__main__":
    run_cognee_pipeline()
