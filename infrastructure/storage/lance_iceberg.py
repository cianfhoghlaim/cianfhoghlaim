"""
LanceDB via Iceberg REST Catalog Integration for Celtic Education Pipeline.

Provides LanceDB access through the Lance Namespace Sidecar,
which registers Lance tables as 'trojan horse' Iceberg tables
in Lakekeeper with table_type=lance property.

This enables:
- Unified catalog discovery (Iceberg REST API)
- Lance-native vector operations
- S3 (Garage) storage backend
- Namespace-based organization for multi-domain data
"""

from dataclasses import dataclass
from typing import Any

import httpx
import structlog

from .config import LakehouseConfig, get_config

logger = structlog.get_logger(__name__)


@dataclass
class LanceTableInfo:
    """Information about a Lance table registered in Iceberg catalog."""

    name: str
    namespace: list[str]
    location: str
    properties: dict[str, str]

    @property
    def s3_uri(self) -> str:
        """Get the S3 URI for the table data."""
        return self.location

    @property
    def full_name(self) -> str:
        """Get the fully qualified table name."""
        return f"{'.'.join(self.namespace)}.{self.name}"

    @property
    def domain(self) -> str | None:
        """Get the domain from namespace (e.g., 'ireland', 'uk', 'celtic')."""
        if self.namespace:
            return self.namespace[0]
        return None


