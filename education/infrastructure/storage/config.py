"""
Storage Configuration for Celtic Education Pipeline.

Environment-based configuration for multi-database storage layer
supporting Ireland, UK nations, and Celtic language data.
"""

import os
from dataclasses import dataclass, field


@dataclass
class PlanetScaleConfig:
    """PlanetScale PostgreSQL configuration."""

    host: str = field(
        default_factory=lambda: os.getenv(
            "PLANETSCALE_HOST", "eu-west-3.pg.psdb.cloud"
        )
    )
    port: int = field(
        default_factory=lambda: int(os.getenv("PLANETSCALE_PORT", "5432"))
    )
    database: str = field(
        default_factory=lambda: os.getenv("PLANETSCALE_DATABASE", "oideachais")
    )
    username: str = field(
        default_factory=lambda: os.getenv("PLANETSCALE_USERNAME", "")
    )
    password: str = field(
        default_factory=lambda: os.getenv("PLANETSCALE_PASSWORD", "")
    )
    sslmode: str = field(
        default_factory=lambda: os.getenv("PLANETSCALE_SSLMODE", "require")
    )

    @property
    def connection_string(self) -> str:
        """Get PostgreSQL connection string."""
        return (
            f"postgresql://{self.username}:{self.password}"
            f"@{self.host}:{self.port}/{self.database}?sslmode={self.sslmode}"
        )

    @property
    def dsn(self) -> dict:
        """Get connection parameters as dict for psycopg2/asyncpg."""
        return {
            "host": self.host,
            "port": self.port,
            "database": self.database,
            "user": self.username,
            "password": self.password,
            "sslmode": self.sslmode,
        }


@dataclass
class LanceDBConfig:
    """LanceDB vector database configuration with namespace support."""

    local_path: str = field(
        default_factory=lambda: os.getenv("LANCEDB_LOCAL_PATH", "./data/lancedb")
    )
    remote_uri: str | None = field(
        default_factory=lambda: os.getenv("LANCEDB_REMOTE_URI")
    )
    api_key: str | None = field(
        default_factory=lambda: os.getenv("LANCEDB_API_KEY")
    )
    region: str = field(
        default_factory=lambda: os.getenv("LANCEDB_REGION", "us-east-1")
    )

    # Namespace prefixes for multi-domain data
    namespace_prefixes: dict = field(default_factory=lambda: {
        "ireland": "oideachas",
        "uk": "oileain",
        "celtic": "teanga",
        "alignment": "alignment",
    })

    @property
    def uri(self) -> str:
        """Get the appropriate URI (remote if configured, else local)."""
        return self.remote_uri if self.remote_uri else self.local_path

    @property
    def is_remote(self) -> bool:
        """Check if using remote storage."""
        return self.remote_uri is not None

    def get_table_name(self, domain: str, table: str) -> str:
        """Get namespaced table name for a domain."""
        prefix = self.namespace_prefixes.get(domain, domain)
        return f"{prefix}.{table}"


@dataclass
class DuckLakeConfig:
    """DuckDB/MotherDuck analytics configuration with Spatial extension."""

    local_path: str = field(
        default_factory=lambda: os.getenv(
            "DUCKDB_LOCAL_PATH", "./data/celtic_education.duckdb"
        )
    )
    motherduck_token: str | None = field(
        default_factory=lambda: os.getenv("MOTHERDUCK_TOKEN")
    )
    database_name: str = field(
        default_factory=lambda: os.getenv("MOTHERDUCK_DATABASE", "oideachais")
    )
    enable_spatial: bool = field(
        default_factory=lambda: os.getenv("DUCKDB_ENABLE_SPATIAL", "true").lower() == "true"
    )

    @property
    def connection_string(self) -> str:
        """Get DuckDB connection string."""
        if self.motherduck_token:
            return f"md:{self.database_name}?motherduck_token={self.motherduck_token}"
        return self.local_path

    @property
    def is_motherduck(self) -> bool:
        """Check if using MotherDuck cloud."""
        return self.motherduck_token is not None


@dataclass
class GarageConfig:
    """Garage S3-compatible storage configuration."""

    endpoint_url: str = field(
        default_factory=lambda: os.getenv(
            "GARAGE_ENDPOINT", "http://localhost:3900"
        )
    )
    access_key: str = field(
        default_factory=lambda: os.getenv("GARAGE_ACCESS_KEY", "")
    )
    secret_key: str = field(
        default_factory=lambda: os.getenv("GARAGE_SECRET_KEY", "")
    )
    bucket: str = field(
        default_factory=lambda: os.getenv("GARAGE_BUCKET", "education-documents")
    )
    region: str = field(
        default_factory=lambda: os.getenv("GARAGE_REGION", "garage")
    )

    @property
    def s3_config(self) -> dict:
        """Get S3 client configuration."""
        return {
            "endpoint_url": self.endpoint_url,
            "aws_access_key_id": self.access_key,
            "aws_secret_access_key": self.secret_key,
            "region_name": self.region,
        }


@dataclass
class RedisConfig:
    """Redis configuration for progress tracking and caching."""

    url: str = field(
        default_factory=lambda: os.getenv("REDIS_URL", "redis://localhost:6379")
    )
    db: int = field(default_factory=lambda: int(os.getenv("REDIS_DB", "0")))

    @property
    def connection_params(self) -> dict:
        """Get Redis connection parameters."""
        return {"url": self.url, "db": self.db}


