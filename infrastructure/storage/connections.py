"""
Storage Backend Implementations for Celtic Education Pipeline.

Provides unified interfaces for:
- LanceDB: Vector storage with hybrid search and namespace support
- PlanetScale: PostgreSQL for structured metadata
- DuckDB/MotherDuck: Analytics with Spatial extension and Iceberg tables
- Garage: S3-compatible document storage
"""

from abc import ABC, abstractmethod
from pathlib import Path

import structlog

from .config import (
    DuckLakeConfig,
    GarageConfig,
    LanceDBConfig,
    PlanetScaleConfig,
    StorageConfig,
    get_config,
)

logger = structlog.get_logger(__name__)


class StorageBackend(ABC):
    """Abstract base class for storage backends."""

    @abstractmethod
    def connect(self) -> None:
        """Establish connection to the storage backend."""

    @abstractmethod
    def close(self) -> None:
        """Close connection to the storage backend."""

    @abstractmethod
    def health_check(self) -> bool:
        """Check if the backend is healthy and accessible."""

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class LanceDBBackend(StorageBackend):
    """LanceDB vector database backend with hybrid search and namespace support."""

    def __init__(self, config: LanceDBConfig | None = None):
        self.config = config or get_config().lancedb
        self._db = None

    def connect(self) -> None:
        """Connect to LanceDB (local or remote)."""
        try:
            import lancedb

            if self.config.is_remote and self.config.api_key:
                self._db = lancedb.connect(
                    self.config.remote_uri,
                    api_key=self.config.api_key,
                    region=self.config.region,
                )
            else:
                Path(self.config.local_path).parent.mkdir(parents=True, exist_ok=True)
                self._db = lancedb.connect(self.config.local_path)

            logger.info("lancedb_connected", uri=self.config.uri)
        except ImportError:
            raise ImportError("lancedb is not installed. Run: pip install lancedb")

    def close(self) -> None:
        """Close LanceDB connection."""
        self._db = None

    def health_check(self) -> bool:
        """Check LanceDB connectivity."""
        if self._db is None:
            return False
        try:
            self._db.table_names()
            return True
        except (OSError, ConnectionError, RuntimeError) as e:
            logger.error("lancedb_health_check_failed", error=str(e))
            return False

    @property
    def db(self):
        """Get the LanceDB connection."""
        if self._db is None:
            self.connect()
        return self._db

    def create_table(
        self,
        name: str,
        data: list[dict] | None = None,
        schema=None,
        mode: str = "create",
        domain: str | None = None,
    ):
        """Create or open a table with optional domain namespacing."""
        if domain:
            name = self.config.get_table_name(domain, name)

        if mode == "overwrite" or name not in self.db.table_names():
            if data:
                return self.db.create_table(name, data=data, mode=mode)
            elif schema:
                return self.db.create_table(name, schema=schema, mode=mode)
            else:
                raise ValueError("Either data or schema must be provided")
        return self.db.open_table(name)

    def open_table(self, name: str, domain: str | None = None):
        """Open an existing table."""
        if domain:
            name = self.config.get_table_name(domain, name)
        return self.db.open_table(name)

    def list_tables(self, domain: str | None = None) -> list[str]:
        """List all tables, optionally filtered by domain."""
        tables = self.db.table_names()
        if domain:
            prefix = self.config.namespace_prefixes.get(domain, domain)
            return [t for t in tables if t.startswith(f"{prefix}.")]
        return tables

    def hybrid_search(
        self,
        table_name: str,
        query_vector: list[float],
        query_text: str | None = None,
        limit: int = 10,
        vector_weight: float = 0.7,
        filters: str | None = None,
        domain: str | None = None,
    ) -> list[dict]:
        """Perform hybrid (vector + FTS) search."""
        if domain:
            table_name = self.config.get_table_name(domain, table_name)

        table = self.open_table(table_name)

        if query_text:
            results = (
                table.search(query_type="hybrid")
                .vector(query_vector)
                .text(query_text)
                .limit(limit)
                .rerank(method="rrf")
            )
        else:
            results = table.search(query_vector).limit(limit)

        if filters:
            results = results.where(filters)

        return results.to_pandas().to_dict(orient="records")