class LanceIcebergClient:
    """
    Client for LanceDB operations via Iceberg REST catalog.

    Uses the Lance Namespace Sidecar to:
    - Register Lance tables in Lakekeeper
    - Discover existing Lance tables
    - Manage namespaces for organization (ireland, uk, celtic, alignment)
    """

    # Standard namespaces for Celtic education data
    EDUCATION_NAMESPACES = {
        "ireland": ["oideachas", "curriculum"],
        "uk": ["oileain", "curriculum"],
        "celtic": ["teanga", "language"],
        "alignment": ["alignment", "bilingual"],
        "geospatial": ["geospatial", "boundaries"],
    }

    def __init__(self, config: LakehouseConfig | None = None):
        self.config = config or get_config().lakehouse
        self._client: httpx.AsyncClient | None = None
        self._sync_client: httpx.Client | None = None

    @property
    def base_url(self) -> str:
        """Get the Lance Sidecar API base URL."""
        return self.config.lance_api_uri.rstrip("/")

    async def _get_async_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=30.0,
                headers={"Content-Type": "application/json"},
            )
        return self._client

    def _get_sync_client(self) -> httpx.Client:
        """Get or create sync HTTP client."""
        if self._sync_client is None:
            self._sync_client = httpx.Client(
                base_url=self.base_url,
                timeout=30.0,
                headers={"Content-Type": "application/json"},
            )
        return self._sync_client

    async def close(self) -> None:
        """Close HTTP clients."""
        if self._client:
            await self._client.aclose()
            self._client = None
        if self._sync_client:
            self._sync_client.close()
            self._sync_client = None

    # =========================================================================
    # Health & Discovery
    # =========================================================================

    async def health_check(self) -> dict[str, Any]:
        """Check sidecar and Lakekeeper connectivity."""
        client = await self._get_async_client()
        response = await client.get("/health/deep")
        response.raise_for_status()
        return response.json()

    def health_check_sync(self) -> dict[str, Any]:
        """Synchronous health check."""
        client = self._get_sync_client()
        response = client.get("/health/deep")
        response.raise_for_status()
        return response.json()

    async def list_namespaces(self, parent: str | None = None) -> list[str]:
        """List all namespaces."""
        client = await self._get_async_client()
        params = {"parent": parent} if parent else {}
        response = await client.get("/namespaces", params=params)
        response.raise_for_status()
        return response.json().get("namespaces", [])

    def list_namespaces_sync(self, parent: str | None = None) -> list[str]:
        """Synchronous namespace listing."""
        client = self._get_sync_client()
        params = {"parent": parent} if parent else {}
        response = client.get("/namespaces", params=params)
        response.raise_for_status()
        return response.json().get("namespaces", [])

    # =========================================================================
    # Namespace Management
    # =========================================================================

    async def create_namespace(
        self, namespace: list[str], properties: dict[str, str] | None = None
    ) -> dict[str, Any]:
        """Create a new namespace."""
        client = await self._get_async_client()
        response = await client.post(
            "/namespaces",
            json={"namespace": namespace, "properties": properties or {}},
        )
        response.raise_for_status()
        return response.json()

    def create_namespace_sync(
        self, namespace: list[str], properties: dict[str, str] | None = None
    ) -> dict[str, Any]:
        """Synchronous namespace creation."""
        client = self._get_sync_client()
        response = client.post(
            "/namespaces",
            json={"namespace": namespace, "properties": properties or {}},
        )
        response.raise_for_status()
        return response.json()

    async def ensure_namespace(self, namespace: list[str]) -> None:
        """Ensure a namespace exists, creating if necessary."""
        try:
            await self.describe_namespace(namespace)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                await self.create_namespace(namespace)
            else:
                raise

    async def ensure_education_namespaces(self) -> None:
        """Ensure all standard education namespaces exist."""
        for domain, namespace_parts in self.EDUCATION_NAMESPACES.items():
            await self.ensure_namespace(namespace_parts)
            logger.info(f"Ensured namespace for {domain}: {'.'.join(namespace_parts)}")

    async def describe_namespace(self, namespace: list[str]) -> dict[str, Any]:
        """Get namespace details."""
        client = await self._get_async_client()
        ns_path = ".".join(namespace)
        response = await client.get(f"/namespaces/{ns_path}")
        response.raise_for_status()
        return response.json()

    async def drop_namespace(self, namespace: list[str]) -> dict[str, Any]:
        """Drop a namespace."""
        client = await self._get_async_client()
        ns_path = ".".join(namespace)
        response = await client.delete(f"/namespaces/{ns_path}")
        response.raise_for_status()
        return response.json()

    # =========================================================================
    # Table Management
    # =========================================================================

    async def list_tables(self, namespace: str) -> list[str]:
        """List Lance tables in a namespace."""
        client = await self._get_async_client()
        response = await client.get(f"/namespaces/{namespace}/tables")
        response.raise_for_status()
        return response.json().get("tables", [])

    def list_tables_sync(self, namespace: str) -> list[str]:
        """Synchronous table listing."""
        client = self._get_sync_client()
        response = client.get(f"/namespaces/{namespace}/tables")
        response.raise_for_status()
        return response.json().get("tables", [])

    async def list_tables_by_domain(self, domain: str) -> list[str]:
        """List tables for a specific education domain."""
        if domain in self.EDUCATION_NAMESPACES:
            namespace = ".".join(self.EDUCATION_NAMESPACES[domain])
            return await self.list_tables(namespace)
        return []

    async def create_table(
        self,
        namespace: str,
        name: str,
        location: str | None = None,
        properties: dict[str, str] | None = None,
    ) -> LanceTableInfo:
        """
        Create a Lance table and register in Iceberg catalog.

        Args:
            namespace: Dot-separated namespace (e.g., "oideachas.curriculum")
            name: Table name
            location: Optional S3 location (auto-generated if not provided)
            properties: Optional table properties

        Returns:
            LanceTableInfo with table metadata
        """
        client = await self._get_async_client()
        response = await client.post(
            f"/namespaces/{namespace}/tables",
            json={
                "name": name,
                "location": location,
                "properties": properties or {},
            },
        )
        response.raise_for_status()
        data = response.json()
        return LanceTableInfo(
            name=data["name"],
            namespace=data["namespace"],
            location=data["location"],
            properties=data.get("properties", {}),
        )

    def create_table_sync(
        self,
        namespace: str,
        name: str,
        location: str | None = None,
        properties: dict[str, str] | None = None,
    ) -> LanceTableInfo:
        """Synchronous table creation."""
        client = self._get_sync_client()
        response = client.post(
            f"/namespaces/{namespace}/tables",
            json={
                "name": name,
                "location": location,
                "properties": properties or {},
            },
        )
        response.raise_for_status()
        data = response.json()
        return LanceTableInfo(
            name=data["name"],
            namespace=data["namespace"],
            location=data["location"],
            properties=data.get("properties", {}),
        )

    async def describe_table(self, namespace: str, name: str) -> LanceTableInfo:
        """Get table details."""
        client = await self._get_async_client()
        response = await client.get(f"/namespaces/{namespace}/tables/{name}")
        response.raise_for_status()
        data = response.json()
        return LanceTableInfo(
            name=data["name"],
            namespace=data["namespace"],
            location=data["location"],
            properties=data.get("properties", {}),
        )

    def describe_table_sync(self, namespace: str, name: str) -> LanceTableInfo:
        """Synchronous table description."""
        client = self._get_sync_client()
        response = client.get(f"/namespaces/{namespace}/tables/{name}")
        response.raise_for_status()
        data = response.json()
        return LanceTableInfo(
            name=data["name"],
            namespace=data["namespace"],
            location=data["location"],
            properties=data.get("properties", {}),
        )

    async def drop_table(self, namespace: str, name: str) -> dict[str, Any]:
        """Drop a table from catalog (does not delete S3 data)."""
        client = await self._get_async_client()
        response = await client.delete(f"/namespaces/{namespace}/tables/{name}")
        response.raise_for_status()
        return response.json()

    # =========================================================================
    # LanceDB Native Operations
    # =========================================================================

    def get_lancedb_connection(self, table_info: LanceTableInfo):
        """
        Get a native LanceDB connection to the table.

        This bypasses the Iceberg catalog and connects directly
        to the Lance table data in S3.
        """
        try:
            import lancedb
        except ImportError:
            raise ImportError("lancedb is not installed. Run: pip install lancedb")

        # Connect to the S3 location with Garage credentials
        storage_options = {
            "aws_access_key_id": self.config.garage_access_key,
            "aws_secret_access_key": self.config.garage_secret_key,
            "aws_endpoint": self.config.garage_endpoint,
            "aws_region": self.config.garage_region,
        }

        # Connect to the parent directory (namespace)
        parent_uri = "/".join(table_info.location.rsplit("/", 1)[:-1])
        db = lancedb.connect(parent_uri, storage_options=storage_options)

        return db.open_table(table_info.name)

    async def get_or_create_table(
        self,
        namespace: str,
        name: str,
        properties: dict[str, str] | None = None,
    ) -> LanceTableInfo:
        """Get existing table or create new one."""
        try:
            return await self.describe_table(namespace, name)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                # Ensure namespace exists
                await self.ensure_namespace(namespace.split("."))
                return await self.create_table(namespace, name, properties=properties)
            raise


