"""
DuckLake SQL Catalog Integration.

Provides DuckDB access through DuckLake SQL-native catalog
with support for both local (SQLite) and production (PostgreSQL) catalogs.

Features:
- ACID transactions via SQL catalog
- Time-travel queries (snapshots)
- Parquet data files on S3
- Federated queries with other DuckDB sources
- Analytics tables for education pipeline
- Celtic language tables (linguistic + manuscript processing)

Celtic Manuscript Tables (from sruth/teanga):
- transcriptions: OCR results with language/dialect metadata
- ocr_results: Model performance (CER, WER, tironian_accuracy, fada_accuracy)
- training_samples: Bounding boxes and quality scores for fine-tuning
- cognates: Cross-language cognate groups (ga, gd, cy, gv, kw, br)
- manuscripts: IIIF manifest references and image metadata

Deployment modes:
- Local: SQLite catalog, file-based storage
- Production: PostgreSQL (PlanetScale), S3/R2 storage
"""

import os
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


# Celtic manuscript table schemas from sruth/teanga/storage/ducklake.py
# Used for OCR workflows, model evaluation, and training data preparation
CELTIC_MANUSCRIPT_SCHEMAS = {
    "transcriptions": {
        "id": "VARCHAR",
        "source": "VARCHAR",
        "collection": "VARCHAR",
        "image_path": "VARCHAR",
        "transcription": "TEXT",
        "normalized": "TEXT",
        "language": "VARCHAR",
        "dialect": "VARCHAR",
        "transcriber": "VARCHAR",
        "verified": "BOOLEAN",
        "created_at": "TIMESTAMP",
        "updated_at": "TIMESTAMP",
    },
    "ocr_results": {
        "id": "VARCHAR",
        "transcription_id": "VARCHAR",
        "model_name": "VARCHAR",
        "model_version": "VARCHAR",
        "prediction": "TEXT",
        "cer": "DOUBLE",
        "wer": "DOUBLE",
        "tironian_accuracy": "DOUBLE",
        "fada_accuracy": "DOUBLE",
        "latency_ms": "DOUBLE",
        "created_at": "TIMESTAMP",
    },
    "training_samples": {
        "id": "VARCHAR",
        "source": "VARCHAR",
        "image_path": "VARCHAR",
        "transcription": "TEXT",
        "bounding_boxes": "JSON",
        "split": "VARCHAR",
        "quality_score": "DOUBLE",
        "created_at": "TIMESTAMP",
    },
    "cognates": {
        "id": "VARCHAR",
        "group_id": "VARCHAR",
        "language": "VARCHAR",
        "word": "VARCHAR",
        "meaning": "VARCHAR",
        "etymology": "TEXT",
        "created_at": "TIMESTAMP",
    },
    "manuscripts": {
        "id": "VARCHAR",
        "source": "VARCHAR",
        "collection": "VARCHAR",
        "volume": "VARCHAR",
        "page": "INTEGER",
        "image_url": "VARCHAR",
        "iiif_manifest": "VARCHAR",
        "has_transcription": "BOOLEAN",
        "metadata": "JSON",
        "created_at": "TIMESTAMP",
    },
}


