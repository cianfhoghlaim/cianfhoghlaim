"""
Lakekeeper Client for Crypteolas.

Provides Lance REST catalog namespace management through Lakekeeper.
Lakekeeper is a Lance REST catalog service that manages table metadata
and versioning for LanceDB tables.

Features:
- Namespace management for embeddings
- Table catalog with versioning
- REST API for table metadata
- PlanetScale PostgreSQL backend (production)
"""

import logging
import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class TableStatus(str, Enum):
    """Table status in Lakekeeper catalog."""
    ACTIVE = "active"
    STAGED = "staged"
    DROPPED = "dropped"


@dataclass
class TableInfo:
    """Information about a table in Lakekeeper."""
    namespace: str
    name: str
    table_uuid: str
    location: str
    created_at: str
    updated_at: str
    status: TableStatus
    properties: dict[str, str]


@dataclass
class LakekeeperConfig:
    """Configuration for Lakekeeper client."""

    # Server configuration
    url: str = "http://localhost:8181"
    warehouse: str = "crypteolas"
    namespace: str = "embeddings"

    # Authentication (if enabled)
    api_key: str = ""

    # PostgreSQL backend (production)
    postgres_host: str = ""
    postgres_port: int = 5432
    postgres_database: str = ""
    postgres_username: str = ""
    postgres_password: str = ""

    @classmethod
    def from_env(cls) -> "LakekeeperConfig":
        """Load configuration from environment variables."""
        return cls(
            url=os.getenv("LAKEKEEPER_URL", "http://localhost:8181"),
            warehouse=os.getenv("LAKEKEEPER_WAREHOUSE", "crypteolas"),
            namespace=os.getenv("LAKEKEEPER_NAMESPACE", "embeddings"),
            api_key=os.getenv("LAKEKEEPER_API_KEY", ""),
            postgres_host=os.getenv("PLANETSCALE_HOST", ""),
            postgres_port=int(os.getenv("PLANETSCALE_PORT", "5432")),
            postgres_database=os.getenv("PLANETSCALE_DATABASE", ""),
            postgres_username=os.getenv("PLANETSCALE_USERNAME", ""),
            postgres_password=os.getenv("PLANETSCALE_PASSWORD", ""),
        )