class PlanetScaleBackend(StorageBackend):
    """PlanetScale PostgreSQL backend for structured metadata."""

    def __init__(self, config: PlanetScaleConfig | None = None):
        self.config = config or get_config().planetscale
        self._conn = None
        self._pool = None

    def connect(self) -> None:
        """Connect to PlanetScale PostgreSQL."""
        try:
            import psycopg2
            from psycopg2 import pool

            self._pool = pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=10,
                **self.config.dsn,
            )
            logger.info("planetscale_connected", host=self.config.host)
        except ImportError:
            raise ImportError("psycopg2 is not installed. Run: pip install psycopg2-binary")

    def close(self) -> None:
        """Close PlanetScale connection pool."""
        if self._pool:
            self._pool.closeall()
            self._pool = None

    def health_check(self) -> bool:
        """Check PlanetScale connectivity."""
        try:
            import psycopg2

            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    return True
        except (psycopg2.Error, ConnectionError, OSError) as e:
            logger.error("planetscale_health_check_failed", error=str(e))
            return False

    def get_connection(self):
        """Get a connection from the pool."""
        if self._pool is None:
            self.connect()
        return self._pool.getconn()

    def return_connection(self, conn):
        """Return a connection to the pool."""
        if self._pool:
            self._pool.putconn(conn)

    def execute(self, query: str, params: tuple | None = None) -> list[dict]:
        """Execute a query and return results as list of dicts."""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(query, params)
                if cur.description:
                    columns = [desc[0] for desc in cur.description]
                    return [dict(zip(columns, row)) for row in cur.fetchall()]
                conn.commit()
                return []
        finally:
            self.return_connection(conn)

    def execute_many(self, query: str, params_list: list[tuple]) -> None:
        """Execute a query with multiple parameter sets."""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.executemany(query, params_list)
                conn.commit()
        finally:
            self.return_connection(conn)

    def init_schema(self) -> None:
        """Initialize the database schema for Celtic education documents."""
        schema_sql = """
        -- Curriculum documents from all nations
        CREATE TABLE IF NOT EXISTS curriculum_documents (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            title TEXT NOT NULL,
            slug VARCHAR(255) UNIQUE,
            nation VARCHAR(50) NOT NULL DEFAULT 'ireland',
            education_level VARCHAR(50),
            subject VARCHAR(100),
            document_type VARCHAR(50),
            language VARCHAR(10) DEFAULT 'en',
            source_url TEXT,
            pdf_storage_key TEXT,
            lancedb_table_name VARCHAR(100),
            embedding_count INTEGER DEFAULT 0,
            metadata JSONB,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );

        -- Embeddings metadata
        CREATE TABLE IF NOT EXISTS embeddings_metadata (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            document_id UUID REFERENCES curriculum_documents(id) ON DELETE CASCADE,
            lancedb_table_name VARCHAR(100),
            chunk_id VARCHAR(100),
            chunk_index INTEGER,
            embedding_model VARCHAR(100),
            embedding_dim INTEGER,
            text_preview TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );

        -- Bilingual alignment pairs
        CREATE TABLE IF NOT EXISTS alignment_pairs (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            source_text TEXT NOT NULL,
            target_text TEXT NOT NULL,
            source_lang VARCHAR(10) NOT NULL,
            target_lang VARCHAR(10) NOT NULL,
            alignment_score FLOAT,
            alignment_method VARCHAR(50),
            source_url TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );

        -- PDF processing status
        CREATE TABLE IF NOT EXISTS pdf_processing_status (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            document_id UUID REFERENCES curriculum_documents(id) ON DELETE CASCADE,
            status VARCHAR(50) DEFAULT 'pending',
            stage VARCHAR(50),
            progress_pct FLOAT DEFAULT 0,
            error_message TEXT,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT NOW()
        );

        -- Indexes
        CREATE INDEX IF NOT EXISTS idx_docs_nation ON curriculum_documents(nation);
        CREATE INDEX IF NOT EXISTS idx_docs_education_level ON curriculum_documents(education_level);
        CREATE INDEX IF NOT EXISTS idx_docs_subject ON curriculum_documents(subject);
        CREATE INDEX IF NOT EXISTS idx_docs_language ON curriculum_documents(language);
        CREATE INDEX IF NOT EXISTS idx_docs_document_type ON curriculum_documents(document_type);
        CREATE INDEX IF NOT EXISTS idx_embeddings_document ON embeddings_metadata(document_id);
        CREATE INDEX IF NOT EXISTS idx_alignment_langs ON alignment_pairs(source_lang, target_lang);
        CREATE INDEX IF NOT EXISTS idx_processing_status ON pdf_processing_status(status);
        """
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(schema_sql)
                conn.commit()
            logger.info("planetscale_schema_initialized", purpose="celtic_education")
        finally:
            self.return_connection(conn)