class CatalogType(str, Enum):
    """DuckLake catalog backend type."""
    SQLITE = "sqlite"
    POSTGRES = "postgres"


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
    catalog_name: str = "ducklake_catalog"

    # SQLite (local development)
    sqlite_path: str = "./storage/data/ducklake.ducklake"
    local_data_path: str = "./storage/data/ducklake_data"

    # PostgreSQL (production)
    postgres_host: str = ""
    postgres_port: int = 5432
    postgres_database: str = ""
    postgres_username: str = ""
    postgres_password: str = ""
    postgres_sslmode: str = "require"

    # S3/R2 storage (production)
    s3_endpoint: str = ""
    s3_access_key: str = ""
    s3_secret_key: str = ""
    s3_region: str = "auto"
    s3_bucket: str = ""
    s3_data_prefix: str = "ducklake/data/"

    @classmethod
    def from_env(cls) -> "DuckLakeConfig":
        """Load configuration from environment variables."""
        catalog_type = os.getenv("DUCKLAKE_CATALOG_TYPE", "sqlite")

        return cls(
            catalog_type=CatalogType(catalog_type),
            catalog_name=os.getenv("DUCKLAKE_CATALOG_NAME", "ducklake_catalog"),
            # SQLite
            sqlite_path=os.getenv("DUCKLAKE_SQLITE_PATH", "./storage/data/ducklake.ducklake"),
            local_data_path=os.getenv("DUCKLAKE_LOCAL_DATA_PATH", "./storage/data/ducklake_data"),
            # PostgreSQL
            postgres_host=os.getenv("PLANETSCALE_HOST", ""),
            postgres_port=int(os.getenv("PLANETSCALE_PORT", "5432")),
            postgres_database=os.getenv("PLANETSCALE_DATABASE", ""),
            postgres_username=os.getenv("PLANETSCALE_USERNAME", ""),
            postgres_password=os.getenv("PLANETSCALE_PASSWORD", ""),
            postgres_sslmode=os.getenv("PLANETSCALE_SSLMODE", "require"),
            # S3/R2
            s3_endpoint=os.getenv("GARAGE_ENDPOINT", os.getenv("R2_ENDPOINT", "")),
            s3_access_key=os.getenv("GARAGE_ACCESS_KEY", os.getenv("R2_ACCESS_KEY", "")),
            s3_secret_key=os.getenv("GARAGE_SECRET_KEY", os.getenv("R2_SECRET_KEY", "")),
            s3_region=os.getenv("GARAGE_REGION", os.getenv("R2_REGION", "auto")),
            s3_bucket=os.getenv("GARAGE_BUCKET", os.getenv("R2_BUCKET", "")),
            s3_data_prefix=os.getenv("DUCKLAKE_S3_PREFIX", "ducklake/data/"),
        )


