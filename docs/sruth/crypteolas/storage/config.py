"""
Storage configuration for Crypteolas.

Manages configuration for all storage backends:
- LanceDB + Lakekeeper
- Garage S3
- DuckDB + MotherDuck
- DuckLake
- PlanetScale PostgreSQL
"""

import os
from dataclasses import dataclass, field
from enum import Enum
from functools import lru_cache


class Environment(str, Enum):
    """Deployment environment."""

    LOCAL = "local"
    DEVELOPMENT = "development"
    PRODUCTION = "production"


@dataclass
class StorageConfig:
    """Unified storage configuration for Crypteolas."""

    environment: Environment = Environment.LOCAL

    # Lakekeeper (Lance REST catalog)
    lakekeeper_url: str = "http://localhost:8181"
    lakekeeper_warehouse: str = "crypteolas"
    lakekeeper_namespace: str = "embeddings"

    # LanceDB
    lancedb_uri: str = "./storage/data/lancedb"
    lancedb_table_prefix: str = "crypteolas_"

    # Garage S3
    garage_endpoint: str = "http://localhost:3900"
    garage_access_key: str = ""
    garage_secret_key: str = ""
    garage_region: str = "garage"
    garage_bucket_raw: str = "crypteolas-raw"
    garage_bucket_embeddings: str = "crypteolas-embeddings"

    # DuckDB / MotherDuck
    duckdb_path: str = "./storage/data/crypteolas.duckdb"
    motherduck_token: str = ""
    motherduck_database: str = "crypteolas"
    use_motherduck: bool = False

    # DuckLake
    ducklake_catalog_type: str = "sqlite"  # "sqlite" or "postgres"
    ducklake_sqlite_path: str = "./storage/data/ducklake.ducklake"
    ducklake_data_path: str = "./storage/data/ducklake_data"

    # PlanetScale PostgreSQL (for production DuckLake + Lakekeeper)
    planetscale_host: str = ""
    planetscale_port: int = 5432
    planetscale_database: str = ""
    planetscale_username: str = ""
    planetscale_password: str = ""
    planetscale_sslmode: str = "require"

    # Source types for filtering
    source_types: list[str] = field(
        default_factory=lambda: [
            "protocol_docs",
            "user_url",
            "github",
            "local",
        ]
    )

    @classmethod
    def from_env(cls) -> "StorageConfig":
        """Load configuration from environment variables."""
        env = os.getenv("ENVIRONMENT", "local")

        return cls(
            environment=Environment(env),
            # Lakekeeper
            lakekeeper_url=os.getenv("LAKEKEEPER_URL", "http://localhost:8181"),
            lakekeeper_warehouse=os.getenv("LAKEKEEPER_WAREHOUSE", "crypteolas"),
            lakekeeper_namespace=os.getenv("LAKEKEEPER_NAMESPACE", "embeddings"),
            # LanceDB
            lancedb_uri=os.getenv("LANCEDB_URI", "./storage/data/lancedb"),
            lancedb_table_prefix=os.getenv("LANCEDB_TABLE_PREFIX", "crypteolas_"),
            # Garage S3
            garage_endpoint=os.getenv("GARAGE_ENDPOINT", "http://localhost:3900"),
            garage_access_key=os.getenv("GARAGE_ACCESS_KEY", ""),
            garage_secret_key=os.getenv("GARAGE_SECRET_KEY", ""),
            garage_region=os.getenv("GARAGE_REGION", "garage"),
            garage_bucket_raw=os.getenv("GARAGE_BUCKET_RAW", "crypteolas-raw"),
            garage_bucket_embeddings=os.getenv("GARAGE_BUCKET_EMBEDDINGS", "crypteolas-embeddings"),
            # DuckDB / MotherDuck
            duckdb_path=os.getenv("DUCKDB_PATH", "./storage/data/crypteolas.duckdb"),
            motherduck_token=os.getenv("MOTHERDUCK_TOKEN", ""),
            motherduck_database=os.getenv("MOTHERDUCK_DATABASE", "crypteolas"),
            use_motherduck=os.getenv("USE_MOTHERDUCK", "false").lower() == "true",
            # DuckLake
            ducklake_catalog_type=os.getenv("DUCKLAKE_CATALOG_TYPE", "sqlite"),
            ducklake_sqlite_path=os.getenv(
                "DUCKLAKE_SQLITE_PATH", "./storage/data/ducklake.ducklake"
            ),
            ducklake_data_path=os.getenv("DUCKLAKE_DATA_PATH", "./storage/data/ducklake_data"),
            # PlanetScale
            planetscale_host=os.getenv("PLANETSCALE_HOST", ""),
            planetscale_port=int(os.getenv("PLANETSCALE_PORT", "5432")),
            planetscale_database=os.getenv("PLANETSCALE_DATABASE", ""),
            planetscale_username=os.getenv("PLANETSCALE_USERNAME", ""),
            planetscale_password=os.getenv("PLANETSCALE_PASSWORD", ""),
            planetscale_sslmode=os.getenv("PLANETSCALE_SSLMODE", "require"),
        )

    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == Environment.PRODUCTION

    def get_ducklake_connection_string(self) -> str:
        """Get DuckLake connection string based on environment."""
        if self.ducklake_catalog_type == "postgres" and self.planetscale_host:
            return (
                f"ducklake:postgres:dbname={self.planetscale_database} "
                f"host={self.planetscale_host} "
                f"port={self.planetscale_port} "
                f"user={self.planetscale_username} "
                f"password={self.planetscale_password} "
                f"sslmode={self.planetscale_sslmode}"
            )
        return f"ducklake:{self.ducklake_sqlite_path}"

    def get_garage_s3_url(self, bucket: str, key: str) -> str:
        """Get full S3 URL for a Garage object."""
        return f"s3://{bucket}/{key}"


@lru_cache(maxsize=1)
def get_storage_config() -> StorageConfig:
    """Get cached storage configuration."""
    return StorageConfig.from_env()