class LakekeeperClient:
    """
    Client for Lakekeeper Lance REST catalog.

    Lakekeeper provides:
    - REST API for Lance table catalog
    - Namespace management for organizing tables
    - Table versioning and metadata
    - PostgreSQL or SQLite backend
    """

    def __init__(self, config: LakekeeperConfig | None = None):
        self.config = config or LakekeeperConfig.from_env()
        self._session = None

    def _get_session(self):
        """Get or create HTTP session."""
        if self._session is not None:
            return self._session

        try:
            import httpx
        except ImportError:
            raise ImportError("httpx is not installed. Run: pip install httpx")

        headers = {"Content-Type": "application/json"}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"

        self._session = httpx.Client(
            base_url=self.config.url,
            headers=headers,
            timeout=30.0,
        )

        return self._session

    @property
    def session(self):
        """Get the HTTP session."""
        return self._get_session()

    def close(self) -> None:
        """Close the HTTP session."""
        if self._session:
            self._session.close()
            self._session = None

    # =========================================================================
    # Warehouse Operations
    # =========================================================================

    def get_config(self) -> dict[str, Any]:
        """Get catalog configuration."""
        response = self.session.get(f"/v1/config")
        response.raise_for_status()
        return response.json()

    def list_warehouses(self) -> list[str]:
        """List all warehouses."""
        response = self.session.get("/v1/warehouses")
        response.raise_for_status()
        return response.json().get("warehouses", [])

    # =========================================================================
    # Namespace Operations
    # =========================================================================

    def create_namespace(
        self,
        namespace: str | None = None,
        properties: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Create a namespace."""
        ns = namespace or self.config.namespace
        payload = {
            "namespace": [ns],
            "properties": properties or {},
        }

        response = self.session.post(
            f"/v1/{self.config.warehouse}/namespaces",
            json=payload,
        )
        response.raise_for_status()
        logger.info(f"Created namespace: {ns}")
        return response.json()

    def list_namespaces(self) -> list[str]:
        """List all namespaces in the warehouse."""
        response = self.session.get(f"/v1/{self.config.warehouse}/namespaces")
        response.raise_for_status()

        namespaces = response.json().get("namespaces", [])
        return [ns[0] if isinstance(ns, list) else ns for ns in namespaces]

    def namespace_exists(self, namespace: str | None = None) -> bool:
        """Check if a namespace exists."""
        ns = namespace or self.config.namespace
        try:
            response = self.session.get(f"/v1/{self.config.warehouse}/namespaces/{ns}")
            return response.status_code == 200
        except Exception:
            return False

    def get_namespace(self, namespace: str | None = None) -> dict[str, Any]:
        """Get namespace details."""
        ns = namespace or self.config.namespace
        response = self.session.get(f"/v1/{self.config.warehouse}/namespaces/{ns}")
        response.raise_for_status()
        return response.json()

    def drop_namespace(self, namespace: str) -> None:
        """Drop a namespace."""
        response = self.session.delete(f"/v1/{self.config.warehouse}/namespaces/{namespace}")
        response.raise_for_status()
        logger.info(f"Dropped namespace: {namespace}")

    # =========================================================================
    # Table Operations
    # =========================================================================

    def list_tables(self, namespace: str | None = None) -> list[str]:
        """List tables in a namespace."""
        ns = namespace or self.config.namespace
        response = self.session.get(f"/v1/{self.config.warehouse}/namespaces/{ns}/tables")
        response.raise_for_status()

        tables = response.json().get("identifiers", [])
        return [t.get("name", t) if isinstance(t, dict) else t for t in tables]

    def get_table(
        self,
        table_name: str,
        namespace: str | None = None,
    ) -> TableInfo | None:
        """Get table metadata."""
        ns = namespace or self.config.namespace
        try:
            response = self.session.get(
                f"/v1/{self.config.warehouse}/namespaces/{ns}/tables/{table_name}"
            )
            response.raise_for_status()
            data = response.json()

            return TableInfo(
                namespace=ns,
                name=table_name,
                table_uuid=data.get("metadata", {}).get("table-uuid", ""),
                location=data.get("metadata-location", ""),
                created_at=data.get("metadata", {}).get("created-at", ""),
                updated_at=data.get("metadata", {}).get("last-updated-ms", ""),
                status=TableStatus.ACTIVE,
                properties=data.get("metadata", {}).get("properties", {}),
            )
        except Exception:
            return None

    def register_table(
        self,
        table_name: str,
        location: str,
        namespace: str | None = None,
        properties: dict[str, str] | None = None,
    ) -> TableInfo:
        """Register a table in the catalog."""
        ns = namespace or self.config.namespace

        payload = {
            "name": table_name,
            "metadata-location": location,
            "properties": properties or {},
        }

        response = self.session.post(
            f"/v1/{self.config.warehouse}/namespaces/{ns}/tables",
            json=payload,
        )
        response.raise_for_status()

        logger.info(f"Registered table: {ns}.{table_name}")
        return self.get_table(table_name, ns)

    def drop_table(
        self,
        table_name: str,
        namespace: str | None = None,
        purge: bool = False,
    ) -> None:
        """Drop a table from the catalog."""
        ns = namespace or self.config.namespace
        params = {"purgeRequested": purge}

        response = self.session.delete(
            f"/v1/{self.config.warehouse}/namespaces/{ns}/tables/{table_name}",
            params=params,
        )
        response.raise_for_status()
        logger.info(f"Dropped table: {ns}.{table_name}")

    def table_exists(
        self,
        table_name: str,
        namespace: str | None = None,
    ) -> bool:
        """Check if a table exists."""
        return self.get_table(table_name, namespace) is not None

    # =========================================================================
    # Embedding Table Management
    # =========================================================================

    def register_embedding_table(
        self,
        table_name: str,
        lance_uri: str,
        model: str,
        dimension: int,
        source_type: str,
    ) -> TableInfo:
        """Register an embedding table with metadata."""
        properties = {
            "embedding-model": model,
            "embedding-dimension": str(dimension),
            "source-type": source_type,
            "created-at": datetime.utcnow().isoformat(),
        }

        return self.register_table(
            table_name=table_name,
            location=lance_uri,
            properties=properties,
        )

    def list_embedding_tables(self) -> list[TableInfo]:
        """List all embedding tables with their metadata."""
        tables = self.list_tables()
        result = []

        for table_name in tables:
            info = self.get_table(table_name)
            if info:
                result.append(info)

        return result

    def get_embedding_table_by_source(self, source_type: str) -> TableInfo | None:
        """Find embedding table for a source type."""
        tables = self.list_embedding_tables()

        for table in tables:
            if table.properties.get("source-type") == source_type:
                return table

        return None

    # =========================================================================
    # Health Check
    # =========================================================================

    def health_check(self) -> bool:
        """Check if Lakekeeper is accessible."""
        try:
            response = self.session.get("/health")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Lakekeeper health check failed: {e}")
            return False


# Singleton instance
_lakekeeper_client: LakekeeperClient | None = None


def get_lakekeeper_client(config: LakekeeperConfig | None = None) -> LakekeeperClient:
    """Get the Lakekeeper client singleton."""
    global _lakekeeper_client
    if _lakekeeper_client is None:
        _lakekeeper_client = LakekeeperClient(config)
    return _lakekeeper_client
