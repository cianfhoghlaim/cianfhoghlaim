"""
DuckLake SQL Catalog Integration for Crypteolas.

Provides DuckDB access through DuckLake SQL-native catalog
with support for both local (SQLite) and production (PostgreSQL) catalogs.

Features:
- ACID transactions via SQL catalog
- Time-travel queries (snapshots)
- Parquet data files on S3/Garage
- Federated queries with other DuckDB sources

Tables:
- scraped_documents: Documentation from URLs, GitHub, local files
- chunk_approvals: Human-in-the-loop chunk verification
- embeddings_metadata: Embedding batch tracking
- search_logs: Search analytics
"""

import logging
import os
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Generator

logger = logging.getLogger(__name__)


class CatalogType(str, Enum):
    """DuckLake catalog backend type."""

    SQLITE = "sqlite"
    POSTGRES = "postgres"


class ChunkApprovalStatus(str, Enum):
    """Status for chunk approval workflow."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class DocumentSourceType(str, Enum):
    """Types of document sources."""

    PROTOCOL_DOCS = "protocol_docs"
    USER_URL = "user_url"
    GITHUB = "github"
    LOCAL = "local"


@dataclass
class DuckLakeSnapshot:
    """DuckLake snapshot information."""

    snapshot_id: int
    created_at: str
    schema_version: int
    table_count: int


@dataclass
class DuckLakeConfig:
    """Configuration for DuckLake client."""

    # Catalog configuration
    catalog_type: CatalogType = CatalogType.SQLITE
    catalog_name: str = "crypteolas_catalog"

    # SQLite (local development)
    sqlite_path: str = "./storage/data/ducklake.ducklake"
    local_data_path: str = "./storage/data/ducklake_data"

    # PostgreSQL (production - PlanetScale)
    postgres_host: str = ""
    postgres_port: int = 5432
    postgres_database: str = ""
    postgres_username: str = ""
    postgres_password: str = ""
    postgres_sslmode: str = "require"

    # S3/Garage storage (production)
    s3_endpoint: str = ""
    s3_access_key: str = ""
    s3_secret_key: str = ""
    s3_region: str = "garage"
    s3_bucket: str = ""
    s3_data_prefix: str = "crypteolas/ducklake/"

    @classmethod
    def from_env(cls) -> "DuckLakeConfig":
        """Load configuration from environment variables."""
        catalog_type = os.getenv("DUCKLAKE_CATALOG_TYPE", "sqlite")

        return cls(
            catalog_type=CatalogType(catalog_type),
            catalog_name=os.getenv("DUCKLAKE_CATALOG_NAME", "crypteolas_catalog"),
            # SQLite
            sqlite_path=os.getenv("DUCKLAKE_SQLITE_PATH", "./storage/data/ducklake.ducklake"),
            local_data_path=os.getenv("DUCKLAKE_LOCAL_DATA_PATH", "./storage/data/ducklake_data"),
            # PostgreSQL (PlanetScale)
            postgres_host=os.getenv("PLANETSCALE_HOST", ""),
            postgres_port=int(os.getenv("PLANETSCALE_PORT", "5432")),
            postgres_database=os.getenv("PLANETSCALE_DATABASE", ""),
            postgres_username=os.getenv("PLANETSCALE_USERNAME", ""),
            postgres_password=os.getenv("PLANETSCALE_PASSWORD", ""),
            postgres_sslmode=os.getenv("PLANETSCALE_SSLMODE", "require"),
            # S3/Garage
            s3_endpoint=os.getenv("GARAGE_ENDPOINT", ""),
            s3_access_key=os.getenv("GARAGE_ACCESS_KEY", ""),
            s3_secret_key=os.getenv("GARAGE_SECRET_KEY", ""),
            s3_region=os.getenv("GARAGE_REGION", "garage"),
            s3_bucket=os.getenv("GARAGE_BUCKET", ""),
            s3_data_prefix=os.getenv("DUCKLAKE_S3_PREFIX", "crypteolas/ducklake/"),
        )


# Schema definitions for crypteolas tables
CRYPTEOLAS_SCHEMAS = {
    "scraped_documents": {
        "id": "VARCHAR PRIMARY KEY",
        "url": "VARCHAR",
        "title": "VARCHAR",
        "markdown": "TEXT",
        "source_type": "VARCHAR",  # protocol_docs, user_url, github, local
        "protocol": "VARCHAR",  # e.g., uniswap, aave, compound
        "file_path": "VARCHAR",  # for local files
        "content_hash": "VARCHAR",
        "pdf_links": "JSON",
        "scraped_at": "TIMESTAMP",
        "updated_at": "TIMESTAMP",
        "requested_by": "VARCHAR",  # user who requested scrape
    },
    "chunk_approvals": {
        "id": "VARCHAR PRIMARY KEY",
        "chunk_id": "VARCHAR",
        "document_id": "VARCHAR",
        "user_id": "VARCHAR",
        "status": "VARCHAR",  # pending, approved, rejected
        "feedback": "TEXT",
        "created_at": "TIMESTAMP",
        "updated_at": "TIMESTAMP",
    },
    "embeddings_metadata": {
        "id": "VARCHAR PRIMARY KEY",
        "batch_id": "VARCHAR",
        "document_id": "VARCHAR",
        "chunk_count": "INTEGER",
        "model": "VARCHAR",
        "dimension": "INTEGER",
        "lance_table": "VARCHAR",
        "created_at": "TIMESTAMP",
    },
    "search_logs": {
        "id": "VARCHAR PRIMARY KEY",
        "query": "TEXT",
        "query_hash": "VARCHAR",
        "source_filter": "JSON",
        "protocol_filter": "JSON",
        "result_count": "INTEGER",
        "top_score": "FLOAT",
        "latency_ms": "FLOAT",
        "user_id": "VARCHAR",
        "created_at": "TIMESTAMP",
    },
}


class DuckLakeClient:
    """
    Client for DuckLake SQL catalog operations.

    DuckLake provides:
    - SQL-native table format (like Iceberg but simpler)
    - Time-travel via snapshots
    - Metadata in SQLite (local) or PostgreSQL (production)
    - Data files in Parquet locally or on S3/Garage
    """

    def __init__(self, config: DuckLakeConfig | None = None):
        self.config = config or DuckLakeConfig.from_env()
        self._conn = None
        self._catalog_name = self.config.catalog_name

    def _get_connection(self):
        """Get or create DuckDB connection with DuckLake attached."""
        if self._conn is not None:
            return self._conn

        try:
            import duckdb
        except ImportError:
            raise ImportError("duckdb is not installed. Run: pip install duckdb")

        self._conn = duckdb.connect(":memory:")

        # Install and load extensions
        self._conn.execute("INSTALL ducklake; LOAD ducklake;")

        if self.config.catalog_type == CatalogType.SQLITE:
            self._attach_sqlite_catalog()
        else:
            self._attach_postgres_catalog()

        logger.info(
            f"DuckLake catalog attached: {self._catalog_name} ({self.config.catalog_type.value})"
        )
        return self._conn

    def _attach_sqlite_catalog(self) -> None:
        """Attach SQLite-based DuckLake catalog (local development)."""
        sqlite_path = Path(self.config.sqlite_path)
        sqlite_path.parent.mkdir(parents=True, exist_ok=True)

        data_path = Path(self.config.local_data_path)
        data_path.mkdir(parents=True, exist_ok=True)

        self._conn.execute(f"""
            ATTACH 'ducklake:{self.config.sqlite_path}'
            AS {self._catalog_name}
            (DATA_PATH '{data_path}');
        """)

    def _attach_postgres_catalog(self) -> None:
        """Attach PostgreSQL-based DuckLake catalog (production)."""
        self._conn.execute("INSTALL postgres; LOAD postgres;")
        self._conn.execute("INSTALL httpfs; LOAD httpfs;")

        cfg = self.config
        endpoint = cfg.s3_endpoint.replace("https://", "").replace("http://", "")
        use_ssl = "true" if "https" in cfg.s3_endpoint else "false"

        self._conn.execute(f"""
            SET s3_endpoint = '{endpoint}';
            SET s3_access_key_id = '{cfg.s3_access_key}';
            SET s3_secret_access_key = '{cfg.s3_secret_key}';
            SET s3_region = '{cfg.s3_region}';
            SET s3_use_ssl = {use_ssl};
        """)

        data_path = f"s3://{cfg.s3_bucket}/{cfg.s3_data_prefix}"

        self._conn.execute(f"""
            ATTACH 'ducklake:postgres:dbname={cfg.postgres_database} host={cfg.postgres_host} port={cfg.postgres_port} user={cfg.postgres_username} password={cfg.postgres_password} sslmode={cfg.postgres_sslmode}'
            AS {self._catalog_name}
            (DATA_PATH '{data_path}');
        """)

    @property
    def conn(self):
        """Get the DuckDB connection."""
        return self._get_connection()

    def close(self) -> None:
        """Close DuckDB connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    @contextmanager
    def transaction(self) -> Generator[Any, None, None]:
        """Context manager for transactions."""
        conn = self.conn
        try:
            yield conn
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            raise

    # =========================================================================
    # Schema Operations
    # =========================================================================

    def create_schema(self, schema_name: str) -> None:
        """Create a schema in DuckLake catalog."""
        self.conn.execute(f"CREATE SCHEMA IF NOT EXISTS {self._catalog_name}.{schema_name};")

    def list_schemas(self) -> list[str]:
        """List all schemas in the catalog."""
        result = self.conn.execute(
            f"SELECT schema_name FROM information_schema.schemata WHERE catalog_name = '{self._catalog_name}';"
        ).fetchall()
        return [row[0] for row in result]

    # =========================================================================
    # Table Operations
    # =========================================================================

    def list_tables(self, schema: str = "main") -> list[str]:
        """List tables in a schema."""
        result = self.conn.execute(f"""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_catalog = '{self._catalog_name}'
            AND table_schema = '{schema}';
        """).fetchall()
        return [row[0] for row in result]

    def create_table(
        self,
        table_name: str,
        schema: str = "main",
        columns: dict[str, str] | None = None,
        as_select: str | None = None,
    ) -> None:
        """Create a table in DuckLake."""
        full_name = f"{self._catalog_name}.{schema}.{table_name}"

        if as_select:
            self.conn.execute(f"CREATE OR REPLACE TABLE {full_name} AS {as_select};")
        elif columns:
            col_defs = ", ".join(f"{name} {dtype}" for name, dtype in columns.items())
            self.conn.execute(f"CREATE TABLE IF NOT EXISTS {full_name} ({col_defs});")
        else:
            raise ValueError("Either columns or as_select must be provided")

    def table_exists(self, table_name: str, schema: str = "main") -> bool:
        """Check if a table exists."""
        return table_name in self.list_tables(schema)

    # =========================================================================
    # Data Operations
    # =========================================================================

    def execute(self, query: str, params: list | None = None) -> list[dict]:
        """Execute a query and return results as list of dicts."""
        result = self.conn.execute(query, params or [])
        if result.description:
            columns = [desc[0] for desc in result.description]
            return [dict(zip(columns, row)) for row in result.fetchall()]
        return []

    def query_df(self, query: str, params: list | None = None):
        """Execute query and return as DataFrame."""
        return self.conn.execute(query, params or []).fetchdf()

    def insert(
        self,
        table_name: str,
        data: list[dict],
        schema: str = "main",
    ) -> int:
        """Insert records into a table. Returns number of rows inserted."""
        if not data:
            return 0

        full_name = f"{self._catalog_name}.{schema}.{table_name}"
        columns = list(data[0].keys())
        placeholders = ", ".join(["?" for _ in columns])
        col_list = ", ".join(columns)

        query = f"INSERT INTO {full_name} ({col_list}) VALUES ({placeholders})"

        for record in data:
            values = [record.get(col) for col in columns]
            self.conn.execute(query, values)

        return len(data)

    def upsert(
        self,
        table_name: str,
        data: list[dict],
        key_columns: list[str],
        schema: str = "main",
    ) -> int:
        """Upsert (INSERT ON CONFLICT UPDATE) records."""
        if not data:
            return 0

        full_name = f"{self._catalog_name}.{schema}.{table_name}"
        columns = list(data[0].keys())
        value_cols = [c for c in columns if c not in key_columns]

        placeholders = ", ".join(["?" for _ in columns])
        col_list = ", ".join(columns)
        key_list = ", ".join(key_columns)
        update_list = ", ".join(f"{c} = EXCLUDED.{c}" for c in value_cols)

        query = f"""
            INSERT INTO {full_name} ({col_list})
            VALUES ({placeholders})
            ON CONFLICT ({key_list})
            DO UPDATE SET {update_list}
        """

        for record in data:
            values = [record.get(col) for col in columns]
            self.conn.execute(query, values)

        return len(data)

    # =========================================================================
    # Time Travel (Snapshots)
    # =========================================================================

    def list_snapshots(self) -> list[DuckLakeSnapshot]:
        """List all snapshots in the catalog."""
        result = self.conn.execute(
            f"SELECT * FROM ducklake_snapshots('{self._catalog_name}');"
        ).fetchall()

        snapshots = []
        for row in result:
            snapshots.append(
                DuckLakeSnapshot(
                    snapshot_id=row[0],
                    created_at=str(row[1]),
                    schema_version=row[2] if len(row) > 2 else 0,
                    table_count=row[3] if len(row) > 3 else 0,
                )
            )
        return snapshots

    def query_at_snapshot(
        self,
        query: str,
        snapshot_id: int,
    ) -> list[dict]:
        """Execute a query at a specific snapshot point."""
        result = self.conn.execute(
            f"SELECT * FROM ducklake_time_travel('{self._catalog_name}', {snapshot_id}, $${query}$$);"
        )
        if result.description:
            columns = [desc[0] for desc in result.description]
            return [dict(zip(columns, row)) for row in result.fetchall()]
        return []

    # =========================================================================
    # Crypteolas Schema Initialization
    # =========================================================================

    def init_crypteolas_schema(self) -> None:
        """Initialize all crypteolas tables."""
        self.create_schema("docs")
        self.create_schema("rag")
        self.create_schema("analytics")

        # Scraped documents
        self.create_table(
            "scraped_documents",
            schema="docs",
            columns=CRYPTEOLAS_SCHEMAS["scraped_documents"],
        )

        # Chunk approvals for HITL
        self.create_table(
            "chunk_approvals",
            schema="rag",
            columns=CRYPTEOLAS_SCHEMAS["chunk_approvals"],
        )

        # Embeddings metadata
        self.create_table(
            "embeddings_metadata",
            schema="rag",
            columns=CRYPTEOLAS_SCHEMAS["embeddings_metadata"],
        )

        # Search analytics
        self.create_table(
            "search_logs",
            schema="analytics",
            columns=CRYPTEOLAS_SCHEMAS["search_logs"],
        )

        logger.info("Crypteolas schema initialized in DuckLake")

    # =========================================================================
    # Document Operations
    # =========================================================================

    def save_document(
        self,
        url: str,
        title: str,
        markdown: str,
        source_type: DocumentSourceType,
        protocol: str | None = None,
        file_path: str | None = None,
        pdf_links: list[str] | None = None,
        requested_by: str | None = None,
    ) -> str:
        """Save a scraped document. Returns document ID."""
        import hashlib
        import json
        import uuid

        doc_id = str(uuid.uuid4())
        content_hash = hashlib.sha256(markdown.encode()).hexdigest()
        now = datetime.utcnow().isoformat()

        self.upsert(
            "scraped_documents",
            schema="docs",
            data=[
                {
                    "id": doc_id,
                    "url": url,
                    "title": title,
                    "markdown": markdown,
                    "source_type": source_type.value,
                    "protocol": protocol,
                    "file_path": file_path,
                    "content_hash": content_hash,
                    "pdf_links": json.dumps(pdf_links) if pdf_links else None,
                    "scraped_at": now,
                    "updated_at": now,
                    "requested_by": requested_by,
                }
            ],
            key_columns=["url"],
        )

        return doc_id

    def get_documents(
        self,
        source_type: DocumentSourceType | None = None,
        protocol: str | None = None,
        limit: int = 100,
    ) -> list[dict]:
        """Get scraped documents with optional filters."""
        query = f"SELECT * FROM {self._catalog_name}.docs.scraped_documents WHERE 1=1"
        params = []

        if source_type:
            query += " AND source_type = ?"
            params.append(source_type.value)

        if protocol:
            query += " AND protocol = ?"
            params.append(protocol)

        query += f" ORDER BY scraped_at DESC LIMIT {limit}"

        return self.execute(query, params)

    # =========================================================================
    # Chunk Approval Operations (HITL)
    # =========================================================================

    def create_chunk_approval(
        self,
        chunk_id: str,
        document_id: str,
        user_id: str | None = None,
    ) -> str:
        """Create a pending chunk approval. Returns approval ID."""
        import uuid

        approval_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        self.insert(
            "chunk_approvals",
            schema="rag",
            data=[
                {
                    "id": approval_id,
                    "chunk_id": chunk_id,
                    "document_id": document_id,
                    "user_id": user_id,
                    "status": ChunkApprovalStatus.PENDING.value,
                    "feedback": None,
                    "created_at": now,
                    "updated_at": now,
                }
            ],
        )

        return approval_id

    def update_chunk_approval(
        self,
        approval_id: str,
        status: ChunkApprovalStatus,
        feedback: str | None = None,
    ) -> None:
        """Update a chunk approval status."""
        now = datetime.utcnow().isoformat()
        self.conn.execute(
            f"""
            UPDATE {self._catalog_name}.rag.chunk_approvals
            SET status = ?, feedback = ?, updated_at = ?
            WHERE id = ?
        """,
            [status.value, feedback, now, approval_id],
        )

    def get_pending_approvals(self, limit: int = 50) -> list[dict]:
        """Get pending chunk approvals."""
        return self.execute(f"""
            SELECT * FROM {self._catalog_name}.rag.chunk_approvals
            WHERE status = 'pending'
            ORDER BY created_at ASC
            LIMIT {limit}
        """)

    # =========================================================================
    # Search Logging
    # =========================================================================

    def log_search(
        self,
        query: str,
        result_count: int,
        top_score: float,
        latency_ms: float,
        source_filter: list[str] | None = None,
        protocol_filter: list[str] | None = None,
        user_id: str | None = None,
    ) -> None:
        """Log a search query for analytics."""
        import hashlib
        import json
        import uuid

        self.insert(
            "search_logs",
            schema="analytics",
            data=[
                {
                    "id": str(uuid.uuid4()),
                    "query": query[:1000],
                    "query_hash": hashlib.md5(query.encode()).hexdigest(),
                    "source_filter": json.dumps(source_filter) if source_filter else None,
                    "protocol_filter": json.dumps(protocol_filter) if protocol_filter else None,
                    "result_count": result_count,
                    "top_score": top_score,
                    "latency_ms": latency_ms,
                    "user_id": user_id,
                    "created_at": datetime.utcnow().isoformat(),
                }
            ],
        )


# Singleton instance
_ducklake_client: DuckLakeClient | None = None


def get_ducklake_client(config: DuckLakeConfig | None = None) -> DuckLakeClient:
    """Get the DuckLake client singleton."""
    global _ducklake_client
    if _ducklake_client is None:
        _ducklake_client = DuckLakeClient(config)
    return _ducklake_client