class DuckLakeBackend(StorageBackend):
    """DuckDB/MotherDuck analytics backend with Spatial extension."""

    def __init__(self, config: DuckLakeConfig | None = None):
        self.config = config or get_config().ducklake
        self._conn = None

    def connect(self) -> None:
        """Connect to DuckDB (local or MotherDuck) with Spatial extension."""
        try:
            import duckdb

            if self.config.is_motherduck:
                self._conn = duckdb.connect(self.config.connection_string)
            else:
                Path(self.config.local_path).parent.mkdir(parents=True, exist_ok=True)
                self._conn = duckdb.connect(self.config.local_path)

            # Load Spatial extension if enabled
            if self.config.enable_spatial:
                try:
                    self._conn.execute("INSTALL spatial; LOAD spatial;")
                    logger.info("duckdb_spatial_extension_loaded")
                except (RuntimeError, OSError) as e:
                    logger.warning("duckdb_spatial_extension_failed", error=str(e))

            logger.info("duckdb_connected", connection=self.config.connection_string)
        except ImportError:
            raise ImportError("duckdb is not installed. Run: pip install duckdb")

    def close(self) -> None:
        """Close DuckDB connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    def health_check(self) -> bool:
        """Check DuckDB connectivity."""
        try:
            import duckdb

            if self._conn is None:
                self.connect()
            self._conn.execute("SELECT 1").fetchone()
            return True
        except (duckdb.Error, ConnectionError, OSError) as e:
            logger.error("duckdb_health_check_failed", error=str(e))
            return False

    @property
    def conn(self):
        """Get the DuckDB connection."""
        if self._conn is None:
            self.connect()
        return self._conn

    def execute(self, query: str, params: list | None = None) -> list[dict]:
        """Execute a query and return results."""
        result = self.conn.execute(query, params or [])
        if result.description:
            columns = [desc[0] for desc in result.description]
            return [dict(zip(columns, row)) for row in result.fetchall()]
        return []

    def query_df(self, query: str, params: list | None = None):
        """Execute query and return as DataFrame."""
        return self.conn.execute(query, params or []).fetchdf()

    def init_schema(self) -> None:
        """Initialize analytics tables for Celtic education with geospatial support."""
        schema_sql = """
        -- Education schema for Ireland
        CREATE SCHEMA IF NOT EXISTS education;

        -- Statistics schema for UK nations
        CREATE SCHEMA IF NOT EXISTS statistics;

        -- Celtic language schema
        CREATE SCHEMA IF NOT EXISTS celtic;

        -- Geospatial schema
        CREATE SCHEMA IF NOT EXISTS geospatial;

        -- Training data schema for ML
        CREATE SCHEMA IF NOT EXISTS training;

        -- Analytics schema
        CREATE SCHEMA IF NOT EXISTS analytics;

        -- Document analytics
        CREATE TABLE IF NOT EXISTS analytics.document_stats (
            document_id VARCHAR PRIMARY KEY,
            title VARCHAR,
            nation VARCHAR,
            education_level VARCHAR,
            subject VARCHAR,
            document_type VARCHAR,
            language VARCHAR,
            chunk_count INTEGER,
            total_tokens INTEGER,
            avg_embedding_score FLOAT,
            indexed_at TIMESTAMP,
            source VARCHAR
        );

        -- Search analytics
        CREATE TABLE IF NOT EXISTS analytics.search_logs (
            id VARCHAR PRIMARY KEY,
            query_text VARCHAR,
            query_vector_hash VARCHAR,
            results_count INTEGER,
            top_score FLOAT,
            search_type VARCHAR,
            nation VARCHAR,
            language VARCHAR,
            latency_ms FLOAT,
            created_at TIMESTAMP DEFAULT NOW()
        );

        -- Alignment quality metrics
        CREATE TABLE IF NOT EXISTS analytics.alignment_quality (
            id VARCHAR PRIMARY KEY,
            source_lang VARCHAR,
            target_lang VARCHAR,
            method VARCHAR,
            avg_score FLOAT,
            pair_count INTEGER,
            evaluated_at TIMESTAMP DEFAULT NOW()
        );

        -- Embedding quality
        CREATE TABLE IF NOT EXISTS analytics.embedding_quality (
            document_id VARCHAR,
            chunk_id VARCHAR,
            embedding_model VARCHAR,
            similarity_score FLOAT,
            is_outlier BOOLEAN,
            analyzed_at TIMESTAMP DEFAULT NOW(),
            PRIMARY KEY (document_id, chunk_id)
        );
        """
        self.conn.execute(schema_sql)
        logger.info("duckdb_schema_initialized", purpose="celtic_education")


class GarageBackend(StorageBackend):
    """Garage S3-compatible storage backend for documents."""

    def __init__(self, config: GarageConfig | None = None):
        self.config = config or get_config().garage
        self._client = None

    def connect(self) -> None:
        """Connect to Garage S3."""
        try:
            import boto3
            from botocore.config import Config

            self._client = boto3.client(
                "s3",
                **self.config.s3_config,
                config=Config(signature_version="s3v4"),
            )
            logger.info("garage_connected", endpoint=self.config.endpoint_url)
        except ImportError:
            raise ImportError("boto3 is not installed. Run: pip install boto3")

    def close(self) -> None:
        """Close Garage connection."""
        self._client = None

    def health_check(self) -> bool:
        """Check Garage connectivity."""
        try:
            from botocore.exceptions import BotoCoreError, ClientError

            if self._client is None:
                self.connect()
            self._client.list_buckets()
            return True
        except (BotoCoreError, ClientError, ConnectionError) as e:
            logger.error("garage_health_check_failed", error=str(e))
            return False

    @property
    def client(self):
        """Get the S3 client."""
        if self._client is None:
            self.connect()
        return self._client

    def ensure_bucket(self) -> None:
        """Ensure the bucket exists."""
        from botocore.exceptions import ClientError

        try:
            self.client.head_bucket(Bucket=self.config.bucket)
        except ClientError as e:
            # 404 means bucket doesn't exist, create it
            error_code = e.response.get("Error", {}).get("Code", "")
            if error_code == "404":
                self.client.create_bucket(Bucket=self.config.bucket)
                logger.info("garage_bucket_created", bucket=self.config.bucket)
            else:
                raise

    def upload_document(
        self,
        key: str,
        data: bytes,
        content_type: str = "application/pdf",
        metadata: dict | None = None,
    ) -> str:
        """Upload a document to storage."""
        self.ensure_bucket()
        extra_args = {"ContentType": content_type}
        if metadata:
            extra_args["Metadata"] = {k: str(v) for k, v in metadata.items()}

        self.client.put_object(
            Bucket=self.config.bucket,
            Key=key,
            Body=data,
            **extra_args,
        )
        return f"s3://{self.config.bucket}/{key}"

    def download_document(self, key: str) -> bytes:
        """Download a document from storage."""
        response = self.client.get_object(Bucket=self.config.bucket, Key=key)
        return response["Body"].read()

    def get_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        """Get a presigned URL for a document."""
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.config.bucket, "Key": key},
            ExpiresIn=expires_in,
        )

    def list_documents(self, prefix: str = "", nation: str | None = None) -> list[dict]:
        """List documents with optional prefix and nation filter."""
        if nation:
            prefix = f"{nation}/{prefix}"

        response = self.client.list_objects_v2(
            Bucket=self.config.bucket,
            Prefix=prefix,
        )
        return [
            {
                "key": obj["Key"],
                "size": obj["Size"],
                "last_modified": obj["LastModified"].isoformat(),
            }
            for obj in response.get("Contents", [])
        ]

    def delete_document(self, key: str) -> None:
        """Delete a document from storage."""
        self.client.delete_object(Bucket=self.config.bucket, Key=key)


class StorageManager:
    """Unified storage manager for all backends."""

    def __init__(self, config: StorageConfig | None = None):
        self.config = config or get_config()
        self._lancedb: LanceDBBackend | None = None
        self._planetscale: PlanetScaleBackend | None = None
        self._ducklake: DuckLakeBackend | None = None
        self._garage: GarageBackend | None = None

    @property
    def lancedb(self) -> LanceDBBackend:
        """Get LanceDB backend."""
        if self._lancedb is None:
            self._lancedb = LanceDBBackend(self.config.lancedb)
        return self._lancedb

    @property
    def planetscale(self) -> PlanetScaleBackend:
        """Get PlanetScale backend."""
        if self._planetscale is None:
            self._planetscale = PlanetScaleBackend(self.config.planetscale)
        return self._planetscale

    @property
    def ducklake(self) -> DuckLakeBackend:
        """Get DuckDB/MotherDuck backend."""
        if self._ducklake is None:
            self._ducklake = DuckLakeBackend(self.config.ducklake)
        return self._ducklake

    @property
    def garage(self) -> GarageBackend:
        """Get Garage S3 backend."""
        if self._garage is None:
            self._garage = GarageBackend(self.config.garage)
        return self._garage

    def init_all(self) -> None:
        """Initialize all storage backends and schemas."""
        self.lancedb.connect()
        self.planetscale.connect()
        self.planetscale.init_schema()
        self.ducklake.connect()
        self.ducklake.init_schema()
        self.garage.connect()
        self.garage.ensure_bucket()
        logger.info("storage_backends_initialized", purpose="celtic_education")

    def health_check_all(self) -> dict[str, bool]:
        """Check health of all backends."""
        return {
            "lancedb": self.lancedb.health_check(),
            "planetscale": self.planetscale.health_check(),
            "ducklake": self.ducklake.health_check(),
            "garage": self.garage.health_check(),
        }

    def close_all(self) -> None:
        """Close all backend connections."""
        if self._lancedb:
            self._lancedb.close()
        if self._planetscale:
            self._planetscale.close()
        if self._ducklake:
            self._ducklake.close()
        if self._garage:
            self._garage.close()


# Factory function for getting specific backends
def get_storage_backend(backend_type: str) -> StorageBackend:
    """
    Get a storage backend by type.

    Args:
        backend_type: One of 'lancedb', 'planetscale', 'ducklake', 'garage'

    Returns:
        The requested storage backend instance
    """
    backends = {
        "lancedb": LanceDBBackend,
        "planetscale": PlanetScaleBackend,
        "ducklake": DuckLakeBackend,
        "garage": GarageBackend,
    }

    if backend_type not in backends:
        raise ValueError(f"Unknown backend type: {backend_type}. Choose from: {list(backends.keys())}")

    return backends[backend_type]()


# Singleton storage manager
_storage_manager: StorageManager | None = None


def get_storage_manager() -> StorageManager:
    """Get the storage manager singleton."""
    global _storage_manager
    if _storage_manager is None:
        _storage_manager = StorageManager()
    return _storage_manager