@dataclass
class LakehouseConfig:
    """Lakehouse infrastructure configuration for Garage S3, Lakekeeper, and Lance Sidecar."""

    # Garage S3 endpoint (CRDT-based object storage)
    garage_endpoint: str = field(
        default_factory=lambda: os.getenv(
            "GARAGE_ENDPOINT", "https://s3.lakehouse.cianfhoghlaim.ie:3900"
        )
    )
    garage_access_key: str = field(
        default_factory=lambda: os.getenv("GARAGE_ACCESS_KEY_ID", "lakehouse")
    )
    garage_secret_key: str = field(
        default_factory=lambda: os.getenv("GARAGE_SECRET_ACCESS_KEY", "")
    )
    garage_region: str = field(
        default_factory=lambda: os.getenv("GARAGE_REGION", "garage")
    )

    # Buckets for different data types
    iceberg_bucket: str = field(
        default_factory=lambda: os.getenv("ICEBERG_BUCKET", "iceberg")
    )
    lance_bucket: str = field(
        default_factory=lambda: os.getenv("LANCE_BUCKET", "lance")
    )
    ducklake_bucket: str = field(
        default_factory=lambda: os.getenv("DUCKLAKE_BUCKET", "ducklake")
    )
    documents_bucket: str = field(
        default_factory=lambda: os.getenv("DOCUMENTS_BUCKET", "documents")
    )

    # Lakekeeper Iceberg REST Catalog
    lakekeeper_uri: str = field(
        default_factory=lambda: os.getenv(
            "LAKEKEEPER_URI", "https://lakekeeper.cianfhoghlaim.ie:8181"
        )
    )
    lakekeeper_warehouse: str = field(
        default_factory=lambda: os.getenv("LAKEKEEPER_WAREHOUSE", "lakehouse")
    )

    # Lance Namespace Sidecar (Lance-as-Iceberg trojan horse)
    lance_api_uri: str = field(
        default_factory=lambda: os.getenv(
            "LANCE_API_URI", "https://lance-api.cianfhoghlaim.ie:8182"
        )
    )

    @property
    def s3_config(self) -> dict:
        """Get S3 client configuration for Garage."""
        return {
            "endpoint_url": self.garage_endpoint,
            "aws_access_key_id": self.garage_access_key,
            "aws_secret_access_key": self.garage_secret_key,
            "region_name": self.garage_region,
        }

    @property
    def lance_s3_uri(self) -> str:
        """Get S3 URI for Lance storage."""
        return f"s3://{self.lance_bucket}/"

    @property
    def iceberg_s3_uri(self) -> str:
        """Get S3 URI for Iceberg storage."""
        return f"s3://{self.iceberg_bucket}/"

    @property
    def ducklake_s3_uri(self) -> str:
        """Get S3 URI for DuckLake storage."""
        return f"s3://{self.ducklake_bucket}/"


@dataclass
class MemgraphConfig:
    """Memgraph graph database configuration."""

    uri: str = field(
        default_factory=lambda: os.getenv("MEMGRAPH_URI", "bolt://localhost:7687")
    )
    username: str = field(
        default_factory=lambda: os.getenv("MEMGRAPH_USERNAME", "")
    )
    password: str = field(
        default_factory=lambda: os.getenv("MEMGRAPH_PASSWORD", "")
    )

    @property
    def connection_params(self) -> dict:
        """Get connection parameters for neo4j driver (Memgraph compatible)."""
        params = {"uri": self.uri}
        if self.username and self.password:
            params["auth"] = (self.username, self.password)
        return params


@dataclass
class FalkorDBConfig:
    """FalkorDB (Redis-based graph) configuration for caching."""

    url: str = field(
        default_factory=lambda: os.getenv("FALKORDB_URL", "redis://localhost:6379")
    )
    graph_name: str = field(
        default_factory=lambda: os.getenv("FALKORDB_GRAPH", "curriculum_cache")
    )

    @property
    def connection_params(self) -> dict:
        """Get FalkorDB connection parameters."""
        return {"url": self.url, "graph_name": self.graph_name}


@dataclass
class CogneeConfig:
    """Cognee AI memory layer configuration."""

    api_url: str = field(
        default_factory=lambda: os.getenv("COGNEE_API_URL", "http://localhost:8001")
    )
    graph_url: str = field(
        default_factory=lambda: os.getenv("COGNEE_GRAPH_URL", "bolt://localhost:7687")
    )
    vector_url: str = field(
        default_factory=lambda: os.getenv(
            "COGNEE_VECTOR_URL", "https://lance-api.cianfhoghlaim.ie:8182"
        )
    )

    @property
    def config_dict(self) -> dict:
        """Get Cognee configuration dictionary."""
        return {
            "graph_database_provider": "neo4j",  # Memgraph compatible
            "graph_database_url": self.graph_url,
            "vector_database_provider": "lancedb",
            "vector_database_url": self.vector_url,
        }


@dataclass
class StorageConfig:
    """Unified storage configuration for Celtic education pipeline."""

    planetscale: PlanetScaleConfig = field(default_factory=PlanetScaleConfig)
    lancedb: LanceDBConfig = field(default_factory=LanceDBConfig)
    ducklake: DuckLakeConfig = field(default_factory=DuckLakeConfig)
    garage: GarageConfig = field(default_factory=GarageConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    # Lakehouse infrastructure
    lakehouse: LakehouseConfig = field(default_factory=LakehouseConfig)
    memgraph: MemgraphConfig = field(default_factory=MemgraphConfig)
    falkordb: FalkorDBConfig = field(default_factory=FalkorDBConfig)
    cognee: CogneeConfig = field(default_factory=CogneeConfig)

    @classmethod
    def from_env(cls) -> "StorageConfig":
        """Create configuration from environment variables."""
        return cls()


# Singleton config instance
_config: StorageConfig | None = None


def get_config() -> StorageConfig:
    """Get the storage configuration singleton."""
    global _config
    if _config is None:
        _config = StorageConfig.from_env()
    return _config


def reset_config() -> None:
    """Reset the configuration singleton (useful for testing)."""
    global _config
    _config = None
