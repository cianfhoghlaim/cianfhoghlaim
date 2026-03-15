"""
Resource definitions for indexing and knowledge graph pipelines.

Provides:
- LanceDB connection for vector storage
- Memgraph connection for static knowledge graphs
- FalkorDB connection for temporal graphs (Graphiti)
- Embedding model configuration
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Optional

from dagster import ConfigurableResource, EnvVar
from pydantic import Field

if TYPE_CHECKING:
    pass


class LanceDBResource(ConfigurableResource):
    """LanceDB vector database resource.

    Provides connection to LanceDB for vector similarity search,
    full-text search, and hybrid search.

    Example:
        ```python
        @asset(required_resource_keys={"lancedb"})
        def my_asset(context):
            db = context.resources.lancedb.get_connection()
            table = db.open_table("embeddings")
        ```
    """

    uri: str = Field(
        default="./data/github_intelligence.lancedb",
        description="Path to LanceDB database"
    )
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="SentenceTransformer model for embeddings"
    )

    def get_connection(self):
        """Get LanceDB connection."""
        import lancedb
        return lancedb.connect(self.uri)

    def get_embedding_fn(self):
        """Get embedding function for LanceDB."""
        from cocoindex.embeddings import EmbeddingFunction
        return EmbeddingFunction(self.embedding_model)


class MemgraphResource(ConfigurableResource):
    """Memgraph graph database resource for static knowledge.

    Uses the Neo4j Bolt driver which is compatible with Memgraph.

    Example:
        ```python
        @asset(required_resource_keys={"memgraph"})
        def my_asset(context):
            driver = context.resources.memgraph.get_driver()
            with driver.session() as session:
                session.run("MATCH (n) RETURN n LIMIT 10")
        ```
    """

    uri: str = Field(
        default="bolt://localhost:7687",
        description="Memgraph bolt URI"
    )
    user: Optional[str] = Field(default=None, description="Username")
    password: Optional[str] = Field(default=None, description="Password")

    def get_driver(self):
        """Get Neo4j/Memgraph driver."""
        from neo4j import GraphDatabase
        auth = (self.user, self.password) if self.user else None
        return GraphDatabase.driver(self.uri, auth=auth)


class FalkorDBResource(ConfigurableResource):
    """FalkorDB resource for temporal knowledge (Graphiti).

    Connects to FalkorDB for storing temporal knowledge graphs
    with bi-temporal edge properties.

    Example:
        ```python
        @asset(required_resource_keys={"falkordb"})
        def my_asset(context):
            client = context.resources.falkordb.get_raw_client()
            graph = client.select_graph("temporal_knowledge")
        ```
    """

    host: str = Field(default="localhost", description="FalkorDB host")
    port: int = Field(default=6379, description="FalkorDB port")

    def get_graphiti_client(self):
        """Get Graphiti client for temporal graph operations."""
        try:
            from graphiti_core import Graphiti
            return Graphiti(
                uri=f"bolt://{self.host}:{self.port}",
            )
        except ImportError:
            raise ImportError(
                "graphiti-core not installed. Run: pip install graphiti-core"
            )

    def get_raw_client(self):
        """Get raw FalkorDB client."""
        try:
            from falkordb import FalkorDB
            return FalkorDB(host=self.host, port=self.port)
        except ImportError:
            raise ImportError(
                "falkordb not installed. Run: pip install falkordb"
            )


class EmbeddingResource(ConfigurableResource):
    """Embedding model resource.

    Provides sentence transformer models for generating embeddings.

    Example:
        ```python
        @asset(required_resource_keys={"embeddings"})
        def my_asset(context):
            model = context.resources.embeddings.get_model()
            vectors = model.encode(["text1", "text2"])
        ```
    """

    model_name: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="SentenceTransformer model name"
    )
    device: str = Field(default="cpu", description="Device to run model on")

    def get_model(self):
        """Get SentenceTransformer model."""
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer(self.model_name, device=self.device)

    def encode(self, texts: list[str]) -> list:
        """Encode texts to embeddings."""
        model = self.get_model()
        return model.encode(texts).tolist()


def build_indexing_resources() -> dict:
    """Build resource instances for Definitions.

    Returns:
        Dictionary of resource name to resource instance
    """
    return {
        "lancedb": LanceDBResource(
            uri=os.getenv("LANCEDB_URI", "./data/github_intelligence.lancedb"),
        ),
        "memgraph": MemgraphResource(
            uri=os.getenv("MEMGRAPH_URI", "bolt://localhost:7687"),
            user=os.getenv("MEMGRAPH_USER"),
            password=os.getenv("MEMGRAPH_PASSWORD"),
        ),
        "falkordb": FalkorDBResource(
            host=os.getenv("FALKORDB_HOST", "localhost"),
            port=int(os.getenv("FALKORDB_PORT", "6379")),
        ),
        "embeddings": EmbeddingResource(),
    }


# Build resources at module load time
indexing_resources = build_indexing_resources()
