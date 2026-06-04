"""DuckLake Catalog Management.

Provides catalog initialization and schema management for the DuckLake lakehouse
backed by Cloudflare R2.
"""

import os
from pathlib import Path
from typing import Any

import duckdb


class DuckLakeCatalog:
    """Manages the DuckLake catalog for Aleyum portfolio data.

    DuckLake architecture:
    - DuckDB as the SQL catalog (local or remote)
    - Cloudflare R2 as object storage for Parquet files
    - Automatic schema evolution and versioning
    """

    def __init__(
        self,
        catalog_path: str = "./data/aleyum_catalog.duckdb",
        r2_bucket: str = "aleyum-data",
    ):
        """Initialize the DuckLake catalog.

        Args:
            catalog_path: Path to the DuckDB catalog database
            r2_bucket: R2 bucket name for data storage
        """
        self.catalog_path = Path(catalog_path)
        self.r2_bucket = r2_bucket
        self.conn: duckdb.DuckDBPyConnection | None = None

        # R2 configuration
        self.r2_account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "")
        self.r2_access_key = os.environ.get("R2_ACCESS_KEY_ID", "")
        self.r2_secret_key = os.environ.get("R2_SECRET_ACCESS_KEY", "")
        self.r2_endpoint = f"https://{self.r2_account_id}.r2.cloudflarestorage.com"

    def connect(self) -> duckdb.DuckDBPyConnection:
        """Establish connection to the catalog database."""
        if self.conn is None:
            # Ensure directory exists
            self.catalog_path.parent.mkdir(parents=True, exist_ok=True)

            self.conn = duckdb.connect(str(self.catalog_path))
            self._configure_extensions()

        return self.conn

    def _configure_extensions(self) -> None:
        """Load and configure required DuckDB extensions."""
        if self.conn is None:
            return

        # Install and load extensions
        self.conn.execute("INSTALL httpfs")
        self.conn.execute("LOAD httpfs")

        # Configure S3/R2 credentials
        if self.r2_access_key and self.r2_secret_key:
            self.conn.execute(f"""
                SET s3_region='auto';
                SET s3_endpoint='{self.r2_endpoint.replace("https://", "")}';
                SET s3_access_key_id='{self.r2_access_key}';
                SET s3_secret_access_key='{self.r2_secret_key}';
                SET s3_url_style='path';
            """)

    def initialize_schemas(self) -> None:
        """Create the lakehouse schemas and metadata tables."""
        conn = self.connect()

        # Create schemas for different data domains
        conn.execute("""
            CREATE SCHEMA IF NOT EXISTS music;
            CREATE SCHEMA IF NOT EXISTS code;
            CREATE SCHEMA IF NOT EXISTS metadata;
        """)

        # Create catalog metadata table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS metadata.catalog_info (
                table_name VARCHAR PRIMARY KEY,
                schema_name VARCHAR NOT NULL,
                parquet_path VARCHAR,
                row_count BIGINT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                version INTEGER DEFAULT 1
            )
        """)

        # Create music schema tables
        conn.execute("""
            CREATE TABLE IF NOT EXISTS music.spotify_tracks (
                id VARCHAR PRIMARY KEY,
                name VARCHAR NOT NULL,
                album_id VARCHAR,
                album_name VARCHAR,
                artist_id VARCHAR,
                artist_name VARCHAR,
                duration_ms INTEGER,
                popularity INTEGER,
                preview_url VARCHAR,
                external_url VARCHAR,
                image_url VARCHAR,
                image_r2_key VARCHAR,
                -- Audio features
                danceability DOUBLE,
                energy DOUBLE,
                key INTEGER,
                loudness DOUBLE,
                mode INTEGER,
                speechiness DOUBLE,
                acousticness DOUBLE,
                instrumentalness DOUBLE,
                liveness DOUBLE,
                valence DOUBLE,
                tempo DOUBLE,
                time_signature INTEGER,
                -- Metadata
                release_date DATE,
                loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS music.soundcloud_tracks (
                id VARCHAR PRIMARY KEY,
                title VARCHAR NOT NULL,
                permalink VARCHAR,
                description TEXT,
                duration_ms INTEGER,
                genre VARCHAR,
                tag_list VARCHAR,
                -- Stats
                playback_count INTEGER,
                likes_count INTEGER,
                comment_count INTEGER,
                repost_count INTEGER,
                download_count INTEGER,
                -- Media
                artwork_url VARCHAR,
                artwork_r2_key VARCHAR,
                stream_url VARCHAR,
                audio_r2_key VARCHAR,
                waveform_url VARCHAR,
                -- Metadata
                created_at TIMESTAMP,
                loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create code schema tables
        conn.execute("""
            CREATE TABLE IF NOT EXISTS code.github_repos (
                id BIGINT PRIMARY KEY,
                name VARCHAR NOT NULL,
                full_name VARCHAR,
                description TEXT,
                html_url VARCHAR,
                homepage VARCHAR,
                -- Stats
                stargazers_count INTEGER,
                forks_count INTEGER,
                watchers_count INTEGER,
                open_issues_count INTEGER,
                -- Metadata
                language VARCHAR,
                topics VARCHAR[],
                license_name VARCHAR,
                is_fork BOOLEAN,
                is_archived BOOLEAN,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                pushed_at TIMESTAMP,
                loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS code.github_languages (
                repo_id BIGINT,
                language VARCHAR,
                bytes BIGINT,
                percentage DOUBLE,
                PRIMARY KEY (repo_id, language)
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS code.github_commits (
                sha VARCHAR PRIMARY KEY,
                repo_id BIGINT,
                message TEXT,
                author_name VARCHAR,
                author_email VARCHAR,
                author_date TIMESTAMP,
                committer_name VARCHAR,
                committer_date TIMESTAMP,
                additions INTEGER,
                deletions INTEGER,
                loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

    def export_to_parquet(self, table: str, schema: str = "music") -> str:
        """Export a table to Parquet on R2.

        Args:
            table: Table name to export
            schema: Schema name (music, code, metadata)

        Returns:
            R2 path where the parquet file was written
        """
        conn = self.connect()

        r2_path = f"s3://{self.r2_bucket}/lakehouse/{schema}/{table}.parquet"

        conn.execute(f"""
            COPY {schema}.{table}
            TO '{r2_path}'
            (FORMAT PARQUET, COMPRESSION 'zstd')
        """)

        # Update catalog metadata
        row_count = conn.execute(
            f"SELECT COUNT(*) FROM {schema}.{table}"
        ).fetchone()[0]

        conn.execute("""
            INSERT OR REPLACE INTO metadata.catalog_info
            (table_name, schema_name, parquet_path, row_count, last_updated, version)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP,
                    COALESCE((SELECT version + 1 FROM metadata.catalog_info
                              WHERE table_name = ? AND schema_name = ?), 1))
        """, [table, schema, r2_path, row_count, table, schema])

        return r2_path

    def import_from_parquet(self, table: str, schema: str = "music") -> int:
        """Import a table from Parquet on R2.

        Args:
            table: Table name to import
            schema: Schema name

        Returns:
            Number of rows imported
        """
        conn = self.connect()

        r2_path = f"s3://{self.r2_bucket}/lakehouse/{schema}/{table}.parquet"

        # Use INSERT OR REPLACE for upsert behavior
        conn.execute(f"""
            INSERT OR REPLACE INTO {schema}.{table}
            SELECT * FROM read_parquet('{r2_path}')
        """)

        row_count = conn.execute(
            f"SELECT COUNT(*) FROM {schema}.{table}"
        ).fetchone()[0]

        return row_count

    def query(self, sql: str) -> list[tuple[Any, ...]]:
        """Execute a query and return results.

        Args:
            sql: SQL query string

        Returns:
            List of result tuples
        """
        conn = self.connect()
        return conn.execute(sql).fetchall()

    def get_catalog_stats(self) -> dict[str, Any]:
        """Get statistics about the catalog.

        Returns:
            Dictionary with table counts and metadata
        """
        conn = self.connect()

        stats = {
            "tables": {},
            "total_rows": 0,
        }

        # Get table info from catalog
        rows = conn.execute("""
            SELECT table_name, schema_name, row_count, last_updated, version
            FROM metadata.catalog_info
            ORDER BY schema_name, table_name
        """).fetchall()

        for table_name, schema_name, row_count, last_updated, version in rows:
            key = f"{schema_name}.{table_name}"
            stats["tables"][key] = {
                "row_count": row_count,
                "last_updated": str(last_updated) if last_updated else None,
                "version": version,
            }
            stats["total_rows"] += row_count or 0

        return stats

    def close(self) -> None:
        """Close the database connection."""
        if self.conn is not None:
            self.conn.close()
            self.conn = None


def initialize_catalog(
    catalog_path: str = "./data/aleyum_catalog.duckdb",
    r2_bucket: str = "aleyum-data",
) -> DuckLakeCatalog:
    """Initialize and return a configured DuckLake catalog.

    Args:
        catalog_path: Path to DuckDB catalog
        r2_bucket: R2 bucket name

    Returns:
        Configured DuckLakeCatalog instance
    """
    catalog = DuckLakeCatalog(catalog_path, r2_bucket)
    catalog.initialize_schemas()
    return catalog


if __name__ == "__main__":
    # Initialize catalog for local development
    catalog = initialize_catalog()
    print("DuckLake catalog initialized!")

    stats = catalog.get_catalog_stats()
    print(f"Catalog stats: {stats}")

    catalog.close()
