"""Unified storage interface for all sruth flows.

This module provides a single API for accessing all storage backends:
- Lakekeeper (Iceberg REST catalog) for table metadata
- DuckDB for local analytics and development
- S3/Garage/R2 for object storage (PDFs, images, etc.)
- LanceDB for vector embeddings
- PostgreSQL for structured metadata

The interface auto-detects backends based on environment variables and
provides a consistent API regardless of the underlying storage.

Usage:
    from sruth.shared.storage import get_storage

    storage = get_storage()

    # Write data
    storage.write_table("curriculum", "documents", data)

    # Read data
    df = storage.read_table("curriculum", "documents")

    # Store objects
    storage.put_object("curriculum", "doc.pdf", pdf_bytes)

    # Vector operations
    storage.upsert_embeddings("curriculum", vectors, metadata)
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, AsyncIterator, BinaryIO, Callable, Iterable

import pydantic


class StorageType(str, Enum):
    """Storage backend types."""

    DUCKDB = "duckdb"
    ICEBERG = "iceberg"
    POSTGRES = "postgres"
    LANCEDB = "lancedb"
    S3 = "s3"


@dataclass
class TableRef:
    """Reference to a table in storage."""

    namespace: str
    name: str

    @property
    def qualified_name(self) -> str:
        return f"{self.namespace}.{self.name}"

    def __str__(self) -> str:
        return self.qualified_name


@dataclass
class ObjectRef:
    """Reference to an object in storage."""

    bucket: str
    key: str

    @property
    def uri(self) -> str:
        return f"s3://{self.bucket}/{self.key}"

    def __str__(self) -> str:
        return self.uri


# ============================================================================
# Abstract Interfaces
# ============================================================================


class TableStorage(ABC):
    """Abstract interface for tabular storage."""

    @abstractmethod
    def write_table(
        self,
        ref: TableRef,
        data: Iterable[dict] | list[dict],
        mode: str = "append",  # append, overwrite, merge
        primary_key: str | list[str] | None = None,
    ) -> TableWriteResult:
        """Write data to a table."""

    @abstractmethod
    def read_table(
        self,
        ref: TableRef,
        columns: list[str] | None = None,
        filters: dict[str, Any] | None = None,
        limit: int | None = None,
    ) -> Any:  # Return DataFrame-like object
        """Read data from a table."""

    @abstractmethod
    def table_exists(self, ref: TableRef) -> bool:
        """Check if a table exists."""

    @abstractmethod
    def list_tables(self, namespace: str) -> list[str]:
        """List tables in a namespace."""

    @abstractmethod
    def drop_table(self, ref: TableRef) -> None:
        """Drop a table."""


class ObjectStorage(ABC):
    """Abstract interface for object storage."""

    @abstractmethod
    def put_object(
        self,
        ref: ObjectRef,
        data: bytes | BinaryIO,
        metadata: dict[str, str] | None = None,
    ) -> str:
        """Store an object, return its URI."""

    @abstractmethod
    def get_object(self, ref: ObjectRef) -> bytes:
        """Retrieve an object."""

    @abstractmethod
    def object_exists(self, ref: ObjectRef) -> bool:
        """Check if an object exists."""

    @abstractmethod
    def delete_object(self, ref: ObjectRef) -> None:
        """Delete an object."""

    @abstractmethod
    def list_objects(self, prefix: str, bucket: str | None = None) -> list[str]:
        """List objects with a prefix."""


class VectorStorage(ABC):
    """Abstract interface for vector storage."""

    @abstractmethod
    def upsert_embeddings(
        self,
        table: str,
        ids: list[str],
        vectors: list[list[float]],
        metadata: list[dict] | None = None,
    ) -> int:
        """Add or update embeddings."""

    @abstractmethod
    def search(
        self,
        table: str,
        query: list[float],
        limit: int = 10,
        filters: dict[str, Any] | None = None,
    ) -> list[dict]:
        """Search for similar vectors."""

    @abstractmethod
    def delete_vectors(self, table: str, ids: list[str]) -> int:
        """Delete vectors by ID."""


# ============================================================================
# Results
# ============================================================================


@dataclass
class TableWriteResult:
    """Result of a table write operation."""

    rows_written: int
    table_ref: TableRef
    write_mode: str
    metadata: dict[str, Any] | None = None


# ============================================================================
# DuckDB Implementation
# ============================================================================


class DuckDBTableStorage(TableStorage):
    """DuckDB-based table storage."""

    def __init__(
        self,
        path: str = "./data.duckdb",
        schema: str = "main",
    ):
        self.path = path
        self.schema = schema
        self._conn = None

    def _get_conn(self):
        """Get or create DuckDB connection."""
        if self._conn is None:
            import duckdb

            self._conn = duckdb.connect(self.path)
        return self._conn

    def close(self):
        """Close the connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    def write_table(
        self,
        ref: TableRef,
        data: Iterable[dict] | list[dict],
        mode: str = "append",
        primary_key: str | list[str] | None = None,
    ) -> TableWriteResult:
        """Write data to DuckDB table."""
        conn = self._get_conn()

        # Convert data to list for counting
        if not isinstance(data, list):
            data = list(data)

        rows_written = len(data)

        if mode == "overwrite" or not self.table_exists(ref):
            # Create table
            conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {ref.qualified_name} AS
                SELECT * FROM data
            """)
        elif mode == "append":
            # Insert data
            conn.execute(f"""
                INSERT INTO {ref.qualified_name}
                SELECT * FROM data
            """)
        elif mode == "merge":
            # Merge using primary key
            if primary_key:
                pk_list = primary_key if isinstance(primary_key, list) else [primary_key]
                pk_cols = ", ".join(pk_list)

                # Delete existing rows with same keys
                conn.execute(f"""
                    DELETE FROM {ref.qualified_name}
                    WHERE ({pk_cols}) IN (
                        SELECT {pk_cols} FROM data
                    )
                """)
                conn.execute(f"""
                    INSERT INTO {ref.qualified_name}
                    SELECT * FROM data
                """)
            else:
                # Fall back to append
                conn.execute(f"""
                    INSERT INTO {ref.qualified_name}
                    SELECT * FROM data
                """)

        return TableWriteResult(
            rows_written=rows_written,
            table_ref=ref,
            write_mode=mode,
        )

    def read_table(
        self,
        ref: TableRef,
        columns: list[str] | None = None,
        filters: dict[str, Any] | None = None,
        limit: int | None = None,
    ) -> Any:
        """Read data from DuckDB table."""
        conn = self._get_conn()

        col_clause = "*"
        if columns:
            col_clause = ", ".join(columns)

        query = f"SELECT {col_clause} FROM {ref.qualified_name}"

        if filters:
            conditions = [f"{k} = {repr(v)}" for k, v in filters.items()]
            query += " WHERE " + " AND ".join(conditions)

        if limit:
            query += f" LIMIT {limit}"

        return conn.execute(query).fetchall()

    def table_exists(self, ref: TableRef) -> bool:
        """Check if table exists."""
        conn = self._get_conn()
        try:
            result = conn.execute(
                f"SELECT 1 FROM information_schema.tables "
                f"WHERE table_schema = '{ref.namespace}' "
                f"AND table_name = '{ref.name}'"
            ).fetchone()
            return result is not None
        except Exception:
            return False

    def list_tables(self, namespace: str) -> list[str]:
        """List tables in schema."""
        conn = self._get_conn()
        try:
            result = conn.execute(
                f"SELECT table_name FROM information_schema.tables "
                f"WHERE table_schema = '{namespace}'"
            ).fetchall()
            return [row[0] for row in result]
        except Exception:
            return []

    def drop_table(self, ref: TableRef) -> None:
        """Drop table."""
        conn = self._get_conn()
        conn.execute(f"DROP TABLE IF EXISTS {ref.qualified_name}")


# ============================================================================
# S3/Garage/R2 Implementation
# ============================================================================


class S3ObjectStorage(ObjectStorage):
    """S3-compatible object storage (Garage, R2, MinIO)."""

    def __init__(
        self,
        endpoint_url: str | None = None,
        aws_access_key_id: str = "",
        aws_secret_access_key: str = "",
        region: str = "garage",
        use_ssl: bool = False,
    ):
        self.endpoint_url = endpoint_url
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.region = region
        self.use_ssl = use_ssl
        self._client = None

    def _get_client(self):
        """Get or create S3 client."""
        if self._client is None:
            import boto3

            from botocore.config import Config

            # CRITICAL: Path-style URLs required for Garage/MinIO
            config = Config(
                signature_version="s3v4",
                s3={"addressing_style": "path"},
            )

            self._client = boto3.client(
                "s3",
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.region,
                use_ssl=self.use_ssl,
                config=config,
            )
        return self._client

    def put_object(
        self,
        ref: ObjectRef,
        data: bytes | BinaryIO,
        metadata: dict[str, str] | None = None,
    ) -> str:
        """Store an object in S3."""
        client = self._get_client()

        if isinstance(data, bytes):
            client.put_object(
                Bucket=ref.bucket,
                Key=ref.key,
                Body=data,
                Metadata=metadata or {},
            )
        else:
            client.upload_fileobj(
                data,
                ref.bucket,
                ref.key,
                ExtraArgs={"Metadata": metadata or {}} if metadata else {},
            )

        return ref.uri

    def get_object(self, ref: ObjectRef) -> bytes:
        """Retrieve an object from S3."""
        client = self._get_client()
        response = client.get_object(Bucket=ref.bucket, Key=ref.key)
        return response["Body"].read()

    def object_exists(self, ref: ObjectRef) -> bool:
        """Check if object exists."""
        client = self._get_client()
        try:
            client.head_object(Bucket=ref.bucket, Key=ref.key)
            return True
        except Exception:
            return False

    def delete_object(self, ref: ObjectRef) -> None:
        """Delete an object."""
        client = self._get_client()
        client.delete_object(Bucket=ref.bucket, Key=ref.key)

    def list_objects(self, prefix: str, bucket: str | None = None) -> list[str]:
        """List objects with prefix."""
        client = self._get_client()
        buckets = [bucket] if bucket else []

        if not buckets:
            # List all buckets if none specified
            buckets = [b["Name"] for b in client.list_buckets()["Buckets"]]

        results = []
        for b in buckets:
            try:
                response = client.list_objects_v2(Bucket=b, Prefix=prefix)
                if "Contents" in response:
                    results.extend([obj["Key"] for obj in response["Contents"]])
            except Exception:
                pass

        return results


# ============================================================================
# Lakekeeper/Iceberg Implementation
# ============================================================================


class IcebergTableStorage(TableStorage):
    """Iceberg table storage via Lakekeeper REST catalog."""

    def __init__(
        self,
        catalog_uri: str = "http://lakekeeper:8181",
        warehouse: str = "s3://garage/warehouse",
        namespace: str = "default",
    ):
        self.catalog_uri = catalog_uri
        self.warehouse = warehouse
        self.namespace = namespace
        self._client = None

    def _get_client(self):
        """Get or create Lakekeeper client."""
        if self._client is None:
            from sruth.shared.dagster.resources import LakeKeeperResource

            self._resource = LakeKeeperResource(
                catalog_uri=self.catalog_uri,
                warehouse=self.warehouse,
                namespace=self.namespace,
            )
        return self._resource

    def write_table(
        self,
        ref: TableRef,
        data: Iterable[dict] | list[dict],
        mode: str = "append",
        primary_key: str | list[str] | None = None,
    ) -> TableWriteResult:
        """Write data using DLT to Iceberg."""
        import dlt

        from sruth.shared.dlt.destinations import get_iceberg_destination

        # Convert to list
        if not isinstance(data, list):
            data = list(data)

        # Infer schema from first row
        if data:
            schema = {k: self._infer_type(v) for k, v in data[0].items()}
        else:
            schema = {}

        # Register table if needed
        resource = self._get_client()
        if mode == "overwrite" or not self.table_exists(ref):
            resource.register_table(
                namespace=ref.namespace,
                table_name=ref.name,
                schema=schema,
            )

        # Use DLT to write
        pipeline = dlt.pipeline(
            pipeline_name=f"write_{ref.name}",
            destination=get_iceberg_destination(),
            dataset_name=ref.namespace,
        )

        @dlt.resource
        def _data_resource():
            for row in data:
                yield row

        result = pipeline.run(
            _data_resource(),
            table_name=ref.name,
            write_disposition=mode,
            primary_key=primary_key or "id",
        )

        rows_written = len(data)

        return TableWriteResult(
            rows_written=rows_written,
            table_ref=ref,
            write_mode=mode,
            metadata={"load_id": str(result.loads_ids[0]) if result.loads_ids else None},
        )

    def _infer_type(self, value: Any) -> str:
        """Infer Iceberg type from Python value."""
        if isinstance(value, bool):
            return "BOOLEAN"
        if isinstance(value, int):
            return "BIGINT"
        if isinstance(value, float):
            return "DOUBLE"
        if isinstance(value, str):
            return "VARCHAR"
        if isinstance(value, (list, dict)):
            return "JSON"
        return "VARCHAR"

    def read_table(
        self,
        ref: TableRef,
        columns: list[str] | None = None,
        filters: dict[str, Any] | None = None,
        limit: int | None = None,
    ) -> Any:
        """Read from Iceberg table."""
        import duckdb

        # Configure DuckDB for Iceberg
        conn = duckdb.connect(":memory:")
        conn.sql("INSTALL iceberg FROM community")
        conn.sql("LOAD iceberg")

        # Build query
        col_clause = "*" if not columns else ", ".join(columns)

        query = f"""
            SELECT {col_clause}
            FROM iceberg_scan('{self.warehouse}/{ref.namespace}/{ref.name}')
        """

        if filters:
            conditions = [f"{k} = {repr(v)}" for k, v in filters.items()]
            query += " WHERE " + " AND ".join(conditions)

        if limit:
            query += f" LIMIT {limit}"

        return conn.execute(query).fetchall()

    def table_exists(self, ref: TableRef) -> bool:
        """Check if table exists in catalog."""
        resource = self._get_client()
        try:
            tables = resource.client.register_table
            # Try to get table metadata
            import requests

            response = requests.get(
                f"{self.catalog_uri}/v1/namespaces/{ref.namespace}/tables/{ref.name}"
            )
            return response.status_code == 200
        except Exception:
            return False

    def list_tables(self, namespace: str) -> list[str]:
        """List tables in namespace."""
        resource = self._get_client()
        try:
            return resource.client.register_table
        except Exception:
            return []

    def drop_table(self, ref: TableRef) -> None:
        """Drop table from catalog."""
        import requests

        requests.delete(
            f"{self.catalog_uri}/v1/namespaces/{ref.namespace}/tables/{ref.name}"
        )


# ============================================================================
# Unified Storage Manager
# ============================================================================


class UnifiedStorage:
    """Unified storage interface combining all backends."""

    def __init__(
        self,
        table_storage: TableStorage | None = None,
        object_storage: ObjectStorage | None = None,
        vector_storage: VectorStorage | None = None,
    ):
        self._table = table_storage
        self._object = object_storage
        self._vector = vector_storage

    @property
    def tables(self) -> TableStorage:
        """Access table storage."""
        if self._table is None:
            raise RuntimeError("Table storage not configured")
        return self._table

    @property
    def objects(self) -> ObjectStorage:
        """Access object storage."""
        if self._object is None:
            raise RuntimeError("Object storage not configured")
        return self._object

    @property
    def vectors(self) -> VectorStorage:
        """Access vector storage."""
        if self._vector is None:
            raise RuntimeError("Vector storage not configured")
        return self._vector

    # Convenience methods

    def write(
        self,
        namespace: str,
        table: str,
        data: Iterable[dict] | list[dict],
        mode: str = "append",
        primary_key: str | list[str] | None = None,
    ) -> TableWriteResult:
        """Write data to a table."""
        return self.tables.write_table(
            TableRef(namespace, table),
            data,
            mode=mode,
            primary_key=primary_key,
        )

    def read(
        self,
        namespace: str,
        table: str,
        columns: list[str] | None = None,
        filters: dict[str, Any] | None = None,
        limit: int | None = None,
    ) -> Any:
        """Read data from a table."""
        return self.tables.read_table(
            TableRef(namespace, table),
            columns=columns,
            filters=filters,
            limit=limit,
        )

    def put(
        self,
        bucket: str,
        key: str,
        data: bytes | BinaryIO,
        metadata: dict[str, str] | None = None,
    ) -> str:
        """Store an object."""
        return self.objects.put_object(
            ObjectRef(bucket, key),
            data,
            metadata=metadata,
        )

    def get(self, bucket: str, key: str) -> bytes:
        """Retrieve an object."""
        return self.objects.get_object(ObjectRef(bucket, key))


# ============================================================================
# Factory Functions
# ============================================================================


def get_storage(
    storage_type: StorageType | None = None,
    config: dict[str, Any] | None = None,
) -> UnifiedStorage:
    """Get unified storage interface.

    Auto-detects storage type based on environment variables:
    - LAKEKEEPER_CATALOG_URI -> Iceberg
    - POSTGRES_URL -> PostgreSQL
    - DUCKDB_PATH -> DuckDB
    - Default -> DuckDB (./data.duckdb)

    Args:
        storage_type: Explicit storage type (auto-detect if None)
        config: Additional configuration

    Returns:
        UnifiedStorage instance with configured backends
    """
    config = config or {}

    # Auto-detect storage type
    if storage_type is None:
        if os.getenv("LAKEKEEPER_CATALOG_URI"):
            storage_type = StorageType.ICEBERG
        elif os.getenv("POSTGRES_URL") or os.getenv("DATABASE_URL"):
            storage_type = StorageType.POSTGRES
        else:
            storage_type = StorageType.DUCKDB

    # Create table storage
    if storage_type == StorageType.DUCKDB:
        table_storage = DuckDBTableStorage(
            path=config.get("duckdb_path", os.getenv("DUCKDB_PATH", "./data.duckdb")),
            schema=config.get("schema", "main"),
        )
    elif storage_type == StorageType.ICEBERG:
        table_storage = IcebergTableStorage(
            catalog_uri=config.get(
                "catalog_uri",
                os.getenv("LAKEKEEPER_CATALOG_URI", "http://lakekeeper:8181"),
            ),
            warehouse=config.get(
                "warehouse",
                os.getenv("ICEBERG_WAREHOUSE", "s3://garage/warehouse"),
            ),
            namespace=config.get("namespace", "default"),
        )
    else:
        # Default to DuckDB
        table_storage = DuckDBTableStorage()

    # Create object storage (S3/Garage/R2)
    object_storage = S3ObjectStorage(
        endpoint_url=config.get(
            "s3_endpoint",
            os.getenv("GARAGE_ENDPOINT_URL", "http://garage:3900"),
        ),
        aws_access_key_id=config.get(
            "aws_access_key_id",
            os.getenv("GARAGE_ACCESS_KEY", "garage_key"),
        ),
        aws_secret_access_key=config.get(
            "aws_secret_access_key",
            os.getenv("GARAGE_SECRET_KEY", "garage_secret"),
        ),
        region=config.get("region", os.getenv("AWS_REGION", "garage")),
        use_ssl=config.get("use_ssl", False),
    )

    # Vector storage can be added when needed
    vector_storage = None

    return UnifiedStorage(
        table_storage=table_storage,
        object_storage=object_storage,
        vector_storage=vector_storage,
    )


# Singleton instance
_storage_instance: UnifiedStorage | None = None


def get_default_storage() -> UnifiedStorage:
    """Get default storage singleton."""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = get_storage()
    return _storage_instance