class DuckLakeClient:
    """
    Client for DuckLake SQL catalog operations.

    DuckLake provides:
    - SQL-native table format (like Iceberg but simpler)
    - Time-travel via snapshots
    - Metadata in SQLite (local) or PostgreSQL (production)
    - Data files in Parquet locally or on S3
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

        logger.info(f"DuckLake catalog attached: {self._catalog_name} ({self.config.catalog_type.value})")
        return self._conn

    def _attach_sqlite_catalog(self) -> None:
        """Attach SQLite-based DuckLake catalog (local development)."""
        # Ensure directory exists
        sqlite_path = Path(self.config.sqlite_path)
        sqlite_path.parent.mkdir(parents=True, exist_ok=True)

        data_path = Path(self.config.local_data_path)
        data_path.mkdir(parents=True, exist_ok=True)

        # Attach DuckLake catalog with SQLite metadata
        self._conn.execute(f"""
            ATTACH 'ducklake:{self.config.sqlite_path}'
            AS {self._catalog_name}
            (DATA_PATH '{data_path}');
        """)

    def _attach_postgres_catalog(self) -> None:
        """Attach PostgreSQL-based DuckLake catalog (production)."""
        # Load additional extensions
        self._conn.execute("INSTALL postgres; LOAD postgres;")
        self._conn.execute("INSTALL httpfs; LOAD httpfs;")

        # Configure S3 access
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

        # Build data path
        data_path = f"s3://{cfg.s3_bucket}/{cfg.s3_data_prefix}"

        # Attach DuckLake catalog with PostgreSQL metadata
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
        import duckdb

        conn = self.conn
        try:
            yield conn
            conn.execute("COMMIT")
        except (duckdb.Error, OSError) as e:
            logger.warning("ducklake_transaction_rollback", error=str(e))
            conn.execute("ROLLBACK")
            raise

    # =========================================================================
    # Schema Operations
    # =========================================================================

    def use_catalog(self) -> None:
        """Set the DuckLake catalog as default."""
        self.conn.execute(f"USE {self._catalog_name};")

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
        """
        Create a table in DuckLake.

        Args:
            table_name: Name of the table
            schema: Schema name
            columns: Dict of column_name -> column_type
            as_select: Optional SELECT statement for CTAS
        """
        full_name = f"{self._catalog_name}.{schema}.{table_name}"

        if as_select:
            self.conn.execute(f"CREATE OR REPLACE TABLE {full_name} AS {as_select};")
        elif columns:
            col_defs = ", ".join(f"{name} {dtype}" for name, dtype in columns.items())
            self.conn.execute(f"CREATE TABLE IF NOT EXISTS {full_name} ({col_defs});")
        else:
            raise ValueError("Either columns or as_select must be provided")

    def drop_table(self, table_name: str, schema: str = "main") -> None:
        """Drop a table."""
        full_name = f"{self._catalog_name}.{schema}.{table_name}"
        self.conn.execute(f"DROP TABLE IF EXISTS {full_name};")

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
    # Analytics Tables for Education Pipeline
    # =========================================================================

    def init_analytics_schema(self) -> None:
        """Initialize analytics tables for education pipeline."""
        self.create_schema("analytics")

        # Document analytics
        self.create_table(
            "document_stats",
            schema="analytics",
            columns={
                "document_id": "VARCHAR",
                "title": "VARCHAR",
                "education_level": "VARCHAR",
                "subject": "VARCHAR",
                "document_type": "VARCHAR",
                "chunk_count": "INTEGER",
                "total_tokens": "INTEGER",
                "embedding_dim": "INTEGER",
                "indexed_at": "TIMESTAMP",
                "source": "VARCHAR",
                "nation": "VARCHAR",
                "language": "VARCHAR",
            },
        )

        # Search analytics
        self.create_table(
            "search_logs",
            schema="analytics",
            columns={
                "search_id": "VARCHAR",
                "query_text": "VARCHAR",
                "query_embedding_hash": "VARCHAR",
                "result_count": "INTEGER",
                "top_score": "FLOAT",
                "search_type": "VARCHAR",
                "latency_ms": "FLOAT",
                "user_id": "VARCHAR",
                "timestamp": "TIMESTAMP",
            },
        )

        # Generation analytics
        self.create_table(
            "generation_logs",
            schema="analytics",
            columns={
                "generation_id": "VARCHAR",
                "asset_type": "VARCHAR",
                "subject": "VARCHAR",
                "education_level": "VARCHAR",
                "model_used": "VARCHAR",
                "tokens_used": "INTEGER",
                "duration_ms": "FLOAT",
                "quality_score": "FLOAT",
                "timestamp": "TIMESTAMP",
            },
        )

        logger.info("Analytics schema initialized in DuckLake")

    # =========================================================================
    # Celtic Language Tables (from teanga)
    # =========================================================================

    def init_celtic_schema(self) -> None:
        """Initialize Celtic language tables."""
        self.create_schema("celtic")

        # Linguistic tokens
        self.create_table(
            "tokens",
            schema="celtic",
            columns={
                "token_id": "VARCHAR",
                "form": "VARCHAR",
                "lemma": "VARCHAR",
                "upos": "VARCHAR",
                "xpos": "VARCHAR",
                "features": "VARCHAR",
                "language": "VARCHAR",
                "dialect": "VARCHAR",
                "sentence_id": "VARCHAR",
                "position": "INTEGER",
            },
        )

        # Sentences
        self.create_table(
            "sentences",
            schema="celtic",
            columns={
                "sentence_id": "VARCHAR",
                "text": "TEXT",
                "translation": "TEXT",
                "language": "VARCHAR",
                "source": "VARCHAR",
                "source_id": "VARCHAR",
            },
        )

        # Lexicon
        self.create_table(
            "lexicon",
            schema="celtic",
            columns={
                "entry_id": "VARCHAR",
                "headword": "VARCHAR",
                "pos": "VARCHAR",
                "definition_en": "TEXT",
                "definition_ga": "TEXT",
                "examples": "TEXT",
                "domain": "VARCHAR",
                "language": "VARCHAR",
            },
        )

        # Initial mutations
        self.create_table(
            "mutations",
            schema="celtic",
            columns={
                "mutation_id": "VARCHAR",
                "base_form": "VARCHAR",
                "mutated_form": "VARCHAR",
                "mutation_type": "VARCHAR",
                "triggering_context": "VARCHAR",
                "language": "VARCHAR",
            },
        )

        # Translations (parallel corpus)
        self.create_table(
            "translations",
            schema="celtic",
            columns={
                "pair_id": "VARCHAR",
                "source_text": "TEXT",
                "target_text": "TEXT",
                "source_lang": "VARCHAR",
                "target_lang": "VARCHAR",
                "alignment_score": "FLOAT",
                "source_url": "VARCHAR",
            },
        )

        logger.info("Celtic schema initialized in DuckLake")

    def init_celtic_manuscript_tables(self) -> None:
        """
        Initialize Celtic manuscript and OCR processing tables.

        Based on sruth/teanga/storage/ducklake.py schemas for:
        - Manuscript transcription workflows
        - OCR model evaluation and comparison
        - Training data preparation
        - Cross-language cognate analysis
        """
        self.create_schema("celtic")

        # Transcriptions - OCR results with language/dialect metadata
        self.create_table(
            "transcriptions",
            schema="celtic",
            columns={
                "id": "VARCHAR",
                "source": "VARCHAR",  # e.g., 'isos', 'dias', 'rcahms'
                "collection": "VARCHAR",  # e.g., 'Book of Leinster'
                "image_path": "VARCHAR",  # Path to source image
                "transcription": "TEXT",  # Raw transcription
                "normalized": "TEXT",  # Normalized/modernized form
                "language": "VARCHAR",  # 'ga', 'gd', 'cy', 'gv'
                "dialect": "VARCHAR",  # 'connacht', 'munster', 'ulster', 'standard'
                "transcriber": "VARCHAR",  # Human or model name
                "verified": "BOOLEAN",  # Human verified flag
                "created_at": "TIMESTAMP",
                "updated_at": "TIMESTAMP",
            },
        )

        # OCR Results - Model performance tracking (CER, WER, tironian_accuracy)
        self.create_table(
            "ocr_results",
            schema="celtic",
            columns={
                "id": "VARCHAR",
                "transcription_id": "VARCHAR",  # FK to transcriptions
                "model_name": "VARCHAR",  # e.g., 'deepseek-ocr', 'qwen2-vl'
                "model_version": "VARCHAR",  # Semantic version
                "prediction": "TEXT",  # Model output
                "cer": "DOUBLE",  # Character Error Rate
                "wer": "DOUBLE",  # Word Error Rate
                "tironian_accuracy": "DOUBLE",  # Tironian note recognition
                "fada_accuracy": "DOUBLE",  # Accent mark accuracy
                "latency_ms": "DOUBLE",  # Inference time
                "created_at": "TIMESTAMP",
            },
        )

        # Training Samples - Prepared data for model fine-tuning
        self.create_table(
            "training_samples",
            schema="celtic",
            columns={
                "id": "VARCHAR",
                "source": "VARCHAR",  # Original source
                "image_path": "VARCHAR",  # Path to training image
                "transcription": "TEXT",  # Ground truth text
                "bounding_boxes": "JSON",  # Character/word boxes as JSON array
                "split": "VARCHAR",  # 'train', 'val', 'test'
                "quality_score": "DOUBLE",  # Data quality rating 0-1
                "created_at": "TIMESTAMP",
            },
        )

        # Cognates - Cross-language cognate groups for Celtic languages
        self.create_table(
            "cognates",
            schema="celtic",
            columns={
                "id": "VARCHAR",
                "group_id": "VARCHAR",  # Links related words across languages
                "language": "VARCHAR",  # 'ga', 'gd', 'cy', 'gv', 'kw', 'br'
                "word": "VARCHAR",  # The word in this language
                "meaning": "VARCHAR",  # English gloss
                "etymology": "TEXT",  # Proto-Celtic or historical notes
                "created_at": "TIMESTAMP",
            },
        )

        # Manuscripts - IIIF manifest references and metadata
        self.create_table(
            "manuscripts",
            schema="celtic",
            columns={
                "id": "VARCHAR",
                "source": "VARCHAR",  # Institution code
                "collection": "VARCHAR",  # Collection name
                "volume": "VARCHAR",  # Volume/folio reference
                "page": "INTEGER",  # Page number within volume
                "image_url": "VARCHAR",  # Direct image URL
                "iiif_manifest": "VARCHAR",  # IIIF manifest URL
                "has_transcription": "BOOLEAN",  # Whether transcription exists
                "metadata": "JSON",  # Additional metadata (date, scribe, etc.)
                "created_at": "TIMESTAMP",
            },
        )

        logger.info("Celtic manuscript tables initialized in DuckLake")

    def init_all_celtic_tables(self) -> None:
        """
        Initialize all Celtic language tables.

        Combines:
        - Linguistic tables (tokens, sentences, lexicon, mutations, translations)
        - Manuscript tables (transcriptions, ocr_results, training_samples, cognates, manuscripts)
        """
        self.init_celtic_schema()
        self.init_celtic_manuscript_tables()
        logger.info("All Celtic tables initialized in DuckLake")

    def log_search(
        self,
        query_text: str,
        result_count: int,
        top_score: float,
        search_type: str,
        latency_ms: float,
        user_id: str | None = None,
    ) -> None:
        """Log a search query for analytics."""
        import hashlib
        import uuid
        from datetime import datetime

        self.insert(
            "search_logs",
            schema="analytics",
            data=[
                {
                    "search_id": str(uuid.uuid4()),
                    "query_text": query_text[:500],
                    "query_embedding_hash": hashlib.md5(query_text.encode()).hexdigest(),
                    "result_count": result_count,
                    "top_score": top_score,
                    "search_type": search_type,
                    "latency_ms": latency_ms,
                    "user_id": user_id,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ],
        )


class DuckLakeBackend:
    """
    High-level backend for DuckLake operations.

    Provides a simpler interface for analytics queries,
    aggregations, cross-table joins, and time-travel queries.
    """

    def __init__(self, config: DuckLakeConfig | None = None):
        self.client = DuckLakeClient(config)

    def close(self) -> None:
        """Close the client."""
        self.client.close()

    def health_check(self) -> bool:
        """Check if DuckLake is accessible."""
        try:
            import duckdb

            self.client.conn.execute("SELECT 1").fetchone()
            return True
        except (duckdb.Error, ConnectionError, OSError) as e:
            logger.error("ducklake_health_check_failed", error=str(e))
            return False

    def get_document_stats(
        self,
        education_level: str | None = None,
        subject: str | None = None,
        nation: str | None = None,
    ) -> list[dict]:
        """Get document statistics with optional filters."""
        catalog = self.client._catalog_name
        query = f"""
            SELECT
                education_level,
                subject,
                document_type,
                nation,
                COUNT(*) as document_count,
                SUM(chunk_count) as total_chunks,
                AVG(total_tokens) as avg_tokens
            FROM {catalog}.analytics.document_stats
            WHERE 1=1
        """
        params = []

        if education_level:
            query += " AND education_level = ?"
            params.append(education_level)

        if subject:
            query += " AND subject = ?"
            params.append(subject)

        if nation:
            query += " AND nation = ?"
            params.append(nation)

        query += " GROUP BY education_level, subject, document_type, nation"

        return self.client.execute(query, params)

    def get_search_analytics(
        self,
        days: int = 7,
        search_type: str | None = None,
    ) -> dict[str, Any]:
        """Get search analytics summary."""
        catalog = self.client._catalog_name
        query = f"""
            SELECT
                COUNT(*) as total_searches,
                AVG(latency_ms) as avg_latency,
                AVG(result_count) as avg_results,
                AVG(top_score) as avg_top_score
            FROM {catalog}.analytics.search_logs
            WHERE timestamp >= NOW() - INTERVAL {days} DAY
        """

        if search_type:
            query += f" AND search_type = '{search_type}'"

        results = self.client.execute(query)
        return results[0] if results else {}

    def federated_query(
        self,
        query: str,
        external_sources: dict[str, str] | None = None,
    ) -> list[dict]:
        """
        Execute a federated query across DuckLake and external sources.

        Args:
            query: SQL query
            external_sources: Dict of alias -> path (s3://bucket/path or local file)
        """
        conn = self.client.conn

        # Attach external sources
        if external_sources:
            for alias, source in external_sources.items():
                if source.startswith("s3://"):
                    conn.execute(f"CREATE OR REPLACE VIEW {alias} AS SELECT * FROM read_parquet('{source}');")
                elif source.endswith(".csv"):
                    conn.execute(f"CREATE OR REPLACE VIEW {alias} AS SELECT * FROM read_csv('{source}');")
                elif source.endswith(".parquet"):
                    conn.execute(f"CREATE OR REPLACE VIEW {alias} AS SELECT * FROM read_parquet('{source}');")

        return self.client.execute(query)


# Singleton instance
_ducklake_backend: DuckLakeBackend | None = None


def get_ducklake_backend(config: DuckLakeConfig | None = None) -> DuckLakeBackend:
    """Get the DuckLake backend singleton."""
    global _ducklake_backend
    if _ducklake_backend is None:
        _ducklake_backend = DuckLakeBackend(config)
    return _ducklake_backend
