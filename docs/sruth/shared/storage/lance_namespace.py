"""LanceDB namespace management with Lakekeeper catalog integration.

Provides Lance namespace handling with the "trojan horse" pattern:
- Lance tables registered as Iceberg tables with table_type=lance property
- S3 storage through Garage
- Namespace discovery and management
- Vector search operations

Usage:
    from sruth.shared.storage.lance_namespace import (
        LanceNamespaceManager,
        EDUCATION_NAMESPACES,
    )

    manager = LanceNamespaceManager()
    await manager.register_table(
        namespace="ireland.oideachas.curriculum",
        table_name="documents",
        dimension=1024,
    )
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

# Standard education namespaces
EDUCATION_NAMESPACES = {
    "ireland": ["oideachas", "curriculum"],
    "uk": ["oileain", "curriculum"],
    "celtic": ["teanga", "language"],
    "alignment": ["alignment", "bilingual"],
}


@dataclass
class LanceTableConfig:
    """Configuration for a Lance table."""

    namespace: str
    table_name: str
    dimension: int
    metric: str = "cosine"  # cosine, euclidean, dot
    vector_column: str = "vector"
    id_column: str = "id"
    text_column: str = "text"

    # Storage
    s3_bucket: str = "lance"
    s3_prefix: str = ""

    # Lakekeeper integration
    register_with_lakekeeper: bool = True
    lakekeeper_uri: str = ""

    # Properties
    properties: dict[str, str] = field(default_factory=dict)

    def get_location(self) -> str:
        """Get S3 location for this table."""
        prefix = self.s3_prefix or self.namespace.replace(".", "/")
        return f"s3://{self.s3_bucket}/{prefix}/{self.table_name}.lance"

    def get_table_properties(self) -> dict[str, str]:
        """Get Iceberg table properties."""
        return {
            "table_type": "lance",
            "dimension": str(self.dimension),
            "metric": self.metric,
            **self.properties,
        }


@dataclass
class LanceNamespaceManager:
    """Manager for Lance namespaces and tables.

    Handles:
    - Namespace creation in Lance sidecar
    - Table registration with Lakekeeper
    - Vector search operations
    """

    # Lakekeeper REST catalog
    lakekeeper_uri: str = "http://lakekeeper:8181"
    warehouse: str = "s3://garage/warehouse"

    # S3/Garage configuration
    s3_endpoint: str = "http://garage:3900"
    s3_access_key: str = "garage_key"
    s3_secret_key: str = "garage_secret"
    s3_bucket: str = "lance"

    # Lance sidecar
    sidecar_uri: str = "http://lance-sidecar:8182"

    def __post_init__(self):
        """Initialize from environment if not provided."""
        self.lakekeeper_uri = os.getenv("LAKEKEEPER_CATALOG_URI", self.lakekeeper_uri)
        self.warehouse = os.getenv("ICEBERG_WAREHOUSE", self.warehouse)
        self.s3_endpoint = os.getenv("GARAGE_ENDPOINT_URL", self.s3_endpoint)
        self.s3_access_key = os.getenv("GARAGE_ACCESS_KEY", self.s3_access_key)
        self.s3_secret_key = os.getenv("GARAGE_SECRET_KEY", self.s3_secret_key)
        self.s3_bucket = os.getenv("LANCEDB_S3_BUCKET", self.s3_bucket)
        self.sidecar_uri = os.getenv("LANCE_SIDECAR_URI", self.sidecar_uri)

    def _get_storage_options(self) -> dict[str, str]:
        """Get S3 storage options for LanceDB with path-style URLs.

        LanceDB uses PyArrow for S3 access. These options are CRITICAL
        for Garage/MinIO which require path-style URLs.

        Returns:
            Storage options dict for lancedb.connect()
        """
        # Determine if we should allow HTTP (non-SSL)
        allow_http = not self.s3_endpoint.startswith("https://")

        return {
            "aws_endpoint": self.s3_endpoint,
            "aws_access_key_id": self.s3_access_key,
            "aws_secret_access_key": self.s3_secret_key,
            "aws_region": "garage",
            "allow_http": str(allow_http).lower(),
            # CRITICAL: Path-style URLs required for Garage/MinIO
            "aws_virtual_hosted_style_request": "false",
        }

    async def register_table(
        self,
        config: LanceTableConfig,
    ) -> dict[str, Any]:
        """Register a Lance table with Lakekeeper.

        Args:
            config: Table configuration

        Returns:
            Table metadata from Lakekeeper
        """
        if not config.register_with_lakekeeper:
            return {"registered": False}

        import requests

        # Build namespace path (dot-separated to slash-separated)
        namespace_path = config.namespace.replace(".", "/")

        # Register with Lakekeeper as Iceberg table
        url = f"{self.lakekeeper_uri}/v1/namespaces/{namespace_path}/tables"

        payload = {
            "name": config.table_name,
            "location": config.get_location(),
            "schema": self._build_schema(config),
            "properties": config.get_table_properties(),
        }

        response = requests.post(url, json=payload)
        response.raise_for_status()

        return response.json()

    def _build_schema(self, config: LanceTableConfig) -> dict[str, str]:
        """Build Iceberg schema for Lance table.

        Args:
            config: Table configuration

        Returns:
            Column schema
        """
        return {
            config.id_column: "VARCHAR",
            config.text_column: "VARCHAR",
            config.vector_column: f"FLOAT[{config.dimension}]",
            "metadata": "JSON",
        }

    async def create_namespace(
        self,
        namespace: str,
    ) -> dict[str, Any]:
        """Create a namespace in Lakekeeper.

        Args:
            namespace: Namespace (dot-separated)

        Returns:
            Namespace metadata
        """
        import requests

        namespace_path = namespace.replace(".", "/")
        url = f"{self.lakekeeper_uri}/v1/namespaces/{namespace_path}"

        # Check if exists
        response = requests.get(url)

        if response.status_code == 200:
            return response.json()  # Already exists

        # Create namespace
        response = requests.post(f"{self.lakekeeper_uri}/v1/namespaces", json={
            "name": namespace_path,
        })

        if response.status_code not in (200, 201):
            # Might be partial path, try creating parent
            parts = namespace_path.split("/")
            for i in range(len(parts)):
                parent = "/".join(parts[:i+1])
                requests.post(f"{self.lakekeeper_uri}/v1/namespaces", json={
                    "name": parent,
                })

        return response.json() if response.status_code == 201 else {}

    async def list_lance_tables(
        self,
        namespace: str | None = None,
    ) -> list[dict[str, Any]]:
        """List Lance tables in a namespace.

        Args:
            namespace: Namespace filter (None for all)

        Returns:
            List of Lance tables
        """
        import requests

        if namespace:
            namespace_path = namespace.replace(".", "/")
            url = f"{self.sidecar_uri}/namespaces/{namespace_path}/tables"
        else:
            url = f"{self.sidecar_uri}/namespaces"

        response = requests.get(url)
        response.raise_for_status()

        tables = response.json()

        # Filter to only Lance tables
        return [
            t for t in tables
            if t.get("properties", {}).get("table_type") == "lance"
        ]

    async def search_vector(
        self,
        namespace: str,
        table_name: str,
        query_vector: list[float],
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Perform vector search on a Lance table.

        Args:
            namespace: Table namespace
            table_name: Table name
            query_vector: Query embedding
            limit: Result limit

        Returns:
            Search results with scores
        """
        try:
            import lancedb
        except ImportError:
            raise ImportError("LanceDB not installed. Install: pip install lancedb")

        # Build LanceDB URI
        table_path = self._get_table_path(namespace, table_name)

        # Connect to LanceDB with path-style S3 options
        db = lancedb.connect(table_path, storage_options=self._get_storage_options())

        # Open table
        table = db.open_table(table_name)

        # Search
        results = table.search(query_vector).limit(limit).to_pandas()

        return results.to_dict("records")

    def _get_table_path(self, namespace: str, table_name: str) -> str:
        """Get S3 path for a table."""
        bucket = os.getenv("LANCEDB_S3_BUCKET", "lance")
        prefix = namespace.replace(".", "/")
        return f"s3://{bucket}/{prefix}/{table_name}.lance"

    async def upsert_embeddings(
        self,
        namespace: str,
        table_name: str,
        ids: list[str],
        vectors: list[list[float]],
        metadata: list[dict[str, Any]] | None = None,
    ) -> int:
        """Upsert embeddings to a Lance table.

        Args:
            namespace: Table namespace
            table_name: Table name
            ids: Document IDs
            vectors: Embedding vectors
            metadata: Optional metadata

        Returns:
            Number of vectors upserted
        """
        try:
            import lancedb
        except ImportError:
            raise ImportError("LanceDB not installed. Install: pip install lancedb")

        table_path = self._get_table_path(namespace, table_name)

        # Connect to LanceDB with path-style S3 options
        db = lancedb.connect(table_path, storage_options=self._get_storage_options())

        # Prepare data
        data = [{
            "id": id_,
            "vector": vector,
            **(metadata[i] if metadata else {}),
        } for i, (id_, vector) in enumerate(zip(ids, vectors))]

        # Upsert
        table = db.open_table(table_name)
        table.add(data)

        return len(data)

    async def create_education_namespaces(self) -> dict[str, list[str]]:
        """Create all standard education namespaces.

        Returns:
            Dictionary mapping domain to created namespaces
        """
        created = {}

        for domain, namespaces in EDUCATION_NAMESPACES.items():
            created[domain] = []
            for ns in namespaces:
                full_namespace = f"{domain}.{ns}"
                await self.create_namespace(full_namespace)
                created[domain].append(full_namespace)

        return created


# ============================================================================
# Convenience Functions
# ============================================================================

async def create_curriculum_namespace(
    nation: str = "ireland",
    subject: str | None = None,
) -> str:
    """Create a curriculum namespace.

    Args:
        nation: Nation code (ireland, uk)
        subject: Optional subject

    Returns:
        Created namespace path
    """
    manager = LanceNamespaceManager()

    if subject:
        namespace = f"{nation}.oideachas.{subject}"
    else:
        namespace = f"{nation}.oideachas"

    await manager.create_namespace(namespace)
    return namespace


def get_lance_config(
    namespace: str,
    table_name: str,
    dimension: int = 1024,
    metric: str = "cosine",
) -> LanceTableConfig:
    """Get Lance table configuration.

    Args:
        namespace: Table namespace
        table_name: Table name
        dimension: Vector dimension
        metric: Distance metric

    Returns:
        LanceTableConfig instance
    """
    return LanceTableConfig(
        namespace=namespace,
        table_name=table_name,
        dimension=dimension,
        metric=metric,
    )