class LanceIcebergBackend:
    """
    High-level backend for LanceDB operations through Iceberg catalog.

    Provides a simpler interface for common operations like:
    - Managing embedding tables by domain
    - Performing vector searches
    - Hybrid search with FTS
    - Cross-domain search
    """

    def __init__(self, config: LakehouseConfig | None = None):
        self.config = config or get_config().lakehouse
        self.catalog = LanceIcebergClient(self.config)
        self._lancedb_connections: dict[str, Any] = {}

    async def close(self) -> None:
        """Close all connections."""
        await self.catalog.close()
        self._lancedb_connections.clear()

    async def get_table(self, namespace: str, name: str):
        """Get a LanceDB table connection with caching."""
        cache_key = f"{namespace}.{name}"

        if cache_key not in self._lancedb_connections:
            table_info = await self.catalog.describe_table(namespace, name)
            self._lancedb_connections[cache_key] = self.catalog.get_lancedb_connection(
                table_info
            )

        return self._lancedb_connections[cache_key]

    async def get_domain_table(self, domain: str, table_name: str):
        """Get a table by education domain."""
        if domain in self.catalog.EDUCATION_NAMESPACES:
            namespace = ".".join(self.catalog.EDUCATION_NAMESPACES[domain])
            return await self.get_table(namespace, table_name)
        raise ValueError(f"Unknown domain: {domain}")

    async def create_embedding_table(
        self,
        namespace: str,
        name: str,
        schema=None,
        initial_data: list[dict] | None = None,
        domain: str | None = None,
    ):
        """
        Create a new embedding table.

        Args:
            namespace: Namespace for organization (e.g., "oideachas.curriculum")
            name: Table name
            schema: PyArrow schema for the table
            initial_data: Optional initial records
            domain: Optional domain shortcut (ireland, uk, celtic, alignment)
        """
        try:
            import lancedb
        except ImportError:
            raise ImportError("lancedb is not installed. Run: pip install lancedb")

        # Use domain namespace if provided
        if domain and domain in self.catalog.EDUCATION_NAMESPACES:
            namespace = ".".join(self.catalog.EDUCATION_NAMESPACES[domain])

        # Register in catalog
        table_info = await self.catalog.get_or_create_table(
            namespace,
            name,
            properties={
                "table_type": "lance",
                "purpose": "embeddings",
                "domain": domain or "general",
            },
        )

        # Create actual LanceDB table with data/schema
        storage_options = {
            "aws_access_key_id": self.config.garage_access_key,
            "aws_secret_access_key": self.config.garage_secret_key,
            "aws_endpoint": self.config.garage_endpoint,
            "aws_region": self.config.garage_region,
        }

        # Extract parent directory
        parent_uri = "/".join(table_info.location.rsplit("/", 1)[:-1]) or self.config.lance_s3_uri
        db = lancedb.connect(parent_uri, storage_options=storage_options)

        if initial_data:
            table = db.create_table(name, data=initial_data, mode="overwrite")
        elif schema:
            table = db.create_table(name, schema=schema, mode="overwrite")
        else:
            raise ValueError("Either schema or initial_data must be provided")

        self._lancedb_connections[f"{namespace}.{name}"] = table
        return table

    async def vector_search(
        self,
        namespace: str,
        table_name: str,
        query_vector: list[float],
        limit: int = 10,
        filters: str | None = None,
        columns: list[str] | None = None,
        domain: str | None = None,
    ) -> list[dict]:
        """
        Perform vector similarity search.

        Args:
            namespace: Table namespace
            table_name: Table name
            query_vector: Query embedding
            limit: Number of results
            filters: SQL-like filter expression
            columns: Columns to return
            domain: Optional domain shortcut

        Returns:
            List of matching records
        """
        if domain:
            table = await self.get_domain_table(domain, table_name)
        else:
            table = await self.get_table(namespace, table_name)

        search = table.search(query_vector).limit(limit)

        if filters:
            search = search.where(filters)

        if columns:
            search = search.select(columns)

        return search.to_pandas().to_dict(orient="records")

    async def hybrid_search(
        self,
        namespace: str,
        table_name: str,
        query_vector: list[float],
        query_text: str,
        limit: int = 10,
        filters: str | None = None,
        domain: str | None = None,
    ) -> list[dict]:
        """
        Perform hybrid vector + full-text search with RRF reranking.

        Args:
            namespace: Table namespace
            table_name: Table name
            query_vector: Query embedding
            query_text: Text query for FTS
            limit: Number of results
            filters: SQL-like filter expression
            domain: Optional domain shortcut

        Returns:
            List of matching records
        """
        if domain:
            table = await self.get_domain_table(domain, table_name)
        else:
            table = await self.get_table(namespace, table_name)

        search = (
            table.search(query_type="hybrid")
            .vector(query_vector)
            .text(query_text)
            .limit(limit)
            .rerank(method="rrf")
        )

        if filters:
            search = search.where(filters)

        return search.to_pandas().to_dict(orient="records")

    async def cross_domain_search(
        self,
        query_vector: list[float],
        table_name: str,
        domains: list[str],
        limit_per_domain: int = 5,
    ) -> dict[str, list[dict]]:
        """
        Search across multiple education domains.

        Args:
            query_vector: Query embedding
            table_name: Common table name across domains
            domains: List of domains to search (ireland, uk, celtic, etc.)
            limit_per_domain: Max results per domain

        Returns:
            Dict mapping domain -> results
        """
        results = {}

        for domain in domains:
            try:
                domain_results = await self.vector_search(
                    namespace="",  # Will be overridden by domain
                    table_name=table_name,
                    query_vector=query_vector,
                    limit=limit_per_domain,
                    domain=domain,
                )
                results[domain] = domain_results
            except (httpx.HTTPError, OSError, ConnectionError) as e:
                logger.warning("lance_iceberg_search_failed", domain=domain, error=str(e))
                results[domain] = []

        return results


# Singleton instance
_lance_iceberg_backend: LanceIcebergBackend | None = None


def get_lance_iceberg_backend() -> LanceIcebergBackend:
    """Get the Lance Iceberg backend singleton."""
    global _lance_iceberg_backend
    if _lance_iceberg_backend is None:
        _lance_iceberg_backend = LanceIcebergBackend()
    return _lance_iceberg_backend
